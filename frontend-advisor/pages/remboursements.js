import React, { useEffect, useState } from 'react';
import { FiDollarSign, FiPlus, FiSearch, FiEdit2, FiTrash2, FiSave, FiX } from 'react-icons/fi';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import Navigation from '../components/Navigation';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function RemboursementsManager() {
  const [remboursements, setRemboursements] = useState([]);
  const [sinistres, setSinistres] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [formData, setFormData] = useState({
    sinistre_id: '',
    montant_reclame: 0,
    montant_accepte: '',
    franchise: '',
    montant_net: '',
    status: 'en_attente',
    motif_rejet: '',
    date_paiement: '',
    reference_paiement: ''
  });

  const fetchAll = async () => {
    try {
      const [rRes, sRes] = await Promise.all([
        axios.get(`${API_BASE}/api/v1/remboursements`),
        axios.get(`${API_BASE}/api/v1/sinistres`)
      ]);
      setRemboursements(rRes.data || []);
      setSinistres(sRes.data || []);
    } catch (err) {
      console.error('Erreur chargement remboursements:', err);
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
      montant_reclame: 0,
      montant_accepte: '',
      franchise: '',
      montant_net: '',
      status: 'en_attente',
      motif_rejet: '',
      date_paiement: '',
      reference_paiement: ''
    });
  };

  const startEdit = (item) => {
    setEditing(item);
    setShowForm(true);
    setFormData({
      sinistre_id: item.sinistre_id,
      montant_reclame: item.montant_reclame || 0,
      montant_accepte: item.montant_accepte ?? '',
      franchise: item.franchise ?? '',
      montant_net: item.montant_net ?? '',
      status: item.status || 'en_attente',
      motif_rejet: item.motif_rejet || '',
      date_paiement: item.date_paiement ? item.date_paiement.substring(0, 10) : '',
      reference_paiement: item.reference_paiement || ''
    });
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    await axios.post(`${API_BASE}/api/v1/remboursements`, formData);
    await fetchAll();
    setShowForm(false);
    resetForm();
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    await axios.put(`${API_BASE}/api/v1/remboursements/${editing.id}`, formData);
    await fetchAll();
    setEditing(null);
    setShowForm(false);
    resetForm();
  };

  const handleDelete = async (id) => {
    if (!confirm('Supprimer ce remboursement ?')) return;
    await axios.delete(`${API_BASE}/api/v1/remboursements/${id}`);
    await fetchAll();
  };

  const filtered = remboursements.filter(r =>
    r.sinistre?.numero_sinistre?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    r.sinistre?.client?.nom?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    r.status?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-emerald-50">
      <Navigation />
      <div className="max-w-7xl mx-auto p-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-4xl font-bold text-gray-800 flex items-center gap-3"><FiDollarSign className="text-emerald-600" /> Remboursements</h1>
            <p className="text-gray-900 mt-2 font-medium">CRUD complet des remboursements</p>
          </div>
          <button
            onClick={() => { setShowForm(true); setEditing(null); resetForm(); }}
            className="flex items-center gap-2 px-6 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition"
          >
            <FiPlus /> Nouveau Remboursement
          </button>
        </div>

        <div className="mb-6">
          <div className="relative">
            <FiSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-600" />
            <input
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Rechercher par sinistre, client, statut..."
              className="w-full pl-12 pr-4 py-3 rounded-lg border border-gray-200 focus:ring-2 focus:ring-emerald-200"
            />
          </div>
        </div>

        <AnimatePresence>
          {(showForm || editing) && (
            <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="bg-white rounded-xl shadow-lg p-6 mb-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold">{editing ? 'Modifier Remboursement' : 'Nouveau Remboursement'}</h2>
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
                  <label className="block text-sm font-bold text-gray-900 mb-1">Statut</label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                  >
                    <option value="en_attente">en_attente</option>
                    <option value="accepté">accepté</option>
                    <option value="payé">payé</option>
                    <option value="rejeté">rejeté</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-900 mb-1">Montant réclamé</label>
                  <input
                    type="number"
                    value={formData.montant_reclame}
                    onChange={(e) => setFormData({ ...formData, montant_reclame: Number(e.target.value) })}
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-900 mb-1">Montant accepté</label>
                  <input
                    type="number"
                    value={formData.montant_accepte}
                    onChange={(e) => setFormData({ ...formData, montant_accepte: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-900 mb-1">Franchise</label>
                  <input
                    type="number"
                    value={formData.franchise}
                    onChange={(e) => setFormData({ ...formData, franchise: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-900 mb-1">Montant net</label>
                  <input
                    type="number"
                    value={formData.montant_net}
                    onChange={(e) => setFormData({ ...formData, montant_net: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-900 mb-1">Date paiement</label>
                  <input
                    type="date"
                    value={formData.date_paiement}
                    onChange={(e) => setFormData({ ...formData, date_paiement: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-900 mb-1">Référence</label>
                  <input
                    type="text"
                    value={formData.reference_paiement}
                    onChange={(e) => setFormData({ ...formData, reference_paiement: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-bold text-gray-900 mb-1">Motif rejet</label>
                  <input
                    type="text"
                    value={formData.motif_rejet}
                    onChange={(e) => setFormData({ ...formData, motif_rejet: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                </div>

                <div className="col-span-2 flex justify-end gap-3">
                  <button type="button" onClick={() => { setShowForm(false); setEditing(null); resetForm(); }} className="px-6 py-2 border rounded-lg">Annuler</button>
                  <button type="submit" className="flex items-center gap-2 px-6 py-2 bg-emerald-600 text-white rounded-lg"><FiSave /> {editing ? 'Mettre à jour' : 'Créer'}</button>
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
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-900">Montant réclamé</th>
                  <th className="px-6 py-4 text-right text-sm font-bold text-gray-900">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(item => (
                  <tr key={item.id} className="border-t">
                    <td className="px-6 py-4 text-sm text-gray-900 font-medium">{item.sinistre?.numero_sinistre}</td>
                    <td className="px-6 py-4 text-sm text-gray-900 font-medium">{item.sinistre?.client?.nom} {item.sinistre?.client?.prenom}</td>
                    <td className="px-6 py-4 text-sm text-gray-900 font-medium">{item.status}</td>
                    <td className="px-6 py-4 text-sm text-gray-900 font-medium">{item.montant_reclame}</td>
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

