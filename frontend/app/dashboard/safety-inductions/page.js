'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Plus, Search, UserCheck, AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import toast from 'react-hot-toast';

export default function SafetyInductionsPage() {
  const [inductions, setInductions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    fetchInductions();
  }, []);

  const fetchInductions = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/safety-inductions', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setInductions(data.inductions || data || []);
      } else {
        toast.error('Failed to load inductions');
      }
    } catch (error) {
      console.error('Error:', error);
      toast.error('Error loading inductions');
    } finally {
      setLoading(false);
    }
  };

  const filteredInductions = inductions.filter(ind => {
    const matchesSearch = ind.worker_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         ind.worker_id?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         ind.aadhar_number?.includes(searchQuery);
    const matchesStatus = filterStatus === 'all' || ind.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status) => {
    const config = {
      'initiated': { label: 'Initiated', color: 'bg-blue-100 text-blue-800', icon: Clock },
      'video_completed': { label: 'Video Completed', color: 'bg-yellow-100 text-yellow-800', icon: Clock },
      'quiz_passed': { label: 'Quiz Passed', color: 'bg-green-100 text-green-800', icon: CheckCircle },
      'quiz_failed': { label: 'Quiz Failed', color: 'bg-red-100 text-red-800', icon: AlertTriangle },
      'completed': { label: 'Completed', color: 'bg-green-100 text-green-800', icon: CheckCircle },
      'expired': { label: 'Expired', color: 'bg-gray-100 text-gray-800', icon: AlertTriangle }
    };
    const cfg = config[status] || config['initiated'];
    const Icon = cfg.icon;
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${cfg.color}`}>
        <Icon className="w-3 h-3" />
        {cfg.label}
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
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Safety Inductions</h1>
        <p className="text-gray-600">Worker onboarding with safety training and certification</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg border p-4">
          <div className="text-2xl font-bold text-green-600">
            {inductions.filter(i => i.status === 'completed').length}
          </div>
          <div className="text-sm text-gray-600">Completed</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-2xl font-bold text-yellow-600">
            {inductions.filter(i => ['initiated', 'video_completed'].includes(i.status)).length}
          </div>
          <div className="text-sm text-gray-600">In Progress</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-2xl font-bold text-red-600">
            {inductions.filter(i => i.status === 'expired').length}
          </div>
          <div className="text-sm text-gray-600">Expired</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-2xl font-bold text-gray-600">{inductions.length}</div>
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
              placeholder="Search by name, worker ID, or Aadhar..."
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
            <option value="initiated">Initiated</option>
            <option value="video_completed">Video Completed</option>
            <option value="quiz_passed">Quiz Passed</option>
            <option value="completed">Completed</option>
            <option value="expired">Expired</option>
          </select>
          <Link
            href="/dashboard/safety-inductions/new"
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus className="w-5 h-5" />
            New Induction
          </Link>
        </div>
      </div>

      {/* Inductions Table */}
      <div className="bg-white rounded-lg border overflow-hidden">
        {filteredInductions.length === 0 ? (
          <div className="text-center py-12">
            <UserCheck className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <h3 className="text-lg font-medium text-gray-900 mb-1">No inductions found</h3>
            <p className="text-gray-500">
              {searchQuery || filterStatus !== 'all' ? 'Try adjusting your filters' : 'Start onboarding workers'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Worker</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Aadhar</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Contractor</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Trade</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Induction Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Expiry Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {filteredInductions.map((induction) => (
                  <tr key={induction.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">{induction.worker_name}</div>
                      <div className="text-sm text-gray-500">{induction.worker_id}</div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">{induction.aadhar_number || 'N/A'}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{induction.contractor_name || 'N/A'}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{induction.trade || 'N/A'}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{formatDate(induction.induction_date)}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{formatDate(induction.expiry_date)}</td>
                    <td className="px-6 py-4">{getStatusBadge(induction.status)}</td>
                    <td className="px-6 py-4 text-right">
                      <Link
                        href={`/dashboard/safety-inductions/${induction.id}`}
                        className="text-blue-600 hover:text-blue-900 font-medium text-sm"
                      >
                        View Details
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
