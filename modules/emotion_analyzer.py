"""
Module d'Analyse Émotionnelle Multimodale (Audio + Texte)
Analyse les émotions basées sur:
1. Caractéristiques acoustiques (pitch, énergie, tempo, MFCCs)
2. Contenu textuel (mots-clés émotionnels, sentiment)
3. Fusion multimodale pour un score composite

Émotions détectées:
- Colère (anger): pitch élevé, énergie haute, mots agressifs
- Stress (stress): tempo rapide, variations pitch, mots d'urgence
- Tristesse (sadness): pitch bas, énergie basse, mots négatifs
- Peur (fear): tremblements, pauses fréquentes
- Neutre (neutral): baseline normal
"""

import os
import numpy as np
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import json
from datetime import datetime


class EmotionAnalyzer:
    """
    Analyseur d'émotions multimodal (audio + texte)
    """
    
    # Dictionnaire étendu d'indicateurs émotionnels
    EMOTION_KEYWORDS = {
        "anger": [
            "furieux", "énervé", "inacceptable", "scandaleux", "honteux",
            "inadmissible", "révoltant", "insupportable", "horrible",
            "نرفوز", "مكلخ", "زعمة", "معقول", "حشومة"  # Darija
        ],
        "stress": [
            "urgent", "vite", "rapidement", "inquiet", "stressé", "anxieux",
            "pressé", "dépêchez", "maintenant", "immédiatement",
            "باش", "دبا", "بزربة", "مسطيطي"  # Darija
        ],
        "sadness": [
            "triste", "désolé", "malheureux", "difficile", "dur", "pénible",
            "désespéré", "abattu", "découragé", "fatigué",
            "مسكين", "زين", "صعيب"  # Darija
        ],
        "fear": [
            "peur", "effrayé", "inquiet", "angoissé", "crainte", "terrorisé",
            "paniqué", "apeuré", "angoisse",
            "خايف", "خلعان"  # Darija
        ],
        "frustration": [
            "frustré", "bloqué", "coincé", "impossible", "compliqué",
            "toujours pas", "ça fait longtemps", "encore",
            "ماكاينش", "معطل"  # Darija
        ]
    }
    
    def __init__(self):
        """Initialise l'analyseur avec les dépendances optionnelles"""
        self.librosa_available = False
        self.parselmouth_available = False
        
        # Tentative d'import librosa (pour analyse audio)
        try:
            import librosa
            self.librosa = librosa
            self.librosa_available = True
            print("✅ Librosa chargé - analyse audio avancée activée")
        except ImportError:
            print("⚠️ Librosa non disponible - analyse audio basique seulement")
            
        # Tentative d'import parselmouth (pour pitch/formants)
        try:
            import parselmouth
            self.parselmouth = parselmouth
            self.parselmouth_available = True
            print("✅ Parselmouth chargé - analyse prosodique activée")
        except ImportError:
            print("⚠️ Parselmouth non disponible - pas d'analyse prosodique")
    
    def analyze_audio_features(self, audio_path: str) -> Dict:
        """
        Extrait les caractéristiques acoustiques de l'audio
        
        Args:
            audio_path: Chemin vers le fichier audio
            
        Returns:
            Dict avec pitch_mean, pitch_std, energy, tempo, mfcc_stats
        """
        if not self.librosa_available:
            return self._fallback_audio_analysis(audio_path)
        
        try:
            # Charger l'audio
            y, sr = self.librosa.load(audio_path, sr=22050)
            
            # 1. Pitch (F0) - indicateur d'émotion clé
            pitches, magnitudes = self.librosa.piptrack(y=y, sr=sr, fmin=75, fmax=400)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            pitch_mean = float(np.mean(pitch_values)) if pitch_values else 0.0
            pitch_std = float(np.std(pitch_values)) if pitch_values else 0.0
            
            # 2. Énergie (RMS) - indicateur d'intensité
            rms = self.librosa.feature.rms(y=y)[0]
            energy_mean = float(np.mean(rms))
            energy_std = float(np.std(rms))
            
            # 3. Tempo - vitesse de parole
            tempo, _ = self.librosa.beat.beat_track(y=y, sr=sr)
            tempo = float(tempo)
            
            # 4. Zero Crossing Rate - indicateur de bruit/stress
            zcr = self.librosa.feature.zero_crossing_rate(y)[0]
            zcr_mean = float(np.mean(zcr))
            
            # 5. MFCCs (Mel-frequency cepstral coefficients) - timbre vocal
            mfccs = self.librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            mfcc_means = [float(np.mean(mfcc)) for mfcc in mfccs]
            
            # 6. Spectral features
            spectral_centroid = self.librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_rolloff = self.librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            
            return {
                "pitch_mean": pitch_mean,
                "pitch_std": pitch_std,
                "energy_mean": energy_mean,
                "energy_std": energy_std,
                "tempo": tempo,
                "zcr_mean": zcr_mean,
                "mfcc_means": mfcc_means,
                "spectral_centroid_mean": float(np.mean(spectral_centroid)),
                "spectral_rolloff_mean": float(np.mean(spectral_rolloff)),
                "duration": float(len(y) / sr)
            }
            
        except Exception as e:
            print(f"❌ Erreur analyse audio: {e}")
            return self._fallback_audio_analysis(audio_path)
    
    def _fallback_audio_analysis(self, audio_path: str) -> Dict:
        """Analyse basique si librosa n'est pas disponible"""
        try:
            # Juste obtenir la durée via l'OS
            file_size = os.path.getsize(audio_path)
            # Estimation grossière: 16kHz, 16-bit mono ≈ 32KB/s
            estimated_duration = file_size / 32000
            
            return {
                "pitch_mean": 0.0,
                "pitch_std": 0.0,
                "energy_mean": 0.0,
                "energy_std": 0.0,
                "tempo": 0.0,
                "zcr_mean": 0.0,
                "mfcc_means": [0.0] * 13,
                "spectral_centroid_mean": 0.0,
                "spectral_rolloff_mean": 0.0,
                "duration": estimated_duration,
                "fallback": True
            }
        except:
            return {"fallback": True, "error": True}
    
    def analyze_text_emotion(self, text: str) -> Dict[str, float]:
        """
        Analyse les émotions basées sur le contenu textuel
        
        Args:
            text: Texte transcrit
            
        Returns:
            Dict avec scores par émotion (0-100)
        """
        text_lower = text.lower()
        
        emotion_scores = {
            "anger": 0.0,
            "stress": 0.0,
            "sadness": 0.0,
            "fear": 0.0,
            "frustration": 0.0,
            "neutral": 0.0
        }
        
        # Compter les occurrences de mots-clés
        total_matches = 0
        for emotion, keywords in self.EMOTION_KEYWORDS.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            emotion_scores[emotion] = matches
            total_matches += matches
        
        # Normaliser les scores (0-100)
        if total_matches > 0:
            for emotion in emotion_scores:
                emotion_scores[emotion] = (emotion_scores[emotion] / total_matches) * 100
        else:
            emotion_scores["neutral"] = 100.0
        
        # Analyse des patterns linguistiques
        # Points d'exclamation = colère ou stress
        exclamation_count = text.count("!")
        if exclamation_count > 2:
            emotion_scores["anger"] += exclamation_count * 10
            emotion_scores["stress"] += exclamation_count * 5
        
        # Points d'interrogation multiples = confusion/stress
        question_count = text.count("?")
        if question_count > 2:
            emotion_scores["stress"] += question_count * 5
            emotion_scores["frustration"] += question_count * 5
        
        # Majuscules excessives = colère
        upper_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if upper_ratio > 0.3:
            emotion_scores["anger"] += 20
        
        # Normaliser à nouveau pour être sûr (max 100)
        max_score = max(emotion_scores.values())
        if max_score > 100:
            for emotion in emotion_scores:
                emotion_scores[emotion] = (emotion_scores[emotion] / max_score) * 100
        
        return emotion_scores
    
    def classify_emotion_from_audio(self, audio_features: Dict) -> Dict[str, float]:
        """
        Classifie les émotions basées sur les features audio
        
        Règles heuristiques (peut être remplacé par ML):
        - Colère: pitch élevé + énergie haute + tempo rapide
        - Stress: pitch variable + tempo rapide
        - Tristesse: pitch bas + énergie basse
        - Peur: pitch variable + ZCR élevé
        """
        if audio_features.get("fallback") or audio_features.get("error"):
            return {
                "anger": 0.0,
                "stress": 0.0,
                "sadness": 0.0,
                "fear": 0.0,
                "frustration": 0.0,
                "neutral": 100.0
            }
        
        scores = {
            "anger": 0.0,
            "stress": 0.0,
            "sadness": 0.0,
            "fear": 0.0,
            "frustration": 0.0,
            "neutral": 50.0  # baseline
        }
        
        pitch_mean = audio_features.get("pitch_mean", 0)
        pitch_std = audio_features.get("pitch_std", 0)
        energy_mean = audio_features.get("energy_mean", 0)
        tempo = audio_features.get("tempo", 0)
        zcr_mean = audio_features.get("zcr_mean", 0)
        
        # Colère: pitch élevé (>200Hz) + énergie haute + tempo rapide
        if pitch_mean > 200:
            scores["anger"] += 30
        if energy_mean > 0.05:
            scores["anger"] += 20
        if tempo > 140:
            scores["anger"] += 15
        
        # Stress: variations pitch importantes + tempo rapide
        if pitch_std > 30:
            scores["stress"] += 25
        if tempo > 130:
            scores["stress"] += 20
        if zcr_mean > 0.15:
            scores["stress"] += 15
        
        # Tristesse: pitch bas (<150Hz) + énergie basse + tempo lent
        if pitch_mean < 150 and pitch_mean > 0:
            scores["sadness"] += 30
        if energy_mean < 0.03:
            scores["sadness"] += 25
        if tempo < 90:
            scores["sadness"] += 15
        
        # Peur: variations pitch + ZCR élevé (voix tremblante)
        if pitch_std > 25:
            scores["fear"] += 20
        if zcr_mean > 0.2:
            scores["fear"] += 25
        
        # Frustration: énergie modérée + tempo variable
        if 0.03 < energy_mean < 0.05 and 100 < tempo < 130:
            scores["frustration"] += 30
        
        # Réduire le neutre si des émotions sont détectées
        total_emotion = sum(scores[e] for e in scores if e != "neutral")
        if total_emotion > 0:
            scores["neutral"] = max(0, 100 - total_emotion)
        
        # Normaliser (max 100)
        max_score = max(scores.values())
        if max_score > 100:
            for emotion in scores:
                scores[emotion] = (scores[emotion] / max_score) * 100
        
        return scores
    
    def fuse_emotion_scores(
        self, 
        text_scores: Dict[str, float], 
        audio_scores: Dict[str, float],
        text_weight: float = 0.6,
        audio_weight: float = 0.4
    ) -> Dict[str, float]:
        """
        Fusionne les scores émotionnels du texte et de l'audio
        
        Args:
            text_scores: Scores basés sur le texte
            audio_scores: Scores basés sur l'audio
            text_weight: Poids du texte (défaut 60%)
            audio_weight: Poids de l'audio (défaut 40%)
            
        Returns:
            Scores fusionnés
        """
        fused = {}
        all_emotions = set(list(text_scores.keys()) + list(audio_scores.keys()))
        
        for emotion in all_emotions:
            text_score = text_scores.get(emotion, 0.0)
            audio_score = audio_scores.get(emotion, 0.0)
            fused[emotion] = (text_score * text_weight) + (audio_score * audio_weight)
        
        return fused
    
    def analyze_complete(
        self, 
        audio_path: str, 
        transcription: str,
        save_results: bool = True
    ) -> Dict:
        """
        Analyse complète multimodale (audio + texte)
        
        Args:
            audio_path: Chemin du fichier audio
            transcription: Texte transcrit
            save_results: Sauvegarder les résultats JSON
            
        Returns:
            Dict avec analyse complète
        """
        # 1. Extraire features audio
        audio_features = self.analyze_audio_features(audio_path)
        
        # 2. Analyser émotions texte
        text_emotions = self.analyze_text_emotion(transcription)
        
        # 3. Analyser émotions audio
        audio_emotions = self.classify_emotion_from_audio(audio_features)
        
        # 4. Fusionner les scores
        fused_emotions = self.fuse_emotion_scores(text_emotions, audio_emotions)
        
        # 5. Déterminer émotion dominante
        dominant_emotion = max(fused_emotions.items(), key=lambda x: x[1])
        
        # 6. Construire le résultat
        result = {
            "timestamp": datetime.now().isoformat(),
            "audio_path": audio_path,
            "transcription": transcription,
            "audio_features": audio_features,
            "text_emotion_scores": text_emotions,
            "audio_emotion_scores": audio_emotions,
            "fused_emotion_scores": fused_emotions,
            "dominant_emotion": {
                "label": dominant_emotion[0],
                "confidence": round(dominant_emotion[1], 2)
            },
            "analysis_mode": "full" if self.librosa_available else "text_only"
        }
        
        # 7. Sauvegarder si demandé
        if save_results:
            self._save_analysis(result, audio_path)
        
        return result
    
    def _save_analysis(self, result: Dict, audio_path: str):
        """Sauvegarde l'analyse en JSON à côté du fichier audio"""
        try:
            audio_path_obj = Path(audio_path)
            json_path = audio_path_obj.with_suffix('.emotion.json')
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Analyse sauvegardée: {json_path}")
        except Exception as e:
            print(f"❌ Erreur sauvegarde analyse: {e}")
    
    def get_emotion_interpretation(self, emotion: str, confidence: float) -> str:
        """
        Retourne une interprétation humaine de l'émotion
        """
        interpretations = {
            "anger": f"Le client exprime de la **colère** (confiance: {confidence:.0f}%). Ton agressif détecté.",
            "stress": f"Le client est **stressé/anxieux** (confiance: {confidence:.0f}%). Urgence perçue.",
            "sadness": f"Le client semble **triste/découragé** (confiance: {confidence:.0f}%). Détresse émotionnelle.",
            "fear": f"Le client manifeste de la **peur/inquiétude** (confiance: {confidence:.0f}%). Besoin de réassurance.",
            "frustration": f"Le client est **frustré** (confiance: {confidence:.0f}%). Impatience détectée.",
            "neutral": f"Le client est **calme/neutre** (confiance: {confidence:.0f}%). Conversation factuelle."
        }
        return interpretations.get(emotion, f"Émotion: {emotion} ({confidence:.0f}%)")


