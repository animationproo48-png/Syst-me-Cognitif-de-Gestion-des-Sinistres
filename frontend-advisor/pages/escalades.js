import React, { useEffect, useState } from 'react';
import { FiAlertCircle, FiPlus, FiSearch, FiEdit2, FiTrash2, FiSave, FiX } from 'react-icons/fi';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import Navigation from '../components/Navigation';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function EscaladesManager() {
  const [escalades, setEscalades] = useState([]);
  const [sinistres, setSinistres] = useState([]);
  const [conseillers, setConseillers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [formData, setFormData] = useState({
    sinistre_id: '',
    conseiller_id: '',
    raison_escalade: 'CCI élevé',
    cci_score_trigger: 0,
    status: 'en_attente'
  });

  const fetchAll = async () => {
    try {
      const [eRes, sRes, cRes] = await Promise.all([
        axios.get(`${API_BASE}/api/v1/escalades`),
        axios.get(`${API_BASE}/api/v1/sinistres`),
        axios.get(`${API_BASE}/api/v1/conseillers`)
      ]);
      setEscalades(eRes.data || []);
      setSinistres(sRes.data || []);
      setConseillers(cRes.data || []);
    } catch (err) {
      console.error('Erreur chargement escalades:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const resetForm = () => {
    setFormData({
      sinistre_id: '',
      conseiller_id: '',
      raison_escalade: 'CCI élevé',
      cci_score_trigger: 0,
      status: 'en_attente'
    });
  };

  const startEdit = (item) => {
    setEditing(item);
    setShowForm(true);
    setFormData({
      sinistre_id: item.sinistre_id,
      conseiller_id: item.conseiller_id || '',
      raison_escalade: item.raison_escalade || '',
      cci_score_trigger: item.cci_score_trigger || 0,
      status: item.status || 'en_attente'
    });
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    await axios.post(`${API_BASE}/api/v1/escalades`, formData);
    await fetchAll();
    setShowForm(false);
    resetForm();
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    await axios.put(`${API_BASE}/api/v1/escalades/${editing.id}`, formData);
    await fetchAll();
    setEditing(null);
    setShowForm(false);
    resetForm();
  };

  const handleDelete = async (id) => {
    if (!confirm('Supprimer cette escalade ?')) return;
    await axios.delete(`${API_BASE}/api/v1/escalades/${id}`);
    await fetchAll();
  };

  const filtered = escalades.filter(e =>
    e.sinistre?.numero_sinistre?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    e.sinistre?.client?.nom?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    e.status?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-rose-50">
      <Navigation />
      <div className="max-w-7xl mx-auto p-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-4xl font-bold text-gray-800 flex items-center gap-3"><FiAlertCircle className="text-rose-600" /> Escalades</h1>
            <p className="text-gray-900 mt-2 font-medium">CRUD complet des escalades et affectations</p>
          </div>
          <button
            onClick={() => { setShowForm(true); setEditing(null); resetForm(); }}
            className="flex items-center gap-2 px-6 py-3 bg-rose-600 text-white rounded-lg hover:bg-rose-700 transition"
          >
            <FiPlus /> Nouvelle Escalade
          </button>
        </div>

        <div className="mb-6">
          <div className="relative">
            <FiSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-600" />
            <input
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Rechercher par sinistre, client, statut..."
              className="w-full pl-12 pr-4 py-3 rounded-lg border border-gray-200 focus:ring-2 focus:ring-rose-200"
            />
          </div>
        </div>

        <AnimatePresence>
          {(showForm || editing) && (
            <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="bg-white rounded-xl shadow-lg p-6 mb-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold">{editing ? 'Modifier Escalade' : 'Nouvelle Escalade'}</h2>
                <button onClick={() => { setShowForm(false); setEditing(null); resetForm(); }} className="text-gray-700 hover:text-gray-900"><FiX size={22} /></button>
              </div>
              <form onSubmit={editing ? handleUpdate : handleCreate} className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-bold text-gray-900 mb-1">Sinistre</label>
                  <select
                    value={formData.sinistre_id}
                    onChange={(e) => setFormData({ ...formData, sinistre_id: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                    required
                  >
                    <option value="">Sélectionner</option>
                    {sinistres.map(s => (
                      <option key={s.id} value={s.id}>{s.numero_sinistre} - {s.client?.nom} {s.client?.prenom}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-900 mb-1">Conseiller</label>
                  <select
                    value={formData.conseiller_id}
                    onChange={(e) => setFormData({ ...formData, conseiller_id: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                  >
                    <option value="">Aucun</option>
                    {conseillers.map(c => (
                      <option key={c.id} value={c.id}>{c.prenom} {c.nom}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-900 mb-1">Raison</label>
                  <input
                    type="text"
                    value={formData.raison_escalade}
                    onChange={(e) => setFormData({ ...formData, raison_escalade: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-900 mb-1">CCI</label>
                  <input
                    type="number"
                    value={formData.cci_score_trigger}
                    onChange={(e) => setFormData({ ...formData, cci_score_trigger: Number(e.target.value) })}
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-900 mb-1">Statut</label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                  >
                    <option value="en_attente">en_attente</option>
                    <option value="transferee">transferee</option>
                    <option value="completee">completee</option>
                  </select>
                </div>

                <div className="col-span-2 flex justify-end gap-3">
                  <button type="button" onClick={() => { setShowForm(false); setEditing(null); resetForm(); }} className="px-6 py-2 border rounded-lg">Annuler</button>
                  <button type="submit" className="flex items-center gap-2 px-6 py-2 bg-rose-600 text-white rounded-lg"><FiSave /> {editing ? 'Mettre à jour' : 'Créer'}</button>
                </div>
              </form>
            </motion.div>
          )}
        </AnimatePresence>

        {loading ? (
          <div className="text-center py-12">Chargement...</div>
        ) : (
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-900">Sinistre</th>
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-900">Client</th>
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-900">Statut</th>
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-900">CCI</th>
                  <th className="px-6 py-4 text-right text-sm font-bold text-gray-900">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(item => (
                  <tr key={item.id} className="border-t">
                    <td className="px-6 py-4 text-sm text-gray-900 font-medium">{item.sinistre?.numero_sinistre}</td>
                    <td className="px-6 py-4 text-sm text-gray-900 font-medium">{item.sinistre?.client?.nom} {item.sinistre?.client?.prenom}</td>
                    <td className="px-6 py-4 text-sm text-gray-900 font-medium">{item.status}</td>
                    <td className="px-6 py-4 text-sm text-gray-900 font-medium">{item.cci_score_trigger}</td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex justify-end gap-3">
                        <button onClick={() => startEdit(item)} className="text-blue-600 hover:text-blue-800"><FiEdit2 /></button>
                        <button onClick={() => handleDelete(item.id)} className="text-red-600 hover:text-red-800"><FiTrash2 /></button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

