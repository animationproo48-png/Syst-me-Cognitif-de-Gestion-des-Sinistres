"""
Script de démonstration rapide du système cognitif.
Exécute un traitement complet sans interface graphique.
"""

import sys
from pathlib import Path

# Ajouter le path
sys.path.insert(0, str(Path(__file__).parent))

from models.claim_models import TranscriptMetadata, ClaimDigitalTwin, ClaimState
from modules.cognitive_engine import CognitiveClaimEngine
from modules.complexity_calculator import ComplexityCalculator
from modules.decision_engine import DecisionEngine
from modules.summary_generator import SummaryGenerator
from modules.crm_system import ClaimCRM
import uuid
from datetime import datetime


def demo_simple_claim():
    """Démonstration avec un sinistre simple"""
    print("\n" + "="*80)
    print("🎙️ DEMO: Sinistre Automobile Simple")
    print("="*80 + "\n")
    
    # 1. Transcription simulée
    transcript = """
    Bonjour, j'ai eu un accident hier soir vers 19 heures sur l'autoroute A1. 
    Un véhicule m'a percuté à l'arrière alors que j'étais arrêté dans les embouteillages. 
    Mon pare-choc est enfoncé et le coffre ne ferme plus. 
    L'autre conducteur a reconnu sa responsabilité et on a rempli un constat amiable.
    J'ai pris des photos des dommages.
    """
    
    transcript_metadata = TranscriptMetadata(
        original_transcript=transcript,
        normalized_transcript=transcript.strip(),
        language="fr",
        confidence_score=0.95,
        emotional_markers=["calme"],
        hesitations=0,
        duration_seconds=45.0
    )
    
    print("✅ Transcription reçue")
    print(f"   Langue: {transcript_metadata.language}")
    print(f"   Confiance: {transcript_metadata.confidence_score*100:.0f}%\n")
    
    # 2. Analyse cognitive
    print("🧠 Analyse cognitive...")
    cognitive_engine = CognitiveClaimEngine(use_llm=False)
    cognitive_structure = cognitive_engine.analyze_claim(transcript_metadata)
    
    print(f"   Type: {cognitive_structure.claim_type.value}")
    print(f"   Date: {cognitive_structure.date_incident}")
    print(f"   Lieu: {cognitive_structure.location}")
    print(f"   Parties: {len(cognitive_structure.parties_involved)}")
    print(f"   Faits: {len(cognitive_structure.facts)}")
    print(f"   Suppositions: {len(cognitive_structure.assumptions)}\n")
    
    # 3. Calcul de complexité
    print("📊 Calcul de complexité...")
    complexity_calc = ComplexityCalculator()
    complexity = complexity_calc.calculate(cognitive_structure)
    
    print(f"   Score total: {complexity.total_score:.1f}/100")
    print(f"   Niveau: {complexity.level.value}")
    print(f"   Garanties: {complexity.guarantees_score:.0f}")
    print(f"   Tiers: {complexity.third_party_score:.0f}")
    print(f"   Documents: {complexity.missing_docs_score:.0f}")
    print(f"   Ambiguïté: {complexity.ambiguity_score:.0f}")
    print(f"   Émotionnel: {complexity.emotional_score:.0f}")
    print(f"   Incohérences: {complexity.inconsistency_score:.0f}\n")
    
    # 4. Création Digital Twin
    print("🔄 Création du Digital Twin...")
    claim_id = f"CLM-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    
    digital_twin = ClaimDigitalTwin(
        claim_id=claim_id,
        transcript_metadata=transcript_metadata,
        cognitive_structure=cognitive_structure,
        complexity=complexity,
        current_state=ClaimState.ANALYZING
    )
    
    digital_twin.add_interaction("audio_input", "Déclaration vocale reçue")
    print(f"   ID: {claim_id}\n")
    
    # 5. Décision
    print("🎯 Prise de décision...")
    decision_engine = DecisionEngine()
    should_escalate, reason, action = decision_engine.make_decision(digital_twin)
    
    if should_escalate:
        digital_twin.escalate(reason)
        print(f"   🔴 ESCALADE: {reason}")
    else:
        digital_twin.change_state(ClaimState.AUTONOMOUS, reason)
        print(f"   🟢 AUTONOME: {reason}")
    
    print(f"   Action: {action}\n")
    
    # 6. Résumés
    print("📝 Génération des résumés...")
    summary_gen = SummaryGenerator()
    
    client_summary = summary_gen.generate_client_summary(digital_twin)
    print(f"\n   👤 RÉSUMÉ CLIENT:")
    print(f"      Status: {client_summary.status}")
    print(f"      Message: {client_summary.message[:100]}...")
    print(f"      Prochaines étapes: {len(client_summary.next_steps)}")
    print(f"      Délai: {client_summary.estimated_processing_time}")
    
    advisor_brief = summary_gen.generate_advisor_brief(digital_twin)
    print(f"\n   👨‍💼 BRIEF CONSEILLER:")
    print(f"      Priorité: {advisor_brief.priority_level}")
    print(f"      Effort estimé: {advisor_brief.estimated_effort}")
    print(f"      Drapeaux de risque: {len(advisor_brief.risk_flags)}")
    print(f"      Actions suggérées: {len(advisor_brief.suggested_actions)}")
    
    # 7. Sauvegarde CRM
    print("\n💾 Sauvegarde dans le CRM...")
    crm = ClaimCRM()
    success = crm.create_claim(digital_twin)
    
    if success:
        print(f"   ✅ Sinistre {claim_id} enregistré\n")
    
    print("="*80)
    print("✨ Démonstration terminée avec succès!")
    print("="*80 + "\n")
    
    return digital_twin


