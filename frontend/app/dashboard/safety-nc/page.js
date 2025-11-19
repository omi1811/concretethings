'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Plus, Search, MessageSquareWarning, AlertTriangle } from 'lucide-react';
import toast from 'react-hot-toast';

export default function SafetyNCPage() {
  const [ncs, setNcs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    fetchNCs();
  }, []);

  const fetchNCs = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/safety/nc', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setNcs(data.non_conformances || data.ncs || data || []);
      } else {
        toast.error('Failed to load NCs');
      }
    } catch (error) {
      console.error('Error:', error);
      toast.error('Error loading NCs');
    } finally {
      setLoading(false);
    }
  };

  const filteredNCs = ncs.filter(nc => {
    const matchesSearch = nc.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         nc.nc_number?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         nc.contractor_name?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = filterStatus === 'all' || nc.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status) => {
    const colors = {
      'open': 'bg-red-100 text-red-800',
      'in_progress': 'bg-yellow-100 text-yellow-800',
      'pending_verification': 'bg-blue-100 text-blue-800',
      'closed': 'bg-green-100 text-green-800'
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[status] || 'bg-gray-100 text-gray-800'}`}>
        {status?.replace('_', ' ').toUpperCase()}
      </span>
    );
  };

  const getSeverityBadge = (severity) => {
    const colors = {
      'critical': 'bg-red-600 text-white',
      'major': 'bg-orange-600 text-white',
      'minor': 'bg-yellow-600 text-white'
    };
    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${colors[severity] || 'bg-gray-600 text-white'}`}>
        {severity?.toUpperCase()}
      </span>
    );
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

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
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Safety Non-Conformance (NC)</h1>
        <p className="text-gray-600">Track and manage safety violations</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg border p-4">
          <div className="text-2xl font-bold text-red-600">
            {ncs.filter(nc => nc.status === 'open').length}
          </div>
          <div className="text-sm text-gray-600">Open</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-2xl font-bold text-yellow-600">
            {ncs.filter(nc => ['in_progress', 'pending_verification'].includes(nc.status)).length}
          </div>
          <div className="text-sm text-gray-600">In Progress</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-2xl font-bold text-green-600">
            {ncs.filter(nc => nc.status === 'closed').length}
          </div>
          <div className="text-sm text-gray-600">Closed</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-2xl font-bold text-gray-600">{ncs.length}</div>
          <div className="text-sm text-gray-600">Total</div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg border p-4 mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search by NC number, description, contractor..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Status</option>
            <option value="open">Open</option>
            <option value="in_progress">In Progress</option>
            <option value="pending_verification">Pending Verification</option>
            <option value="closed">Closed</option>
          </select>
          <Link
            href="/dashboard/safety-nc/new"
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 whitespace-nowrap"
          >
            <Plus className="w-5 h-5" />
            Raise NC
          </Link>
        </div>
      </div>

      {/* NCs Table */}
      <div className="bg-white rounded-lg border overflow-hidden">
        {filteredNCs.length === 0 ? (
          <div className="text-center py-12">
            <MessageSquareWarning className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <h3 className="text-lg font-medium text-gray-900 mb-1">No NCs found</h3>
            <p className="text-gray-500">
              {searchQuery || filterStatus !== 'all' ? 'Try adjusting your filters' : 'No safety NCs raised yet'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">NC #</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Contractor</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Severity</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Raised Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Due Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {filteredNCs.map((nc) => (
                  <tr key={nc.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm font-medium text-blue-600">{nc.nc_number}</td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900 max-w-xs truncate">{nc.description}</div>
                      <div className="text-sm text-gray-500">{nc.location}</div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">{nc.contractor_name}</td>
                    <td className="px-6 py-4">{getSeverityBadge(nc.severity)}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{formatDate(nc.raised_date)}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{formatDate(nc.due_date)}</td>
                    <td className="px-6 py-4">{getStatusBadge(nc.status)}</td>
                    <td className="px-6 py-4 text-right">
                      <Link
                        href={`/dashboard/safety-nc/${nc.id}`}
                        className="text-blue-600 hover:text-blue-900 font-medium text-sm"
                      >
                        View
                      </Link>
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
