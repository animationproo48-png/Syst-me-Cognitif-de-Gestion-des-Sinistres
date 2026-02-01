"""
Module Text-to-Speech (TTS) pour la synthèse vocale.
Génère des réponses audio avec un ton professionnel et rassurant.
Utilise pyttsx3 (offline, fiable) pour génération robuste.
"""

import os
from typing import Optional
from pathlib import Path


class TTSEngine:
    """Moteur de synthèse vocale Text-to-Speech"""
    
    # Voix disponibles ElevenLabs
    AVAILABLE_VOICES = {
        "george": {"id": "JBFqnCBsd6RMkjVDRZzb", "language": "fr", "gender": "male", "description": "Voix masculine chaleureuse, conteur captivant (multilingue)"},
        "alice": {"id": "Xb7hH8MSUJpSbSDYk0k2", "language": "fr", "gender": "female", "description": "Voix féminine claire, éducatrice professionnelle (British)"},
        "eric": {"id": "cjVigY5qzO86Huf0OWal", "language": "fr", "gender": "male", "description": "Voix masculine lisse, digne de confiance"},
        "jessica": {"id": "cgSgspJ2msm6clMCkdW9", "language": "fr", "gender": "female", "description": "Voix féminine joyeuse, chaleureuse et lumineuse"},
        "will": {"id": "bIHbv24MWmeRgasZH58o", "language": "fr", "gender": "male", "description": "Voix masculine relaxée, optimiste"},
        "roger": {"id": "CwhRBWXzGAHq8TQ4Fs17", "language": "fr", "gender": "male", "description": "Voix masculine décontractée, causelle, résonnante"},
        "sarah": {"id": "EXAVITQu4vr4xnSDxMaL", "language": "fr", "gender": "female", "description": "Voix féminine mûre, rassurante, confiante"},
    }
    
    def __init__(self, language: str = "fr", use_lemonfoxx: bool = True, voice: str = None):
        """
        Initialise le moteur TTS
        
        Args:
            language: Code langue (fr, ar, en)
            use_lemonfoxx: Inutilisé (maintient la compatibilité)
            voice: Nom de la voix (george, alice, eric, jessica, will, roger, sarah) ou voice_id
        """
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        self.language = language
        self.voice_name = voice or self._get_default_voice(language)
        self.elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
        self.engine = None
        self._initialize_engine()
    
    def _get_default_voice(self, language: str) -> str:
        """Retourne la voix par défaut selon la langue"""
        default_voices = {
            "fr": "george",      # George - warm, trustworthy (meilleur pour FR)
            "ar": "roger",       # Roger support AR
            "en": "sarah"        # Sarah - professional
        }
        return default_voices.get(language, "george")
    
    def get_voice_id(self, voice_name: str = None) -> str:
        """Retourne le voice_id pour une voix donnée"""
        voice_name = voice_name or self.voice_name
        
        # Si c'est un voice_id direct (UUID-like), retourner tel quel
        if len(voice_name) > 20 and voice_name.startswith(("J", "C", "E", "g", "p")):
            return voice_name
        
        # Sinon chercher dans le mapping
        if voice_name.lower() in self.AVAILABLE_VOICES:
            return self.AVAILABLE_VOICES[voice_name.lower()]["id"]
        
        # Fallback: Bella
        return self.AVAILABLE_VOICES["bella"]["id"]
    
    def _initialize_engine(self):
        """Initialise le moteur TTS approprié"""
        # Priorité: ElevenLabs (voix très naturelle)
        if self.elevenlabs_key:
            self.engine = "elevenlabs"
            print("✅ ElevenLabs TTS activé (voix premium)")
            return
        
        # Fallback: pyttsx3 (offline)
        try:
            import pyttsx3
            self.engine = "pyttsx3"
            print("✅ pyttsx3 initialisé (fallback)")
            return
        except ImportError:
            print("⚠️ pyttsx3 non installé...")
        
        # Final fallback: gTTS (Google TTS)
        try:
            from gtts import gTTS
            self.engine = "gtts"
            print("✅ gTTS initialisé (fallback final)")
        except ImportError:
            print("⚠️ Aucun moteur TTS disponible. Mode simulation audio.")
            self.engine = None
    
    def synthesize(
        self, 
        text: str, 
        output_path: Optional[str] = None,
        tone: str = "professional",
        voice: str = None
    ) -> str:
        """
        Synthétise du texte en audio
        
        Args:
            text: Texte à synthétiser
            output_path: Chemin de sortie (généré auto si None)
            tone: Ton de la voix (professional, empathetic, neutral)
            voice: Nom de la voix (bella, adam, sarah, rachel, ethan, serena) ou voice_id
            
        Returns:
            Chemin du fichier audio généré
        """
        if not text or text.strip() == "":
            print("⚠️ Texte vide, pas de synthèse audio")
            return None
        
        # Si une voix différente est spécifiée, la sauvegarder
        if voice:
            self.voice_name = voice
        
        # Préparer le texte selon le ton
        prepared_text = self._prepare_text_for_tone(text, tone)
        
        # Générer nom de fichier si non fourni
        if output_path is None:
            output_dir = Path("c:/Users/HP/Inssurance Advanced/data/audio_responses")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(output_dir / f"response_{timestamp}.mp3")
        
        # Synthèse selon l'engine disponible
        if self.engine == "elevenlabs":
            return self._synthesize_elevenlabs(prepared_text, output_path)
        elif self.engine == "pyttsx3":
            return self._synthesize_pyttsx3(prepared_text, output_path)
        elif self.engine == "gtts":
            return self._synthesize_gtts(prepared_text, output_path)
        else:
            return self._simulate_synthesis(prepared_text, output_path)
    
    def _synthesize_gtts(self, text: str, output_path: str) -> str:
        """Synthèse avec gTTS"""
        try:
            from gtts import gTTS
            
            # Mapping des langues
            lang_code = {
                "fr": "fr",
                "ar": "ar",
                "en": "en"
            }.get(self.language, "fr")
            
            tts = gTTS(text=text, lang=lang_code, slow=False)
            tts.save(output_path)
            
            print(f"🔊 Audio généré (gTTS): {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Erreur gTTS: {e}")
            return self._simulate_synthesis(text, output_path)
    
    def _synthesize_elevenlabs(self, text: str, output_path: str) -> str:
        """Synthèse avec ElevenLabs (voix naturelle, professionnel)"""
        try:
            print(f"🎤 [ELEVENLABS] Début synthèse...")
            from elevenlabs.client import ElevenLabs
            
            # Initialiser client officiel
            print(f"🔑 [ELEVENLABS] Clé API présente: {bool(self.elevenlabs_key)}")
            client = ElevenLabs(api_key=self.elevenlabs_key)
            
            # Récupérer le voice_id
            voice_id = self.get_voice_id(self.voice_name)
            print(f"🎙️ [ELEVENLABS] Voix sélectionnée: {self.voice_name} ({voice_id})")
            
            # Convertir texte en audio avec API officielle
            print(f"📡 [ELEVENLABS] Appel API convert...")
            audio_generator = client.text_to_speech.convert(
                voice_id=voice_id,
                text=text,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128"
            )
            
            # Sauvegarder l'audio (c'est un generator, pas bytes direct)
            with open(output_path, 'wb') as f:
                for chunk in audio_generator:
                    f.write(chunk)
            
            print(f"✅ [ELEVENLABS] Audio reçu et sauvegardé")
            
            print(f"💾 [ELEVENLABS] Fichier sauvegardé: {output_path}")
            
            print(f"🔊 Audio généré (ElevenLabs API officielle): {output_path}")
            return output_path
            
        except Exception as e:
            print(f"⚠️ ElevenLabs échoué ({str(e)[:60]}...), fallback pyttsx3...")
            self.engine = "pyttsx3"
            return self._synthesize_pyttsx3(text, output_path)
    
    def _synthesize_pyttsx3(self, text: str, output_path: str) -> str:
        """Synthèse avec pyttsx3 (offline, très fiable)"""
        try:
            import pyttsx3
            
            # Initialiser le moteur
            engine = pyttsx3.init()
            
            # Configurer langue et voix
            engine.setProperty('rate', 150)  # Vitesse (par défaut 200, on ralentit pour clarté)
            engine.setProperty('volume', 0.9)  # Volume
            
            # Sauvegarder vers fichier
            engine.save_to_file(text, output_path)
            engine.runAndWait()
            
            # Vérifier que le fichier a été créé et n'est pas vide
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                print(f"🔊 Audio généré (pyttsx3): {output_path}")
                return output_path
            else:
                print(f"⚠️ pyttsx3 a généré un fichier vide, essai gTTS...")
                return self._synthesize_gtts(text, output_path)
                
        except Exception as e:
            print(f"❌ Erreur pyttsx3: {e}")
            return self._synthesize_gtts(text, output_path)
    

    
    def _simulate_synthesis(self, text: str, output_path: str) -> str:
        """
        Simule la synthèse audio en créant un fichier de log
        (pour démo sans dépendances TTS)
        """
        print(f"🎙️ [MODE SIMULATION] Synthèse de: {text[:100]}...")
        
        # Créer un fichier texte à la place pour la démo
        txt_path = output_path.replace('.mp3', '.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"[AUDIO SIMULÉ]\n\n{text}")
        
        print(f"📝 Transcription sauvegardée: {txt_path}")
        return txt_path
    
    def _prepare_text_for_tone(self, text: str, tone: str) -> str:
        """
        Adapte le texte selon le ton souhaité
        
        Args:
            text: Texte original
            tone: Ton souhaité (professional, empathetic, neutral)
            
        Returns:
            Texte adapté
        """
        if tone == "empathetic":
            # Ajouter des pauses et adoucir le ton
            text = text.replace(". ", "... ")
            
        elif tone == "professional":
            # Ton formel et structuré (déjà approprié généralement)
            pass
        
        # Ajouter des pauses naturelles pour la prosodie
        text = text.replace(", ", ", ... ")
        text = text.replace(": ", ": ... ")
        
        return text
    
    def create_response_audio(
        self,
        response_type: str,
        claim_id: str,
        content: dict,
        output_path: Optional[str] = None
    ) -> str:
        """
        Crée une réponse audio structurée pour le client
        
        Args:
            response_type: Type de réponse (greeting, summary, next_steps, etc.)
            claim_id: Identifiant du sinistre
            content: Contenu structuré de la réponse
            output_path: Chemin de sortie personnalisé
            
        Returns:
            Chemin du fichier audio généré
        """
        script = self._generate_speech_script(response_type, claim_id, content)
        return self.synthesize(script, output_path, tone="professional")
    
    def _generate_speech_script(
        self, 
        response_type: str, 
        claim_id: str, 
        content: dict
    ) -> str:
        """
        Génère un script de discours naturel et professionnel
        """
        scripts = {
            "greeting": """
                Bonjour, je suis votre assistant cognitif de gestion des sinistres.
                J'ai bien enregistré votre déclaration concernant le sinistre numéro {claim_id}.
                Je vais analyser votre situation et vous guider dans les prochaines étapes.
            """,
            
            "analysis_complete": """
                Merci pour ces informations. J'ai terminé l'analyse de votre sinistre.
                Votre dossier a été classifié comme {complexity_level}.
                Le score de complexité est de {complexity_score} sur 100.
            """,
            
            "autonomous_handling": """
                Bonne nouvelle: votre sinistre peut être traité de manière autonome.
                Voici les prochaines étapes:
                {next_steps}
                
                Vous recevrez une mise à jour dans les {timeframe}.
            """,
            
            "escalation": """
                Votre dossier nécessite l'attention d'un conseiller expert.
                Un de nos spécialistes va prendre en charge votre sinistre.
                Vous serez contacté dans les {timeframe}.
                
                Raison de l'escalade: {escalation_reason}
            """,
            
            "missing_documents": """
                Pour traiter votre sinistre, nous avons besoin des documents suivants:
                {documents_list}
                
                Vous pouvez les transmettre via notre application ou par email.
            """
        }
        
        template = scripts.get(response_type, "Merci de votre appel.")
        
        # Remplir le template avec les données du content
        try:
            script = template.format(claim_id=claim_id, **content)
        except KeyError:
            script = template.replace("{claim_id}", claim_id)
        
        return script.strip()


# Fonctions utilitaires
def text_to_speech(
    text: str, 
    output_file: str = None, 
    language: str = "fr"
) -> str:
    """
    Fonction utilitaire pour synthèse vocale rapide
    
    Args:
        text: Texte à synthétiser
        output_file: Fichier de sortie
        language: Langue (fr, ar, en)
        
    Returns:
        Chemin du fichier audio généré
    """
    engine = TTSEngine(language=language)
    return engine.synthesize(text, output_file)


def create_client_response(claim_id: str, summary: dict, language: str = "fr") -> str:
    """
    Crée une réponse audio complète pour le client
    
    Args:
        claim_id: ID du sinistre
        summary: Dictionnaire avec les informations du résumé client
        language: Langue de la réponse
        
    Returns:
        Chemin du fichier audio de la réponse
    """
    engine = TTSEngine(language=language)
    
    # Construire le texte de la réponse
    response_text = f"""
    Bonjour, je confirme la réception de votre déclaration de sinistre numéro {claim_id}.
    
    {summary.get('message', '')}
    
    Voici les prochaines étapes: {', '.join(summary.get('next_steps', []))}
    
    Documents requis: {', '.join(summary.get('documents_required', []))}
    
    Délai de traitement estimé: {summary.get('estimated_processing_time', 'à déterminer')}
    
    Pour toute question, vous pouvez nous contacter au {summary.get('contact_info', '0800 123 456')}.
    
    Nous restons à votre disposition. Au revoir.
    """
    
    return engine.synthesize(response_text.strip(), tone="empathetic")
