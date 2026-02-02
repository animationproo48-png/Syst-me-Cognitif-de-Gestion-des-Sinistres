import React, { useEffect, useState } from 'react';
import Navigation from '../components/Navigation';
import { 
  FiCpu, FiActivity, FiAlertTriangle, FiCheckCircle, 
  FiFileText, FiZap, FiThermometer, FiHeart, FiMessageSquare
} from 'react-icons/fi';
import { 
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell
} from 'recharts';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function AnalyseCognitive() {
  const [sinistres, setSinistres] = useState([]);
  const [selectedSinistre, setSelectedSinistre] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 15000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/sinistres`);
      const data = await res.json();
      setSinistres(data || []);
      if (!selectedSinistre && data.length > 0) {
        setSelectedSinistre(data[0]);
      }
    } catch (e) {
      console.error('Erreur:', e);
    } finally {
      setLoading(false);
    }
  };

  const analyzeText = (text) => {
    if (!text) return { faits: [], suppositions: [], emotions: [], phrases: [] };
    
    const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
    const faits = [];
    const suppositions = [];
    const emotions = [];
    
    const factIndicators = ['le', 'la', 'à', 'dans', 'sur', 'date', 'lieu', 'heure', 'numéro', 'plaque'];
    const suppositionIndicators = ['peut-être', 'probablement', 'semble', 'pourrait', 'je pense', 'je crois', 'sans doute'];
    const emotionIndicators = {
      stress: ['urgent', 'vite', 'rapidement', 'inquiet', 'stressé', 'anxieux'],
      colere: ['furieux', 'énervé', 'inacceptable', 'scandaleux', 'honteux'],
      tristesse: ['triste', 'désolé', 'malheureux', 'difficile', 'dur'],
      peur: ['peur', 'effrayé', 'inquiet', 'angoissé', 'crainte']
    };

    sentences.forEach((sentence, idx) => {
      const lower = sentence.toLowerCase();
      let isFait = false;
      let isSupposition = false;
      let detectedEmotions = [];

      factIndicators.forEach(indicator => {
        if (lower.includes(indicator)) isFait = true;
      });

      suppositionIndicators.forEach(indicator => {
        if (lower.includes(indicator)) {
          isSupposition = true;
          isFait = false;
        }
      });

      Object.keys(emotionIndicators).forEach(emotion => {
        emotionIndicators[emotion].forEach(word => {
          if (lower.includes(word)) {
            detectedEmotions.push(emotion);
          }
        });
      });

      const phraseData = {
        id: idx,
        texte: sentence.trim(),
        type: isSupposition ? 'supposition' : isFait ? 'fait' : 'neutre',
        emotions: detectedEmotions,
        longueur: sentence.trim().split(' ').length,
        confiance: isSupposition ? 40 : isFait ? 85 : 65
      };

      if (isFait) faits.push(phraseData);
      if (isSupposition) suppositions.push(phraseData);
      if (detectedEmotions.length > 0) emotions.push(phraseData);
    });

    return { faits, suppositions, emotions, phrases: sentences.map((s, idx) => ({
      id: idx,
      texte: s.trim(),
      mots: s.trim().split(' ').length
    })) };
  };

  const calculateEmotionalScore = (analysis) => {
    let stressLevel = 0;
    let colereLevel = 0;
    let tristesseLevel = 0;
    let peurLevel = 0;

    analysis.emotions.forEach(phrase => {
      phrase.emotions.forEach(emotion => {
        if (emotion === 'stress') stressLevel += 20;
        if (emotion === 'colere') colereLevel += 25;
        if (emotion === 'tristesse') tristesseLevel += 15;
        if (emotion === 'peur') peurLevel += 20;
      });
    });

    return {
      stress: Math.min(100, stressLevel),
      colere: Math.min(100, colereLevel),
      tristesse: Math.min(100, tristesseLevel),
      peur: Math.min(100, peurLevel),
      global: Math.min(100, (stressLevel + colereLevel + tristesseLevel + peurLevel) / 4)
    };
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Navigation />
        <div className="max-w-7xl mx-auto p-8">
          <div className="text-center text-gray-900 font-medium">Chargement de l'analyse cognitive...</div>
        </div>
      </div>
    );
  }

  const analysis = selectedSinistre ? analyzeText(selectedSinistre.description) : null;
  const emotionalScore = analysis ? calculateEmotionalScore(analysis) : null;

  const cognitiveMetrics = selectedSinistre ? [
    { name: 'Faits', value: analysis.faits.length, max: 10 },
    { name: 'Suppositions', value: analysis.suppositions.length, max: 10 },
    { name: 'Émotions', value: analysis.emotions.length, max: 10 },
    { name: 'CCI', value: (selectedSinistre.cci_score || 0) / 10, max: 10 },
    { name: 'Confiance', value: analysis.faits.length > analysis.suppositions.length ? 8 : 4, max: 10 },
  ] : [];

  const emotionalData = emotionalScore ? [
    { name: 'Stress', value: emotionalScore.stress, color: '#EF4444' },
    { name: 'Colère', value: emotionalScore.colere, color: '#F59E0B' },
    { name: 'Tristesse', value: emotionalScore.tristesse, color: '#3B82F6' },
    { name: 'Peur', value: emotionalScore.peur, color: '#8B5CF6' },
  ] : [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50">
      <Navigation />
      <div className="max-w-7xl mx-auto p-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 flex items-center gap-3">
            <FiCpu className="text-purple-600" /> 
            Analyse Cognitive & Textuelle Avancée
          </h1>
          <p className="text-gray-900 mt-2 font-medium">
            Analyse scientifique des déclarations : détection de faits, suppositions, émotions et indices cognitifs
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <FiFileText className="text-indigo-600" /> 
            Sélectionner un dossier à analyser
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {sinistres.slice(0, 8).map(s => (
              <button
                key={s.id}
                onClick={() => setSelectedSinistre(s)}
                className={`p-4 rounded-xl border-2 transition-all text-left hover:shadow-lg ${
                  selectedSinistre?.id === s.id 
                    ? 'border-purple-600 bg-purple-50' 
                    : 'border-gray-200 hover:border-purple-300'
                }`}
              >
                <div className="font-bold text-gray-900">{s.numero_sinistre}</div>
                <div className="text-sm text-gray-800">{s.client?.nom} {s.client?.prenom}</div>
                <div className="text-xs text-gray-700 mt-1">{s.type_sinistre}</div>
                <div className="text-xs text-purple-600 font-semibold mt-2">CCI: {s.cci_score || 0}</div>
              </button>
            ))}
          </div>
        </div>

        {selectedSinistre && analysis && (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <FiActivity className="text-purple-600" /> 
                  Profil Cognitif Global
                </h3>
                <ResponsiveContainer width="100%" height={350}>
                  <RadarChart data={cognitiveMetrics}>
                    <PolarGrid stroke="#E5E7EB" />
                    <PolarAngleAxis dataKey="name" tick={{ fill: '#1F2937', fontWeight: 600 }} />
                    <PolarRadiusAxis angle={90} domain={[0, 10]} />
                    <Radar name="Score" dataKey="value" stroke="#8B5CF6" fill="#8B5CF6" fillOpacity={0.6} />
                    <Tooltip />
                  </RadarChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <FiHeart className="text-red-600" /> 
                  Analyse Émotionnelle
                </h3>
                <ResponsiveContainer width="100%" height={350}>
                  <BarChart data={emotionalData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" tick={{ fill: '#1F2937', fontWeight: 600 }} />
                    <YAxis domain={[0, 100]} />
                    <Tooltip />
                    <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                      {emotionalData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
                <div className="mt-4 p-4 bg-red-50 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <FiThermometer className="text-red-600" />
                    <span className="font-bold text-gray-900">Niveau de Stress Global</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-4">
                    <div 
                      className="bg-red-600 h-4 rounded-full transition-all"
                      style={{ width: `${emotionalScore.global}%` }}
                    />
                  </div>
                  <div className="text-right text-sm text-gray-900 font-bold mt-1">
                    {emotionalScore.global.toFixed(0)}%
                  </div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
              <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-6 text-white">
                <FiCheckCircle size={32} className="mb-2" />
                <div className="text-3xl font-bold">{analysis.faits.length}</div>
                <div className="text-sm font-medium">Faits Détectés</div>
              </div>
              <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl p-6 text-white">
                <FiAlertTriangle size={32} className="mb-2" />
                <div className="text-3xl font-bold">{analysis.suppositions.length}</div>
                <div className="text-sm font-medium">Suppositions</div>
              </div>
              <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-xl p-6 text-white">
                <FiHeart size={32} className="mb-2" />
                <div className="text-3xl font-bold">{analysis.emotions.length}</div>
                <div className="text-sm font-medium">Émotions</div>
              </div>
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white">
                <FiMessageSquare size={32} className="mb-2" />
                <div className="text-3xl font-bold">{analysis.phrases.length}</div>
                <div className="text-sm font-medium">Phrases</div>
              </div>
              <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 text-white">
                <FiZap size={32} className="mb-2" />
                <div className="text-3xl font-bold">{selectedSinistre.cci_score || 0}</div>
                <div className="text-sm font-medium">Score CCI</div>
              </div>
            </div>

            {analysis.faits.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
                <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <FiCheckCircle className="text-green-600" /> 
                  Faits Structurés & Vérifiables
                </h3>
                <div className="space-y-3">
                  {analysis.faits.map((fait) => (
                    <div
                      key={fait.id}
                      className="p-4 bg-green-50 border-l-4 border-green-600 rounded-lg"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="text-gray-900 font-medium">{fait.texte}</div>
                          <div className="flex gap-4 mt-2 text-sm">
                            <span className="text-green-700 font-semibold">✓ FAIT</span>
                            <span className="text-gray-700">Mots: {fait.longueur}</span>
                            <span className="text-gray-700">Confiance: {fait.confiance}%</span>
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="bg-green-600 text-white px-3 py-1 rounded-full text-xs font-bold">
                            {fait.confiance}%
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {analysis.suppositions.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
                <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <FiAlertTriangle className="text-orange-600" /> 
                  Suppositions & Hypothèses
                </h3>
                <div className="space-y-3">
                  {analysis.suppositions.map((sup) => (
                    <div
                      key={sup.id}
                      className="p-4 bg-orange-50 border-l-4 border-orange-600 rounded-lg"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="text-gray-900 font-medium">{sup.texte}</div>
                          <div className="flex gap-4 mt-2 text-sm">
                            <span className="text-orange-700 font-semibold">⚠ SUPPOSITION</span>
                            <span className="text-gray-700">Mots: {sup.longueur}</span>
                            <span className="text-gray-700">Confiance: {sup.confiance}%</span>
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="bg-orange-600 text-white px-3 py-1 rounded-full text-xs font-bold">
                            {sup.confiance}%
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {analysis.emotions.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
                <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <FiHeart className="text-red-600" /> 
                  Indices Émotionnels & Stress
                </h3>
                <div className="space-y-3">
                  {analysis.emotions.map((emo) => (
                    <div
                      key={emo.id}
                      className="p-4 bg-red-50 border-l-4 border-red-600 rounded-lg"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="text-gray-900 font-medium">{emo.texte}</div>
                          <div className="flex gap-2 mt-2 flex-wrap">
                            {emo.emotions.map((emotion, i) => (
                              <span key={i} className="px-3 py-1 bg-red-600 text-white rounded-full text-xs font-bold uppercase">
                                {emotion}
                              </span>
                            ))}
                          </div>
                        </div>
                        <FiHeart className="text-red-600" size={24} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <FiFileText className="text-indigo-600" /> 
                Déclaration Originale
              </h3>
              <div className="p-6 bg-gray-50 rounded-lg border border-gray-200">
                <p className="text-gray-900 leading-relaxed font-medium whitespace-pre-wrap">
                  {selectedSinistre.description || 'Aucune description disponible'}
                </p>
              </div>
              <div className="mt-4 grid grid-cols-3 gap-4">
                <div className="p-4 bg-indigo-50 rounded-lg">
                  <div className="text-sm text-gray-700 font-medium">Longueur totale</div>
                  <div className="text-2xl font-bold text-gray-900">{(selectedSinistre.description || '').length} caractères</div>
                </div>
                <div className="p-4 bg-purple-50 rounded-lg">
                  <div className="text-sm text-gray-700 font-medium">Nombre de mots</div>
                  <div className="text-2xl font-bold text-gray-900">{(selectedSinistre.description || '').split(' ').length} mots</div>
                </div>
                <div className="p-4 bg-pink-50 rounded-lg">
                  <div className="text-sm text-gray-700 font-medium">Phrases détectées</div>
                  <div className="text-2xl font-bold text-gray-900">{analysis.phrases.length} phrases</div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
