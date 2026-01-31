"""
Moteur Cognitif de Compréhension des Sinistres.
Transforme la transcription brute en structure cognitive exploitable.
"""

import re
from typing import List, Dict, Any
from datetime import datetime
from models.claim_models import (
    CognitiveClaimStructure, 
    ClaimType, 
    Party, 
    Document,
    AmbiguityFlag,
    TranscriptMetadata
)


class CognitiveClaimEngine:
    """
    Moteur d'analyse cognitive pour extraction et structuration 
    des informations d'un sinistre à partir de la transcription.
    """
    
    def __init__(self, use_llm: bool = True, llm_provider: str = "gemini"):
        """
        Initialise le moteur cognitif
        
        Args:
            use_llm: Utiliser un LLM pour l'extraction (recommandé)
            llm_provider: Provider LLM (gemini, groq, openai)
        """
        self.use_llm = use_llm
        self.llm_provider = llm_provider
        self.llm_client = None
        
        if use_llm:
            self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialise le client LLM pour l'extraction cognitive"""
        try:
            # Charger les variables d'environnement
            from dotenv import load_dotenv
            load_dotenv()
            
            if self.llm_provider == "gemini":
                from google import genai
                import os
                api_key = os.getenv("GEMINI_API_KEY")
                if api_key:
                    self.llm_client = genai.Client(api_key=api_key)
                    print("✅ Gemini LLM initialisé (gemini-2.0-flash)")
                    self.llm_model = "models/gemini-2.0-flash"
                else:
                    print("⚠️ GEMINI_API_KEY non définie, mode règles")
                    self.use_llm = False
            elif self.llm_provider == "groq":
                from groq import Groq
                import os
                api_key = os.getenv("GROQ_API_KEY")
                if api_key:
                    self.llm_client = Groq(api_key=api_key)
                    print("✅ Groq LLM initialisé (llama-3.3-70b-versatile)")
                    self.llm_model = "llama-3.3-70b-versatile"
                else:
                    print("⚠️ GROQ_API_KEY non définie, mode règles")
                    self.use_llm = False
            elif self.llm_provider == "openai":
                from openai import OpenAI
                import os
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self.llm_client = OpenAI(api_key=api_key)
                    print("✅ OpenAI LLM initialisé")
                    self.llm_model = "gpt-4o-mini"
                else:
                    print("⚠️ OPENAI_API_KEY non définie, mode règles")
                    self.use_llm = False
            else:
                print("⚠️ Provider LLM non supporté, mode règles")
                self.use_llm = False
        except ImportError as e:
            print(f"⚠️ SDK LLM non installé ({e}), mode règles")
            self.use_llm = False
    
    def analyze_claim(
        self, 
        transcript_metadata: TranscriptMetadata
    ) -> CognitiveClaimStructure:
        """
        Analyse cognitive complète d'une déclaration de sinistre
        
        Args:
            transcript_metadata: Métadonnées de transcription avec texte (dict ou objet)
            
        Returns:
            Structure cognitive du sinistre
        """
        # Support dict et objet
        if isinstance(transcript_metadata, dict):
            text = transcript_metadata["normalized_transcript"]
        else:
            text = transcript_metadata.normalized_transcript
        
        if self.use_llm and self.llm_client:
            return self._analyze_with_llm(text, transcript_metadata)
        else:
            return self._analyze_with_rules(text, transcript_metadata)
    
    def _analyze_with_llm(
        self, 
        text: str, 
        metadata: TranscriptMetadata
    ) -> CognitiveClaimStructure:
        """
        Analyse cognitive avec LLM (extraction structurée)
        """
        prompt = self._build_extraction_prompt(text)
        
        try:
            if self.llm_provider == "gemini":
                # Gemini utilise la nouvelle API
                response = self.llm_client.models.generate_content(
                    model=self.llm_model,
                    contents=f"""Tu es un expert en analyse cognitive de sinistres d'assurance.
Ton rôle est d'extraire et structurer les informations d'une déclaration de sinistre.
Sois précis, factuel, et distingue les faits des suppositions.
Tu dois analyser en français, arabe et darija marocain.
Réponds UNIQUEMENT avec du JSON valide, sans markdown ni texte supplémentaire.

{prompt}""",
                    config={"temperature": 0.1}
                )
                content = response.text
            else:
                # Groq et OpenAI utilisent l'API Chat Completions
                response = self.llm_client.chat.completions.create(
                    model=self.llm_model,
                    messages=[
                        {
                            "role": "system",
                            "content": """Tu es un expert en analyse cognitive de sinistres d'assurance.
                            Ton rôle est d'extraire et structurer les informations d'une déclaration de sinistre.
                            Sois précis, factuel, et distingue les faits des suppositions.
                            Tu dois analyser en français, arabe et darija marocain.
                            Réponds UNIQUEMENT avec du JSON valide, sans markdown ni texte supplémentaire."""
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"} if self.llm_provider == "openai" else None
                )
                content = response.choices[0].message.content
            
            import json
            
            # Nettoyer le markdown si présent
            if "```" in content:
                parts = content.split("```")
                for part in parts:
                    part = part.strip()
                    if part.startswith("json"):
                        content = part[4:].strip()
                        break
                    elif part.startswith("{"):
                        content = part
                        break
            
            # Retirer tout texte avant le premier {
            if "{" in content:
                content = content[content.index("{"):]
            
            # Retirer tout texte après le dernier }
            if "}" in content:
                content = content[:content.rindex("}")+1]
            
            extracted = json.loads(content)
            
            return self._build_cognitive_structure(extracted, metadata)
            
        except Exception as e:
            print(f"❌ Erreur LLM: {e}, fallback sur règles")
            return self._analyze_with_rules(text, metadata)
    
    def _analyze_with_rules(
        self, 
        text: str, 
        metadata: TranscriptMetadata
    ) -> CognitiveClaimStructure:
        """
        Analyse cognitive avec règles expertes (sans LLM)
        """
        text_lower = text.lower()
        
        # 1. Déterminer le type de sinistre
        claim_type, type_confidence = self._classify_claim_type(text_lower)
        
        # 2. Extraire les entités temporelles
        date_incident = self._extract_date(text)
        location = self._extract_location(text)
        
        # 3. Identifier les parties impliquées
        parties = self._extract_parties(text)
        
        # 4. Extraire la description des dommages
        damages = self._extract_damages(text)
        
        # 5. Identifier les documents mentionnés
        documents = self._extract_documents(text)
        
        # 6. Séparer faits et suppositions
        facts, assumptions = self._separate_facts_assumptions(text)
        
        # 7. Détecter les ambiguïtés
        ambiguities = self._detect_ambiguities(text, metadata)
        
        # 8. Construire la timeline
        timeline = self._build_timeline(text, date_incident)
        
        # 9. Identifier les informations manquantes
        missing_info = self._identify_missing_information(
            claim_type, documents, text
        )
        
        # 10. Évaluer le stress émotionnel
        emotional_stress = self._assess_emotional_stress(metadata)
        
        # Support dict et objet pour emotional_markers
        emotional_markers = metadata["emotional_markers"] if isinstance(metadata, dict) else metadata.emotional_markers
        
        # Support dict et objet pour emotional_markers
        emotional_markers = metadata["emotional_markers"] if isinstance(metadata, dict) else metadata.emotional_markers
        
        return CognitiveClaimStructure(
            claim_type=claim_type,
            claim_type_confidence=type_confidence,
            date_incident=date_incident,
            location=location,
            parties_involved=parties,
            damages_description=damages,
            mentioned_documents=documents,
            missing_information=missing_info,
            facts=facts,
            assumptions=assumptions,
            ambiguities=ambiguities,
            timeline_events=timeline,
            emotional_stress_level=emotional_stress,
            emotional_keywords=emotional_markers
        )
    
    def _classify_claim_type(self, text: str) -> tuple:
        """
        Classifie le type de sinistre avec niveau de confiance
        
        Returns:
            (ClaimType, confidence_score)
        """
        type_keywords = {
            ClaimType.AUTO: [
                "voiture", "véhicule", "accident", "collision", "pare-choc",
                "carrosserie", "autoroute", "route", "stationnement", "constat amiable"
            ],
            ClaimType.HOME: [
                "maison", "appartement", "domicile", "dégât des eaux", "incendie",
                "cambriolage", "vol", "fenêtre", "toiture", "inondation"
            ],
            ClaimType.HEALTH: [
                "santé", "médical", "hôpital", "blessure", "fracture", "soins",
                "docteur", "médecin", "hospitalisation", "maladie"
            ],
            ClaimType.TRAVEL: [
                "voyage", "avion", "bagage", "annulation", "retard", "vol annulé",
                "hôtel", "vacances", "étranger"
            ],
            ClaimType.LIABILITY: [
                "responsabilité civile", "dommage causé", "tiers", "préjudice",
                "responsable", "faute"
            ]
        }
        
        scores = {}
        for claim_type, keywords in type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                scores[claim_type] = score
        
        if not scores:
            return ClaimType.UNKNOWN, 0.0
        
        best_type = max(scores, key=scores.get)
        max_score = scores[best_type]
        total_keywords = len(type_keywords[best_type])
        confidence = min(1.0, max_score / (total_keywords * 0.3))
        
        return best_type, confidence
    
    def _extract_date(self, text: str) -> str:
        """Extrait la date de l'incident"""
        # Patterns de dates
        date_patterns = [
            r"hier( soir| matin)?",
            r"aujourd'hui",
            r"la semaine dernière",
            r"\d{1,2}\/\d{1,2}\/\d{2,4}",
            r"\d{1,2}\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)",
            r"il y a \d+ jours?",
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return "date non précisée"
    
    def _extract_location(self, text: str) -> str:
        """Extrait le lieu de l'incident"""
        # Patterns de lieux
        location_patterns = [
            r"sur (l'autoroute|la route|l'avenue|le boulevard) [A-Z0-9\s]+",
            r"à [A-Z][a-zéèêà]+(?: [A-Z][a-zéèêà]+)?",
            r"près de [A-Z][a-zéèêà]+",
            r"sortie \d+",
            r"parking (de|du) [A-Z][a-zéèêà]+"
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return "lieu non précisé"
    
    def _extract_parties(self, text: str) -> List[Party]:
        """Identifie les parties impliquées"""
        parties = []
        text_lower = text.lower()
        
        # Assuré (toujours présent)
        parties.append(Party(
            name="Déclarant",
            role="assuré",
            involvement="victime/déclarant"
        ))
        
        # Tiers impliqué
        if any(word in text_lower for word in ["autre", "conducteur", "tiers", "percuté"]):
            parties.append(Party(
                name="Tiers",
                role="tiers_impliqué",
                involvement="partie adverse"
            ))
        
        # Témoins
        if "témoin" in text_lower:
            parties.append(Party(
                name="Témoin(s)",
                role="témoin",
                involvement="observateur"
            ))
        
        return parties
    
    def _extract_damages(self, text: str) -> str:
        """Extrait la description des dommages"""
        damage_keywords = [
            "pare-choc", "coffre", "portière", "aile", "phare", "rétroviseur",
            "brisé", "cassé", "enfoncé", "rayé", "bosselé", "endommagé"
        ]
        
        sentences = text.split('.')
        damage_sentences = []
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in damage_keywords):
                damage_sentences.append(sentence.strip())
        
        if damage_sentences:
            return ". ".join(damage_sentences)
        
        return "Dommages à évaluer"
    
    def _extract_documents(self, text: str) -> List[Document]:
        """Identifie les documents mentionnés ou requis"""
        documents = []
        text_lower = text.lower()
        
        doc_mentions = {
            "constat amiable": "constat",
            "photos": "photo",
            "facture": "facture",
            "devis": "devis",
            "rapport": "rapport",
            "certificat": "certificat"
        }
        
        for mention, doc_type in doc_mentions.items():
            if mention in text_lower:
                documents.append(Document(
                    type=doc_type,
                    status="mentionné",
                    required=True
                ))
        
        # Documents standards requis selon le contexte
        if "accident" in text_lower or "collision" in text_lower:
            if not any(d.type == "constat" for d in documents):
                documents.append(Document(
                    type="constat_amiable",
                    status="manquant",
                    required=True,
                    description="Constat amiable d'accident"
                ))
        
        return documents
    
    def _separate_facts_assumptions(self, text: str) -> tuple:
        """Sépare les faits avérés des suppositions"""
        facts = []
        assumptions = []
        
        assumption_markers = [
            "je pense", "je crois", "peut-être", "probablement",
            "il me semble", "j'imagine", "je suppose"
        ]
        
        sentences = text.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            is_assumption = any(marker in sentence.lower() for marker in assumption_markers)
            
            if is_assumption:
                assumptions.append(sentence)
            else:
                # Faits = affirmations directes
                if len(sentence.split()) > 4:  # Phrases significatives
                    facts.append(sentence)
        
        return facts, assumptions
    
    def _detect_ambiguities(
        self, 
        text: str, 
        metadata: TranscriptMetadata
    ) -> List[AmbiguityFlag]:
        """Détecte les zones d'ambiguïté ou d'incertitude"""
        ambiguities = []
        
        # Ambiguïté temporelle
        if "date non précisée" in self._extract_date(text):
            ambiguities.append(AmbiguityFlag(
                category="temporelle",
                description="Date de l'incident imprécise",
                severity=3,
                impact_on_decision="Peut retarder le traitement"
            ))
        
        # Ambiguïté factuelle (trop de suppositions)
        _, assumptions = self._separate_facts_assumptions(text)
        if len(assumptions) > 2:
            ambiguities.append(AmbiguityFlag(
                category="factuelle",
                description=f"{len(assumptions)} suppositions vs faits certains",
                severity=2,
                impact_on_decision="Nécessite clarification"
            ))
        
        # Ambiguïté émotionnelle (stress élevé)
        hesitations = metadata["hesitations"] if isinstance(metadata, dict) else metadata.hesitations
        if hesitations > 5:
            ambiguities.append(AmbiguityFlag(
                category="émotionnelle",
                description=f"Nombreuses hésitations ({hesitations})",
                severity=2,
                impact_on_decision="Client sous stress, possibles omissions"
            ))
        
        return ambiguities
    
    def _build_timeline(self, text: str, date_incident: str) -> List[Dict[str, str]]:
        """Construit une timeline des événements"""
        timeline = []
        
        # Événement principal
        timeline.append({
            "moment": date_incident,
            "événement": "Incident principal",
            "description": "Sinistre déclaré"
        })
        
        # Événements post-incident
        if "constat" in text.lower():
            timeline.append({
                "moment": "Immédiatement après",
                "événement": "Constat amiable",
                "description": "Constat établi avec le tiers"
            })
        
        if "photos" in text.lower() or "photo" in text.lower():
            timeline.append({
                "moment": "Sur les lieux",
                "événement": "Documentation photographique",
                "description": "Prises de photos des dommages"
            })
        
        # Déclaration
        timeline.append({
            "moment": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "événement": "Déclaration au système",
            "description": "Enregistrement vocal du sinistre"
        })
        
        return timeline
    
    def _identify_missing_information(
        self, 
        claim_type: ClaimType, 
        documents: List[Document],
        text: str
    ) -> List[str]:
        """Identifie les informations manquantes critiques"""
        missing = []
        text_lower = text.lower()
        
        # Informations génériques
        if "numéro de police" not in text_lower and "contrat" not in text_lower:
            missing.append("Numéro de police d'assurance")
        
        # Spécifique automobile
        if claim_type == ClaimType.AUTO:
            if not any(d.type == "constat" for d in documents):
                missing.append("Constat amiable")
            if "immatriculation" not in text_lower:
                missing.append("Numéro d'immatriculation du véhicule")
        
        # Spécifique habitation
        if claim_type == ClaimType.HOME:
            if "devis" not in text_lower:
                missing.append("Devis de réparation")
        
        return missing
    
    def _assess_emotional_stress(self, metadata) -> int:
        """Évalue le niveau de stress émotionnel (0-10)"""
        stress_score = 0
        
        # Support dict et objet
        hesitations = metadata["hesitations"] if isinstance(metadata, dict) else metadata.hesitations
        emotional_markers = metadata["emotional_markers"] if isinstance(metadata, dict) else metadata.emotional_markers
        
        # Basé sur les hésitations
        stress_score += min(3, hesitations // 2)
        
        # Basé sur les marqueurs émotionnels
        stress_markers = {"stress", "urgence", "colère", "confusion"}
        detected_stress = stress_markers.intersection(set(emotional_markers))
        stress_score += len(detected_stress) * 2
        
        return min(10, stress_score)
    
    def _build_extraction_prompt(self, text: str) -> str:
        """Construit le prompt pour extraction LLM"""
        return f"""
        Analyse la déclaration de sinistre suivante et extrais les informations structurées.
        
        DÉCLARATION:
        {text}
        
        Extrais et retourne un JSON avec:
        - claim_type: type de sinistre (automobile, habitation, santé, etc.)
        - confidence: niveau de confiance (0-1)
        - date_incident: date mentionnée
        - location: lieu de l'incident
        - parties: liste des personnes/entités impliquées
        - damages: description des dommages
        - documents_mentioned: documents évoqués
        - facts: liste des faits avérés
        - assumptions: liste des suppositions
        - missing_info: informations manquantes critiques
        - emotional_level: niveau émotionnel (0-10)
        
        Sois factuel, précis, et distingue clairement faits et suppositions.
        """
    
    def _build_cognitive_structure(
        self, 
        extracted_data: dict, 
        metadata: TranscriptMetadata
    ) -> CognitiveClaimStructure:
        """Construit la structure cognitive depuis les données LLM"""
        # Mapping du type de sinistre
        type_mapping = {
            "automobile": ClaimType.AUTO,
            "habitation": ClaimType.HOME,
            "santé": ClaimType.HEALTH,
            "vie": ClaimType.LIFE,
            "voyage": ClaimType.TRAVEL,
            "responsabilité_civile": ClaimType.LIABILITY
        }
        
        claim_type_str = extracted_data.get("claim_type", "indéterminé")
        claim_type = type_mapping.get(claim_type_str, ClaimType.UNKNOWN)
        
        # Construire les parties (gérer à la fois str et dict)
        parties = []
        for p in extracted_data.get("parties", []):
            if isinstance(p, str):
                # Chaîne simple
                parties.append(Party(name=p, role="partie_impliquée", involvement=None))
            elif isinstance(p, dict):
                # Dictionnaire
                parties.append(Party(
                    name=p.get("name", ""),
                    role=p.get("role", ""),
                    involvement=p.get("involvement")
                ))
        
        # Construire les documents
        documents = [
            Document(type=d, status="mentionné", required=True)
            for d in extracted_data.get("documents_mentioned", [])
        ]
        
        # Support dict et objet
        emotional_markers = metadata["emotional_markers"] if isinstance(metadata, dict) else metadata.emotional_markers
        
        return CognitiveClaimStructure(
            claim_type=claim_type,
            claim_type_confidence=extracted_data.get("confidence", 0.7),
            date_incident=extracted_data.get("date_incident"),
            location=extracted_data.get("location"),
            parties_involved=parties,
            damages_description=extracted_data.get("damages", ""),
            mentioned_documents=documents,
            missing_information=extracted_data.get("missing_info", []),
            facts=extracted_data.get("facts", []),
            assumptions=extracted_data.get("assumptions", []),
            ambiguities=[],
            timeline_events=[],
            emotional_stress_level=extracted_data.get("emotional_level", 5),
            emotional_keywords=emotional_markers
        )
