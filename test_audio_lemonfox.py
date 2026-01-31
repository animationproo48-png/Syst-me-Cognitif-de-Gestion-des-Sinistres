"""
Test de transcription audio avec l'API LemonFox
Ce script teste la transcription avec un fichier audio réel ou une URL
"""

import os
import requests
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()
api_key = os.getenv("WHISPER_API_KEY")

if not api_key:
    print("❌ Clé API non trouvée dans .env")
    exit(1)

print("🧪 TEST D'API LEMONFOX - TRANSCRIPTION AUDIO")
print("=" * 60)

# URL de l'API
url = "https://api.lemonfox.ai/v1/audio/transcriptions"

# Headers avec authentification
headers = {
    "Authorization": f"Bearer {api_key}"
}

print("\n📝 Test 1: Transcription avec URL audio")
print("-" * 60)

# Test avec une URL audio (exemple de la doc)
data_url = {
    "file": "https://output.lemonfox.ai/wikipedia_ai.mp3",
    "language": "english",
    "response_format": "json"
}

try:
    print("🌐 Envoi de la requête...")
    response = requests.post(url, headers=headers, data=data_url)
    
    print(f"📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Succès! Transcription reçue:")
        print(f"   Texte: {result.get('text', 'N/A')[:200]}...")
        if 'duration' in result:
            print(f"   Durée: {result['duration']}s")
        if 'confidence' in result:
            print(f"   Confiance: {result['confidence']}")
    else:
        print(f"❌ Erreur: {response.status_code}")
        print(f"   Réponse: {response.text}")
        
except Exception as e:
    print(f"❌ Exception: {e}")

# Test avec un fichier local (si disponible)
print("\n\n📁 Test 2: Transcription avec fichier local")
print("-" * 60)

# Chercher un fichier audio dans le dossier data/temp_audio
import glob
from pathlib import Path

audio_dir = Path("data/temp_audio")
if audio_dir.exists():
    audio_files = list(audio_dir.glob("*.wav")) + list(audio_dir.glob("*.mp3"))
    
    if audio_files:
        test_file = audio_files[0]
        print(f"📂 Fichier trouvé: {test_file}")
        
        try:
            with open(test_file, 'rb') as audio_file:
                files = {"file": audio_file}
                data_local = {
                    "language": "french",
                    "response_format": "json"
                }
                
                print("🌐 Envoi du fichier...")
                response = requests.post(url, headers=headers, files=files, data=data_local)
                
                print(f"📊 Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ Succès! Transcription reçue:")
                    print(f"   Texte: {result.get('text', 'N/A')}")
                    if 'duration' in result:
                        print(f"   Durée: {result['duration']}s")
                else:
                    print(f"❌ Erreur: {response.status_code}")
                    print(f"   Réponse: {response.text}")
                    
        except Exception as e:
            print(f"❌ Exception: {e}")
    else:
        print("⚠️ Aucun fichier audio trouvé dans data/temp_audio")
else:
    print("⚠️ Dossier data/temp_audio n'existe pas")

print("\n" + "=" * 60)
print("✅ Tests terminés")
print("\n💡 Pour tester avec votre propre fichier:")
print("   1. Placez un fichier .wav ou .mp3 dans data/temp_audio/")
print("   2. Relancez ce script")
print("\n   OU utilisez le module STT:")
print("   from modules.stt_module import STTEngine")
print("   engine = STTEngine(use_api=True)")
print("   result = engine.transcribe_audio('votre_fichier.wav', language='fr')")
