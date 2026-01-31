import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, ScatterChart, Scatter } from 'recharts';
import { FiTrendingUp, FiAlertCircle, FiCheckCircle, FiClock, FiFilter, FiDownload, FiPhone, FiMail, FiMapPin, FiUser, FiDollarSign, FiBarChart2, FiLayers, FiCalendar, FiFlag, FiFileText } from 'react-icons/fi';

export default function DashboardAdvisor() {
  // ============= DONNÉES CRM MAROCAINES =============
  const crm_database = [
    {
      id: 'C001',
      name: 'Mohammed El Fassi',
      phone: '+212 6 12 34 56 78',
      email: 'mohammed.fassi@gmail.com',
      city: 'Casablanca',
      contract: 'AUTO-PREM-2024',
      premium: 1250,
      customer_since: '2020-03-15',
      claims_history: 2,
      policy: {
        policy_number: 'MA-AUTO-CP-2024-001',
        provider: 'AssuraTech Maroc',
        product: 'Auto Premium Plus',
        status: 'Actif',
        coverage: ['Responsabilité civile', 'Tous risques', 'Vol', 'Incendie', 'Bris de glace', 'Assistance 24/7'],
        deductible: 500,
        coverage_limit: 500000,
        renewal_date: '2026-03-15',
        vehicle: {
          plate: '12345-A-10',
          brand: 'Renault',
          model: 'Clio V',
          year: 2022,
          vin: 'VF1RJA006X1234567'
        },
        beneficiaries: ['Épouse: Salma El Fassi']
      }
    },
    {
      id: 'C002',
      name: 'Fatima Bennani',
      phone: '+212 6 98 76 54 32',
      email: 'fatima.bennani@hotmail.com',
      city: 'Fès',
      contract: 'AUTO-STAND-2023',
      premium: 850,
      customer_since: '2022-07-20',
      claims_history: 0,
      policy: {
        policy_number: 'MA-AUTO-ST-2023-019',
        provider: 'AssuraTech Maroc',
        product: 'Auto Standard',
        status: 'Actif',
        coverage: ['Responsabilité civile', 'Vol', 'Incendie', 'Assistance 24/7'],
        deductible: 800,
        coverage_limit: 300000,
        renewal_date: '2026-07-20',
        vehicle: {
          plate: '67890-B-12',
          brand: 'Dacia',
          model: 'Sandero',
          year: 2020,
          vin: 'UU1SDXDJX65432109'
        },
        beneficiaries: ['Père: Abdelkader Bennani']
      }
    },
    {
      id: 'C003',
      name: 'Ali Tazi',
      phone: '+212 6 55 44 33 22',
      email: 'ali.tazi@yahoo.com',
      city: 'Rabat',
      contract: 'AUTO-ELITE-2024',
      premium: 2150,
      customer_since: '2019-01-10',
      claims_history: 3,
      policy: {
        policy_number: 'MA-AUTO-EL-2024-077',
        provider: 'AssuraTech Maroc',
        product: 'Auto Elite',
        status: 'Actif',
        coverage: ['Tous risques', 'Vol', 'Incendie', 'Bris de glace', 'Catastrophes naturelles', 'Assistance premium'],
        deductible: 0,
        coverage_limit: 800000,
        renewal_date: '2026-01-10',
        vehicle: {
          plate: '23456-R-13',
          brand: 'Volkswagen',
          model: 'Tiguan',
          year: 2023,
          vin: 'WVGZZZ5NZMW123456'
        },
        beneficiaries: ['Épouse: Lina Tazi', 'Fils: Adam Tazi']
      }
    },
    {
      id: 'C004',
      name: 'Nadia Chraibi',
      phone: '+212 6 77 88 99 00',
      email: 'nadia.chraibi@outlook.com',
      city: 'Marrakech',
      contract: 'AUTO-PREM-2024',
      premium: 1400,
      customer_since: '2021-05-22',
      claims_history: 1,
      policy: {
        policy_number: 'MA-AUTO-CP-2024-055',
        provider: 'AssuraTech Maroc',
        product: 'Auto Premium Plus',
        status: 'Actif',
        coverage: ['Responsabilité civile', 'Tous risques', 'Vol', 'Incendie', 'Assistance 24/7'],
        deductible: 700,
        coverage_limit: 500000,
        renewal_date: '2026-05-22',
        vehicle: {
          plate: '44556-M-8',
          brand: 'Peugeot',
          model: '208',
          year: 2021,
          vin: 'VF3URHNZMN1234567'
        },
        beneficiaries: ['Mère: Amina Chraibi']
      }
    },
    {
      id: 'C005',
      name: 'Hassan Ouaaziz',
      phone: '+212 6 11 22 33 44',
      email: 'hassan.ouaaziz@gmail.com',
      city: 'Tangier',
      contract: 'AUTO-STAND-2024',
      premium: 950,
      customer_since: '2023-02-14',
      claims_history: 0,
      policy: {
        policy_number: 'MA-AUTO-ST-2024-031',
        provider: 'AssuraTech Maroc',
        product: 'Auto Standard',
        status: 'Actif',
        coverage: ['Responsabilité civile', 'Vol', 'Assistance 24/7'],
        deductible: 1000,
        coverage_limit: 250000,
        renewal_date: '2026-02-14',
        vehicle: {
          plate: '77889-T-16',
          brand: 'Hyundai',
          model: 'i20',
          year: 2019,
          vin: 'KMHBT51HSLU123456'
        },
        beneficiaries: ['Frère: Said Ouaaziz']
      }
    },
    {
      id: 'C006',
      name: 'Zahra Belkadi',
      phone: '+212 6 66 55 44 33',
      email: 'zahra.belkadi@gmail.com',
      city: 'Agadir',
      contract: 'AUTO-PREM-2024',
      premium: 1180,
      customer_since: '2020-11-08',
      claims_history: 2,
      policy: {
        policy_number: 'MA-AUTO-CP-2024-088',
        provider: 'AssuraTech Maroc',
        product: 'Auto Premium Plus',
        status: 'Actif',
        coverage: ['Responsabilité civile', 'Tous risques', 'Vol', 'Incendie', 'Bris de glace'],
        deductible: 600,
        coverage_limit: 450000,
        renewal_date: '2026-11-08',
        vehicle: {
          plate: '33990-A-9',
          brand: 'Toyota',
          model: 'Corolla',
          year: 2021,
          vin: 'JTNBZRBJ0MJ123456'
        },
        beneficiaries: ['Époux: Omar Belkadi']
      }
    },
    {
      id: 'C007',
      name: 'Yassine Alaoui',
      phone: '+212 6 22 33 44 55',
      email: 'yassine.alaoui@gmail.com',
      city: 'Rabat',
      contract: 'AUTO-COMP-2025',
      premium: 1650,
      customer_since: '2024-04-05',
      claims_history: 1,
      policy: {
        policy_number: 'MA-AUTO-COMP-2025-014',
        provider: 'AssuraTech Maroc',
        product: 'Auto Complet',
        status: 'Actif',
        coverage: ['Responsabilité civile', 'Tous risques', 'Vol', 'Incendie', 'Bris de glace', 'Catastrophes naturelles', 'Assistance premium'],
        deductible: 750,
        coverage_limit: 600000,
        renewal_date: '2026-04-05',
        vehicle: {
          plate: '11223-R-19',
          brand: 'Mercedes',
          model: 'A200',
          year: 2022,
          vin: 'W1K3F4HB9NN123456'
        },
        beneficiaries: ['Mère: Samira Alaoui', 'Père: Abdelrahman Alaoui']
      }
    },
  ];

  // ============= DONNÉES SINISTRES DÉTAILLÉES =============
  const claims_database = [
    {
      id: 'SINISTRE-001',
      customer_id: 'C001',
      type: 'Accrochage',
      description: 'J\'ai eu un accrochage hier. L\'autre conducteur a rayé mon aile. Nous avons fait un constat amiable.',
      date_declared: '2026-01-31 14:23',
      date_incident: '2026-01-30 09:15',
      location: 'Route Casa-Fès, Km 45',
      third_party: 'Autre conducteur (inconnu)',
      damage_estimate: 8500,
      status: 'En Analyse',
      complexity_score: 28,
      escalation_required: false,
      escalation_reason: null,
      priority: 'BASSE',
      
      // Données cognitives détaillées
      cognitive_analysis: {
        facts_count: 7,
        assumptions_count: 1,
        contradictions: 0,
        ambiguities: 0,
        emotional_stress: 2,
        confidence: 95,
      },
      
      // Dimensions du CCI
      cci_breakdown: {
        guarantees: { score: 20, details: 'Couverture responsabilité civile standard' },
        third_parties: { score: 15, details: 'Tiers non identifié - faible complexité' },
        documents: { score: 25, details: 'Constat amiable disponible' },
        ambiguities: { score: 10, details: 'Détails clairs du sinistre' },
        emotional: { score: 8, details: 'Client calme, communication directe' },
        inconsistencies: { score: 5, details: 'Aucune contradiction détectée' }
      },
      
      // Transcription complète
      full_transcript: 'Bonjour, j\'ai eu un accrochage hier. L\'autre conducteur a rayé mon aile. Nous avons fait un constat amiable.',
      transcript_language: 'Français',
      
      // Analyse économique
      economics: {
        damage_estimate: 8500,
        third_party_liability: true,
        deductible_applicable: 500,
        coverage_limit: 500000,
        probable_payout: 8000
      },
      
      // Timeline
      timeline: [
        { time: '2026-01-30 09:15', action: 'Sinistre', description: 'Accrochage sur route Casa-Fès' },
        { time: '2026-01-30 09:45', action: 'Constat', description: 'Constat amiable signé' },
        { time: '2026-01-31 14:23', action: 'Déclaration', description: 'Déclaration reçue via système AI' },
        { time: '2026-01-31 14:35', action: 'Analyse', description: 'Analyse cognitive complétée' },
        { time: '2026-01-31 14:40', action: 'Décision', description: 'Traitement autonome recommandé' }
      ],
      
      next_actions: ['Demander photos dégâts', 'Vérifier antécédents tiers', 'Estimation expert'],
      assigned_to: null
    },
    {
      id: 'SINISTRE-002',
      customer_id: 'C003',
      type: 'Accident Multi-véhicule',
      description: 'Euh... il y a eu un accident il y a quelques jours. Je crois qu\'il y avait 3 voitures. Je ne sais pas qui a commencé. Je n\'ai pas tous les papiers. Je suis stressé.',
      date_declared: '2026-01-31 16:50',
      date_incident: '2026-01-28 17:30',
      location: 'Autoroute A3, Sortie Skhirat',
      third_party: 'Deux autres conducteurs',
      damage_estimate: 35000,
      status: 'ESCALADE URGENTE',
      complexity_score: 72,
      escalation_required: true,
      escalation_reason: 'Ambiguïtés élevées + stress émotionnel + multi-tiers',
      priority: 'HAUTE',
      
      cognitive_analysis: {
        facts_count: 3,
        assumptions_count: 6,
        contradictions: 1,
        ambiguities: 5,
        emotional_stress: 8,
        confidence: 45,
      },
      
      cci_breakdown: {
        guarantees: { score: 45, details: 'Couverture collision complète à vérifier' },
        third_parties: { score: 80, details: '2 tiers - identités flou' },
        documents: { score: 40, details: 'Papiers manquants - situation complexe' },
        ambiguities: { score: 75, details: 'Multiple: date vague, culpabilité inconnue' },
        emotional: { score: 72, details: 'Client très stressé - besoin support' },
        inconsistencies: { score: 50, details: 'Contradiction sur responsabilité' }
      },
      
      full_transcript: 'Euh... il y a eu un accident il y a quelques jours. Je crois qu\'il y avait 3 voitures. Je ne sais pas qui a commencé. Je n\'ai pas tous les papiers. Je suis stressé.',
      transcript_language: 'Français',
      
      economics: {
        damage_estimate: 35000,
        third_party_liability: true,
        deductible_applicable: 1500,
        coverage_limit: 500000,
        probable_payout: 33500
      },
      
      timeline: [
        { time: '2026-01-28 17:30', action: 'Sinistre', description: 'Accident à 3 véhicules sur A3' },
        { time: '2026-01-28 18:00', action: 'Police', description: 'Rapport police demandé' },
        { time: '2026-01-31 16:50', action: 'Déclaration', description: 'Déclaration reçue - STRESS détecté' },
        { time: '2026-01-31 17:05', action: 'Escalade', description: 'Escalade automatique - complexité haute' }
      ],
      
      next_actions: ['Contact client urgent', 'Demander rapport police', 'Identifier tiers', 'Expert inspection'],
      assigned_to: 'Ahmed El Mansouri'
    },
    {
      id: 'SINISTRE-003',
      customer_id: 'C002',
      type: 'Vandalisme',
      description: 'Quelqu\'un a endommagé ma voiture la nuit dernière dans mon garage. Les vitres sont cassées et la carrosserie rayée.',
      date_declared: '2026-01-31 10:15',
      date_incident: '2026-01-30 21:00',
      location: 'Garage privé, Fès - Ville Nouvelle',
      third_party: 'Inconnu',
      damage_estimate: 12000,
      status: 'En Analyse',
      complexity_score: 38,
      escalation_required: false,
      escalation_reason: null,
      priority: 'MOYENNE',
      
      cognitive_analysis: {
        facts_count: 4,
        assumptions_count: 2,
        contradictions: 0,
        ambiguities: 2,
        emotional_stress: 5,
        confidence: 80,
      },
      
      cci_breakdown: {
        guarantees: { score: 30, details: 'Couverture vandalisme applicable' },
        third_parties: { score: 50, details: 'Tiers inconnu - pas d\'info' },
        documents: { score: 35, details: 'Photos des dégâts nécessaires' },
        ambiguities: { score: 35, details: 'Heure et circonstances floues' },
        emotional: { score: 40, details: 'Client préoccupé mais calme' },
        inconsistencies: { score: 25, details: 'Pas d\'incohérence majeure' }
      },
      
      full_transcript: 'Quelqu\'un a endommagé ma voiture la nuit dernière dans mon garage. Les vitres sont cassées et la carrosserie rayée.',
      transcript_language: 'Français',
      
      economics: {
        damage_estimate: 12000,
        third_party_liability: false,
        deductible_applicable: 800,
        coverage_limit: 300000,
        probable_payout: 11200
      },
      
      timeline: [
        { time: '2026-01-30 21:00', action: 'Sinistre', description: 'Vandalisme constaté' },
        { time: '2026-01-31 10:15', action: 'Déclaration', description: 'Déclaration via système AI' },
        { time: '2026-01-31 10:30', action: 'Analyse', description: 'Analyse cognitive: complexité moyenne' }
      ],
      
      next_actions: ['Demander rapport police', 'Photos des dégâts', 'Estimation réparation'],
      assigned_to: null
    },
    {
      id: 'SINISTRE-004',
      customer_id: 'C004',
      type: 'Collision',
      description: 'Accident frontale avec une autre voiture. L\'autre conducteur était responsable, témoin présent. Constat amiable fait.',
      date_declared: '2026-01-31 12:45',
      date_incident: '2026-01-31 11:30',
      location: 'Boulevard Mohammed V, Marrakech',
      third_party: 'Yamaha Mouhcine',
      damage_estimate: 18500,
      status: 'En Analyse',
      complexity_score: 32,
      escalation_required: false,
      escalation_reason: null,
      priority: 'MOYENNE',
      
      cognitive_analysis: {
        facts_count: 8,
        assumptions_count: 0,
        contradictions: 0,
        ambiguities: 1,
        emotional_stress: 3,
        confidence: 92,
      },
      
      cci_breakdown: {
        guarantees: { score: 25, details: 'Responsabilité civile tiers' },
        third_parties: { score: 20, details: 'Tiers identifié - données complètes' },
        documents: { score: 28, details: 'Constat amiable complet' },
        ambiguities: { score: 15, details: 'Une seule ambiguïté mineure' },
        emotional: { score: 10, details: 'Client très calme' },
        inconsistencies: { score: 5, details: 'Aucune incohérence' }
      },
      
      full_transcript: 'Accident frontale avec une autre voiture. L\'autre conducteur était responsable, témoin présent. Constat amiable fait.',
      transcript_language: 'Français',
      
      economics: {
        damage_estimate: 18500,
        third_party_liability: true,
        deductible_applicable: 0,
        coverage_limit: 500000,
        probable_payout: 18500
      },
      
      timeline: [
        { time: '2026-01-31 11:30', action: 'Sinistre', description: 'Collision boulevard Mohammed V' },
        { time: '2026-01-31 11:45', action: 'Police', description: 'Rapport police établi' },
        { time: '2026-01-31 12:00', action: 'Constat', description: 'Constat amiable signé' },
        { time: '2026-01-31 12:45', action: 'Déclaration', description: 'Déclaration système AI' }
      ],
      
      next_actions: ['Vérifier couverture tiers', 'Estimation expert', 'Contact tiers assurance'],
      assigned_to: null
    },
    {
      id: 'SINISTRE-005',
      customer_id: 'C006',
      type: 'Vol',
      description: 'Ahhh non! Ma voiture a été volée. Elle était garée devant mon immeuble. Je n\'ai pas vu qui a fait. Je suis très angoissé... c\'est quoi maintenant? C\'était une belle voiture...',
      date_declared: '2026-01-31 08:30',
      date_incident: '2026-01-30 20:00',
      location: 'Immeuble résidentiel, Agadir - Quartier Talborjt',
      third_party: 'Inconnu - Crime',
      damage_estimate: 125000,
      status: 'ESCALADE URGENTE',
      complexity_score: 68,
      escalation_required: true,
      escalation_reason: 'Sinistre majeur (vol véhicule) + stress émotionnel élevé',
      priority: 'CRITIQUE',
      
      cognitive_analysis: {
        facts_count: 4,
        assumptions_count: 3,
        contradictions: 0,
        ambiguities: 3,
        emotional_stress: 9,
        confidence: 50,
      },
      
      cci_breakdown: {
        guarantees: { score: 60, details: 'Vol - couverture vol/incendie' },
        third_parties: { score: 70, details: 'Criminel inconnu - investigation police' },
        documents: { score: 50, details: 'Rapport police en cours' },
        ambiguities: { score: 55, details: 'Circonstances vol floues' },
        emotional: { score: 85, details: 'Client paniqué - besoin support urgent' },
        inconsistencies: { score: 20, details: 'Pas d\'incohérence logique' }
      },
      
      full_transcript: 'Ahhh non! Ma voiture a été volée. Elle était garée devant mon immeuble. Je n\'ai pas vu qui a fait. Je suis très angoissé... c\'est quoi maintenant? C\'était une belle voiture...',
      transcript_language: 'Français/Darija',
      
      economics: {
        damage_estimate: 125000,
        third_party_liability: false,
        deductible_applicable: 5000,
        coverage_limit: 500000,
        probable_payout: 120000
      },
      
      timeline: [
        { time: '2026-01-30 20:00', action: 'Sinistre', description: 'Vol véhicule constaté' },
        { time: '2026-01-31 08:30', action: 'Déclaration', description: 'Déclaration urgente via système AI' },
        { time: '2026-01-31 08:45', action: 'Escalade', description: 'ESCALADE CRITIQUE: Vol majeur + stress' }
      ],
      
      next_actions: ['Contact immédiat client', 'Rapport police vol', 'Investigation', 'Prise en charge juridique'],
      assigned_to: 'Karim Benali (Spécialiste Sinistres Majeurs)'
    }
  ];

  // ============= ÉTATS =============
  const [selectedClaim, setSelectedClaim] = useState(null);
  const [filterPriority, setFilterPriority] = useState('ALL');
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [sortBy, setSortBy] = useState('complexity');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newClaims, setNewClaims] = useState([]);
  const [formData, setFormData] = useState({
    customer_name: '',
    customer_phone: '',
    customer_email: '',
    customer_city: 'Casablanca',
    claim_type: 'Accrochage',
    description: '',
    location: '',
    damage_estimate: '',
    third_party: ''
  });


  // ============= STATISTIQUES CALCULÉES =============
  const stats = {
    total_claims: claims_database.length,
    total_escalations: claims_database.filter(c => c.escalation_required).length,
    total_value: claims_database.reduce((sum, c) => sum + c.damage_estimate, 0),
    avg_complexity: Math.round(claims_database.reduce((sum, c) => sum + c.complexity_score, 0) / claims_database.length),
    critical_count: claims_database.filter(c => c.priority === 'CRITIQUE').length,
    high_count: claims_database.filter(c => c.priority === 'HAUTE').length,
    medium_count: claims_database.filter(c => c.priority === 'MOYENNE').length,
    low_count: claims_database.filter(c => c.priority === 'BASSE').length,
  };

  // Filtrage et tri
  let filtered_claims = [...claims_database, ...newClaims].filter(c => {
    if (filterPriority !== 'ALL' && c.priority !== filterPriority) return false;
    if (filterStatus !== 'ALL' && c.status !== filterStatus) return false;
    return true;
  });

  if (sortBy === 'complexity') {
    filtered_claims.sort((a, b) => b.complexity_score - a.complexity_score);
  } else if (sortBy === 'value') {
    filtered_claims.sort((a, b) => b.damage_estimate - a.damage_estimate);
  } else if (sortBy === 'recent') {
    filtered_claims.sort((a, b) => new Date(b.date_declared) - new Date(a.date_declared));
  }

  // Données graphiques
  const complexity_trend = [
    { name: 'Simple (<40)', count: claims_database.filter(c => c.complexity_score < 40).length, value: 0 },
    { name: 'Moyen (40-60)', count: claims_database.filter(c => c.complexity_score >= 40 && c.complexity_score < 60).length, value: 1 },
    { name: 'Complexe (60-80)', count: claims_database.filter(c => c.complexity_score >= 60 && c.complexity_score < 80).length, value: 2 },
    { name: 'Très Complexe (>80)', count: claims_database.filter(c => c.complexity_score >= 80).length, value: 3 }
  ];

  const priority_distribution = [
    { name: 'CRITIQUE', value: stats.critical_count, fill: '#ef4444' },
    { name: 'HAUTE', value: stats.high_count, fill: '#f97316' },
    { name: 'MOYENNE', value: stats.medium_count, fill: '#eab308' },
    { name: 'BASSE', value: stats.low_count, fill: '#22c55e' }
  ];

  const claim_type_data = [
    { name: 'Accrochage', count: claims_database.filter(c => c.type === 'Accrochage').length },
    { name: 'Accident', count: claims_database.filter(c => c.type.includes('Accident')).length },
    { name: 'Vol', count: claims_database.filter(c => c.type === 'Vol').length },
    { name: 'Vandalisme', count: claims_database.filter(c => c.type === 'Vandalisme').length },
    { name: 'Collision', count: claims_database.filter(c => c.type === 'Collision').length },
  ];

  const getCustomer = (id) => crm_database.find(c => c.id === id);
  const getPriorityColor = (priority) => {
    switch(priority) {
      case 'CRITIQUE': return 'from-red-600 to-red-800';
      case 'HAUTE': return 'from-orange-600 to-orange-800';
      case 'MOYENNE': return 'from-yellow-600 to-yellow-800';
      case 'BASSE': return 'from-green-600 to-green-800';
      default: return 'from-slate-600 to-slate-800';
    }
  };

  const getComplexityColor = (score) => {
    if (score < 40) return 'text-green-400';
    if (score < 60) return 'text-yellow-400';
    if (score < 80) return 'text-orange-400';
    return 'text-red-400';
  };

  const createNewClaim = () => {
    if (!formData.customer_name || !formData.description || !formData.damage_estimate) {
      alert('⚠️ Remplissez tous les champs obligatoires');
      return;
    }

    // Générer un ID unique
    const claimId = `SINISTRE-${String(claims_database.length + newClaims.length + 1).padStart(3, '0')}`;
    const customerId = `C${String(crm_database.length + 1).padStart(3, '0')}`;

    // Créer le nouveau sinistre
    const newClaim = {
      id: claimId,
      customer_id: customerId,
      type: formData.claim_type,
      description: formData.description,
      date_declared: new Date().toLocaleString('fr-MA'),
      date_incident: new Date(Date.now() - 86400000).toLocaleString('fr-MA'), // hier
      location: formData.location || 'Lieu non spécifié',
      third_party: formData.third_party || 'Non indiqué',
      damage_estimate: parseInt(formData.damage_estimate),
      status: 'En Analyse',
      complexity_score: 45, // Score moyen par défaut
      escalation_required: false,
      escalation_reason: null,
      priority: 'MOYENNE',
      
      cognitive_analysis: {
        facts_count: 3,
        assumptions_count: 2,
        contradictions: 0,
        ambiguities: 1,
        emotional_stress: 3,
        confidence: 75,
      },
      
      cci_breakdown: {
        guarantees: { score: 40, details: 'Couverture standard' },
        third_parties: { score: 40, details: 'Tiers non complètement identifié' },
        documents: { score: 45, details: 'Documents en cours de collecte' },
        ambiguities: { score: 45, details: 'Certains détails à clarifier' },
        emotional: { score: 35, details: 'Client à gérer avec empathie' },
        inconsistencies: { score: 40, details: 'À vérifier' }
      },
      
      full_transcript: formData.description,
      transcript_language: 'Français',
      
      economics: {
        damage_estimate: parseInt(formData.damage_estimate),
        third_party_liability: !!formData.third_party,
        deductible_applicable: 500,
        coverage_limit: 500000,
        probable_payout: parseInt(formData.damage_estimate) - 500
      },
      
      timeline: [
        { time: new Date().toLocaleString('fr-MA'), action: 'Création', description: 'Sinistre créé manuellement via dashboard' }
      ],
      
      next_actions: ['Collecter documents', 'Vérifier couverture', 'Estimer dégâts'],
      assigned_to: null
    };

    // Ajouter le client au CRM
    const newCustomer = {
      id: customerId,
      name: formData.customer_name,
      phone: formData.customer_phone,
      email: formData.customer_email,
      city: formData.customer_city,
      contract: 'AUTO-NOUVEAU-2026',
      premium: 0,
      customer_since: new Date().toISOString().split('T')[0],
      claims_history: 0
    };

    crm_database.push(newCustomer);
    setNewClaims([...newClaims, newClaim]);

    // Réinitialiser formulaire
    setFormData({
      customer_name: '',
      customer_phone: '',
      customer_email: '',
      customer_city: 'Casablanca',
      claim_type: 'Accrochage',
      description: '',
      location: '',
      damage_estimate: '',
      third_party: ''
    });
    setShowCreateModal(false);

    // Sauvegarder en localStorage
    localStorage.setItem('customClaims', JSON.stringify(newClaims));
    alert('✅ Sinistre créé avec succès: ' + claimId);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <header className="sticky top-0 z-50 backdrop-blur-xl bg-slate-900/90 border-b border-slate-700/50">
        <div className="max-w-7xl mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                📊 Dashboard Expert
              </h1>
              <p className="text-slate-400 text-sm">Gestion Cognitive & Monitoring des Sinistres</p>
            </div>
            <div className="flex gap-3">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center gap-2 text-sm"
              >
                <FiDownload className="w-4 h-4" />
                Export Rapport
              </motion.button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* KPIs */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-4 rounded-lg bg-gradient-to-br from-blue-600/20 to-blue-900/20 border border-blue-600/30"
          >
            <div className="flex items-center justify-between mb-2">
              <p className="text-blue-300 text-sm font-semibold">Total Sinistres</p>
              <FiTrendingUp className="w-5 h-5 text-blue-400" />
            </div>
            <p className="text-3xl font-bold text-white">{stats.total_claims}</p>
            <p className="text-xs text-blue-300 mt-2">📌 {stats.total_escalations} escalations</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="p-4 rounded-lg bg-gradient-to-br from-red-600/20 to-red-900/20 border border-red-600/30"
          >
            <div className="flex items-center justify-between mb-2">
              <p className="text-red-300 text-sm font-semibold">Valeur Totale</p>
              <FiDollarSign className="w-5 h-5 text-red-400" />
            </div>
            <p className="text-3xl font-bold text-white">
              {(stats.total_value / 1000).toFixed(1)}K DH
            </p>
            <p className="text-xs text-red-300 mt-2">💰 Exposition assurant</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="p-4 rounded-lg bg-gradient-to-br from-orange-600/20 to-orange-900/20 border border-orange-600/30"
          >
            <div className="flex items-center justify-between mb-2">
              <p className="text-orange-300 text-sm font-semibold">Complexité Moy.</p>
              <FiBarChart2 className="w-5 h-5 text-orange-400" />
            </div>
            <p className="text-3xl font-bold text-white">{stats.avg_complexity}/100</p>
            <p className="text-xs text-orange-300 mt-2">📊 Score CCI moyen</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="p-4 rounded-lg bg-gradient-to-br from-purple-600/20 to-purple-900/20 border border-purple-600/30"
          >
            <div className="flex items-center justify-between mb-2">
              <p className="text-purple-300 text-sm font-semibold">CRITIQUE</p>
              <FiAlertCircle className="w-5 h-5 text-purple-400" />
            </div>
            <p className="text-3xl font-bold text-white">{stats.critical_count}</p>
            <p className="text-xs text-purple-300 mt-2">🔴 Escalade urgente</p>
          </motion.div>
        </div>

        {/* Graphiques */}
        <div className="grid grid-cols-2 gap-6 mb-8">
          {/* Répartition Complexité */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="p-6 rounded-lg bg-slate-800/50 border border-slate-700/50 backdrop-blur"
          >
            <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
              <FiBarChart2 className="w-5 h-5 text-blue-400" />
              📈 Répartition Complexité
            </h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={complexity_trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="name" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }} />
                <Bar dataKey="count" fill="#3b82f6" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Distribution Priorité */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            className="p-6 rounded-lg bg-slate-800/50 border border-slate-700/50 backdrop-blur"
          >
            <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
              <FiFlag className="w-5 h-5 text-red-400" />
              🚨 Distribution Priorité
            </h3>
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={priority_distribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {priority_distribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </motion.div>
        </div>

        {/* Types Sinistres */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="p-6 rounded-lg bg-slate-800/50 border border-slate-700/50 backdrop-blur mb-8"
        >
          <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
            <FiLayers className="w-5 h-5 text-cyan-400" />
            📋 Types de Sinistres
          </h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={claim_type_data} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis type="number" stroke="#9ca3af" />
              <YAxis dataKey="name" type="category" stroke="#9ca3af" width={120} />
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }} />
              <Bar dataKey="count" fill="#06b6d4" radius={[0, 8, 8, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Filtres */}
        <div className="flex gap-4 mb-6">
          <select
            value={filterPriority}
            onChange={(e) => setFilterPriority(e.target.value)}
            className="px-4 py-2 bg-slate-800 border border-slate-700 text-white rounded-lg text-sm hover:border-slate-600"
          >
            <option value="ALL">🎯 Toutes Priorités</option>
            <option value="CRITIQUE">🔴 CRITIQUE</option>
            <option value="HAUTE">🟠 HAUTE</option>
            <option value="MOYENNE">🟡 MOYENNE</option>
            <option value="BASSE">🟢 BASSE</option>
          </select>

          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-2 bg-slate-800 border border-slate-700 text-white rounded-lg text-sm hover:border-slate-600"
          >
            <option value="ALL">📊 Tous Statuts</option>
            <option value="En Analyse">⏳ En Analyse</option>
            <option value="ESCALADE URGENTE">🚨 Escalade Urgente</option>
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-4 py-2 bg-slate-800 border border-slate-700 text-white rounded-lg text-sm hover:border-slate-600"
          >
            <option value="complexity">📊 Par Complexité</option>
            <option value="value">💰 Par Valeur</option>
            <option value="recent">📅 Plus Récent</option>
          </select>
        </div>

        {/* Liste Sinistres */}
        <div className="space-y-3">
          {filtered_claims.map((claim, idx) => {
            const customer = getCustomer(claim.customer_id);
            return (
              <motion.div
                key={claim.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.05 }}
                onClick={() => setSelectedClaim(claim)}
                className="p-4 rounded-lg bg-slate-800/40 border border-slate-700/50 hover:border-slate-600/80 cursor-pointer hover:bg-slate-800/60 transition-all"
              >
                <div className="grid grid-cols-12 gap-4 items-center">
                  {/* Priorité */}
                  <div className={`col-span-2 p-3 rounded-lg bg-gradient-to-r ${getPriorityColor(claim.priority)} border border-slate-700/50`}>
                    <p className="text-white font-bold text-sm">{claim.priority}</p>
                    <p className="text-xs text-slate-200">{claim.id}</p>
                  </div>

                  {/* Client */}
                  <div className="col-span-3">
                    <p className="text-white font-semibold text-sm">{customer?.name || 'Unknown'}</p>
                    <p className="text-slate-400 text-xs">{customer?.phone}</p>
                  </div>

                  {/* Type & Description */}
                  <div className="col-span-3">
                    <p className="text-slate-300 text-sm font-semibold">{claim.type}</p>
                    <p className="text-slate-500 text-xs truncate">{claim.description.substring(0, 50)}...</p>
                  </div>

                  {/* Complexité */}
                  <div className="col-span-1 text-center">
                    <p className={`text-lg font-bold ${getComplexityColor(claim.complexity_score)}`}>
                      {claim.complexity_score}
                    </p>
                    <p className="text-xs text-slate-400">CCI</p>
                  </div>

                  {/* Valeur */}
                  <div className="col-span-1 text-right">
                    <p className="text-white font-semibold text-sm">{(claim.damage_estimate / 1000).toFixed(1)}K</p>
                    <p className="text-slate-400 text-xs">DH</p>
                  </div>

                  {/* Escalade */}
                  <div className="col-span-1 text-center">
                    {claim.escalation_required ? (
                      <div className="inline-block px-2 py-1 rounded-lg bg-red-600/30 border border-red-600/60">
                        <p className="text-red-300 text-xs font-bold">⚡ ESCALADE</p>
                      </div>
                    ) : (
                      <div className="inline-block px-2 py-1 rounded-lg bg-green-600/30 border border-green-600/60">
                        <p className="text-green-300 text-xs font-bold">✓ OK</p>
                      </div>
                    )}
                  </div>

                  {/* Status */}
                  <div className="col-span-1 text-right">
                    <p className={`text-xs font-semibold ${claim.escalation_required ? 'text-red-400' : 'text-yellow-400'}`}>
                      {claim.status}
                    </p>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </main>

      {/* MODAL DÉTAILS SINISTRE */}
      <AnimatePresence>
        {selectedClaim && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSelectedClaim(null)}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              onClick={(e) => e.stopPropagation()}
              className="max-w-5xl w-full max-h-[90vh] overflow-y-auto bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-700/50 rounded-xl shadow-2xl"
            >
              <div className="sticky top-0 z-10 p-6 bg-slate-900/95 border-b border-slate-700/50 flex items-center justify-between">
                <h2 className="text-2xl font-bold text-white">
                  🔍 Détails Sinistre
                </h2>
                <button
                  onClick={() => setSelectedClaim(null)}
                  className="text-slate-400 hover:text-white text-2xl"
                >
                  ✕
                </button>
              </div>

              <div className="p-6 space-y-6">
                {/* Header Sinistre */}
                <div className={`p-6 rounded-lg bg-gradient-to-r ${getPriorityColor(selectedClaim.priority)} border border-slate-600/30`}>
                  <div className="grid grid-cols-3 gap-6">
                    <div>
                      <p className="text-slate-200 text-xs uppercase font-semibold mb-1">ID Sinistre</p>
                      <p className="text-white text-xl font-bold">{selectedClaim.id}</p>
                    </div>
                    <div>
                      <p className="text-slate-200 text-xs uppercase font-semibold mb-1">Type</p>
                      <p className="text-white text-xl font-bold">{selectedClaim.type}</p>
                    </div>
                    <div>
                      <p className="text-slate-200 text-xs uppercase font-semibold mb-1">Priorité</p>
                      <p className="text-white text-xl font-bold">{selectedClaim.priority}</p>
                    </div>
                  </div>
                </div>

                {/* Client Info */}
                {getCustomer(selectedClaim.customer_id) && (
                  <div className="p-6 rounded-lg bg-slate-800/50 border border-slate-700/50">
                    <h3 className="text-white font-bold mb-4 flex items-center gap-2">
                      <FiUser className="w-5 h-5 text-blue-400" />
                      👤 Informations Client
                    </h3>
                    <div className="grid grid-cols-2 gap-6">
                      <div>
                        <p className="text-slate-400 text-sm">Nom</p>
                        <p className="text-white font-semibold">{getCustomer(selectedClaim.customer_id)?.name}</p>
                      </div>
                      <div>
                        <p className="text-slate-400 text-sm">Téléphone</p>
                        <p className="text-white font-semibold">{getCustomer(selectedClaim.customer_id)?.phone}</p>
                      </div>
                      <div>
                        <p className="text-slate-400 text-sm">Email</p>
                        <p className="text-white font-semibold text-sm">{getCustomer(selectedClaim.customer_id)?.email}</p>
                      </div>
                      <div>
                        <p className="text-slate-400 text-sm">Ville</p>
                        <p className="text-white font-semibold">{getCustomer(selectedClaim.customer_id)?.city}</p>
                      </div>
                      <div>
                        <p className="text-slate-400 text-sm">Contrat</p>
                        <p className="text-white font-semibold">{getCustomer(selectedClaim.customer_id)?.contract}</p>
                      </div>
                      <div>
                        <p className="text-slate-400 text-sm">Prime Annuelle</p>
                        <p className="text-white font-semibold">{getCustomer(selectedClaim.customer_id)?.premium} DH</p>
                      </div>
                      <div>
                        <p className="text-slate-400 text-sm">Client depuis</p>
                        <p className="text-white font-semibold">{new Date(getCustomer(selectedClaim.customer_id)?.customer_since).toLocaleDateString('fr-MA')}</p>
                      </div>
                      <div>
                        <p className="text-slate-400 text-sm">Historique Sinistres</p>
                        <p className="text-white font-semibold">{getCustomer(selectedClaim.customer_id)?.claims_history} sinistre(s)</p>
                      </div>
                    </div>

                    {/* Contrat d'assurance détaillé */}
                    {getCustomer(selectedClaim.customer_id)?.policy && (
                      <div className="mt-6 p-5 rounded-lg bg-slate-900/50 border border-slate-700/40">
                        <h4 className="text-white font-semibold mb-4 flex items-center gap-2">
                          <FiFileText className="w-4 h-4 text-cyan-400" />
                          📄 Contrat d'assurance (Police complète)
                        </h4>
                        <div className="grid grid-cols-2 gap-6">
                          <div>
                            <p className="text-slate-400 text-sm">N° Police</p>
                            <p className="text-white font-semibold">{getCustomer(selectedClaim.customer_id)?.policy?.policy_number}</p>
                          </div>
                          <div>
                            <p className="text-slate-400 text-sm">Produit</p>
                            <p className="text-white font-semibold">{getCustomer(selectedClaim.customer_id)?.policy?.product}</p>
                          </div>
                          <div>
                            <p className="text-slate-400 text-sm">Statut</p>
                            <p className="text-white font-semibold">{getCustomer(selectedClaim.customer_id)?.policy?.status}</p>
                          </div>
                          <div>
                            <p className="text-slate-400 text-sm">Renouvellement</p>
                            <p className="text-white font-semibold">{getCustomer(selectedClaim.customer_id)?.policy?.renewal_date}</p>
                          </div>
                          <div>
                            <p className="text-slate-400 text-sm">Franchise</p>
                            <p className="text-white font-semibold">{getCustomer(selectedClaim.customer_id)?.policy?.deductible} DH</p>
                          </div>
                          <div>
                            <p className="text-slate-400 text-sm">Plafond couverture</p>
                            <p className="text-white font-semibold">{getCustomer(selectedClaim.customer_id)?.policy?.coverage_limit} DH</p>
                          </div>
                        </div>

                        <div className="mt-4">
                          <p className="text-slate-400 text-sm mb-2">Garanties incluses</p>
                          <div className="flex flex-wrap gap-2">
                            {getCustomer(selectedClaim.customer_id)?.policy?.coverage?.map((cvg, idx) => (
                              <span key={idx} className="px-2 py-1 text-xs rounded-full bg-cyan-600/20 text-cyan-300 border border-cyan-600/40">
                                {cvg}
                              </span>
                            ))}
                          </div>
                        </div>

                        <div className="mt-5 p-4 rounded-lg bg-slate-800/50 border border-slate-700/40">
                          <p className="text-slate-400 text-sm mb-2">Véhicule assuré</p>
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <p className="text-slate-400 text-xs">Marque / Modèle</p>
                              <p className="text-white font-semibold">
                                {getCustomer(selectedClaim.customer_id)?.policy?.vehicle?.brand} {getCustomer(selectedClaim.customer_id)?.policy?.vehicle?.model}
                              </p>
                            </div>
                            <div>
                              <p className="text-slate-400 text-xs">Immatriculation</p>
                              <p className="text-white font-semibold">{getCustomer(selectedClaim.customer_id)?.policy?.vehicle?.plate}</p>
                            </div>
                            <div>
                              <p className="text-slate-400 text-xs">Année</p>
                              <p className="text-white font-semibold">{getCustomer(selectedClaim.customer_id)?.policy?.vehicle?.year}</p>
                            </div>
                            <div>
                              <p className="text-slate-400 text-xs">VIN</p>
                              <p className="text-white font-semibold">{getCustomer(selectedClaim.customer_id)?.policy?.vehicle?.vin}</p>
                            </div>
                          </div>
                        </div>

                        <div className="mt-4">
                          <p className="text-slate-400 text-sm mb-2">Bénéficiaires</p>
                          <ul className="list-disc list-inside text-slate-200 text-sm">
                            {getCustomer(selectedClaim.customer_id)?.policy?.beneficiaries?.map((b, idx) => (
                              <li key={idx}>{b}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Détails Sinistre */}
                <div className="p-6 rounded-lg bg-slate-800/50 border border-slate-700/50">
                  <h3 className="text-white font-bold mb-4 flex items-center gap-2">
                    <FiAlertCircle className="w-5 h-5 text-orange-400" />
                    📋 Détails du Sinistre
                  </h3>
                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <p className="text-slate-400 text-sm">Date Incident</p>
                      <p className="text-white font-semibold">{new Date(selectedClaim.date_incident).toLocaleString('fr-MA')}</p>
                    </div>
                    <div>
                      <p className="text-slate-400 text-sm">Date Déclaration</p>
                      <p className="text-white font-semibold">{new Date(selectedClaim.date_declared).toLocaleString('fr-MA')}</p>
                    </div>
                    <div>
                      <p className="text-slate-400 text-sm">Lieu</p>
                      <p className="text-white font-semibold flex items-center gap-1">
                        <FiMapPin className="w-4 h-4" /> {selectedClaim.location}
                      </p>
                    </div>
                    <div>
                      <p className="text-slate-400 text-sm">Tiers</p>
                      <p className="text-white font-semibold">{selectedClaim.third_party}</p>
                    </div>
                    <div>
                      <p className="text-slate-400 text-sm">Estim. Dégâts</p>
                      <p className="text-white font-bold text-lg">{selectedClaim.damage_estimate.toLocaleString()} DH</p>
                    </div>
                    <div>
                      <p className="text-slate-400 text-sm">Statut</p>
                      <p className={`font-semibold ${selectedClaim.escalation_required ? 'text-red-400' : 'text-yellow-400'}`}>
                        {selectedClaim.status}
                      </p>
                    </div>
                  </div>

                  <div className="mt-6 p-4 rounded-lg bg-slate-900/50 border border-slate-700/30">
                    <p className="text-slate-400 text-sm mb-2">📝 Description Complète</p>
                    <p className="text-white italic">{selectedClaim.description}</p>
                  </div>
                </div>

                {/* Analyse Cognitive Détaillée */}
                <div className="p-6 rounded-lg bg-slate-800/50 border border-slate-700/50">
                  <h3 className="text-white font-bold mb-4 flex items-center gap-2">
                    🧠 Analyse Cognitive
                  </h3>
                  <div className="grid grid-cols-3 gap-4 mb-6">
                    <div className="p-4 rounded-lg bg-blue-600/20 border border-blue-600/30">
                      <p className="text-blue-300 text-xs">Faits Détectés</p>
                      <p className="text-white text-2xl font-bold">{selectedClaim.cognitive_analysis.facts_count}</p>
                    </div>
                    <div className="p-4 rounded-lg bg-yellow-600/20 border border-yellow-600/30">
                      <p className="text-yellow-300 text-xs">Suppositions</p>
                      <p className="text-white text-2xl font-bold">{selectedClaim.cognitive_analysis.assumptions_count}</p>
                    </div>
                    <div className="p-4 rounded-lg bg-red-600/20 border border-red-600/30">
                      <p className="text-red-300 text-xs">Stress Émotionnel</p>
                      <p className="text-white text-2xl font-bold">{selectedClaim.cognitive_analysis.emotional_stress}/10</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-slate-400 text-sm mb-2">Contradictions Détectées</p>
                      <p className="text-white font-bold text-lg">{selectedClaim.cognitive_analysis.contradictions}</p>
                    </div>
                    <div>
                      <p className="text-slate-400 text-sm mb-2">Ambiguïtés</p>
                      <p className="text-white font-bold text-lg">{selectedClaim.cognitive_analysis.ambiguities}</p>
                    </div>
                    <div className="col-span-2">
                      <p className="text-slate-400 text-sm mb-2">Confiance IA</p>
                      <div className="w-full bg-slate-900/50 rounded-full h-3 overflow-hidden">
                        <div
                          className="bg-gradient-to-r from-green-500 to-blue-500 h-full rounded-full"
                          style={{ width: `${selectedClaim.cognitive_analysis.confidence}%` }}
                        />
                      </div>
                      <p className="text-white font-bold mt-1">{selectedClaim.cognitive_analysis.confidence}%</p>
                    </div>
                  </div>
                </div>

                {/* CCI Breakdown */}
                <div className="p-6 rounded-lg bg-slate-800/50 border border-slate-700/50">
                  <h3 className="text-white font-bold mb-4 flex items-center gap-2">
                    📊 Indice de Complexité (CCI)
                  </h3>
                  <div className={`mb-6 p-6 rounded-lg text-center ${selectedClaim.complexity_score < 40 ? 'bg-green-600/20 border border-green-600/30' : selectedClaim.complexity_score < 60 ? 'bg-yellow-600/20 border border-yellow-600/30' : selectedClaim.complexity_score < 80 ? 'bg-orange-600/20 border border-orange-600/30' : 'bg-red-600/20 border border-red-600/30'}`}>
                    <p className={`text-3xl font-bold ${getComplexityColor(selectedClaim.complexity_score)}`}>
                      {selectedClaim.complexity_score}/100
                    </p>
                    <p className="text-slate-300 text-sm mt-2">
                      {selectedClaim.complexity_score < 40 ? '✅ SIMPLE - Traitement autonome recommandé' : selectedClaim.complexity_score < 60 ? '⚠️ MOYEN - Suivi conseiller' : selectedClaim.complexity_score < 80 ? '🔶 COMPLEXE - Escalade recommandée' : '🔴 TRÈS COMPLEXE - Escalade URGENTE'}
                    </p>
                  </div>

                  <div className="space-y-3">
                    {Object.entries(selectedClaim.cci_breakdown).map(([key, value]) => (
                      <div key={key} className="flex items-center justify-between p-3 rounded-lg bg-slate-900/50 border border-slate-700/30">
                        <div>
                          <p className="text-slate-300 capitalize font-semibold text-sm">{key.replace('_', ' ')}</p>
                          <p className="text-slate-500 text-xs">{value.details}</p>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="w-32 h-2 bg-slate-800 rounded-full overflow-hidden">
                            <div
                              className="bg-gradient-to-r from-blue-500 to-cyan-500 h-full rounded-full"
                              style={{ width: `${value.score}%` }}
                            />
                          </div>
                          <p className="text-white font-bold text-lg w-12 text-right">{value.score}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Économie */}
                <div className="p-6 rounded-lg bg-slate-800/50 border border-slate-700/50">
                  <h3 className="text-white font-bold mb-4 flex items-center gap-2">
                    <FiDollarSign className="w-5 h-5 text-green-400" />
                    💰 Analyse Économique
                  </h3>
                  <div className="grid grid-cols-2 gap-6">
                    <div className="p-4 rounded-lg bg-slate-900/50 border border-slate-700/30">
                      <p className="text-slate-400 text-sm">Estim. Dégâts</p>
                      <p className="text-white font-bold text-xl">{selectedClaim.economics.damage_estimate.toLocaleString()} DH</p>
                    </div>
                    <div className="p-4 rounded-lg bg-slate-900/50 border border-slate-700/30">
                      <p className="text-slate-400 text-sm">Franchise Applicable</p>
                      <p className="text-white font-bold text-xl">{selectedClaim.economics.deductible_applicable.toLocaleString()} DH</p>
                    </div>
                    <div className="p-4 rounded-lg bg-slate-900/50 border border-slate-700/30">
                      <p className="text-slate-400 text-sm">Limite Couverture</p>
                      <p className="text-white font-bold text-xl">{(selectedClaim.economics.coverage_limit / 1000).toFixed(0)}K DH</p>
                    </div>
                    <div className="p-4 rounded-lg bg-green-600/20 border border-green-600/30">
                      <p className="text-green-300 text-sm">Paiement Probable</p>
                      <p className="text-white font-bold text-xl">{selectedClaim.economics.probable_payout.toLocaleString()} DH</p>
                    </div>
                  </div>
                  <div className="mt-4 p-4 rounded-lg bg-slate-900/50 border border-slate-700/30">
                    <p className="text-slate-400 text-sm mb-2">Responsabilité Tiers</p>
                    <p className="text-white font-semibold">{selectedClaim.economics.third_party_liability ? '✅ OUI - Tiers responsable identifié' : '❌ NON - Sinistre propre'}</p>
                  </div>
                </div>

                {/* Timeline */}
                <div className="p-6 rounded-lg bg-slate-800/50 border border-slate-700/50">
                  <h3 className="text-white font-bold mb-4 flex items-center gap-2">
                    <FiCalendar className="w-5 h-5 text-cyan-400" />
                    📅 Timeline du Sinistre
                  </h3>
                  <div className="space-y-4">
                    {selectedClaim.timeline.map((event, idx) => (
                      <div key={idx} className="flex gap-4">
                        <div className="flex flex-col items-center">
                          <div className="w-3 h-3 rounded-full bg-cyan-400 mt-2"></div>
                          {idx < selectedClaim.timeline.length - 1 && (
                            <div className="w-0.5 h-12 bg-slate-700/50 my-2"></div>
                          )}
                        </div>
                        <div className="pb-4">
                          <p className="text-cyan-400 font-semibold text-sm">{event.time}</p>
                          <p className="text-white font-semibold">{event.action}</p>
                          <p className="text-slate-400 text-sm">{event.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Actions Recommandées */}
                <div className="p-6 rounded-lg bg-blue-600/20 border border-blue-600/30">
                  <h3 className="text-white font-bold mb-4 flex items-center gap-2">
                    <FiCheckCircle className="w-5 h-5 text-blue-400" />
                    ✅ Actions Recommandées
                  </h3>
                  <ul className="space-y-2">
                    {selectedClaim.next_actions.map((action, idx) => (
                      <li key={idx} className="flex items-center gap-3 text-slate-300">
                        <div className="w-2 h-2 rounded-full bg-blue-400"></div>
                        {action}
                      </li>
                    ))}
                  </ul>
                  {selectedClaim.assigned_to && (
                    <div className="mt-4 p-3 rounded-lg bg-slate-900/50 border border-slate-700/30">
                      <p className="text-slate-400 text-sm">Assigné à</p>
                      <p className="text-white font-semibold flex items-center gap-2">
                        <FiUser className="w-4 h-4" />
                        {selectedClaim.assigned_to}
                      </p>
                    </div>
                  )}
                </div>

                {/* Escalade Info */}
                {selectedClaim.escalation_required && (
                  <div className="p-6 rounded-lg bg-red-600/20 border border-red-600/30">
                    <h3 className="text-white font-bold mb-4 flex items-center gap-2">
                      <FiAlertCircle className="w-5 h-5 text-red-400" />
                      🚨 ESCALADE REQUISE
                    </h3>
                    <p className="text-red-300 mb-3">{selectedClaim.escalation_reason}</p>
                    <button className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg font-semibold flex items-center gap-2 w-full justify-center">
                      <FiPhone className="w-5 h-5" />
                      📞 Appeler Client Immédiatement
                    </button>
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