# --- FONCTION UTILITAIRE ---
def analyze_claim_audio(audio_path: str, transcription: str) -> Dict:
    """
    Fonction helper pour analyser rapidement un audio de sinistre
    
    Args:
        audio_path: Chemin du fichier audio
        transcription: Texte transcrit
        
    Returns:
        Résultats de l'analyse émotionnelle
    """
    analyzer = EmotionAnalyzer()
    return analyzer.analyze_complete(audio_path, transcription)


if __name__ == "__main__":
    # Test du module
    print("🧪 Test du module d'analyse émotionnelle\n")
    
    analyzer = EmotionAnalyzer()
    
    # Test 1: Analyse texte seule
    print("Test 1: Analyse texte")
    test_text = "Je suis vraiment furieux ! C'est inacceptable ! Vous devez régler ça MAINTENANT !"
    text_scores = analyzer.analyze_text_emotion(test_text)
    print(f"Texte: {test_text}")
    print(f"Scores: {text_scores}")
    print(f"Dominant: {max(text_scores.items(), key=lambda x: x[1])}")
    
    print("\n" + "="*60 + "\n")
    
    # Test 2: Analyse avec audio (si fichier existe)
    test_audio = Path("c:/Users/HP/Inssurance Advanced/data/temp_audio")
    if test_audio.exists():
        audio_files = list(test_audio.glob("*.wav")) + list(test_audio.glob("*.mp3"))
        if audio_files:
            print(f"Test 2: Analyse complète avec {audio_files[0].name}")
            result = analyzer.analyze_complete(
                str(audio_files[0]),
                "Je suis stressé, j'ai besoin d'aide rapidement"
            )
            print(f"Émotion dominante: {result['dominant_emotion']['label']} ({result['dominant_emotion']['confidence']}%)")
            print(f"Scores fusionnés: {result['fused_emotion_scores']}")
