"""
Système de Décision Intelligente et Escalade.
Détermine si un sinistre peut être traité en autonomie ou nécessite une intervention humaine.
"""

from typing import Tuple, Optional
from models.claim_models import (
    ClaimDigitalTwin,
    ComplexityBreakdown,
    ComplexityLevel,
    ClaimState,
    CognitiveClaimStructure
)


class DecisionEngine:
    """
    Moteur de décision intelligent pour la gestion autonome ou l'escalade des sinistres.
    Basé sur des règles métier expertes et le score de complexité.
    """
    
    # Seuils de décision
    AUTONOMOUS_THRESHOLD = 40  # Score < 40 -> autonomie
    REVIEW_THRESHOLD = 60      # Score 40-60 -> revue automatisée
    ESCALATION_THRESHOLD = 60  # Score > 60 -> escalade humaine
    
    def __init__(self):
        """Initialise le moteur de décision"""
        self.decision_log = []
    
    def make_decision(
        self,
        digital_twin: ClaimDigitalTwin
    ) -> Tuple[bool, str, str]:
        """
        Prend une décision sur le traitement du sinistre
        
        Args:
            digital_twin: Digital Twin complet du sinistre
            
        Returns:
            Tuple (should_escalate: bool, decision_reason: str, recommended_action: str)
        """
        complexity = digital_twin.complexity
        cognitive_structure = digital_twin.cognitive_structure
        
        # Vérifications critiques (escalade immédiate)
        critical_check, critical_reason = self._check_critical_conditions(
            digital_twin
        )
        if critical_check:
            return True, critical_reason, "escalade_immediate"
        
        # Décision basée sur le score de complexité
        complexity_score = complexity.total_score
        
        if complexity_score < self.AUTONOMOUS_THRESHOLD:
            # Traitement autonome
            return self._decision_autonomous(digital_twin)
        
        elif complexity_score < self.ESCALATION_THRESHOLD:
            # Zone de revue (validation automatisée possible)
            return self._decision_review(digital_twin)
        
        else:
            # Escalade conseiller
            return self._decision_escalate(digital_twin)
    
    def _check_critical_conditions(
        self, 
        digital_twin: ClaimDigitalTwin
    ) -> Tuple[bool, str]:
        """
        Vérifie les conditions critiques nécessitant escalade immédiate
        
        Returns:
            (is_critical: bool, reason: str)
        """
        complexity = digital_twin.complexity
        cognitive = digital_twin.cognitive_structure
        
        # Condition 1: Complexité critique
        if complexity.level == ComplexityLevel.CRITICAL:
            return True, "Complexité critique détectée"
        
        # Condition 2: Ambiguïtés sévères multiples
        severe_ambiguities = [
            amb for amb in cognitive.ambiguities if amb.severity >= 4
        ]
        if len(severe_ambiguities) >= 2:
            return True, "Multiples ambiguïtés sévères nécessitant expertise humaine"
        
        # Condition 3: Type de sinistre inconnu avec confiance faible
        if (cognitive.claim_type.value == "indéterminé" and 
            cognitive.claim_type_confidence < 0.4):
            return True, "Type de sinistre indéterminé, classification humaine requise"
        
        # Condition 4: Stress émotionnel extrême
        if cognitive.emotional_stress_level >= 8:
            return True, "Niveau de stress émotionnel très élevé, accompagnement humain requis"
        
        # Condition 5: Incohérences narratives majeures
        if complexity.inconsistency_score > 80:
            return True, "Incohérences narratives majeures nécessitant investigation"
        
        return False, ""
    
    def _decision_autonomous(
        self, 
        digital_twin: ClaimDigitalTwin
    ) -> Tuple[bool, str, str]:
        """
        Décision de traitement autonome
        """
        reason = f"Sinistre simple (score: {digital_twin.complexity.total_score:.1f}), traitement autonome possible"
        
        # Déterminer l'action autonome appropriée
        cognitive = digital_twin.cognitive_structure
        
        # Si des documents manquent
        if len(cognitive.missing_information) > 0:
            action = "demande_documents_automatique"
            reason += ". Demande automatique de documents complémentaires."
        
        # Si tout est complet
        else:
            action = "traitement_automatise_complet"
            reason += ". Tous les éléments sont présents pour traitement automatisé."
        
        return False, reason, action
    
    def _decision_review(
        self, 
        digital_twin: ClaimDigitalTwin
    ) -> Tuple[bool, str, str]:
        """
        Décision de revue automatisée (zone grise)
        """
        complexity_score = digital_twin.complexity.total_score
        reason = f"Complexité modérée (score: {complexity_score:.1f}), revue automatisée avec validation"
        
        # Analyser les sous-scores pour décision fine
        complexity = digital_twin.complexity
        
        # Si l'ambiguïté est le facteur principal
        if complexity.ambiguity_score > 60:
            return True, reason + ". Ambiguïtés trop importantes.", "escalade_clarification"
        
        # Si les documents manquants sont le problème principal
        if complexity.missing_docs_score > 70:
            action = "demande_documents_avec_suivi"
            reason += ". Demande de documents avec suivi automatisé."
            return False, reason, action
        
        # Sinon, revue automatisée
        action = "revue_automatique_approfondie"
        reason += ". Analyse automatisée approfondie avec seuils de validation."
        return False, reason, action
    
    def _decision_escalate(
        self, 
        digital_twin: ClaimDigitalTwin
    ) -> Tuple[bool, str, str]:
        """
        Décision d'escalade à un conseiller humain
        """
        complexity_score = digital_twin.complexity.total_score
        reason = f"Complexité élevée (score: {complexity_score:.1f}), expertise humaine requise"
        
        # Déterminer le type d'escalade
        complexity = digital_twin.complexity
        
        # Escalade urgente
        if complexity_score > 80:
            action = "escalade_prioritaire"
            reason += ". Traitement prioritaire recommandé."
        
        # Escalade standard
        else:
            action = "escalade_standard"
            reason += ". Assignation à conseiller expert."
        
        return True, reason, action
    
    def generate_escalation_brief(
        self, 
        digital_twin: ClaimDigitalTwin,
        escalation_reason: str
    ) -> dict:
        """
        Génère un brief structuré pour le conseiller en cas d'escalade
        
        Returns:
            Dictionnaire avec les informations essentielles pour le conseiller
        """
        cognitive = digital_twin.cognitive_structure
        complexity = digital_twin.complexity
        
        brief = {
            "claim_id": digital_twin.claim_id,
            "escalation_date": digital_twin.last_updated.isoformat(),
            "escalation_reason": escalation_reason,
            "priority": self._determine_priority(complexity.total_score),
            
            # Synthèse factuelle
            "claim_summary": {
                "type": cognitive.claim_type.value,
                "confidence": f"{cognitive.claim_type_confidence * 100:.1f}%",
                "date_incident": cognitive.date_incident,
                "location": cognitive.location,
                "damages": cognitive.damages_description
            },
            
            # Complexité détaillée
            "complexity_analysis": {
                "total_score": complexity.total_score,
                "level": complexity.level.value,
                "main_factors": self._identify_main_complexity_factors(complexity),
                "explanation": complexity.explanation
            },
            
            # Zones d'attention
            "attention_points": {
                "ambiguities": [
                    {
                        "category": amb.category,
                        "description": amb.description,
                        "severity": amb.severity
                    }
                    for amb in cognitive.ambiguities
                ],
                "missing_information": cognitive.missing_information,
                "emotional_context": f"Niveau de stress: {cognitive.emotional_stress_level}/10"
            },
            
            # Parties impliquées
            "parties": [
                {
                    "role": party.role,
                    "name": party.name or "Non spécifié",
                    "involvement": party.involvement
                }
                for party in cognitive.parties_involved
            ],
            
            # Documents
            "documents_status": {
                "mentioned": [d.type for d in cognitive.mentioned_documents],
                "required": [d.type for d in cognitive.mentioned_documents if d.required],
                "missing": cognitive.missing_information
            },
            
            # Recommandations
            "recommended_actions": self._generate_advisor_recommendations(digital_twin),
            
            # Métadonnées
            "metadata": {
                "transcript_language": digital_twin.transcript_metadata.language if digital_twin.transcript_metadata else "fr",
                "confidence_score": digital_twin.transcript_metadata.confidence_score if digital_twin.transcript_metadata else 0,
                "emotional_markers": cognitive.emotional_keywords
            }
        }
        
        return brief
    
    def _determine_priority(self, complexity_score: float) -> str:
        """Détermine la priorité de traitement"""
        if complexity_score > 80:
            return "HAUTE"
        elif complexity_score > 60:
            return "MOYENNE"
        else:
            return "NORMALE"
    
    def _identify_main_complexity_factors(
        self, 
        complexity: ComplexityBreakdown
    ) -> list:
        """Identifie les 2-3 facteurs principaux de complexité"""
        factors = {
            "Garanties multiples": complexity.guarantees_score,
            "Implication de tiers": complexity.third_party_score,
            "Documents manquants": complexity.missing_docs_score,
            "Ambiguïtés": complexity.ambiguity_score,
            "Stress émotionnel": complexity.emotional_score,
            "Incohérences": complexity.inconsistency_score
        }
        
        # Trier par score décroissant et prendre les 3 premiers
        sorted_factors = sorted(
            factors.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:3]
        
        return [
            {"factor": name, "score": score}
            for name, score in sorted_factors if score > 30
        ]
    
    def _generate_advisor_recommendations(
        self, 
        digital_twin: ClaimDigitalTwin
    ) -> list:
        """Génère des recommandations d'actions pour le conseiller"""
        recommendations = []
        cognitive = digital_twin.cognitive_structure
        complexity = digital_twin.complexity
        
        # Recommandation 1: Clarification prioritaire
        if complexity.ambiguity_score > 50:
            recommendations.append(
                "Clarifier les ambiguïtés identifiées avant traitement"
            )
        
        # Recommandation 2: Collecte de documents
        if len(cognitive.missing_information) > 0:
            recommendations.append(
                f"Demander les documents manquants: {', '.join(cognitive.missing_information[:3])}"
            )
        
        # Recommandation 3: Contact tiers
        if len(cognitive.parties_involved) > 1:
            recommendations.append(
                "Vérifier les déclarations croisées avec les tiers impliqués"
            )
        
        # Recommandation 4: Gestion émotionnelle
        if cognitive.emotional_stress_level > 6:
            recommendations.append(
                "Client en situation de stress, approche empathique recommandée"
            )
        
        # Recommandation 5: Vérification contractuelle
        if complexity.guarantees_score > 60:
            recommendations.append(
                "Vérifier les clauses contractuelles applicables (garanties multiples)"
            )
        
        return recommendations


# Fonction utilitaire
def decide_claim_routing(digital_twin: ClaimDigitalTwin) -> dict:
    """
    Fonction utilitaire pour décision de routage d'un sinistre
    
    Returns:
        Dictionnaire avec décision et brief si escalade
    """
    engine = DecisionEngine()
    should_escalate, reason, action = engine.make_decision(digital_twin)
    
    result = {
        "should_escalate": should_escalate,
        "reason": reason,
        "recommended_action": action
    }
    
    if should_escalate:
        result["escalation_brief"] = engine.generate_escalation_brief(
            digital_twin, reason
        )
    
    return result
