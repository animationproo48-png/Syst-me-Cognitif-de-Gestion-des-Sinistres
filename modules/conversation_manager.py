"""
Module Conversation Manager - Orchestration LAMA
=================================================
Gère le flux conversationnel selon la méthode LAMA :
- Listen: Écouter et transcrire
- Acknowledge: Empathiser et reconnaître
- Make Statement: Résumer ce qui a été entendu
- Ask Questions: Poser des questions structurées

Intégration complète avec CRM pour mémoriser l'état.
"""

from enum import Enum
from typing import Dict, Optional, Tuple, List
from datetime import datetime
from models.claim_models import ClaimDigitalTwin, ClaimState


class ConversationPhase(Enum):
    """Phase de la conversation LAMA"""
    GREETING = "greeting"           # Accueil
    LISTEN = "listen"               # Écouter le sinistre
    ACKNOWLEDGE = "acknowledge"     # Empathiser
    MAKE_STATEMENT = "make_statement"  # Résumer
    ASK_CALLER_ID = "ask_caller_id"    # Identifier l'appellant
    ASK_VEHICLE = "ask_vehicle"        # Matricule véhicule
    ASK_NAME = "ask_name"              # Confirmer nom
    ASK_CIN = "ask_cin"                # Numéro CIN
    ASK_DETAILS = "ask_details"        # Détails contrat
    CLOSING = "closing"             # Clôture


