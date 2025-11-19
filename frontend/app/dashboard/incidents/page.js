'use client';

import { useState, useEffect } from 'react';
import { 
  AlertTriangle, Plus, Eye, Edit, FileText, Search,
  Filter, Calendar, User, MapPin, Clock, AlertOctagon
} from 'lucide-react';
import { apiRequest } from '@/lib/api-optimized';
import toast from 'react-hot-toast';
import Link from 'next/link';
import { format } from 'date-fns';

export default function IncidentsPage() {
  const [loading, setLoading] = useState(true);
  const [incidents, setIncidents] = useState([]);
  const [filteredIncidents, setFilteredIncidents] = useState([]);
  const [statusFilter, setStatusFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const incidentTypes = [
    'INJURY', 'NEAR_MISS', 'PROPERTY_DAMAGE', 'ENVIRONMENTAL',
    'EQUIPMENT_FAILURE', 'FIRE', 'CHEMICAL_SPILL', 'FALL_FROM_HEIGHT',
    'ELECTRIC_SHOCK', 'VEHICLE_ACCIDENT', 'FATALITY'
  ];

  const incidentStatuses = [
    'reported', 'under_investigation', 'investigation_complete',
    'corrective_actions_pending', 'closed'
  ];

  useEffect(() => {
    fetchIncidents();
  }, []);

  useEffect(() => {
    filterIncidents();
  }, [incidents, statusFilter, typeFilter, searchTerm]);

  const fetchIncidents = async () => {
    try {
      const projectId = localStorage.getItem('activeProjectId');
      if (!projectId) {
        toast.error('Please select a project');
        return;
      }

      const data = await apiRequest(`/api/incidents?project_id=${projectId}`);
      setIncidents(data.incidents || []);
    } catch (error) {
      console.error('Failed to load incidents:', error);
      toast.error('Failed to load incidents');
    } finally {
      setLoading(false);
    }
  };

  const filterIncidents = () => {
    let filtered = [...incidents];

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(inc => inc.incident_status === statusFilter);
    }

    // Type filter
    if (typeFilter !== 'all') {
      filtered = filtered.filter(inc => inc.incident_type === typeFilter);
    }

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(inc =>
        inc.incident_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        inc.incident_description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        inc.incident_location?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    setFilteredIncidents(filtered);
  };

  const getSeverityColor = (severity) => {
    const colors = {
      1: 'bg-blue-100 text-blue-800 border-blue-200',
      2: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      3: 'bg-orange-100 text-orange-800 border-orange-200',
      4: 'bg-red-100 text-red-800 border-red-200',
      5: 'bg-purple-100 text-purple-800 border-purple-200'
    };
    return colors[severity] || colors[3];
  };

  const getStatusColor = (status) => {
    const colors = {
      'reported': 'bg-gray-100 text-gray-800',
      'under_investigation': 'bg-blue-100 text-blue-800',
      'investigation_complete': 'bg-yellow-100 text-yellow-800',
      'corrective_actions_pending': 'bg-orange-100 text-orange-800',
      'closed': 'bg-green-100 text-green-800'
    };
    return colors[status] || colors.reported;
  };

  const getTypeIcon = (type) => {
    const icons = {
      'INJURY': '🤕',
      'NEAR_MISS': '⚠️',
      'PROPERTY_DAMAGE': '🏗️',
      'ENVIRONMENTAL': '🌍',
      'EQUIPMENT_FAILURE': '⚙️',
      'FIRE': '🔥',
      'CHEMICAL_SPILL': '☣️',
      'FALL_FROM_HEIGHT': '⬇️',
      'ELECTRIC_SHOCK': '⚡',
      'VEHICLE_ACCIDENT': '🚗',
      'FATALITY': '💀'
    };
    return icons[type] || '📋';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading incidents...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <AlertTriangle className="w-8 h-8 text-red-600" />
            Incident Investigation
          </h1>
          <p className="text-gray-600 mt-1">Report and investigate workplace incidents</p>
        </div>
        <Link
          href="/dashboard/incidents/new"
          className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          <Plus className="w-5 h-5" />
          Report Incident
        </Link>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Total Incidents</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{incidents.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Open</p>
          <p className="text-2xl font-bold text-blue-600 mt-1">
            {incidents.filter(i => i.incident_status !== 'closed').length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Near Misses</p>
          <p className="text-2xl font-bold text-yellow-600 mt-1">
            {incidents.filter(i => i.incident_type === 'NEAR_MISS').length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Injuries</p>
          <p className="text-2xl font-bold text-orange-600 mt-1">
            {incidents.filter(i => i.incident_type === 'INJURY').length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">This Month</p>
          <p className="text-2xl font-bold text-purple-600 mt-1">
            {incidents.filter(i => {
              const incDate = new Date(i.incident_date);
              const now = new Date();
              return incDate.getMonth() === now.getMonth() && incDate.getFullYear() === now.getFullYear();
            }).length}
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search incidents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Status Filter */}
          <div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Statuses</option>
              {incidentStatuses.map(status => (
                <option key={status} value={status}>
                  {status.replace(/_/g, ' ').toUpperCase()}
                </option>
              ))}
            </select>
          </div>

          {/* Type Filter */}
          <div>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Types</option>
              {incidentTypes.map(type => (
                <option key={type} value={type}>
                  {type.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </div>

          {/* Results Count */}
          <div className="flex items-center justify-end text-sm text-gray-600">
            Showing {filteredIncidents.length} of {incidents.length} incidents
          </div>
        </div>
      </div>

      {/* Incidents List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {filteredIncidents.length === 0 ? (
          <div className="text-center py-12">
            <AlertOctagon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No incidents found</h3>
            <p className="text-gray-500">
              {searchTerm || statusFilter !== 'all' || typeFilter !== 'all'
                ? 'Try adjusting your filters'
                : 'No incidents have been reported yet'}
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {filteredIncidents.map((incident) => (
              <div
                key={incident.id}
                className="p-6 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start justify-between">
                  {/* Main Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-3">
                      <span className="text-2xl">{getTypeIcon(incident.incident_type)}</span>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">
                          {incident.incident_number}
                        </h3>
                        <p className="text-sm text-gray-500">
                          {incident.incident_type?.replace(/_/g, ' ')}
                        </p>
                      </div>
                    </div>

                    <p className="text-gray-700 mb-3 line-clamp-2">
                      {incident.incident_description}
                    </p>

                    {/* Meta Information */}
                    <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {format(new Date(incident.incident_date), 'dd MMM yyyy')}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        {incident.incident_time}
                      </span>
                      <span className="flex items-center gap-1">
                        <MapPin className="w-4 h-4" />
                        {incident.incident_location}
                      </span>
                      <span className="flex items-center gap-1">
                        <User className="w-4 h-4" />
                        {incident.reported_by_name}
                      </span>
                    </div>

                    {/* Badges */}
                    <div className="flex flex-wrap items-center gap-2 mt-3">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getSeverityColor(incident.severity)}`}>
                        Severity {incident.severity}
                      </span>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(incident.incident_status)}`}>
                        {incident.incident_status?.replace(/_/g, ' ').toUpperCase()}
                      </span>
                      {incident.reportable_to_authority && (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          REPORTABLE
                        </span>
                      )}
                      {incident.lost_time_days > 0 && (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                          {incident.lost_time_days} Lost Days
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 ml-4">
                    <Link
                      href={`/dashboard/incidents/${incident.id}`}
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                      title="View Details"
                    >
                      <Eye className="w-5 h-5" />
                    </Link>
                    <Link
                      href={`/dashboard/incidents/${incident.id}/edit`}
                      className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                      title="Edit"
                    >
                      <Edit className="w-5 h-5" />
                    </Link>
                    <button
                      onClick={() => {/* Generate Report */}}
                      className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                      title="Generate Report"
                    >
                      <FileText className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
