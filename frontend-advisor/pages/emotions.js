import React, { useEffect, useState } from 'react';
import Navigation from '../components/Navigation';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { FiHeart, FiActivity, FiAlertTriangle, FiThermometer, FiZap, FiTrendingUp, FiFrown, FiSmile } from 'react-icons/fi';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const EMOTION_CONFIG = {
  anger: {
    label: 'Colère',
    color: '#EF4444',
    icon: FiAlertTriangle,
    bgColor: 'bg-red-50',
    borderColor: 'border-red-600',
    textColor: 'text-red-700'
  },
  stress: {
    label: 'Stress',
    color: '#F59E0B',
    icon: FiZap,
    bgColor: 'bg-orange-50',
    borderColor: 'border-orange-600',
    textColor: 'text-orange-700'
  },
  sadness: {
    label: 'Tristesse',
    color: '#3B82F6',
    icon: FiFrown,
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-600',
    textColor: 'text-blue-700'
  },
  fear: {
    label: 'Peur',
    color: '#8B5CF6',
    icon: FiThermometer,
    bgColor: 'bg-purple-50',
    borderColor: 'border-purple-600',
    textColor: 'text-purple-700'
  },
  frustration: {
    label: 'Frustration',
    color: '#EC4899',
    icon: FiActivity,
    bgColor: 'bg-pink-50',
    borderColor: 'border-pink-600',
    textColor: 'text-pink-700'
  },
  neutral: {
    label: 'Neutre',
    color: '#6B7280',
    icon: FiSmile,
    bgColor: 'bg-gray-50',
    borderColor: 'border-gray-600',
    textColor: 'text-gray-700'
  }
};

