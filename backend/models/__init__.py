# backend/models/__init__.py
from .db_models import (
    ClientDB, ContratDB, SinistreDB, HistoriqueConversationDB,
    ActionRecommandeeDB, RemboursementDB, ConseillerDB, EscaladeDB, Base
)

__all__ = [
    "ClientDB", "ContratDB", "SinistreDB", "HistoriqueConversationDB",
    "ActionRecommandeeDB", "RemboursementDB", "ConseillerDB", "EscaladeDB", "Base"
]
