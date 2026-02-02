import React, { useEffect, useState } from 'react';
import { FiFileText, FiPlus, FiSearch, FiEdit2, FiTrash2, FiSave, FiX } from 'react-icons/fi';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import Navigation from '../components/Navigation';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function SinistresManager() {
  const [sinistres, setSinistres] = useState([]);
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [formData, setFormData] = useState({
    client_id: '',
    type_sinistre: 'collision',
    date_sinistre: '',
    lieu_sinistre: '',
    description: '',
    cci_score: 0,
    status_dossier: 'nouveau',
    type_traitement: 'autonome',
    documents_complets: false
  });

  const fetchAll = async () => {
    try {
      const [sRes, cRes] = await Promise.all([
        axios.get(`${API_BASE}/api/v1/sinistres`),
        axios.get(`${API_BASE}/api/v1/clients`)
      ]);
      setSinistres(sRes.data || []);
      setClients(cRes.data || []);
    } catch (err) {
      console.error('Erreur chargement sinistres:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const resetForm = () => {
    setFormData({
      client_id: '',
      type_sinistre: 'collision',
      date_sinistre: '',
      lieu_sinistre: '',
      description: '',
      cci_score: 0,
      status_dossier: 'nouveau',
      type_traitement: 'autonome',
      documents_complets: false
    });
  };

  const startEdit = (item) => {
    setEditing(item);
    setShowForm(true);
    setFormData({
      client_id: item.client_id,
      type_sinistre: item.type_sinistre || 'collision',
      date_sinistre: item.date_sinistre ? item.date_sinistre.substring(0, 10) : '',
      lieu_sinistre: item.lieu_sinistre || '',
      description: item.description || '',
      cci_score: item.cci_score || 0,
      status_dossier: item.status_dossier || 'nouveau',
      type_traitement: item.type_traitement || 'autonome',
      documents_complets: !!item.documents_complets
    });
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    await axios.post(`${API_BASE}/api/v1/sinistres`, formData);
    await fetchAll();
    setShowForm(false);
    resetForm();
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    await axios.put(`${API_BASE}/api/v1/sinistres/${editing.id}`, formData);
    await fetchAll();
    setEditing(null);
    setShowForm(false);
    resetForm();
  };

  const handleDelete = async (id, numero) => {
    if (!confirm(`Supprimer le sinistre ${numero} ?`)) return;
    await axios.delete(`${API_BASE}/api/v1/sinistres/${id}`);
    await fetchAll();
  };

  const filtered = sinistres.filter(s =>
    s.numero_sinistre?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.client?.nom?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.client?.prenom?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.type_sinistre?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-indigo-50">
      <Navigation />
      <div className="max-w-7xl mx-auto p-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-4xl font-bold text-gray-800 flex items-center gap-3"><FiFileText className="text-indigo-600" /> Dossiers Sinistres</h1>
            <p className="text-gray-900 mt-2 font-medium">Vue dynamique de tous les sinistres, CRUD complet</p>
          </div>
          <button
            onClick={() => { setShowForm(true); setEditing(null); resetForm(); }}
            className="flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
          >
            <FiPlus /> Nouveau Sinistre
          </button>
        </div>

        <div className="mb-6">
          <div className="relative">
            <FiSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-600" />
            <input
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Rechercher par numéro, client, type..."
              className="w-full pl-12 pr-4 py-3 rounded-lg border border-gray-200 focus:ring-2 focus:ring-indigo-200"
            />
          </div>
        </div>

        <AnimatePresence>
          {(showForm || editing) && (
            <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="bg-white rounded-xl shadow-lg p-6 mb-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold">{editing ? 'Modifier Sinistre' : 'Nouveau Sinistre'}</h2>
                <button onClick={() => { setShowForm(false); setEditing(null); resetForm(); }} className="text-gray-700 hover:text-gray-900"><FiX size={22} /></button>
              </div>
              <form onSubmit={editing ? handleUpdate : handleCreate} className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-bold text-gray-900 mb-1">Client</label>
                  <select
                    value={formData.client_id}
                    onChange={(e) => setFormData({ ...formData, client_id: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                    required
                  >
                    <option value="">Sélectionner</option>
                    {clients.map(c => (
                      <option key={c.id} value={c.id}>{c.matricule} - {c.nom} {c.prenom}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-900 mb-1">Type sinistre</label>
                  <select
                    value={formData.type_sinistre}
                    onChange={(e) => setFormData({ ...formData, type_sinistre: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                  >
                    <option value="collision">collision</option>
                    <option value="vol">vol</option>
                    <option value="incendie">incendie</option>
                    <option value="dégâts">dégâts</option>
                    <option value="blessure">blessure</option>
                    <option value="autre">autre</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-900 mb-1">Date sinistre</label>
                  <input
                    type="date"
                    value={formData.date_sinistre}
                    onChange={(e) => setFormData({ ...formData, date_sinistre: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-900 mb-1">Lieu</label>
                  <input
                    type="text"
                    value={formData.lieu_sinistre}
                    onChange={(e) => setFormData({ ...formData, lieu_sinistre: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-bold text-gray-900 mb-1">Description</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                    rows={3}
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-900 mb-1">CCI</label>
                  <input
                    type="number"
                    value={formData.cci_score}
                    onChange={(e) => setFormData({ ...formData, cci_score: Number(e.target.value) })}
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-900 mb-1">Statut</label>
                  <select
                    value={formData.status_dossier}
                    onChange={(e) => setFormData({ ...formData, status_dossier: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                  >
                    <option value="nouveau">nouveau</option>
                    <option value="en_cours">en_cours</option>
                    <option value="validation">validation</option>
                    <option value="expert">expert</option>
                    <option value="escalade">escalade</option>
                    <option value="en_attente_client">en_attente_client</option>
                    <option value="fermé">fermé</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-900 mb-1">Type traitement</label>
                  <select
                    value={formData.type_traitement}
                    onChange={(e) => setFormData({ ...formData, type_traitement: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                  >
                    <option value="autonome">autonome</option>
                    <option value="escalade">escalade</option>
                    <option value="expert">expert</option>
                  </select>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.documents_complets}
                    onChange={(e) => setFormData({ ...formData, documents_complets: e.target.checked })}
                  />
                  <label className="text-sm text-gray-900 font-medium">Documents complets</label>
                </div>

                <div className="col-span-2 flex justify-end gap-3">
                  <button type="button" onClick={() => { setShowForm(false); setEditing(null); resetForm(); }} className="px-6 py-2 border rounded-lg">Annuler</button>
                  <button type="submit" className="flex items-center gap-2 px-6 py-2 bg-indigo-600 text-white rounded-lg">
                    <FiSave /> {editing ? 'Mettre à jour' : 'Créer'}
                  </button>
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
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-900">N°</th>
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-900">Client</th>
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-900">Type</th>
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-900">Statut</th>
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-900">CCI</th>
                  <th className="px-6 py-4 text-right text-sm font-bold text-gray-900">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(item => (
                  <tr key={item.id} className="border-t">
                    <td className="px-6 py-4 text-sm text-gray-900 font-medium">{item.numero_sinistre}</td>
                    <td className="px-6 py-4 text-sm text-gray-900 font-medium">{item.client?.nom} {item.client?.prenom}</td>
                    <td className="px-6 py-4 text-sm text-gray-900 font-medium">{item.type_sinistre}</td>
                    <td className="px-6 py-4 text-sm text-gray-900 font-medium">{item.status_dossier}</td>
                    <td className="px-6 py-4 text-sm text-gray-900 font-medium">{item.cci_score}</td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex justify-end gap-3">
                        <button onClick={() => startEdit(item)} className="text-blue-600 hover:text-blue-800"><FiEdit2 /></button>
                        <button onClick={() => handleDelete(item.id, item.numero_sinistre)} className="text-red-600 hover:text-red-800"><FiTrash2 /></button>
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