class ConversationManager:
    """Orchestre les conversations LAMA en temps réel"""
    
    def __init__(self, digital_twin: ClaimDigitalTwin):
        """
        Initialise le gestionnaire de conversation
        
        Args:
            digital_twin: Twin du sinistre pour mémoriser l'état
        """
        self.digital_twin = digital_twin
        self.current_phase = ConversationPhase.GREETING
        self.collected_data = {
            "caller_name": None,
            "caller_id": None,
            "vehicle_plate": None,
            "vehicle_vin": None,
            "cin": None,
            "accident_description": None,
            "claim_type": None,
            "location": None,
            "damages": None
        }
        self.conversation_history = []
        self.phase_completion = {
            ConversationPhase.ASK_CALLER_ID: False,
            ConversationPhase.ASK_VEHICLE: False,
            ConversationPhase.ASK_NAME: False,
            ConversationPhase.ASK_CIN: False
        }
    
    def get_greeting_prompt(self) -> str:
        """Récupère le prompt d'accueil TTS"""
        return "Service gestion Sinistre, Bonjour!"
    
    def process_accident_description(
        self, 
        transcript: str, 
        cognitive_analysis: Dict
    ) -> Tuple[str, str, str]:
        """
        Traite la description de l'accident (LISTEN + ACKNOWLEDGE + MAKE STATEMENT)
        
        Args:
            transcript: Texte transcrit de l'utilisateur
            cognitive_analysis: Analyse cognitive du texte
            
        Returns:
            (acknowledge_text, summary_text, next_question)
        """
        # PHASE 1: LISTEN (déjà fait par STT + Cognitive Engine)
        self.collected_data["accident_description"] = transcript
        self.collected_data["claim_type"] = cognitive_analysis.get("claim_type")
        self.collected_data["location"] = cognitive_analysis.get("location")
        self.collected_data["damages"] = cognitive_analysis.get("damages")
        
        # Mémoriser dans CRM
        self.digital_twin.add_interaction(
            "accident_description",
            transcript,
            {
                "claim_type": cognitive_analysis.get("claim_type"),
                "location": cognitive_analysis.get("location"),
                "emotional_stress": cognitive_analysis.get("emotional_stress")
            }
        )
        
        # PHASE 2: ACKNOWLEDGE (empathie)
        emotional_stress = cognitive_analysis.get("emotional_stress", 5)
        acknowledge_text = self._generate_acknowledgement(emotional_stress, cognitive_analysis.get("claim_type"))
        
        # PHASE 3: MAKE STATEMENT (résumer)
        summary_text = self._generate_summary(cognitive_analysis)
        
        # PHASE 4: Passer à ASK_CALLER_ID
        self.current_phase = ConversationPhase.ASK_CALLER_ID
        next_question = self._generate_next_question()
        
        return acknowledge_text, summary_text, next_question
    
    def process_caller_identification(self, response: str) -> str:
        """
        Traite l'identification de l'appellant
        
        Args:
            response: Réponse de l'appellant (nom ou ID)
            
        Returns:
            next_question: Question suivante
        """
        self.collected_data["caller_id"] = response
        self.phase_completion[ConversationPhase.ASK_CALLER_ID] = True
        
        self.digital_twin.add_interaction(
            "caller_identification",
            response,
            {"status": "identified"}
        )
        
        self.current_phase = ConversationPhase.ASK_VEHICLE
        return self._generate_next_question()
    
    def process_vehicle_info(self, response: str) -> str:
        """Traite les informations véhicule (matricule/VIN)"""
        self.collected_data["vehicle_plate"] = response
        self.phase_completion[ConversationPhase.ASK_VEHICLE] = True
        
        self.digital_twin.add_interaction(
            "vehicle_identification",
            response,
            {"vehicle_plate": response}
        )
        
        self.current_phase = ConversationPhase.ASK_NAME
        return self._generate_next_question()
    
    def process_name_confirmation(self, response: str) -> str:
        """Traite la confirmation du nom"""
        self.collected_data["caller_name"] = response
        self.phase_completion[ConversationPhase.ASK_NAME] = True
        
        self.digital_twin.add_interaction(
            "name_confirmation",
            response,
            {"caller_name": response}
        )
        
        self.current_phase = ConversationPhase.ASK_CIN
        return self._generate_next_question()
    
    def process_cin(self, response: str) -> str:
        """Traite le numéro CIN"""
        self.collected_data["cin"] = response
        self.phase_completion[ConversationPhase.ASK_CIN] = True
        
        self.digital_twin.add_interaction(
            "cin_collection",
            response,
            {"cin": response}
        )
        
        # Toutes les infos requises collectées
        self.current_phase = ConversationPhase.ASK_DETAILS
        return self._generate_closing_question()
    
    def _generate_acknowledgement(self, stress_level: int, claim_type: str) -> str:
        """Génère un texte d'empathie adapté au stress émotionnel"""
        empathy_prompts = {
            "high": "Je comprends que c'est une situation stressante. Nous allons vous aider.",
            "medium": "Je suis là pour vous assister. Rassurez-vous, nous gérerons votre sinistre avec sérieux.",
            "low": "Merci de nous avoir contactés. Nous allons traiter votre dossier rapidement."
        }
        
        stress_category = "high" if stress_level > 7 else "medium" if stress_level > 4 else "low"
        return empathy_prompts[stress_category]
    
    def _generate_summary(self, analysis: Dict) -> str:
        """Génère un résumé de ce qui a été entendu"""
        return (
            f"D'après ce que vous m'avez décrit, "
            f"vous avez eu un sinistre de type {analysis.get('claim_type', 'automobile')} "
            f"à {analysis.get('location', 'un endroit')}. "
            f"Vous mentionnez {analysis.get('damages', 'des dommages')}. "
            f"C'est bien ça?"
        )
    
    def _generate_next_question(self) -> str:
        """Génère la question suivante selon la phase"""
        questions = {
            ConversationPhase.ASK_CALLER_ID: (
                "Pour commencer, pouvez-vous me donner votre nom ou votre numéro de client?"
            ),
            ConversationPhase.ASK_VEHICLE: (
                "Quel est le numéro d'immatriculation ou le VIN de votre véhicule?"
            ),
            ConversationPhase.ASK_NAME: (
                "Pouvez-vous confirmer votre nom complet?"
            ),
            ConversationPhase.ASK_CIN: (
                "Et votre numéro de pièce d'identité CIN, s'il vous plaît?"
            )
        }
        
        return questions.get(self.current_phase, "")
    
    def _generate_closing_question(self) -> str:
        """Génère la question de clôture (détails contrat)"""
        return (
            "Avez-vous besoin des détails de votre contrat d'assurance? "
            "Nous pouvons vous communiquer les conditions et garanties."
        )
    
    def get_collected_data(self) -> Dict:
        """Retourne les données collectées jusqu'à présent"""
        return self.collected_data.copy()
    
    def get_phase_status(self) -> Dict:
        """Retourne le statut des phases complétées"""
        return {
            "current_phase": self.current_phase.value,
            "caller_id_collected": self.phase_completion[ConversationPhase.ASK_CALLER_ID],
            "vehicle_collected": self.phase_completion[ConversationPhase.ASK_VEHICLE],
            "name_collected": self.phase_completion[ConversationPhase.ASK_NAME],
            "cin_collected": self.phase_completion[ConversationPhase.ASK_CIN],
            "all_required_info": all(self.phase_completion.values())
        }
    
    def is_required_info_complete(self) -> bool:
        """Vérifie si toutes les infos requises ont été collectées"""
        return all(self.phase_completion.values())
