import Link from 'next/link';
import { FiHome, FiUsers, FiAlertCircle, FiFileText, FiLayers, FiDollarSign, FiCpu, FiHeart } from 'react-icons/fi';

export default function Navigation() {
  return (
    <nav className="bg-white shadow-md mb-6">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="text-2xl font-bold text-blue-600">CRM Advisor</div>
          <div className="flex gap-6">
            <Link href="/" className="flex items-center gap-2 text-gray-700 hover:text-blue-600 transition">
              <FiHome /> Dashboard
            </Link>
            <Link href="/clients" className="flex items-center gap-2 text-gray-700 hover:text-blue-600 transition">
              <FiUsers /> Gestion Clients
            </Link>
            <Link href="/sinistres" className="flex items-center gap-2 text-gray-700 hover:text-blue-600 transition">
              <FiFileText /> Dossiers Sinistres
            </Link>
            <Link href="/contrats" className="flex items-center gap-2 text-gray-700 hover:text-blue-600 transition">
              <FiLayers /> Contrats
            </Link>
            <Link href="/remboursements" className="flex items-center gap-2 text-gray-700 hover:text-blue-600 transition">
              <FiDollarSign /> Remboursements
            </Link>
            <Link href="/escalades" className="flex items-center gap-2 text-gray-700 hover:text-blue-600 transition">
              <FiAlertCircle /> Escalades
            </Link>
            <Link href="/analyse" className="flex items-center gap-2 text-gray-700 hover:text-blue-600 transition">
              <FiCpu /> Analyse Cognitive
            </Link>
            <Link href="/emotions" className="flex items-center gap-2 text-gray-700 hover:text-blue-600 transition">
              <FiHeart /> Émotions
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}
