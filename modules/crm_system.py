"""
Simulation de CRM pour la gestion des sinistres (Digital Twin).
Système de persistance en mémoire avec export SQLite.
"""

import sqlite3
import json
from typing import List, Optional
from datetime import datetime
from pathlib import Path
from models.claim_models import ClaimDigitalTwin, ClaimState


class ClaimCRM:
    """
    Système de gestion CRM pour les sinistres.
    Simule un vrai CRM d'assurance avec Digital Twins.
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialise le CRM
        
        Args:
            db_path: Chemin vers la base SQLite (optionnel, défaut: in-memory)
        """
        if db_path is None:
            db_path = "c:/Users/HP/Inssurance Advanced/data/claims_crm.db"
        
        self.db_path = db_path
        self._ensure_db_dir()
        self.connection = None
        self._init_database()
    
    def _ensure_db_dir(self):
        """Crée le répertoire de la base de données si nécessaire"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    def _init_database(self):
        """Initialise le schéma de la base de données"""
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.connection.cursor()
        
        # Table principale des sinistres
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS claims (
                claim_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                current_state TEXT NOT NULL,
                is_escalated INTEGER NOT NULL,
                escalation_reason TEXT,
                assigned_advisor TEXT,
                confidence_level REAL,
                
                -- Données JSON sérialisées
                transcript_metadata TEXT,
                cognitive_structure TEXT,
                complexity TEXT,
                interaction_history TEXT,
                state_history TEXT,
                risk_indicators TEXT,
                tags TEXT
            )
        """)
        
        # Table des interactions (pour requêtes rapides)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                claim_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                interaction_type TEXT NOT NULL,
                content TEXT,
                metadata TEXT,
                FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
            )
        """)
        
        # Index pour recherches rapides
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_claims_state 
            ON claims(current_state)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_claims_escalated 
            ON claims(is_escalated)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_interactions_claim 
            ON interactions(claim_id)
        """)
        
        self.connection.commit()
        print(f"✅ CRM Database initialisée: {self.db_path}")
    
    def create_claim(self, digital_twin: ClaimDigitalTwin) -> bool:
        """
        Crée un nouveau sinistre dans le CRM
        
        Args:
            digital_twin: Digital Twin du sinistre
            
        Returns:
            True si succès, False sinon
        """
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT INTO claims (
                    claim_id, created_at, last_updated, current_state,
                    is_escalated, escalation_reason, assigned_advisor, confidence_level,
                    transcript_metadata, cognitive_structure, complexity,
                    interaction_history, state_history, risk_indicators, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                digital_twin.claim_id,
                digital_twin.created_at.isoformat(),
                digital_twin.last_updated.isoformat(),
                digital_twin.current_state.value,
                int(digital_twin.is_escalated),
                digital_twin.escalation_reason,
                digital_twin.assigned_advisor,
                digital_twin.confidence_level,
                json.dumps(digital_twin.transcript_metadata.dict()) if digital_twin.transcript_metadata else None,
                json.dumps(digital_twin.cognitive_structure.dict()) if digital_twin.cognitive_structure else None,
                json.dumps(digital_twin.complexity.dict()) if digital_twin.complexity else None,
                json.dumps([log.dict() for log in digital_twin.interaction_history]),
                json.dumps(digital_twin.state_history),
                json.dumps(digital_twin.risk_indicators),
                json.dumps(digital_twin.tags)
            ))
            
            # Ajouter les interactions
            for interaction in digital_twin.interaction_history:
                cursor.execute("""
                    INSERT INTO interactions (claim_id, timestamp, interaction_type, content, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    digital_twin.claim_id,
                    interaction.timestamp.isoformat(),
                    interaction.interaction_type,
                    interaction.content,
                    json.dumps(interaction.metadata)
                ))
            
            self.connection.commit()
            print(f"✅ Sinistre {digital_twin.claim_id} créé dans le CRM")
            return True
            
        except Exception as e:
            print(f"❌ Erreur création sinistre: {e}")
            self.connection.rollback()
            return False
    
    def update_claim(self, digital_twin: ClaimDigitalTwin) -> bool:
        """
        Met à jour un sinistre existant
        
        Args:
            digital_twin: Digital Twin mis à jour
            
        Returns:
            True si succès
        """
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                UPDATE claims SET
                    last_updated = ?,
                    current_state = ?,
                    is_escalated = ?,
                    escalation_reason = ?,
                    assigned_advisor = ?,
                    confidence_level = ?,
                    transcript_metadata = ?,
                    cognitive_structure = ?,
                    complexity = ?,
                    interaction_history = ?,
                    state_history = ?,
                    risk_indicators = ?,
                    tags = ?
                WHERE claim_id = ?
            """, (
                digital_twin.last_updated.isoformat(),
                digital_twin.current_state.value,
                int(digital_twin.is_escalated),
                digital_twin.escalation_reason,
                digital_twin.assigned_advisor,
                digital_twin.confidence_level,
                json.dumps(digital_twin.transcript_metadata.dict()) if digital_twin.transcript_metadata else None,
                json.dumps(digital_twin.cognitive_structure.dict()) if digital_twin.cognitive_structure else None,
                json.dumps(digital_twin.complexity.dict()) if digital_twin.complexity else None,
                json.dumps([log.dict() for log in digital_twin.interaction_history]),
                json.dumps(digital_twin.state_history),
                json.dumps(digital_twin.risk_indicators),
                json.dumps(digital_twin.tags),
                digital_twin.claim_id
            ))
            
            self.connection.commit()
            print(f"✅ Sinistre {digital_twin.claim_id} mis à jour")
            return True
            
        except Exception as e:
            print(f"❌ Erreur mise à jour: {e}")
            self.connection.rollback()
            return False
    
    def get_claim(self, claim_id: str) -> Optional[ClaimDigitalTwin]:
        """
        Récupère un sinistre par son ID
        
        Args:
            claim_id: Identifiant du sinistre
            
        Returns:
            ClaimDigitalTwin ou None
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM claims WHERE claim_id = ?", (claim_id,))
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            return self._row_to_digital_twin(row, cursor.description)
            
        except Exception as e:
            print(f"❌ Erreur récupération sinistre: {e}")
            return None
    
    def list_claims(
        self, 
        state: Optional[ClaimState] = None,
        escalated_only: bool = False,
        limit: int = 100
    ) -> List[ClaimDigitalTwin]:
        """
        Liste les sinistres avec filtres optionnels
        
        Args:
            state: Filtrer par état
            escalated_only: Uniquement les sinistres escaladés
            limit: Nombre maximum de résultats
            
        Returns:
            Liste de ClaimDigitalTwin
        """
        try:
            cursor = self.connection.cursor()
            
            query = "SELECT * FROM claims WHERE 1=1"
            params = []
            
            if state:
                query += " AND current_state = ?"
                params.append(state.value)
            
            if escalated_only:
                query += " AND is_escalated = 1"
            
            query += " ORDER BY last_updated DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [
                self._row_to_digital_twin(row, cursor.description)
                for row in rows
            ]
            
        except Exception as e:
            print(f"❌ Erreur listage sinistres: {e}")
            return []
    
    def get_statistics(self) -> dict:
        """
        Récupère des statistiques globales du CRM
        
        Returns:
            Dictionnaire avec métriques clés
        """
        try:
            cursor = self.connection.cursor()
            
            stats = {}
            
            # Total de sinistres
            cursor.execute("SELECT COUNT(*) FROM claims")
            stats["total_claims"] = cursor.fetchone()[0]
            
            # Par état
            cursor.execute("""
                SELECT current_state, COUNT(*) 
                FROM claims 
                GROUP BY current_state
            """)
            stats["by_state"] = dict(cursor.fetchall())
            
            # Escaladés
            cursor.execute("SELECT COUNT(*) FROM claims WHERE is_escalated = 1")
            stats["escalated_count"] = cursor.fetchone()[0]
            
            # Complexité moyenne
            cursor.execute("""
                SELECT AVG(json_extract(complexity, '$.total_score'))
                FROM claims
                WHERE complexity IS NOT NULL
            """)
            avg_complexity = cursor.fetchone()[0]
            stats["avg_complexity"] = round(avg_complexity, 2) if avg_complexity else 0
            
            return stats
            
        except Exception as e:
            print(f"❌ Erreur statistiques: {e}")
            return {}
    
    def _row_to_digital_twin(self, row, description) -> ClaimDigitalTwin:
        """Convertit une ligne SQL en ClaimDigitalTwin"""
        from models.claim_models import TranscriptMetadata, CognitiveClaimStructure, ComplexityBreakdown
        
        columns = [col[0] for col in description]
        data = dict(zip(columns, row))
        
        # Parsing JSON
        transcript_metadata = None
        if data.get("transcript_metadata"):
            transcript_metadata = TranscriptMetadata(**json.loads(data["transcript_metadata"]))
        
        cognitive_structure = None
        if data.get("cognitive_structure"):
            cognitive_structure = CognitiveClaimStructure(**json.loads(data["cognitive_structure"]))
        
        complexity = None
        if data.get("complexity"):
            complexity = ComplexityBreakdown(**json.loads(data["complexity"]))
        
        interaction_history = []
        if data.get("interaction_history"):
            from models.claim_models import InteractionLog
            interaction_history = [
                InteractionLog(**log) for log in json.loads(data["interaction_history"])
            ]
        
        # Reconstruction du Digital Twin
        return ClaimDigitalTwin(
            claim_id=data["claim_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_updated=datetime.fromisoformat(data["last_updated"]),
            current_state=ClaimState(data["current_state"]),
            transcript_metadata=transcript_metadata,
            cognitive_structure=cognitive_structure,
            complexity=complexity,
            interaction_history=interaction_history,
            state_history=json.loads(data["state_history"]) if data.get("state_history") else [],
            is_escalated=bool(data["is_escalated"]),
            escalation_reason=data.get("escalation_reason"),
            assigned_advisor=data.get("assigned_advisor"),
            confidence_level=data.get("confidence_level", 0.0),
            risk_indicators=json.loads(data["risk_indicators"]) if data.get("risk_indicators") else [],
            tags=json.loads(data["tags"]) if data.get("tags") else []
        )
    
    def close(self):
        """Ferme la connexion à la base de données"""
        if self.connection:
            self.connection.close()
            print("🔒 Connexion CRM fermée")


# Instance globale (singleton pattern pour Streamlit)
_crm_instance = None

def get_crm() -> ClaimCRM:
    """Récupère l'instance globale du CRM (singleton)"""
    global _crm_instance
    if _crm_instance is None:
        _crm_instance = ClaimCRM()
    return _crm_instance
