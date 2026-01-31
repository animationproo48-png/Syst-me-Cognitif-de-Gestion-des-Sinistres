"""
Module Speech-to-Text (STT) Intelligent pour ClaimAI.
Fonctionnalités :
1. Transcription Audio (Priorité API LemonFox, Fallback Local Faster-Whisper)
2. Auto-détection langue
3. Traduction Automatique (Darija -> Français Pro via Groq)
"""

import os
import re
import requests
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Import pour les type hints uniquement
from models.claim_models import TranscriptMetadata


# --- Moteur Principal ---
class STTEngine:
    def __init__(self, model_name: str = "large-v3", use_api: bool = True):
        """
        Initialise le moteur STT.
        Args:
            model_name: Modèle Whisper (large-v3 est vital pour le Darija).
            use_api: Si True, tente d'utiliser LemonFox avant le modèle local.
        """
        load_dotenv()
        self.api_key = os.getenv("WHISPER_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")  # Seulement Groq pour la traduction
        self.model_name = model_name
        self.use_api = use_api
        self.local_model = None
        
        # --- LE SECRET DU DARIJA ---
        # Ce prompt force l'IA à rester dans le contexte dialectal marocain + assurance
        self.darija_prompt = (
            "هاد التسجيل فيه الدارجة المغربية ديال واحد السيد دار كسيدة. "
            "السيارة، الكسيدة، الموتور، لوتوروت، كاين، بزاف، دابا، واخا، صافي، "
            "الكونصطا، لاسيرونس، الطوموبيل، البارشو، الباربريز."
        )

        # Chargement préventif du modèle local si pas d'API
        if not use_api or not self.api_key:
            self._load_local_model()

    def _load_local_model(self):
        """Charge Faster-Whisper (optimisé CPU/GPU)."""
        try:
            from faster_whisper import WhisperModel
            print(f"📥 Chargement du modèle local '{self.model_name}' (Fallback)...")
            # compute_type="int8" permet de faire tourner le gros modèle sur un CPU standard
            self.local_model = WhisperModel(self.model_name, device="cpu", compute_type="int8")
            print("✅ Modèle local prêt.")
        except ImportError:
            print("⚠️ Module 'faster-whisper' non trouvé. Le mode local ne fonctionnera pas.")

    def transcribe_audio(self, audio_path: str, language: str = None) -> Optional[TranscriptMetadata]:
        """
        Fonction principale : Transcrit ET Traduit.
        STRATÉGIE: Auto-détection de langue, transcription fidèle, puis traduction si arabe.
        
        Args:
            audio_path: Chemin du fichier audio
            language: Langue forcée (fr, ar, en) - Si None, auto-détection
        """
        if not os.path.exists(audio_path):
            print(f"❌ Fichier introuvable : {audio_path}")
            return None

        metadata = None

        # ÉTAPE 1 : TRANSCRIPTION AVEC LANGUE FORCÉE OU AUTO-DÉTECTION
        # --------------------------------------------
        if self.use_api and self.api_key:
            try:
                metadata = self._transcribe_with_api(audio_path, use_prompt=False, force_language=language)
            except Exception as e:
                print(f"⚠️ Erreur API LemonFox ({e}). Passage en local...")
        
        # Fallback Local si l'API a échoué ou n'est pas active
        if metadata is None and self.local_model:
            metadata = self._transcribe_with_local_model(audio_path, language)

        # Si tout a échoué
        if metadata is None:
            return self._simulate_error()

        # ÉTAPE 2 : TRADUCTION SI LANGUE ARABE DÉTECTÉE
        # -----------------------------------------------
        # Vérifier toutes les variantes d'arabe (ar, ara, arabic, ar-MA, ar-EG, etc.)
        detected_lang = metadata.language.lower() if metadata.language else ""
        is_arabic = any(marker in detected_lang for marker in ["ar", "arabic", "عربي"])
        
        # Si langue inconnue, vérifier si le texte contient des caractères arabes
        if not is_arabic and detected_lang in ["unknown", "", "none"]:
            has_arabic_chars = bool(re.search(r'[\u0600-\u06FF]', metadata.original_transcript))
            if has_arabic_chars:
                is_arabic = True
                print("🔍 Détection: Caractères arabes trouvés dans le texte")
        
        if is_arabic:
            if self.groq_key:
                print(f"🤖 Langue arabe détectée - Lancement traduction Groq...")
                translation = self._translate_with_llm(metadata.original_transcript)
                
                if translation:
                    metadata.normalized_transcript = translation
                    print(f"✅ Traduction: {translation[:80]}...")
                else:
                    print("⚠️ Traduction échouée, conservation du texte original.")
            else:
                print("⚠️ Pas de clé Groq - traduction désactivée")
        else:
            print(f"ℹ️ Langue détectée: {metadata.language} - Pas de traduction nécessaire")

        return metadata

    def _transcribe_with_api(self, audio_path: str, use_prompt: bool = False, force_language: str = None) -> TranscriptMetadata:
        """Appel API LemonFox avec option de forcer la langue."""
        url = "https://api.lemonfox.ai/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        with open(audio_path, 'rb') as f:
            files = {"file": f}
            data = {
                "response_format": "json"
            }
            
            # Si une langue est forcée, l'ajouter
            if force_language:
                data["language"] = force_language
                print(f"🌐 Envoi à LemonFox (langue forcée: {force_language})...")
            else:
                print(f"🌐 Envoi à LemonFox (auto-détection langue pure)...")
            
            response = requests.post(url, headers=headers, files=files, data=data)
            response.raise_for_status()

        result = response.json()
        text = result.get("text", "").strip()
        detected_lang = force_language if force_language else result.get("language", "unknown")
        
        print(f"📝 Langue: {detected_lang}")
        print(f"📝 Transcription: {text[:80]}...")
        
        # Retourner un objet Pydantic TranscriptMetadata
        return TranscriptMetadata(
            original_transcript=text,
            normalized_transcript=self._basic_cleanup(text),
            language=detected_lang,
            confidence_score=result.get("confidence", 0.9),
            emotional_markers=self._detect_emotions(text),
            hesitations=self._count_hesitations(text),
            duration_seconds=result.get("duration", 0.0)
        )

    def _transcribe_with_local_model(self, audio_path: str, language: str) -> TranscriptMetadata:
        """Utilisation de Faster-Whisper en local."""
        print("🖥️ Transcription locale en cours...")
        segments, info = self.local_model.transcribe(
            audio_path, 
            language=language, 
            initial_prompt=self.darija_prompt,
            vad_filter=True # Supprime les silences avant transcription
        )
        
        full_text = " ".join([seg.text for seg in segments]).strip()
        
        # Retourner un objet Pydantic TranscriptMetadata
        return TranscriptMetadata(
            original_transcript=full_text,
            normalized_transcript=self._basic_cleanup(full_text),
            language=info.language,
            confidence_score=info.language_probability,
            emotional_markers=self._detect_emotions(full_text),
            hesitations=self._count_hesitations(full_text),
            duration_seconds=info.duration
        )

    def _translate_with_llm(self, text: str) -> Optional[str]:
        """Traduction via Groq avec prompt enrichi et dictionnaire darija."""
        
        if not self.groq_key:
            print("⚠️ Clé Groq manquante, traduction impossible")
            return None
        
        try:
            from groq import Groq
            client = Groq(api_key=self.groq_key)
            
            # Instructions système pour le modèle
            system_prompt = (
                "Tu es un expert en traduction du Darija marocain vers le français professionnel pour les assurances. "
                "Traduis fidèlement le texte suivant en utilisant le dictionnaire de référence. "
                "Si le texte est déjà en français, corrige simplement la syntaxe."
            )
            
            # Dictionnaire darija marocain -> français (contexte assurance)
            context_dictionary = """
DICTIONNAIRE DARIJA MAROCAIN → FRANÇAIS (Assurance Automobile):

Véhicule & Accident:
- الطوموبيل / الطونوبيل / لوطو = la voiture, le véhicule
- الكسيدة/كسيدة / لكسيدة = l'accident
- درت كسيدة = j'ai eu un accident
- تصادم = collision, accrochage
- لوتوروت = l'autoroute
- الطريق = la route
- لباربريز = le pare-brise
- الموتور = la moto
- الفرامل = les freins
- الرويضة = les roues
- لكابو = le capot
- لبارشو = le pare-chocs
- صدمة / صدام = choc, impact

Parties & Responsabilité:
- دار معايا = il m'a percuté
- صدمني = il m'a heurté
- أنا اللي صدمتو = c'est moi qui l'ai heurté
- ماشي غلطي = ce n'est pas ma faute
- هو المسؤول = c'est lui le responsable
- الخسارة = les dégâts

Localisation:
- فكازا / فالدار البيضا = à Casablanca
- فالرباط = à Rabat
- فمراكش = à Marrakech
- قدام = devant
- من ورا = par derrière
- على اليمين / على اليسار = à droite / à gauche

Documents & Assurance:
- لكونصطا = le constat amiable
- لاسيرونس = l'assurance
- لبابيات / لوراق = les papiers, documents
- رقم الشاصي = numéro de châssis
- إماتريكيل / الرقم = immatriculation, numéro de plaque

Expressions temporelles:
- البارح = hier
- اليوم = aujourd'hui
- دابا = maintenant, tout à l'heure
- الصباح = le matin
- العشية = le soir
- نهار = jour

Modalités:
- بزاف = beaucoup
- شوية = un peu
- واخا = d'accord, même si
- صافي = c'est tout, terminé
- يعني / زعما = c'est-à-dire
- كاين = il y a
- ماكاينش = il n'y a pas

EXEMPLES DE TRADUCTIONS:
Darija: "دار معايا كسيدة البارح فلوتوروت قدام كازا، الطوموبيل ديالي تخسرات بزاف"
Français: "J'ai eu un accident hier sur l'autoroute avant Casablanca, ma voiture a subi beaucoup de dégâts"

Darija: "واحد الكارو صدمني من ورا و لباربريز تكسر"
Français: "Une voiture m'a percuté par derrière et le pare-brise s'est brisé"

Darija: "خصني نكمل لكونصطا و ندير لبابيات ديال لاسيرونس"
Français: "Je dois compléter le constat amiable et fournir les documents d'assurance"
"""
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt + "\n" + context_dictionary},
                    {"role": "user", "content": f"Texte à traduire : {text}"}
                ],
                temperature=0.1,
                max_tokens=800
            )
            
            translation = response.choices[0].message.content.strip()
            print(f"✨ Traduction Groq enrichie: {translation[:70]}...")
            return translation
            
        except Exception as e:
            print(f"❌ Erreur Groq: {str(e)[:60]}...")
            return None

    # --- Outils d'analyse ---
    
    def _basic_cleanup(self, text: str) -> str:
        """Nettoyage basique (espaces, retours ligne)."""
        return re.sub(r'\s+', ' ', text).strip()

    def _detect_emotions(self, text: str) -> List[str]:
        """Détecte les mots clés émotionnels (Maroc & Français)."""
        emotions = []
        keywords = {
            "urgence": ["دغيا", "vite", "urgent", "بسرعة", "عتقني"],
            "colère": ["حشومة", "énervé", "scandale", "الله ياخذ الحق"],
            "peur": ["خايف", "peur", "tramp", "مخلوع"],
            "doute": ["يمكن", "je crois", "peut-être", "waqila"]
        }
        text_lower = text.lower()
        for emotion, words in keywords.items():
            if any(w in text_lower for w in words):
                emotions.append(emotion)
        return list(set(emotions))

    def _count_hesitations(self, text: str) -> int:
        """Compte les hésitations vocales."""
        patterns = [r'\beuh\b', r'\buh\b', r'\bmmm\b', r'\bيعني\b', r'\bزعما\b']
        count = 0
        for p in patterns:
            count += len(re.findall(p, text, re.IGNORECASE))
        return count

    def _simulate_error(self):
        """Retourne un objet TranscriptMetadata d'erreur."""
        return TranscriptMetadata(
            original_transcript="Error",
            normalized_transcript="Error",
            language="en",
            confidence_score=0.0,
            emotional_markers=[],
            hesitations=0,
            duration_seconds=0.0
        )

# --- Bloc de Test ---
if __name__ == "__main__":
    # 1. Instanciation
    print("🚀 Initialisation du moteur STT...")
    engine = STTEngine(model_name="large-v3", use_api=True)
    
    # 2. Chemin vers votre fichier audio de test (modifier le chemin)
    audio_file = "test_darija.mp3" 
    
    # Création d'un fichier dummy si inexistant pour éviter le crash du test
    if not os.path.exists(audio_file):
        print(f"⚠️ Fichier {audio_file} absent. Veuillez mettre un vrai fichier audio.")
    else:
        # 3. Exécution
        result = engine.transcribe_audio(audio_file)
        
        # 4. Affichage Résultat
        if result:
            print("\n" + "="*50)
            print(f"🎧 ORIGINAL (Darija) : {result.original_transcript}")
            print("-" * 50)
            print(f"🇫🇷 TRADUIT (Français): {result.normalized_transcript}")
            print(f"📊 Confiance : {result.confidence_score:.2f}")
            print(f"❤️ Émotions : {result.emotional_markers}")
            print("="*50)