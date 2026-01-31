#!/usr/bin/env python3
"""
Test standalone pour ElevenLabs TTS
Vérifie que la clé API fonctionne et génère un fichier audio valide
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()
elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")

print("=" * 60)
print("TEST ELEVENLABS TTS")
print("=" * 60)

if not elevenlabs_key:
    print("❌ ERREUR: ELEVENLABS_API_KEY non trouvée dans .env")
    exit(1)

print(f"✅ Clé trouvée: {elevenlabs_key[:20]}...")

# Test 1: Importer la librairie
print("\n[Test 1] Import de la librairie elevenlabs...")
try:
    from elevenlabs.client import ElevenLabs
    print("✅ Import réussi")
except ImportError as e:
    print(f"❌ Erreur import: {e}")
    exit(1)

# Test 2: Générer un audio simple
print("\n[Test 2] Génération d'un audio simple...")
test_text = "Bonjour, ceci est un test de synthèse vocale avec ElevenLabs."

try:
    client = ElevenLabs(api_key=elevenlabs_key)
    
    # Lister les voix disponibles
    voices = client.voices.get_all()
    print(f"✅ {len(voices.voices)} voix disponibles")
    
    # Afficher les voix disponibles
    print("\n   Voix disponibles:")
    for voice in voices.voices[:5]:
        print(f"   - {voice.name}: {voice.voice_id}")
    
    # Utiliser la première voix disponible
    voice_id = voices.voices[0].voice_id
    print(f"\n   Utilisation de: {voices.voices[0].name} ({voice_id})")
    
    # Générer audio avec la vraie voix
    audio = client.text_to_speech.convert(
        voice_id=voice_id,
        text=test_text,
        model_id="eleven_multilingual_v2"
    )
    
    # Convertir le stream en bytes
    audio_bytes = b"".join(audio)
    print(f"✅ Audio généré: {len(audio_bytes)} bytes")
    
except Exception as e:
    print(f"❌ Erreur génération: {e}")
    exit(1)

# Test 3: Sauvegarder le fichier
print("\n[Test 3] Sauvegarde du fichier audio...")
output_dir = Path("c:/Users/HP/Inssurance Advanced/data/audio_responses")
output_dir.mkdir(parents=True, exist_ok=True)

output_path = output_dir / "test_elevenlabs.mp3"

try:
    with open(output_path, 'wb') as f:
        f.write(audio_bytes)
    print(f"✅ Fichier sauvegardé: {output_path}")
    print(f"   Taille: {os.path.getsize(output_path)} bytes")
    
    if os.path.getsize(output_path) > 5000:
        print("✅ Fichier semble valide!")
    else:
        print("⚠️ Fichier très petit, vérifier permissions API")
        
except Exception as e:
    print(f"❌ Erreur sauvegarde: {e}")
    exit(1)

# Test 4: Tester différentes langues et voix
print("\n[Test 4] Test multi-langue...")
voice_ids = {
    "fr": ("Bella" if any(v.name == "Bella" for v in voices.voices) else voices.voices[0].voice_id, "Bonjour, ceci est un test en français."),
    "en": (voices.voices[0].voice_id, "Hello, this is a test in English."),
    "ar": (voices.voices[0].voice_id, "مرحبا، هذا اختبار باللغة العربية.")
}

for lang, (voice_ref, text) in voice_ids.items():
    try:
        # Si voice_ref est une string de nom, chercher l'ID
        if isinstance(voice_ref, str) and len(voice_ref) < 20:
            voice_id_test = next((v.voice_id for v in voices.voices if v.name == voice_ref), voices.voices[0].voice_id)
        else:
            voice_id_test = voice_ref
            
        audio_stream = client.text_to_speech.convert(
            voice_id=voice_id_test,
            text=text,
            model_id="eleven_multilingual_v2"
        )
        audio_data = b"".join(audio_stream)
        size = len(audio_data)
        status = "✅" if size > 5000 else "⚠️"
        print(f"{status} {lang.upper()}: {size} bytes")
    except Exception as e:
        print(f"❌ {lang.upper()}: {str(e)[:50]}")

print("\n" + "=" * 60)
print("✅ TESTS TERMINÉS - ElevenLabs TTS fonctionne!")
print("=" * 60)
