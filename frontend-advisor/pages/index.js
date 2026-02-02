import React, { useEffect, useState } from 'react';
import Navigation from '../components/Navigation';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { FiActivity, FiUsers, FiAlertCircle, FiFileText, FiTrendingUp, FiHeart, FiAlertTriangle, FiSmile } from 'react-icons/fi';
import Link from 'next/link';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const COLORS = ['#4F46E5', '#06B6D4', '#10B981', '#F59E0B', '#EF4444', '#A855F7'];
const EMOTION_COLORS = {
  anger: '#EF4444',
  stress: '#F59E0B',
  sadness: '#3B82F6',
  fear: '#8B5CF6',
  frustration: '#EC4899',
  neutral: '#6B7280'
};

export default function DashboardAdvisor() {
  const [analytics, setAnalytics] = useState(null);
  const [sinistres, setSinistres] = useState([]);
  const [emotions, setEmotions] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchAll = async () => {
    try {
      const [aRes, sRes, eRes] = await Promise.all([
        fetch(`${API_BASE}/api/v1/analytics/overview`).then(r => r.json()),
        fetch(`${API_BASE}/api/v1/sinistres`).then(r => r.json()),
        fetch(`${API_BASE}/api/v1/emotions/dashboard-summary`).then(r => r.json()).catch(() => null)
      ]);
      setAnalytics(aRes);
      setSinistres(sRes || []);
      setEmotions(eRes);
    } catch (e) {
      console.error('Erreur dashboard:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Navigation />
        <div className="max-w-7xl mx-auto p-8">Chargement...</div>
      </div>
    );
  }

  const kpis = analytics?.kpis || {};
  const sinistresByDay = analytics?.sinistres_by_day || [];
  const sinistresByType = analytics?.sinistres_by_type || [];
  const sinistresByStatus = analytics?.sinistres_by_status || [];
  const escaladesByStatus = analytics?.escalades_by_status || [];
  const rembByStatus = analytics?.remboursements_by_status || [];
  const cciBuckets = analytics?.cci_buckets || [];
  const cognitiveCards = analytics?.cognitive_cards || [];
  const rembSum = analytics?.remboursements_sum || {};

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50">
      <Navigation />
      <div className="max-w-7xl mx-auto p-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 flex items-center gap-3"><FiActivity className="text-indigo-600" /> Dashboard Cognitif</h1>
          <p className="text-gray-800 mt-2 font-medium">Analyse scientifique, explicable et temps réel des sinistres</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          <div className="bg-white rounded-xl shadow p-5">
            <div className="text-sm text-gray-700 font-semibold">Clients</div>
            <div className="text-3xl font-bold text-gray-900 flex items-center gap-2"><FiUsers className="text-indigo-500" /> {kpis.clients_total}</div>
          </div>
          <div className="bg-white rounded-xl shadow p-5">
            <div className="text-sm text-gray-700 font-semibold">Sinistres</div>
            <div className="text-3xl font-bold text-gray-900 flex items-center gap-2"><FiFileText className="text-cyan-500" /> {kpis.sinistres_total}</div>
          </div>
          <div className="bg-white rounded-xl shadow p-5">
            <div className="text-sm text-gray-700 font-semibold">Escalades</div>
            <div className="text-3xl font-bold text-gray-900 flex items-center gap-2"><FiAlertCircle className="text-rose-500" /> {kpis.escalades_total}</div>
          </div>
          <div className="bg-white rounded-xl shadow p-5">
            <div className="text-sm text-gray-700 font-semibold">Remboursements</div>
            <div className="text-3xl font-bold text-gray-900 flex items-center gap-2"><FiTrendingUp className="text-emerald-500" /> {kpis.remboursements_total}</div>
          </div>
          <div className="bg-white rounded-xl shadow p-5">
            <div className="text-sm text-gray-700 font-semibold">CCI moyen</div>
            <div className="text-3xl font-bold text-gray-900">{kpis.cci_avg}</div>
            <div className="text-xs text-gray-700">Min {kpis.cci_min} / Max {kpis.cci_max}</div>
          </div>
        </div>

        {/* NOUVEAU: Section Analyse Émotionnelle */}
        {emotions && (
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                <FiHeart className="text-pink-500" />
                Analyse Émotionnelle
              </h2>
              <Link href="/emotions" className="text-indigo-600 hover:text-indigo-700 font-medium flex items-center gap-1">
                Voir détails →
              </Link>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-white rounded-xl shadow p-4 border-l-4 border-pink-500">
                <div className="text-sm text-gray-600 font-semibold">Analyses totales</div>
                <div className="text-3xl font-bold text-gray-900 mt-2">{emotions.total_analyses}</div>
              </div>
              <div className="bg-white rounded-xl shadow p-4 border-l-4 border-red-500">
                <div className="text-sm text-gray-600 font-semibold flex items-center gap-1">
                  <FiAlertTriangle className="text-red-500" />
                  Alertes actives
                </div>
                <div className="text-3xl font-bold text-red-600 mt-2">{emotions.alert_count}</div>
              </div>
              <div className="bg-white rounded-xl shadow p-4 border-l-4 border-indigo-500">
                <div className="text-sm text-gray-600 font-semibold">Émotion dominante</div>
                <div className="text-xl font-bold mt-2" style={{color: EMOTION_COLORS[emotions.dominant_emotion?.label]}}>
                  {emotions.dominant_emotion?.label === 'anger' && '😡 Colère'}
                  {emotions.dominant_emotion?.label === 'stress' && '😰 Stress'}
                  {emotions.dominant_emotion?.label === 'sadness' && '😢 Tristesse'}
                  {emotions.dominant_emotion?.label === 'fear' && '😨 Peur'}
                  {emotions.dominant_emotion?.label === 'frustration' && '😤 Frustration'}
                  {emotions.dominant_emotion?.label === 'neutral' && '😐 Neutre'}
                </div>
                <div className="text-sm text-gray-500 mt-1">{emotions.dominant_emotion?.percentage}%</div>
              </div>
              <div className="bg-white rounded-xl shadow p-4 border-l-4 border-green-500">
                <div className="text-sm text-gray-600 font-semibold flex items-center gap-1">
                  <FiSmile className="text-green-500" />
                  État global
                </div>
                <div className="text-xl font-bold text-gray-900 mt-2">
                  {emotions.alert_count === 0 && '✅ Stable'}
                  {emotions.alert_count > 0 && emotions.alert_count <= 3 && '⚠️ Vigilance'}
                  {emotions.alert_count > 3 && '🚨 Critique'}
                </div>
              </div>
            </div>

            {/* Mini graphique émotions */}
            <div className="bg-white rounded-xl shadow p-4">
              <h3 className="font-semibold text-gray-900 mb-3">Répartition émotionnelle</h3>
              <div className="grid grid-cols-6 gap-2">
                {Object.entries(emotions.emotion_percentages || {}).map(([emotion, percent]) => (
                  <div key={emotion} className="text-center">
                    <div className="text-2xl mb-1">
                      {emotion === 'anger' && '😡'}
                      {emotion === 'stress' && '😰'}
                      {emotion === 'sadness' && '😢'}
                      {emotion === 'fear' && '😨'}
                      {emotion === 'frustration' && '😤'}
                      {emotion === 'neutral' && '😐'}
                    </div>
                    <div className="text-xs font-medium text-gray-600 capitalize">{emotion}</div>
                    <div className="text-lg font-bold mt-1" style={{color: EMOTION_COLORS[emotion]}}>
                      {percent}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow p-4">
            <h3 className="font-bold text-gray-900 mb-2 text-lg">Sinistres par jour</h3>
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={sinistresByDay}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="count" name="Sinistres" stroke="#4F46E5" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="bg-white rounded-xl shadow p-4">
            <h3 className="font-bold text-gray-900 mb-2 text-lg">Sinistres par type</h3>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={sinistresByType}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" name="Volume" fill="#06B6D4" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="bg-white rounded-xl shadow p-4">
            <h3 className="font-bold text-gray-900 mb-2 text-lg">Sinistres par statut</h3>
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={sinistresByStatus} dataKey="value" nameKey="name" outerRadius={90}>
                  {sinistresByStatus.map((_, idx) => (
                    <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow p-4">
            <h3 className="font-bold text-gray-900 mb-2 text-lg">Distribution CCI</h3>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={cciBuckets}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="range" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" name="Dossiers" fill="#10B981" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="bg-white rounded-xl shadow p-4">
            <h3 className="font-bold text-gray-900 mb-2 text-lg">Escalades par statut</h3>
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={escaladesByStatus} dataKey="value" nameKey="name" outerRadius={90}>
                  {escaladesByStatus.map((_, idx) => (
                    <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="bg-white rounded-xl shadow p-4">
            <h3 className="font-bold text-gray-900 mb-2 text-lg">Remboursements par statut</h3>
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={rembByStatus} dataKey="value" nameKey="name" outerRadius={90}>
                  {rembByStatus.map((_, idx) => (
                    <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
            <div className="text-sm text-gray-800 mt-2 font-medium">Total réclamé: {rembSum.reclame} | Accepté: {rembSum.accepte} | Net: {rembSum.net}</div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow p-6 mb-8">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Système Cognitif — Faits vs Propositions</h3>
          <p className="text-gray-800 mb-4 font-medium">Mesure explicable de la qualité informationnelle: faits structurés, propositions textuelles, confiance et CCI.</p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {cognitiveCards.map((c, idx) => (
              <div key={idx} className="border rounded-xl p-4">
                <div className="text-sm text-gray-800 font-semibold">{c.numero_sinistre}</div>
                <div className="font-bold text-gray-900">{c.client}</div>
                <div className="text-sm text-gray-700">Type: {c.type} • Statut: {c.status}</div>
                <div className="mt-2 text-sm text-gray-800">Faits: <b>{c.facts}</b> • Propositions: <b>{c.propositions}</b></div>
                <div className="text-sm text-gray-800">Confiance: <b>{c.confidence}%</b> • CCI: <b>{c.cci_score}</b></div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="px-6 py-4 border-b">
            <h3 className="text-xl font-bold text-gray-900">Tous les dossiers client (temps réel)</h3>
            <p className="text-gray-800 text-sm font-medium">Chaque déclaration ajoutée apparaît automatiquement ici.</p>
          </div>
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-bold text-gray-900">N° Sinistre</th>
                <th className="px-6 py-3 text-left text-sm font-bold text-gray-900">Client</th>
                <th className="px-6 py-3 text-left text-sm font-bold text-gray-900">Type</th>
                <th className="px-6 py-3 text-left text-sm font-bold text-gray-900">Statut</th>
                <th className="px-6 py-3 text-left text-sm font-bold text-gray-900">CCI</th>
              </tr>
            </thead>
            <tbody>
              {sinistres.map(s => (
                <tr key={s.id} className="border-t hover:bg-gray-50">
                  <td className="px-6 py-3 text-sm text-gray-900 font-medium">{s.numero_sinistre}</td>
                  <td className="px-6 py-3 text-sm text-gray-900">{s.client?.nom} {s.client?.prenom}</td>
                  <td className="px-6 py-3 text-sm text-gray-800">{s.type_sinistre}</td>
                  <td className="px-6 py-3 text-sm text-gray-800">{s.status_dossier}</td>
                  <td className="px-6 py-3 text-sm text-gray-900 font-semibold">{s.cci_score}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
