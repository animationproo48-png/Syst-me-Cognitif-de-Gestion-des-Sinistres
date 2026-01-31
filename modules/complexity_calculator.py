"""
Calculateur de Complexité de Sinistre (Claim Complexity Index - CCI).
Évalue la complexité d'un sinistre sur une échelle 0-100 avec décomposition expliquable.
"""

from models.claim_models import (
    CognitiveClaimStructure,
    ComplexityBreakdown,
    ComplexityLevel
)


class ComplexityCalculator:
    """
    Calculateur de l'indice de complexité d'un sinistre.
    Produit un score expliquable et déterministe.
    """
    
    # Poids des différents facteurs (total = 100)
    WEIGHTS = {
        "guarantees": 15,        # Nombre de garanties impliquées
        "third_party": 20,       # Implication de tiers
        "missing_docs": 20,      # Documents manquants
        "ambiguity": 20,         # Niveau d'ambiguïté
        "emotional": 10,         # Stress émotionnel
        "inconsistency": 15      # Incohérences narratives
    }
    
    # Seuils de classification
    THRESHOLDS = {
        ComplexityLevel.SIMPLE: (0, 30),
        ComplexityLevel.MODERATE: (30, 55),
        ComplexityLevel.COMPLEX: (55, 75),
        ComplexityLevel.CRITICAL: (75, 100)
    }
    
    def calculate(
        self, 
        cognitive_structure: CognitiveClaimStructure
    ) -> ComplexityBreakdown:
        """
        Calcule l'indice de complexité avec décomposition explicable
        
        Args:
            cognitive_structure: Structure cognitive du sinistre
            
        Returns:
            ComplexityBreakdown avec score total et détails
        """
        
        # 1. Score des garanties impliquées
        guarantees_score = self._calculate_guarantees_score(cognitive_structure)
        
        # 2. Score de l'implication de tiers
        third_party_score = self._calculate_third_party_score(cognitive_structure)
        
        # 3. Score des documents manquants
        missing_docs_score = self._calculate_missing_docs_score(cognitive_structure)
        
        # 4. Score d'ambiguïté
        ambiguity_score = self._calculate_ambiguity_score(cognitive_structure)
        
        # 5. Score émotionnel
        emotional_score = self._calculate_emotional_score(cognitive_structure)
        
        # 6. Score des incohérences
        inconsistency_score = self._calculate_inconsistency_score(cognitive_structure)
        
        # Calcul du score total pondéré
        total_score = (
            guarantees_score * self.WEIGHTS["guarantees"] / 100 +
            third_party_score * self.WEIGHTS["third_party"] / 100 +
            missing_docs_score * self.WEIGHTS["missing_docs"] / 100 +
            ambiguity_score * self.WEIGHTS["ambiguity"] / 100 +
            emotional_score * self.WEIGHTS["emotional"] / 100 +
            inconsistency_score * self.WEIGHTS["inconsistency"] / 100
        )
        
        # Détermination du niveau de complexité
        complexity_level = self._determine_level(total_score)
        
        # Génération de l'explication
        explanation = self._generate_explanation(
            total_score,
            complexity_level,
            guarantees_score,
            third_party_score,
            missing_docs_score,
            ambiguity_score,
            emotional_score,
            inconsistency_score
        )
        
        return ComplexityBreakdown(
            guarantees_score=round(guarantees_score, 2),
            third_party_score=round(third_party_score, 2),
            missing_docs_score=round(missing_docs_score, 2),
            ambiguity_score=round(ambiguity_score, 2),
            emotional_score=round(emotional_score, 2),
            inconsistency_score=round(inconsistency_score, 2),
            total_score=round(total_score, 2),
            level=complexity_level,
            explanation=explanation
        )
    
    def _calculate_guarantees_score(
        self, 
        structure: CognitiveClaimStructure
    ) -> float:
        """
        Évalue la complexité liée aux garanties impliquées
        
        Score basé sur:
        - Type de sinistre (certains types sont intrinsèquement plus complexes)
        - Nombre de dommages mentionnés
        - Multiplicité des éléments affectés
        """
        base_complexity = {
            "automobile": 30,
            "habitation": 40,
            "santé": 50,
            "vie": 70,
            "responsabilité_civile": 60,
            "voyage": 35,
            "indéterminé": 50
        }
        
        score = base_complexity.get(structure.claim_type.value, 50)
        
        # Ajustement selon les dommages multiples
        damage_keywords = ["et", ",", "aussi", "également"]
        damage_count = sum(1 for kw in damage_keywords if kw in structure.damages_description.lower())
        score += min(30, damage_count * 10)
        
        return min(100, score)
    
    def _calculate_third_party_score(
        self, 
        structure: CognitiveClaimStructure
    ) -> float:
        """
        Évalue la complexité liée à l'implication de tiers
        
        Plus de parties = plus de complexité contractuelle et légale
        """
        num_parties = len(structure.parties_involved)
        
        if num_parties <= 1:
            return 0  # Pas de tiers
        elif num_parties == 2:
            return 40  # Un tiers (cas standard)
        elif num_parties == 3:
            return 70  # Plusieurs tiers
        else:
            return 90  # Cas très complexe
    
    def _calculate_missing_docs_score(
        self, 
        structure: CognitiveClaimStructure
    ) -> float:
        """
        Évalue la complexité liée aux documents manquants
        
        Documents manquants = retards et validations supplémentaires
        """
        total_docs = len(structure.mentioned_documents)
        missing_info_count = len(structure.missing_information)
        
        if total_docs == 0 and missing_info_count == 0:
            return 50  # Aucune mention de documents (suspect)
        
        # Ratio de documents requis vs mentionnés
        missing_ratio = missing_info_count / max(1, missing_info_count + total_docs)
        
        return min(100, missing_ratio * 100)
    
    def _calculate_ambiguity_score(
        self, 
        structure: CognitiveClaimStructure
    ) -> float:
        """
        Évalue la complexité liée aux ambiguïtés
        
        Ambiguïtés = incertitudes nécessitant clarification humaine
        """
        num_ambiguities = len(structure.ambiguities)
        
        if num_ambiguities == 0:
            return 0
        
        # Score basé sur le nombre et la sévérité
        total_severity = sum(amb.severity for amb in structure.ambiguities)
        avg_severity = total_severity / num_ambiguities
        
        base_score = min(50, num_ambiguities * 15)
        severity_bonus = avg_severity * 10
        
        return min(100, base_score + severity_bonus)
    
    def _calculate_emotional_score(
        self, 
        structure: CognitiveClaimStructure
    ) -> float:
        """
        Évalue la complexité liée au stress émotionnel
        
        Client stressé = communication plus difficile, risque d'omissions
        """
        stress_level = structure.emotional_stress_level
        
        # Normalisation 0-10 vers 0-100
        score = (stress_level / 10) * 100
        
        # Bonus si marqueurs de stress multiples
        if len(structure.emotional_keywords) > 2:
            score += 20
        
        return min(100, score)
    
    def _calculate_inconsistency_score(
        self, 
        structure: CognitiveClaimStructure
    ) -> float:
        """
        Évalue la complexité liée aux incohérences narratives
        
        Incohérences = suppositions vs faits, timeline floue, etc.
        """
        score = 0
        
        # Ratio suppositions / faits
        num_facts = len(structure.facts)
        num_assumptions = len(structure.assumptions)
        
        if num_facts == 0:
            score += 40  # Aucun fait clair
        elif num_assumptions > num_facts:
            score += 30  # Plus de suppositions que de faits
        
        # Date ou lieu imprécis
        if structure.date_incident in [None, "date non précisée", ""]:
            score += 25
        
        if structure.location in [None, "lieu non précisé", ""]:
            score += 25
        
        # Type de sinistre incertain
        if structure.claim_type_confidence < 0.6:
            score += 20
        
        return min(100, score)
    
    def _determine_level(self, score: float) -> ComplexityLevel:
        """Détermine le niveau de complexité selon le score"""
        for level, (min_score, max_score) in self.THRESHOLDS.items():
            if min_score <= score < max_score:
                return level
        return ComplexityLevel.CRITICAL
    
    def _generate_explanation(
        self,
        total_score: float,
        level: ComplexityLevel,
        guarantees: float,
        third_party: float,
        missing_docs: float,
        ambiguity: float,
        emotional: float,
        inconsistency: float
    ) -> str:
        """
        Génère une explication textuelle du score de complexité
        """
        explanations = []
        
        # Identification des facteurs principaux (score > 50)
        factors = {
            "garanties impliquées": guarantees,
            "implication de tiers": third_party,
            "documents manquants": missing_docs,
            "zones d'ambiguïté": ambiguity,
            "stress émotionnel": emotional,
            "incohérences narratives": inconsistency
        }
        
        high_factors = [
            name for name, score in factors.items() if score > 50
        ]
        
        # Construction de l'explication
        explanation = f"Complexité {level.value} (score: {total_score:.1f}/100). "
        
        if high_factors:
            explanation += f"Facteurs principaux: {', '.join(high_factors)}. "
        else:
            explanation += "Tous les facteurs sont dans des niveaux acceptables. "
        
        # Recommandation selon le niveau
        recommendations = {
            ComplexityLevel.SIMPLE: "Traitement autonome recommandé.",
            ComplexityLevel.MODERATE: "Traitement autonome possible avec validation.",
            ComplexityLevel.COMPLEX: "Revue par conseiller recommandée.",
            ComplexityLevel.CRITICAL: "Escalade immédiate nécessaire."
        }
        
        explanation += recommendations[level]
        
        return explanation


# Fonction utilitaire
def calculate_complexity(
    cognitive_structure: CognitiveClaimStructure
) -> ComplexityBreakdown:
    """
    Fonction utilitaire pour calcul rapide de complexité
    
    Args:
        cognitive_structure: Structure cognitive du sinistre
        
    Returns:
        ComplexityBreakdown avec détails
    """
    calculator = ComplexityCalculator()
    return calculator.calculate(cognitive_structure)