def demo_complex_claim():
    """Démonstration avec un sinistre complexe"""
    print("\n" + "="*80)
    print("🎙️ DEMO: Sinistre Complexe avec Ambiguïtés")
    print("="*80 + "\n")
    
    transcript = """
    Euh, bonjour... je ne sais pas trop par où commencer. 
    Il y a eu un accident, peut-être il y a trois jours, ou quatre. 
    Il y avait plusieurs voitures impliquées, je pense trois ou quatre. 
    Je ne suis pas sûr de qui a commencé, c'était confus. 
    J'ai des dégâts importants mais je n'ai pas tous les papiers.
    Je suis vraiment stressé, je ne sais pas quoi faire.
    """
    
    transcript_metadata = TranscriptMetadata(
        original_transcript=transcript,
        normalized_transcript=transcript.strip(),
        language="fr",
        confidence_score=0.80,
        emotional_markers=["stress", "confusion"],
        hesitations=5,
        duration_seconds=50.0
    )
    
    print("✅ Transcription reçue (avec marqueurs de stress)")
    
    # Analyse complète
    cognitive_engine = CognitiveClaimEngine(use_llm=False)
    cognitive_structure = cognitive_engine.analyze_claim(transcript_metadata)
    
    complexity_calc = ComplexityCalculator()
    complexity = complexity_calc.calculate(cognitive_structure)
    
    print(f"\n📊 Score de complexité: {complexity.total_score:.1f}/100 ({complexity.level.value})")
    print(f"   Ambiguïtés détectées: {len(cognitive_structure.ambiguities)}")
    
    # Digital Twin & Décision
    claim_id = f"CLM-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    digital_twin = ClaimDigitalTwin(
        claim_id=claim_id,
        transcript_metadata=transcript_metadata,
        cognitive_structure=cognitive_structure,
        complexity=complexity,
        current_state=ClaimState.ANALYZING
    )
    
    decision_engine = DecisionEngine()
    should_escalate, reason, action = decision_engine.make_decision(digital_twin)
    
    if should_escalate:
        digital_twin.escalate(reason)
        print(f"\n🔴 ESCALADE DÉCLENCHÉE")
        print(f"   Raison: {reason}")
        
        # Brief d'escalade
        brief = decision_engine.generate_escalation_brief(digital_twin, reason)
        print(f"\n📋 Brief d'escalade généré:")
        print(f"   Priorité: {brief['priority']}")
        print(f"   Facteurs principaux: {len(brief['complexity_analysis']['main_factors'])}")
        print(f"   Points d'attention: {len(brief['attention_points']['ambiguities'])}")
        print(f"   Recommandations: {len(brief['recommended_actions'])}")
    
    # Sauvegarde
    crm = ClaimCRM()
    crm.create_claim(digital_twin)
    
    print(f"\n✅ Sinistre {claim_id} enregistré avec escalade\n")
    print("="*80 + "\n")


def main():
    """Exécute les démonstrations"""
    print("\n🚀 Démonstration du Système Cognitif de Gestion des Sinistres\n")
    
    # Demo 1: Cas simple
    demo_simple_claim()
    
    # Demo 2: Cas complexe
    demo_complex_claim()
    
    # Statistiques finales
    print("="*80)
    print("📊 STATISTIQUES FINALES CRM")
    print("="*80)
    
    crm = ClaimCRM()
    stats = crm.get_statistics()
    
    print(f"\nTotal de sinistres: {stats.get('total_claims', 0)}")
    print(f"Escaladés: {stats.get('escalated_count', 0)}")
    print(f"Complexité moyenne: {stats.get('avg_complexity', 0):.1f}/100")
    
    if stats.get('by_state'):
        print("\nDistribution par état:")
        for state, count in stats['by_state'].items():
            print(f"  - {state}: {count}")
    
    print("\n" + "="*80)
    print("✨ Toutes les démonstrations terminées!")
    print("🎯 Lancez 'streamlit run app.py' pour l'interface graphique")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
