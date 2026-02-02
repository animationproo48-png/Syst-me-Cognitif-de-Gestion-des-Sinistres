"""
Module d'Enregistrement et Gestion des Audios
Sauvegarde tous les audios clients avec métadonnées organisées
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
import json


class AudioRecorder:
    """Gestionnaire d'enregistrement et archivage des audios"""
    
    def __init__(self, base_dir: str = None):
        """
        Initialise le recorder
        
        Args:
            base_dir: Répertoire de base pour les audios (défaut: data/recordings)
        """
        if base_dir is None:
            base_dir = "c:/Users/HP/Inssurance Advanced/data/recordings"
        
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Sous-répertoires organisés
        self.client_audio_dir = self.base_dir / "client_inputs"
        self.advisor_audio_dir = self.base_dir / "advisor_responses"
        self.metadata_dir = self.base_dir / "metadata"
        
        # Créer les répertoires
        self.client_audio_dir.mkdir(exist_ok=True)
        self.advisor_audio_dir.mkdir(exist_ok=True)
        self.metadata_dir.mkdir(exist_ok=True)
        
        print(f"✅ AudioRecorder initialisé: {self.base_dir}")
    
    def save_client_audio(
        self,
        source_path: str,
        client_id: Optional[str] = None,
        sinistre_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Sauvegarde un audio client avec métadonnées
        
        Args:
            source_path: Chemin du fichier audio source
            client_id: ID du client (optionnel)
            sinistre_id: ID du sinistre (optionnel)
            metadata: Métadonnées additionnelles
            
        Returns:
            Chemin du fichier sauvegardé
        """
        # Générer nom de fichier unique
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        source_ext = Path(source_path).suffix
        
        if sinistre_id:
            filename = f"client_{sinistre_id}_{timestamp}{source_ext}"
        elif client_id:
            filename = f"client_{client_id}_{timestamp}{source_ext}"
        else:
            filename = f"client_{timestamp}{source_ext}"
        
        # Copier le fichier
        dest_path = self.client_audio_dir / filename
        shutil.copy2(source_path, dest_path)
        
        # Sauvegarder métadonnées
        self._save_metadata(
            dest_path,
            audio_type="client_input",
            client_id=client_id,
            sinistre_id=sinistre_id,
            metadata=metadata
        )
        
        print(f"✅ Audio client sauvegardé: {filename}")
        return str(dest_path)
    
    def save_advisor_audio(
        self,
        source_path: str,
        client_id: Optional[str] = None,
        sinistre_id: Optional[str] = None,
        response_text: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Sauvegarde un audio de réponse conseiller
        
        Args:
            source_path: Chemin du fichier audio source
            client_id: ID du client
            sinistre_id: ID du sinistre
            response_text: Texte de la réponse
            metadata: Métadonnées additionnelles
            
        Returns:
            Chemin du fichier sauvegardé
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        source_ext = Path(source_path).suffix
        
        if sinistre_id:
            filename = f"advisor_{sinistre_id}_{timestamp}{source_ext}"
        elif client_id:
            filename = f"advisor_{client_id}_{timestamp}{source_ext}"
        else:
            filename = f"advisor_{timestamp}{source_ext}"
        
        dest_path = self.advisor_audio_dir / filename
        shutil.copy2(source_path, dest_path)
        
        # Métadonnées enrichies
        enriched_metadata = metadata or {}
        if response_text:
            enriched_metadata["response_text"] = response_text
        
        self._save_metadata(
            dest_path,
            audio_type="advisor_response",
            client_id=client_id,
            sinistre_id=sinistre_id,
            metadata=enriched_metadata
        )
        
        print(f"✅ Audio conseiller sauvegardé: {filename}")
        return str(dest_path)
    
    def _save_metadata(
        self,
        audio_path: Path,
        audio_type: str,
        client_id: Optional[str] = None,
        sinistre_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """Sauvegarde les métadonnées en JSON"""
        meta = {
            "timestamp": datetime.now().isoformat(),
            "audio_path": str(audio_path),
            "audio_type": audio_type,
            "client_id": client_id,
            "sinistre_id": sinistre_id,
            "file_size": audio_path.stat().st_size,
            "format": audio_path.suffix,
        }
        
        # Ajouter métadonnées custom
        if metadata:
            meta.update(metadata)
        
        # Sauvegarder JSON
        json_filename = audio_path.stem + ".meta.json"
        json_path = self.metadata_dir / json_filename
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
    
    def get_client_audios(self, client_id: str = None, sinistre_id: str = None) -> list:
        """
        Récupère la liste des audios d'un client ou sinistre
        
        Args:
            client_id: ID du client
            sinistre_id: ID du sinistre
            
        Returns:
            Liste de tuples (audio_path, metadata)
        """
        results = []
        
        # Parcourir les métadonnées
        for meta_file in self.metadata_dir.glob("*.meta.json"):
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            
            # Filtrer
            match = True
            if client_id and meta.get("client_id") != client_id:
                match = False
            if sinistre_id and meta.get("sinistre_id") != sinistre_id:
                match = False
            
            if match:
                results.append((meta.get("audio_path"), meta))
        
        # Trier par timestamp (plus récent en premier)
        results.sort(key=lambda x: x[1].get("timestamp", ""), reverse=True)
        return results
    
    def get_recording_stats(self) -> Dict:
        """
        Statistiques sur les enregistrements
        
        Returns:
            Dict avec nombre d'audios, taille totale, etc.
        """
        client_audios = list(self.client_audio_dir.glob("*"))
        advisor_audios = list(self.advisor_audio_dir.glob("*"))
        
        client_size = sum(f.stat().st_size for f in client_audios)
        advisor_size = sum(f.stat().st_size for f in advisor_audios)
        
        return {
            "client_audio_count": len(client_audios),
            "advisor_audio_count": len(advisor_audios),
            "total_audio_count": len(client_audios) + len(advisor_audios),
            "client_total_size_mb": round(client_size / (1024 * 1024), 2),
            "advisor_total_size_mb": round(advisor_size / (1024 * 1024), 2),
            "total_size_mb": round((client_size + advisor_size) / (1024 * 1024), 2),
            "storage_path": str(self.base_dir)
        }
    
    def cleanup_old_audios(self, days: int = 30):
        """
        Nettoie les audios plus anciens que X jours
        
        Args:
            days: Nombre de jours à garder
        """
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        deleted_count = 0
        for meta_file in self.metadata_dir.glob("*.meta.json"):
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            
            timestamp_str = meta.get("timestamp", "")
            try:
                file_date = datetime.fromisoformat(timestamp_str)
                if file_date < cutoff_date:
                    # Supprimer audio et métadonnées
                    audio_path = Path(meta.get("audio_path", ""))
                    if audio_path.exists():
                        audio_path.unlink()
                    meta_file.unlink()
                    deleted_count += 1
            except:
                pass
        
        print(f"✅ {deleted_count} anciens audios supprimés (>{days} jours)")
        return deleted_count


if __name__ == "__main__":
    # Test du module
    print("🧪 Test du module AudioRecorder\n")
    
    recorder = AudioRecorder()
    
    # Test 1: Stats
    print("Stats actuelles:")
    stats = recorder.get_recording_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Module AudioRecorder opérationnel")
