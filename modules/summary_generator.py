"""
Générateur de Résumés Multi-Niveaux.
Produit des résumés adaptés à chaque audience: client, conseiller, management.
"""

from datetime import datetime, timedelta
from models.claim_models import (
    ClaimDigitalTwin,
    ClientSummary,
    AdvisorBrief,
    ManagementSummary,
    ComplexityLevel
)


class SummaryGenerator:
    """
    Génère des résumés multi-niveaux adaptés à chaque type d'audience.
    Principe: même information, communication différenciée.
    """
    
    def __init__(self):
        """Initialise le générateur de résumés"""
        self.contact_info = "0800 123 456"  # À configurer
    
    def generate_client_summary(
        self, 
        digital_twin: ClaimDigitalTwin
    ) -> ClientSummary:
        """
        Génère un résumé clair et rassurant pour le client
        
        Caractéristiques:
        - Langage simple et accessible
        - Prochaines étapes actionnables
        - Timeframes clairs
        - Ton rassurant
        """
        cognitive = digital_twin.cognitive_structure
        complexity = digital_twin.complexity
        
        # Déterminer le statut client-friendly
        status = self._format_status_for_client(digital_twin.current_state)
        
        # Générer les prochaines étapes
        next_steps = self._generate_client_next_steps(digital_twin)
        
        # Lister les documents requis
        documents_required = self._list_required_documents(cognitive)
        
        # Estimer le délai de traitement
        processing_time = self._estimate_processing_time(complexity)
        
        # Message personnalisé
        message = self._craft_client_message(digital_twin)
        
        return ClientSummary(
            claim_id=digital_twin.claim_id,
            status=status,
            next_steps=next_steps,
            documents_required=documents_required,
            estimated_processing_time=processing_time,
            contact_info=self.contact_info,
            message=message
        )
    
    def generate_advisor_brief(
        self, 
        digital_twin: ClaimDigitalTwin
    ) -> AdvisorBrief:
        """
        Génère un brief structuré et technique pour le conseiller
        
        Caractéristiques:
        - Vue structurée des faits
        - Identification des zones à risque
        - Recommandations d'actions expertes
        - Contexte émotionnel pour adaptation de la communication
        """
        cognitive = digital_twin.cognitive_structure
        complexity = digital_twin.complexity
        
        # Structurer les faits vérifiés
        structured_facts = self._structure_facts_for_advisor(cognitive)
        
        # Identifier les ambiguïtés non résolues
        unresolved_ambiguities = [
            {
                "category": amb.category,
                "description": amb.description,
                "severity": amb.severity,
                "impact": amb.impact_on_decision
            }
            for amb in cognitive.ambiguities
        ]
        
        # Identifier les drapeaux de risque
        risk_flags = self._identify_risk_flags(digital_twin)
        
        # Générer les actions suggérées
        suggested_actions = self._generate_advisor_actions(digital_twin)
        
        # Déterminer la priorité
        priority_level = self._determine_advisor_priority(complexity)
        
        # Estimer l'effort
        estimated_effort = self._estimate_advisor_effort(complexity)
        
        # Contexte émotionnel
        emotional_context = self._describe_emotional_context(cognitive)
        
        return AdvisorBrief(
            claim_id=digital_twin.claim_id,
            claim_type=cognitive.claim_type.value,
            complexity_score=complexity.total_score,
            complexity_level=complexity.level.value,
            structured_facts=structured_facts,
            unresolved_ambiguities=unresolved_ambiguities,
            risk_flags=risk_flags,
            suggested_actions=suggested_actions,
            priority_level=priority_level,
            estimated_effort=estimated_effort,
            emotional_context=emotional_context,
            client_stress_level=cognitive.emotional_stress_level
        )
    
    def generate_management_summary(
        self, 
        digital_twin: ClaimDigitalTwin
    ) -> ManagementSummary:
        """
        Génère un résumé exécutif pour le management
        
        Caractéristiques:
        - KPIs et métriques clés
        - Indicateurs de risque
        - Impact financier estimé
        - Nécessité d'attention spéciale
        """
        cognitive = digital_twin.cognitive_structure
        complexity = digital_twin.complexity
        
        # Raison d'escalade (si applicable)
        escalation_reason = digital_twin.escalation_reason or "N/A"
        
        # Indicateurs de risque
        risk_indicators = self._identify_management_risks(digital_twin)
        
        # Statut de traitement
        processing_status = self._format_processing_status(digital_twin)
        
        # Estimation d'impact financier
        cost_impact = self._estimate_cost_impact(cognitive, complexity)
        
        # Nécessité d'attention
        requires_attention = self._determine_management_attention(complexity)
        
        return ManagementSummary(
            claim_id=digital_twin.claim_id,
            claim_type=cognitive.claim_type.value,
            complexity_score=complexity.total_score,
            escalation_reason=escalation_reason,
            risk_indicators=risk_indicators,
            processing_status=processing_status,
            estimated_cost_impact=cost_impact,
            requires_attention=requires_attention
        )
    
    # === Méthodes utilitaires pour Client Summary ===
    
    def _format_status_for_client(self, state) -> str:
        """Formatte le statut en langage client"""
        status_mapping = {
            "reçu": "Votre déclaration a été reçue",
            "en_analyse": "Votre dossier est en cours d'analyse",
            "documents_manquants": "En attente de documents complémentaires",
            "traitement_autonome": "Votre dossier est en cours de traitement",
            "escaladé_conseiller": "Un conseiller va prendre contact avec vous",
            "résolu": "Votre sinistre a été traité",
            "rejeté": "Décision prise sur votre dossier"
        }
        return status_mapping.get(state.value, "En cours de traitement")
    
    def _generate_client_next_steps(self, digital_twin: ClaimDigitalTwin) -> list:
        """Génère les prochaines étapes pour le client"""
        steps = []
        cognitive = digital_twin.cognitive_structure
        
        # Si documents manquants
        if len(cognitive.missing_information) > 0:
            steps.append(
                f"Envoyez-nous les documents suivants: {', '.join(cognitive.missing_information[:2])}"
            )
        
        # Si escaladé
        if digital_twin.is_escalated:
            steps.append(
                f"Un conseiller vous contactera dans les 24-48 heures"
            )
        else:
            steps.append(
                "Nous analysons votre dossier et reviendrons vers vous rapidement"
            )
        
        # Toujours: possibilité de contact
        steps.append(
            f"Pour toute question, contactez-nous au {self.contact_info}"
        )
        
        return steps
    
    def _list_required_documents(self, cognitive) -> list:
        """Liste les documents requis manquants"""
        docs = []
        
        # Documents explicitement manquants
        docs.extend(cognitive.missing_information)
        
        # Documents mentionnés mais à confirmer
        for doc in cognitive.mentioned_documents:
            if doc.status == "manquant":
                docs.append(doc.type)
        
        return list(set(docs))  # Déduplliquer
    
    def _estimate_processing_time(self, complexity) -> str:
        """Estime le délai de traitement"""
        if complexity.level == ComplexityLevel.SIMPLE:
            return "24-48 heures"
        elif complexity.level == ComplexityLevel.MODERATE:
            return "3-5 jours ouvrés"
        elif complexity.level == ComplexityLevel.COMPLEX:
            return "1-2 semaines"
        else:
            return "2-4 semaines"
    
    def _craft_client_message(self, digital_twin: ClaimDigitalTwin) -> str:
        """Crée un message personnalisé et rassurant"""
        cognitive = digital_twin.cognitive_structure
        
        if digital_twin.is_escalated:
            return (
                "Nous avons bien enregistré votre déclaration. "
                "Compte tenu de la nature de votre sinistre, un conseiller expert "
                "va prendre en charge votre dossier personnellement. "
                "Nous mettons tout en œuvre pour vous accompagner au mieux."
            )
        
        elif digital_twin.complexity.level == ComplexityLevel.SIMPLE:
            return (
                "Bonne nouvelle ! Votre sinistre peut être traité rapidement. "
                "Nous avons toutes les informations nécessaires et allons "
                "procéder au traitement dans les meilleurs délais."
            )
        
        else:
            return (
                "Nous avons bien reçu votre déclaration. "
                "Notre équipe analyse votre dossier avec attention. "
                "Vous recevrez une mise à jour prochainement."
            )
    
    # === Méthodes utilitaires pour Advisor Brief ===
    
    def _structure_facts_for_advisor(self, cognitive) -> list:
        """Structure les faits de manière exploitable pour le conseiller"""
        structured = []
        
        # Fait 1: Type et confiance
        structured.append(
            f"Type: {cognitive.claim_type.value} "
            f"(confiance: {cognitive.claim_type_confidence * 100:.0f}%)"
        )
        
        # Fait 2: Circonstances
        if cognitive.date_incident and cognitive.location:
            structured.append(
                f"Incident: {cognitive.date_incident} à {cognitive.location}"
            )
        
        # Fait 3: Parties
        if len(cognitive.parties_involved) > 1:
            parties_str = ", ".join([p.role for p in cognitive.parties_involved])
            structured.append(f"Parties impliquées: {parties_str}")
        
        # Fait 4: Dommages
        if cognitive.damages_description:
            structured.append(f"Dommages: {cognitive.damages_description[:150]}")
        
        # Fait 5: Documents
        if cognitive.mentioned_documents:
            docs_str = ", ".join([d.type for d in cognitive.mentioned_documents])
            structured.append(f"Documents mentionnés: {docs_str}")
        
        return structured
    
    def _identify_risk_flags(self, digital_twin: ClaimDigitalTwin) -> list:
        """Identifie les drapeaux de risque pour le conseiller"""
        flags = []
        cognitive = digital_twin.cognitive_structure
        complexity = digital_twin.complexity
        
        # Risque 1: Incohérences narratives
        if complexity.inconsistency_score > 60:
            flags.append("⚠️ Incohérences narratives à clarifier")
        
        # Risque 2: Ambiguïtés contractuelles
        contractual_ambiguities = [
            amb for amb in cognitive.ambiguities 
            if amb.category == "contractuelle"
        ]
        if contractual_ambiguities:
            flags.append("⚠️ Ambiguïtés contractuelles identifiées")
        
        # Risque 3: Tiers multiples
        if len(cognitive.parties_involved) > 2:
            flags.append("⚠️ Multiples parties impliquées (complexité légale)")
        
        # Risque 4: Information critique manquante
        if len(cognitive.missing_information) > 3:
            flags.append("⚠️ Nombreux documents manquants")
        
        # Risque 5: Client sous stress
        if cognitive.emotional_stress_level > 7:
            flags.append("⚠️ Client en état de stress élevé")
        
        return flags
    
    def _generate_advisor_actions(self, digital_twin: ClaimDigitalTwin) -> list:
        """Génère des actions concrètes pour le conseiller"""
        actions = []
        cognitive = digital_twin.cognitive_structure
        
        # Action 1: Contact client
        actions.append("Contacter le client pour confirmation des faits")
        
        # Action 2: Documents
        if cognitive.missing_information:
            actions.append(
                f"Demander: {', '.join(cognitive.missing_information[:2])}"
            )
        
        # Action 3: Vérifications
        if len(cognitive.ambiguities) > 0:
            actions.append("Clarifier les ambiguïtés identifiées")
        
        # Action 4: Validation contractuelle
        actions.append("Vérifier la couverture contractuelle applicable")
        
        return actions
    
    def _determine_advisor_priority(self, complexity) -> str:
        """Détermine la priorité pour le conseiller"""
        if complexity.total_score > 75:
            return "URGENTE"
        elif complexity.total_score > 55:
            return "ÉLEVÉE"
        else:
            return "NORMALE"
    
    def _estimate_advisor_effort(self, complexity) -> str:
        """Estime l'effort requis"""
        if complexity.total_score < 40:
            return "Faible (< 1h)"
        elif complexity.total_score < 60:
            return "Modéré (1-3h)"
        else:
            return "Élevé (> 3h)"
    
    def _describe_emotional_context(self, cognitive) -> str:
        """Décrit le contexte émotionnel pour le conseiller"""
        stress = cognitive.emotional_stress_level
        markers = cognitive.emotional_keywords
        
        if stress < 3:
            context = "Client calme et factuel"
        elif stress < 6:
            context = "Client légèrement préoccupé"
        elif stress < 8:
            context = "Client anxieux, nécessite écoute attentive"
        else:
            context = "Client très stressé, approche empathique essentielle"
        
        if markers:
            context += f" (marqueurs: {', '.join(markers[:3])})"
        
        return context
    
    # === Méthodes utilitaires pour Management Summary ===
    
    def _identify_management_risks(self, digital_twin: ClaimDigitalTwin) -> list:
        """Identifie les risques pour le management"""
        risks = []
        complexity = digital_twin.complexity
        
        if complexity.total_score > 70:
            risks.append("Complexité élevée")
        
        if complexity.third_party_score > 60:
            risks.append("Risque contentieux (tiers)")
        
        if complexity.inconsistency_score > 60:
            risks.append("Incohérences à investiguer")
        
        if digital_twin.cognitive_structure.emotional_stress_level > 7:
            risks.append("Risque de réclamation client")
        
        return risks
    
    def _format_processing_status(self, digital_twin: ClaimDigitalTwin) -> str:
        """Formatte le statut de traitement pour management"""
        if digital_twin.is_escalated:
            return f"Escaladé - {digital_twin.assigned_advisor or 'En attente assignation'}"
        else:
            return f"Traitement autonome - {digital_twin.current_state.value}"
    
    def _estimate_cost_impact(self, cognitive, complexity) -> str:
        """Estime l'impact financier potentiel"""
        # Estimation simplifiée basée sur le type et la complexité
        base_costs = {
            "automobile": "2000-5000€",
            "habitation": "3000-8000€",
            "santé": "1000-10000€",
            "responsabilité_civile": "5000-20000€",
            "voyage": "500-2000€"
        }
        
        base = base_costs.get(cognitive.claim_type.value, "À évaluer")
        
        if complexity.total_score > 70:
            return f"{base} (potentiellement plus élevé)"
        else:
            return base
    
    def _determine_management_attention(self, complexity) -> bool:
        """Détermine si le sinistre nécessite l'attention du management"""
        return (
            complexity.level == ComplexityLevel.CRITICAL or
            complexity.total_score > 75
        )


# Fonctions utilitaires
def generate_all_summaries(digital_twin: ClaimDigitalTwin) -> dict:
    """
    Génère tous les résumés en une seule fois
    
    Returns:
        Dict avec client_summary, advisor_brief, management_summary
    """
    generator = SummaryGenerator()
    
    return {
        "client_summary": generator.generate_client_summary(digital_twin),
        "advisor_brief": generator.generate_advisor_brief(digital_twin),
        "management_summary": generator.generate_management_summary(digital_twin)
    }
