"""
Conversation Manager - Flux conversationnel réaliste CRM.
Gère les phases de conversation avec contexte persistant.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)

# Enums (using same as schema definitions)
class ConversationPhaseEnum(str, Enum):
    AUTHENTIFICATION = "authentification"
    DESCRIPTION = "description"
    SINISTRE_DETAILS = "sinistre_details"
    DOCUMENTS = "documents"
    DECISION = "decision"
    TRANSFERT = "transfert"
    SUIVI = "suivi"

class StatusDossierEnum(str, Enum):
    NOUVEAU = "nouveau"
    EN_COURS = "en_cours"
    EXPERT = "expert"
    VALIDATION = "validation"
    ESCALADE = "escalade"
    EN_ATTENTE_CLIENT = "en_attente_client"
    FERME = "fermé"

class TypeTraitementEnum(str, Enum):
    AUTONOME = "autonome"
    ESCALADE = "escalade"
    EXPERT = "expert"

class ConversationManager:
    """Gère le flux complet de conversation multi-tours"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.contexte = None
        self.client = None
        self.sinistre = None
        self.phase_actuelle = ConversationPhaseEnum.AUTHENTIFICATION
        
    # ==================== PHASE 1: AUTHENTIFICATION ====================
    
    def get_greeting(self) -> Dict[str, Any]:
        """Salutation initiale + demande matricule"""
        return {
            "phase": ConversationPhaseEnum.AUTHENTIFICATION,
            "message": "Assistant sinistre, Bonjour! pouvez-vous me donner votre numéro de matricule?",
            "action": "attendre_matricule",
            "expected_input": "matricule"
        }
    
    def verifier_matricule(self, matricule: str, clients_db: Dict[str, Any]) -> Dict[str, Any]:
        """Vérifie matricule en BDD et charge données client"""
        matricule_clean = matricule.upper().strip()
        
        # Chercher le client
        client = None
        for cid, c in clients_db.items():
            if c.matricule.upper() == matricule_clean:
                client = c
                break
        
        if not client:
            return {
                "valide": False,
                "message": "Je n'ai pas trouvé ce numéro de matricule. Pouvez-vous vérifier et réessayer?",
                "action": "redemander_matricule"
            }
        
        self.client = client
        return {
            "valide": True,
            "client_id": client.id,
            "message": f"Merci! Vous êtes bien {client.civilite.value if client.civilite else ''} {client.nom} {client.prenom}?",
            "action": "confirmer_identite",
            "next_phase": ConversationPhaseEnum.DESCRIPTION
        }
    
    def confirmer_identite(self, confirmation: str) -> Dict[str, Any]:
        """Confirme l'identité et passe à phase suivante"""
        # Normaliser la réponse STT
        response = confirmation.lower().strip()
        response = re.sub(r"[\.,;:!\?\-\_\(\)\[\]\"']", " ", response)
        response = re.sub(r"\s+", " ", response).strip()

        # Variantes positives courantes (STT)
        positive_phrases = {
            "oui",
            "yes",
            "ouais",
            "ok",
            "oui c est moi",
            "oui c est bien moi",
            "c est moi",
            "c est bien moi",
            "c est exact",
            "c est correct",
            "exact",
            "exactement",
            "tout a fait",
            "oui je confirme",
            "je confirme",
            "oui c est bien mon contrat",
            "vous avez la bonne personne",
            "oui vous avez la bonne personne",
            # Darija (transcription STT simplifiée)
            "iyah",
            "iyah ana",
            "iyah ana howa",
            "iyah hadchi howa",
            "ana",
            "ana howa",
            "ana li",
            "mzyan",
            "sahih",
            "wakha",
            "na3am",
        }

        # Variantes négatives
        negative_phrases = {
            "non",
            "pas moi",
            "ce n est pas moi",
            "c est pas moi",
            "vous n avez pas la bonne personne",
            "mauvaise personne",
            "erreur",
            # Darija (transcription STT simplifiée)
            "la",
            "la machi ana",
            "machi ana",
            "mashi ana",
            "ghalat",
        }

        if response in positive_phrases:
            self.phase_actuelle = ConversationPhaseEnum.DESCRIPTION
            return {
                "confirme": True,
                "message": "Parfait! Pouvez-vous m'expliquer brièvement ce qui s'est passé?",
                "action": "attendre_description",
                "next_phase": ConversationPhaseEnum.DESCRIPTION
            }
        elif response in negative_phrases:
            return {
                "confirme": False,
                "message": "D'accord, recommençons. Quel est votre numéro de matricule?",
                "action": "restart_authentification",
                "next_phase": ConversationPhaseEnum.AUTHENTIFICATION
            }
        else:
            return {
                "confirme": False,
                "message": "Je n'ai pas bien compris. Pouvez-vous confirmer si c'est bien vous?",
                "action": "confirmer_identite",
                "next_phase": ConversationPhaseEnum.AUTHENTIFICATION
            }
    
    # ==================== PHASE 2: DESCRIPTION SINISTRE ====================
    
    def analyser_description(self, description: str, stt_confidence: float = 1.0) -> Dict[str, Any]:
        """
        Analyse la description du sinistre.
        - Détecte type sinistre
        - Extrait entités (date, lieu, tiers)
        - Commence analyse cognitive
        """
        self.phase_actuelle = ConversationPhaseEnum.SINISTRE_DETAILS
        
        # Détection type sinistre simple (règles)
        type_sinistre = self._detecter_type_sinistre(description)
        
        # Extraction entités
        entites = self._extraire_entites(description)
        
        # Augmenter CCI basé sur complétude description
        cci_score = self._calculer_cci_description(description, entites)
        
        # Question suivante basée sur type sinistre
        questions_contexte = self._generer_questions_contexte(type_sinistre)
        
        return {
            "type_sinistre": type_sinistre,
            "entites": entites,
            "cci_score": cci_score,
            "stt_confidence": stt_confidence,
            "message": f"D'accord, je comprends que vous avez eu un sinistre de type {type_sinistre}. {questions_contexte[0] if questions_contexte else ''}",
            "next_questions": questions_contexte,
            "next_phase": ConversationPhaseEnum.SINISTRE_DETAILS
        }
    
    # ==================== PHASE 3: QUESTIONS CONTEXTUELLES ====================
    
    def poser_questions_details(self, type_sinistre: str) -> List[Dict[str, str]]:
        """Génère questions basées sur type sinistre"""
        questions = {
            "collision": [
                "Y a-t-il des blessés ou une douleur physique, même légère?",
                "Un constat amiable a-t-il été rempli ou la police est-elle intervenue?",
                "Avez-vous des photos ou des documents à nous envoyer?"
            ],
            "vol": [
                "Avez-vous porté plainte à la police?",
                "Quels sont les biens volés ou endommagés?",
                "Pouvez-vous nous envoyer l'inventaire et les photos?"
            ],
            "incendie": [
                "Toutes les personnes sont-elles en sécurité?",
                "Avez-vous une estimation des dégâts?",
                "Des experts ont-ils été contactés?"
            ],
            "blessure": [
                "Avez-vous consulté un médecin?",
                "Avez-vous une déclaration médicale?",
                "Y a-t-il des témoins?"
            ]
        }
        
        return [{
            "question": q,
            "type": "oui_non",
            "phase": ConversationPhaseEnum.SINISTRE_DETAILS
        } for q in questions.get(type_sinistre, [])]
    
    # ==================== PHASE 4: DOCUMENTS ====================
    
    def demander_documents(self) -> Dict[str, Any]:
        """Demande documents/photos"""
        self.phase_actuelle = ConversationPhaseEnum.DOCUMENTS
        
        return {
            "message": "Pouvez-vous nous envoyer les documents pertinents? (constat, photos, factures, etc.)",
            "documents_attendus": [
                "constat_amiable",
                "photos_dommage",
                "proces_verbal",
                "factures"
            ],
            "action": "attendre_documents"
        }
    
    # ==================== PHASE 5: DÉCISION ====================
    
    def evaluer_decision(self, cci_score: int, data_sinistre: Dict[str, Any]) -> Dict[str, Any]:
        """
        Évalue: traitement autonome vs escalade
        Basé sur CCI + règles métier
        """
        self.phase_actuelle = ConversationPhaseEnum.DECISION
        
        # Règles d'escalade
        triggers_escalade = [
            cci_score > 60,
            data_sinistre.get("blessures", False),
            data_sinistre.get("tiers_responsable_incertain", False),
            not data_sinistre.get("constat_amiable", False),
            not data_sinistre.get("documents_complets", False)
        ]
        
        escalade_requiree = any(triggers_escalade)
        
        if escalade_requiree:
            type_traitement = TypeTraitementEnum.ESCALADE
            message = (
                "Ce sinistre nécessite une attention particulière. "
                "Je vais vous transférer à un conseiller spécialisé pour une meilleure prise en charge. "
                "Un moment s'il vous plaît..."
            )
            next_phase = ConversationPhaseEnum.TRANSFERT
        else:
            type_traitement = TypeTraitementEnum.AUTONOME
            message = (
                "Votre déclaration est enregistrée et peut être traitée automatiquement. "
                "Un garage agréé vous sera proposé sous 24 heures. "
                "Les frais médicaux sont couverts si la douleur persiste. "
                "Souhaitez-vous avoir d'autres informations sur votre contrat?"
            )
            next_phase = ConversationPhaseEnum.DECISION
        
        return {
            "cci_score": cci_score,
            "type_traitement": type_traitement,
            "escalade_requiree": escalade_requiree,
            "message": message,
            "audio": True,
            "next_phase": next_phase,
            "actions": self._generer_actions(type_traitement, data_sinistre)
        }
    
    # ==================== PHASE 6: TRANSFERT ====================
    
    def preparer_transfert(self, sinistre_id: str) -> Dict[str, Any]:
        """Prépare transfert vers conseiller"""
        self.phase_actuelle = ConversationPhaseEnum.TRANSFERT
        
        return {
            "sinistre_id": sinistre_id,
            "message_audio": "Je vais vous transférer vers un conseiller spécialisé en sinistre complexe. Merci de patienter un instant.",
            "action": "escalader_sinistre",
            "rechercher_conseiller": True,
            "timeout_attente": 30  # secondes
        }
    
    # ==================== PHASE 7: SUIVI DOSSIER ====================
    
    def suivi_dossier(self, sinistre_id: str) -> Dict[str, Any]:
        """Requête client demandant suivi dossier existant"""
        self.phase_actuelle = ConversationPhaseEnum.SUIVI
        
        return {
            "message": f"Vous pouvez suivre votre dossier {sinistre_id} en temps réel. État actuel: EN_COURS. Dernière mise à jour: il y a 2 heures.",
            "dossier_info": {
                "numero": sinistre_id,
                "status": "en_cours",
                "derniere_update": "il y a 2 heures",
                "etape": "En attente des documents"
            },
            "actions_disponibles": [
                "consulter_remboursement",
                "envoyer_documents",
                "consulter_garanties"
            ]
        }
    
    # ==================== HELPERS ====================
    
    def _detecter_type_sinistre(self, texte: str) -> str:
        """Détecte type sinistre par mots-clés"""
        texte_lower = texte.lower()
        
        patterns = {
            "collision": r"(accident|percuté|choc|collision|percute|arrière)",
            "vol": r"(vol|volé|voler|disparu)",
            "incendie": r"(feu|incendie|brûlé|flamme)",
            "blessure": r"(blessur|douleur|mal|cou|dos|blessé)",
            "dommage_materiel": r"(dégât|endommagé|cassé|fenêtre)"
        }
        
        for type_sin, pattern in patterns.items():
            if re.search(pattern, texte_lower):
                return type_sin
        
        return "dommage_materiel"
    
    def _extraire_entites(self, texte: str) -> Dict[str, Any]:
        """Extrait entités (date, lieu, tiers) du texte"""
        return {
            "date": self._extraire_date(texte),
            "lieu": self._extraire_lieu(texte),
            "tiers": self._detecter_tiers(texte)
        }
    
    def _extraire_date(self, texte: str) -> Optional[str]:
        """Extrait date du texte"""
        # Implémentation simple
        return None
    
    def _extraire_lieu(self, texte: str) -> Optional[str]:
        """Extrait lieu du texte"""
        # Implémentation simple
        return None
    
    def _detecter_tiers(self, texte: str) -> bool:
        """Détecte si tiers impliqué"""
        return bool(re.search(r"(autre|tiers|voiture|personne|conducteur)", texte.lower()))
    
    def _calculer_cci_description(self, description: str, entites: Dict) -> int:
        """Calcule CCI basé sur description"""
        score = 20  # Base
        
        if len(description) > 100:
            score += 10
        if entites.get("tiers"):
            score += 15
        if entites.get("date"):
            score += 5
        
        return min(100, score)
    
    def _generer_questions_contexte(self, type_sinistre: str) -> List[str]:
        """Génère première question contexte"""
        questions = {
            "collision": "Y a-t-il des blessés ou une douleur physique?",
            "vol": "Avez-vous porté plainte à la police?",
            "incendie": "Toutes les personnes sont-elles en sécurité?",
        }
        return [questions.get(type_sinistre, "Pouvez-vous nous donner plus de détails?")]
    
    def _generer_actions(self, type_traitement: TypeTraitementEnum, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Génère liste actions à effectuer"""
        actions = []
        
        if not data.get("constat_amiable"):
            actions.append({
                "type": "envoyer_constat",
                "description": "Envoyer le constat amiable",
                "priorite": "haute"
            })
        
        if not data.get("documents_complets"):
            actions.append({
                "type": "envoyer_documents",
                "description": "Envoyer photos et documents",
                "priorite": "haute"
            })
        
        if data.get("blessures"):
            actions.append({
                "type": "consulter_medical",
                "description": "Prendre RDV médecin",
                "priorite": "normale"
            })
        
        actions.append({
            "type": "expertise",
            "description": "Planifier expertise",
            "priorite": "normale"
        })
        
        return actions
    # ==================== MÉTHODES SUPPLÉMENTAIRES ====================

    def ask_description(self) -> str:
        """Demander description du sinistre"""
        return "Merci! Pouvez-vous me décrire ce qui s'est passé? Les détails nous aident à traiter votre dossier plus rapidement."

    def suivi_dossier(self, sinistres, db) -> str:
        """Afficher options de suivi pour dossiers existants"""
        if len(sinistres) == 1:
            return f"Je vois que vous avez un dossier en cours: {sinistres[0].numero_sinistre}. C'est celui-ci que vous voulez suivre?"
        else:
            return f"Vous avez {len(sinistres)} dossiers actifs. Lequel voulez-vous suivre?"

    def suivi_message_autonome(self, numero_sinistre: str) -> str:
        """Message de fin pour traitement autonome"""
        return f"""Parfait! J'ai tous les éléments. Voici votre numéro de dossier: {numero_sinistre}

Vous allez recevoir un email avec les détails de votre dossier et les prochaines étapes.
L'expert vous contactera sous 48 heures pour planifier l'expertise.

Vous pouvez suivre votre dossier à tout moment sur notre portail client avec votre matricule.

Merci et au revoir!"""

    def preparer_transfert(self, sinistre_id: str) -> str:
        """Message de transfert vers conseiller"""
        return """Je vais vous transférer vers l'un de nos conseillers spécialisés.

Il aura accès à toutes les informations que vous m'avez données et pourra mieux vous accompagner.
Merci de patienter quelques instants..."""

    def calculer_cci_incremental(self, reponse: str) -> int:
        """Calculer incrément CCI basé sur la réponse"""
        cci = 0
        reponse_lower = reponse.lower()
        
        if "oui" in reponse_lower or "correct" in reponse_lower:
            cci += 10
        if "blessure" in reponse_lower or "mal" in reponse_lower or "douleur" in reponse_lower:
            cci += 15
        if "document" in reponse_lower or "constat" in reponse_lower or "photos" in reponse_lower:
            cci += 10
        if "tiers" in reponse_lower or "autre" in reponse_lower:
            cci += 5
        
        return cci

    @property
    def current_phase(self):
        """Getter phase actuelle"""
        return self.phase_actuelle.value

    @current_phase.setter
    def current_phase(self, value: str):
        """Setter phase actuelle"""
        try:
            self.phase_actuelle = ConversationPhaseEnum(value)
        except ValueError:
            logger.warning(f"Phase inconnue: {value}")