import React, { useEffect, useState } from 'react';
import { FiLayers, FiPlus, FiSearch, FiEdit2, FiTrash2, FiSave, FiX } from 'react-icons/fi';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import Navigation from '../components/Navigation';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function ContratsManager() {
  const [contrats, setContrats] = useState([]);
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [formData, setFormData] = useState({
    client_id: '',
    numero_contrat: '',
    type_assurance: 'auto',
    date_debut: '',
    date_fin: '',
    statut: 'actif',
    garantie_collision: false,
    garantie_vol: false,
    garantie_incendie: false,
    garantie_responsabilite: true,
    garantie_assistance: true,
    franchise_collision: 500,
    franchise_vol: 500,
    franchise_incendie: 500,
    limite_responsabilite: 50000,
    limite_collision: 50000,
    limite_vol: 50000
  });

  const fetchAll = async () => {
    try {
      const [cRes, clRes] = await Promise.all([
        axios.get(`${API_BASE}/api/v1/contrats`),
        axios.get(`${API_BASE}/api/v1/clients`)
      ]);
      setContrats(cRes.data || []);
      setClients(clRes.data || []);
    } catch (err) {
      console.error('Erreur chargement contrats:', err);
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
      numero_contrat: '',
      type_assurance: 'auto',
      date_debut: '',
      date_fin: '',
      statut: 'actif',
      garantie_collision: false,
      garantie_vol: false,
      garantie_incendie: false,
      garantie_responsabilite: true,
      garantie_assistance: true,
      franchise_collision: 500,
      franchise_vol: 500,
      franchise_incendie: 500,
      limite_responsabilite: 50000,
      limite_collision: 50000,
      limite_vol: 50000
    });
  };

  const startEdit = (item) => {
    setEditing(item);
    setShowForm(true);
    setFormData({
      client_id: item.client_id,
      numero_contrat: item.numero_contrat || '',
      type_assurance: item.type_assurance || 'auto',
      date_debut: item.date_debut ? item.date_debut.substring(0, 10) : '',
      date_fin: item.date_fin ? item.date_fin.substring(0, 10) : '',
      statut: item.statut || 'actif',
      garantie_collision: !!item.garantie_collision,
      garantie_vol: !!item.garantie_vol,
      garantie_incendie: !!item.garantie_incendie,
      garantie_responsabilite: !!item.garantie_responsabilite,
      garantie_assistance: !!item.garantie_assistance,
      franchise_collision: item.franchise_collision || 500,
      franchise_vol: item.franchise_vol || 500,
      franchise_incendie: item.franchise_incendie || 500,
      limite_responsabilite: item.limite_responsabilite || 50000,
      limite_collision: item.limite_collision || 50000,
      limite_vol: item.limite_vol || 50000
    });
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    await axios.post(`${API_BASE}/api/v1/contrats`, formData);
    await fetchAll();
    setShowForm(false);
    resetForm();
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    await axios.put(`${API_BASE}/api/v1/contrats/${editing.id}`, formData);
    await fetchAll();
    setEditing(null);
    setShowForm(false);
    resetForm();
  };

  const handleDelete = async (id, numero) => {
    if (!confirm(`Supprimer le contrat ${numero} ?`)) return;
    await axios.delete(`${API_BASE}/api/v1/contrats/${id}`);
    await fetchAll();
  };

  const filtered = contrats.filter(c =>
    c.numero_contrat?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.client?.nom?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.client?.prenom?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-indigo-50">
      <Navigation />
      <div className="max-w-7xl mx-auto p-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-4xl font-bold text-gray-800 flex items-center gap-3"><FiLayers className="text-indigo-600" /> Contrats</h1>
            <p className="text-gray-900 mt-2 font-medium">CRUD complet des contrats et garanties</p>
          </div>
          <button
            onClick={() => { setShowForm(true); setEditing(null); resetForm(); }}
            className="flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
          >
            <FiPlus /> Nouveau Contrat
          </button>
        </div>

        <div className="mb-6">
          <div className="relative">
            <FiSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-600" />
            <input
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Rechercher par numéro ou client..."
              className="w-full pl-12 pr-4 py-3 rounded-lg border border-gray-200 focus:ring-2 focus:ring-indigo-200"
            />
          </div>
        </div>

        <AnimatePresence>
          {(showForm || editing) && (
            <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="bg-white rounded-xl shadow-lg p-6 mb-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold">{editing ? 'Modifier Contrat' : 'Nouveau Contrat'}</h2>
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
                  <label className="block text-sm font-bold text-gray-900 mb-1">Numéro contrat</label>
                  <input
                    type="text"
                    value={formData.numero_contrat}
                    onChange={(e) => setFormData({ ...formData, numero_contrat: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-900 mb-1">Type assurance</label>
                  <input
                    type="text"
                    value={formData.type_assurance}
                    onChange={(e) => setFormData({ ...formData, type_assurance: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-900 mb-1">Statut</label>
                  <select
                    value={formData.statut}
                    onChange={(e) => setFormData({ ...formData, statut: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                  >
                    <option value="actif">actif</option>
                    <option value="suspendu">suspendu</option>
                    <option value="expiré">expiré</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-900 mb-1">Date début</label>
                  <input
                    type="date"
                    value={formData.date_debut}
                    onChange={(e) => setFormData({ ...formData, date_debut: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold text-gray-900 mb-1">Date fin</label>
                  <input
                    type="date"
                    value={formData.date_fin}
                    onChange={(e) => setFormData({ ...formData, date_fin: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-bold text-gray-900 mb-1">Garanties</label>
                  <div className="grid grid-cols-3 gap-3">
                    <label className="flex items-center gap-2"><input type="checkbox" checked={formData.garantie_collision} onChange={(e) => setFormData({ ...formData, garantie_collision: e.target.checked })} /> Collision</label>
                    <label className="flex items-center gap-2"><input type="checkbox" checked={formData.garantie_vol} onChange={(e) => setFormData({ ...formData, garantie_vol: e.target.checked })} /> Vol</label>
                    <label className="flex items-center gap-2"><input type="checkbox" checked={formData.garantie_incendie} onChange={(e) => setFormData({ ...formData, garantie_incendie: e.target.checked })} /> Incendie</label>
                    <label className="flex items-center gap-2"><input type="checkbox" checked={formData.garantie_responsabilite} onChange={(e) => setFormData({ ...formData, garantie_responsabilite: e.target.checked })} /> Responsabilité</label>
                    <label className="flex items-center gap-2"><input type="checkbox" checked={formData.garantie_assistance} onChange={(e) => setFormData({ ...formData, garantie_assistance: e.target.checked })} /> Assistance</label>
                  </div>
                </div>

                <div className="col-span-2 flex justify-end gap-3">
                  <button type="button" onClick={() => { setShowForm(false); setEditing(null); resetForm(); }} className="px-6 py-2 border rounded-lg">Annuler</button>
                  <button type="submit" className="flex items-center gap-2 px-6 py-2 bg-indigo-600 text-white rounded-lg"><FiSave /> {editing ? 'Mettre à jour' : 'Créer'}</button>
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
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-900">N° Contrat</th>
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-900">Client</th>
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-900">Type</th>
                  <th className="px-6 py-4 text-left text-sm font-bold text-gray-900">Statut</th>
                  <th className="px-6 py-4 text-right text-sm font-bold text-gray-900">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(item => (
                  <tr key={item.id} className="border-t">
                    <td className="px-6 py-4 text-sm text-gray-900 font-medium">{item.numero_contrat}</td>
                    <td className="px-6 py-4 text-sm text-gray-900 font-medium">{item.client?.nom} {item.client?.prenom}</td>
                    <td className="px-6 py-4 text-sm text-gray-900 font-medium">{item.type_assurance}</td>
                    <td className="px-6 py-4 text-sm text-gray-900 font-medium">{item.statut}</td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex justify-end gap-3">
                        <button onClick={() => startEdit(item)} className="text-blue-600 hover:text-blue-800"><FiEdit2 /></button>
                        <button onClick={() => handleDelete(item.id, item.numero_contrat)} className="text-red-600 hover:text-red-800"><FiTrash2 /></button>
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

