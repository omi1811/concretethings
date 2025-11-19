'use client';

import { useState, useEffect } from 'react';
import { 
  ClipboardCheck, Plus, Calendar, User, FileText,
  CheckCircle, XCircle, AlertTriangle, Search
} from 'lucide-react';
import { apiRequest } from '@/lib/api-optimized';
import toast from 'react-hot-toast';
import Link from 'next/link';
import { format } from 'date-fns';

export default function SafetyAuditsPage() {
  const [loading, setLoading] = useState(true);
  const [audits, setAudits] = useState([]);
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    fetchAudits();
  }, []);

  const fetchAudits = async () => {
    try {
      const projectId = localStorage.getItem('activeProjectId');
      const data = await apiRequest(`/api/safety-audits?project_id=${projectId}`);
      setAudits(data.audits || []);
    } catch (error) {
      toast.error('Failed to load audits');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'scheduled': 'bg-blue-100 text-blue-800',
      'in_progress': 'bg-yellow-100 text-yellow-800',
      'completed': 'bg-green-100 text-green-800',
      'cancelled': 'bg-red-100 text-red-800'
    };
    return colors[status] || colors.scheduled;
  };

  const getGradeColor = (grade) => {
    const colors = {
      'A_EXCELLENT': 'bg-green-100 text-green-800',
      'B_GOOD': 'bg-blue-100 text-blue-800',
      'C_SATISFACTORY': 'bg-yellow-100 text-yellow-800',
      'D_NEEDS_IMPROVEMENT': 'bg-orange-100 text-orange-800',
      'F_FAIL': 'bg-red-100 text-red-800'
    };
    return colors[grade] || 'bg-gray-100 text-gray-800';
  };

  const filteredAudits = statusFilter === 'all' 
    ? audits 
    : audits.filter(a => a.audit_status === statusFilter);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <ClipboardCheck className="w-8 h-8 text-blue-600" />
            Safety Audits
          </h1>
          <p className="text-gray-600 mt-1">Schedule and conduct safety audits</p>
        </div>
        <Link
          href="/dashboard/safety-audits/new"
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus className="w-5 h-5" />
          Schedule Audit
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Total Audits</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{audits.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Scheduled</p>
          <p className="text-2xl font-bold text-blue-600 mt-1">
            {audits.filter(a => a.audit_status === 'scheduled').length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">In Progress</p>
          <p className="text-2xl font-bold text-yellow-600 mt-1">
            {audits.filter(a => a.audit_status === 'in_progress').length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Completed</p>
          <p className="text-2xl font-bold text-green-600 mt-1">
            {audits.filter(a => a.audit_status === 'completed').length}
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex gap-2">
          {['all', 'scheduled', 'in_progress', 'completed'].map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                statusFilter === status
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {status.replace('_', ' ').toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Audits List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredAudits.map((audit) => (
          <div key={audit.id} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h3 className="font-semibold text-lg text-gray-900 mb-1">
                  {audit.audit_title}
                </h3>
                <p className="text-sm text-gray-500">{audit.audit_number}</p>
              </div>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(audit.audit_status)}`}>
                {audit.audit_status?.replace('_', ' ').toUpperCase()}
              </span>
            </div>

            <div className="space-y-2 text-sm text-gray-600">
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                <span>{format(new Date(audit.scheduled_date), 'dd MMM yyyy')}</span>
              </div>
              <div className="flex items-center gap-2">
                <User className="w-4 h-4" />
                <span>{audit.lead_auditor_name}</span>
              </div>
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4" />
                <span>{audit.audit_type?.replace('_', ' ')}</span>
              </div>
            </div>

            {audit.audit_score && (
              <div className="mt-4 pt-4 border-t">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Score:</span>
                  <span className="text-lg font-bold text-blue-600">{audit.audit_score}%</span>
                </div>
                {audit.audit_grade && (
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium mt-2 ${getGradeColor(audit.audit_grade)}`}>
                    {audit.audit_grade.replace('_', ' ')}
                  </span>
                )}
              </div>
            )}

            <div className="mt-4 flex gap-2">
              <Link
                href={`/dashboard/safety-audits/${audit.id}`}
                className="flex-1 text-center px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
              >
                View Details
              </Link>
            </div>
          </div>
        ))}
      </div>

      {filteredAudits.length === 0 && (
        <div className="text-center py-12">
          <ClipboardCheck className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No audits found</h3>
          <p className="text-gray-500">Schedule your first safety audit to get started</p>
        </div>
      )}
    </div>
  );
}