export default function EmotionDashboard() {
  const [stats, setStats] = useState(null);
  const [recent, setRecent] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [statsRes, recentRes, alertsRes] = await Promise.all([
        fetch(`${API_BASE}/api/v1/emotions/stats`).then(r => r.json()),
        fetch(`${API_BASE}/api/v1/emotions/recent?limit=10`).then(r => r.json()),
        fetch(`${API_BASE}/api/v1/emotions/alerts`).then(r => r.json())
      ]);
      
      setStats(statsRes);
      setRecent(recentRes.recent_analyses || []);
      setAlerts(alertsRes.alerts || []);
    } catch (e) {
      console.error('Erreur chargement émotions:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 15000); // Refresh toutes les 15s
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Navigation />
        <div className="max-w-7xl mx-auto p-8">
          <div className="text-center text-gray-900 font-medium">Chargement analyse émotionnelle...</div>
        </div>
      </div>
    );
  }

  const emotionsSummary = stats?.emotions_summary || {};
  const emotionChartData = Object.entries(emotionsSummary).map(([emotion, count]) => ({
    name: EMOTION_CONFIG[emotion]?.label || emotion,
    value: count,
    color: EMOTION_CONFIG[emotion]?.color || '#6B7280'
  }));

  const totalEmotions = Object.values(emotionsSummary).reduce((sum, val) => sum + val, 0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-rose-50 via-white to-purple-50">
      <Navigation />
      <div className="max-w-7xl mx-auto p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 flex items-center gap-3">
            <FiHeart className="text-rose-600" />
            Analyse Émotionnelle Client
          </h1>
          <p className="text-gray-800 mt-2 font-medium">
            Détection multimodale (audio + texte) des émotions en temps réel
          </p>
        </div>

        {/* KPIs Globaux */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-lg p-6 text-white">
            <div className="text-sm opacity-90 font-semibold">Total Enregistrements</div>
            <div className="text-4xl font-bold mt-2">{stats?.total_recordings || 0}</div>
            <div className="text-xs opacity-75 mt-1">Client + Conseiller</div>
          </div>
          
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg p-6 text-white">
            <div className="text-sm opacity-90 font-semibold">Audios Clients</div>
            <div className="text-4xl font-bold mt-2">{stats?.client_audios || 0}</div>
            <div className="text-xs opacity-75 mt-1">Déclarations vocales</div>
          </div>
          
          <div className="bg-gradient-to-br from-rose-500 to-rose-600 rounded-xl shadow-lg p-6 text-white">
            <div className="text-sm opacity-90 font-semibold">Alertes Actives</div>
            <div className="text-4xl font-bold mt-2">{alerts.length}</div>
            <div className="text-xs opacity-75 mt-1">Clients en détresse</div>
          </div>
          
          <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg p-6 text-white">
            <div className="text-sm opacity-90 font-semibold">Stockage Audio</div>
            <div className="text-4xl font-bold mt-2">{stats?.storage_mb?.toFixed(1) || 0} MB</div>
            <div className="text-xs opacity-75 mt-1">Données archivées</div>
          </div>
        </div>

        {/* KPIs par Émotion */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
          {Object.entries(EMOTION_CONFIG).map(([key, config]) => {
            const count = emotionsSummary[key] || 0;
            const percentage = totalEmotions > 0 ? ((count / totalEmotions) * 100).toFixed(1) : 0;
            const Icon = config.icon;
            
            return (
              <div key={key} className={`${config.bgColor} border-l-4 ${config.borderColor} rounded-xl shadow p-4`}>
                <div className="flex items-center gap-2 mb-2">
                  <Icon className={config.textColor} size={20} />
                  <div className={`text-sm font-bold ${config.textColor}`}>{config.label}</div>
                </div>
                <div className="text-3xl font-bold text-gray-900">{count}</div>
                <div className="text-xs text-gray-600 mt-1">{percentage}% du total</div>
              </div>
            );
          })}
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Distribution émotions */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <FiActivity className="text-purple-600" />
              Distribution des Émotions
            </h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={emotionChartData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={(entry) => `${entry.name}: ${entry.value}`}
                >
                  {emotionChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Intensité émotionnelle */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <FiTrendingUp className="text-rose-600" />
              Intensité par Émotion
            </h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={emotionChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" name="Nombre de détections">
                  {emotionChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Alertes Émotionnelles */}
        {alerts.length > 0 && (
          <div className="bg-rose-50 border-l-4 border-rose-600 rounded-xl shadow-lg p-6 mb-8">
            <h2 className="text-2xl font-bold text-rose-900 flex items-center gap-2 mb-4">
              <FiAlertTriangle className="animate-pulse" />
              Alertes Émotionnelles Actives ({alerts.length})
            </h2>
            <p className="text-rose-800 mb-4 font-medium">
              Ces clients nécessitent une attention immédiate de la part d'un superviseur
            </p>
            
            <div className="space-y-3">
              {alerts.slice(0, 5).map((alert, idx) => (
                <div key={idx} className="bg-white rounded-lg p-4 border-l-4 border-rose-500">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                          alert.severity === 'high' ? 'bg-red-600 text-white' : 'bg-orange-500 text-white'
                        }`}>
                          {alert.severity === 'high' ? 'URGENT' : 'PRIORITAIRE'}
                        </span>
                        <span className="font-bold text-gray-900">
                          {EMOTION_CONFIG[alert.emotion]?.label || alert.emotion}
                        </span>
                        <span className="text-gray-700 font-semibold">
                          {alert.confidence.toFixed(0)}% confiance
                        </span>
                      </div>
                      <p className="text-gray-800 text-sm">
                        "{alert.transcription}"
                      </p>
                      <div className="text-xs text-gray-600 mt-2">
                        {new Date(alert.timestamp).toLocaleString('fr-FR')}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Analyses Récentes */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <FiActivity className="text-indigo-600" />
            Analyses Récentes
          </h2>
          
          {recent.length === 0 ? (
            <div className="text-center py-8 text-gray-600">
              <p className="font-medium">Aucune analyse disponible</p>
              <p className="text-sm mt-2">Les nouvelles analyses apparaîtront ici automatiquement</p>
            </div>
          ) : (
            <div className="space-y-3">
              {recent.map((item, idx) => {
                const emotion = item.dominant_emotion?.label || 'neutral';
                const confidence = item.dominant_emotion?.confidence || 0;
                const config = EMOTION_CONFIG[emotion];
                const Icon = config.icon;
                
                return (
                  <div key={idx} className={`${config.bgColor} border-l-4 ${config.borderColor} rounded-lg p-4`}>
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3 mb-2">
                        <Icon className={config.textColor} size={24} />
                        <div>
                          <div className={`font-bold ${config.textColor}`}>{config.label}</div>
                          <div className="text-xs text-gray-600">
                            Confiance: {confidence.toFixed(0)}%
                          </div>
                        </div>
                      </div>
                      <div className="text-xs text-gray-600">
                        {new Date(item.timestamp).toLocaleString('fr-FR')}
                      </div>
                    </div>
                    <p className="text-gray-800 text-sm mt-2">
                      "{item.transcription}"
                    </p>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
