'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Plus, Search, Beaker } from 'lucide-react';
import toast from 'react-hot-toast';

export default function MixDesignsPage() {
  const [mixDesigns, setMixDesigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchMixDesigns();
  }, []);

  const fetchMixDesigns = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/mix-designs', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setMixDesigns(data.mix_designs || data || []);
      } else {
        toast.error('Failed to load mix designs');
      }
    } catch (error) {
      console.error('Error:', error);
      toast.error('Error loading mix designs');
    } finally {
      setLoading(false);
    }
  };

  const filteredDesigns = mixDesigns.filter(design =>
    design.grade?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    design.mix_id?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Mix Designs</h1>
        <p className="text-gray-600">Concrete grade specifications per IS 456:2000</p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg border p-4">
          <div className="text-2xl font-bold text-blue-600">{mixDesigns.length}</div>
          <div className="text-sm text-gray-600">Total Mix Designs</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-2xl font-bold text-green-600">
            {mixDesigns.filter(m => m.status === 'approved').length}
          </div>
          <div className="text-sm text-gray-600">Approved</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-2xl font-bold text-yellow-600">
            {mixDesigns.filter(m => m.status === 'draft').length}
          </div>
          <div className="text-sm text-gray-600">Draft</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-2xl font-bold text-gray-600">
            {new Set(mixDesigns.map(m => m.grade)).size}
          </div>
          <div className="text-sm text-gray-600">Unique Grades</div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg border p-4 mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search by grade or mix ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <Link
            href="/dashboard/mix-designs/new"
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 whitespace-nowrap"
          >
            <Plus className="w-5 h-5" />
            New Mix Design
          </Link>
        </div>
      </div>

      {/* Mix Designs Grid */}
      {filteredDesigns.length === 0 ? (
        <div className="bg-white rounded-lg border p-12 text-center">
          <Beaker className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <h3 className="text-lg font-medium text-gray-900 mb-1">No mix designs found</h3>
          <p className="text-gray-500">
            {searchQuery ? 'Try adjusting your search' : 'Create your first mix design'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredDesigns.map((design) => (
            <Link
              key={design.id}
              href={`/dashboard/mix-designs/${design.id}`}
              className="bg-white rounded-lg border p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-1">{design.grade}</h3>
                  <p className="text-sm text-gray-500">{design.mix_id || 'N/A'}</p>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  design.status === 'approved' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {design.status || 'Draft'}
                </span>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">W/C Ratio:</span>
                  <span className="font-medium text-gray-900">{design.wc_ratio || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Cement Content:</span>
                  <span className="font-medium text-gray-900">{design.cement_content ? `${design.cement_content} kg/m³` : 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Target Strength:</span>
                  <span className="font-medium text-gray-900">{design.target_strength ? `${design.target_strength} MPa` : 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Slump:</span>
                  <span className="font-medium text-gray-900">{design.slump ? `${design.slump} mm` : 'N/A'}</span>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t">
                <p className="text-xs text-gray-500">
                  {design.description?.substring(0, 80)}{design.description?.length > 80 ? '...' : ''}
                </p>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
