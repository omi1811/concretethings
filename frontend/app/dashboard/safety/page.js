'use client';

import { useState, useEffect } from 'react';
import { 
  Shield, AlertTriangle, CheckCircle2, Activity, 
  FileWarning, Users, TrendingUp, Clock, Calendar,
  HardHat, ClipboardCheck, AlertOctagon, BarChart3
} from 'lucide-react';
import { apiRequest } from '@/lib/api-optimized';
import toast from 'react-hot-toast';
import Link from 'next/link';
import { format } from 'date-fns';

export default function SafetyDashboard() {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalIncidents: 0,
    openIncidents: 0,
    nearMisses: 0,
    safetyScore: 0,
    daysWithoutIncident: 0,
    lostTimeDays: 0,
    upcomingAudits: 0,
    ppeCompliance: 0,
    criticalActions: 0
  });
  const [recentIncidents, setRecentIncidents] = useState([]);
  const [upcomingAudits, setUpcomingAudits] = useState([]);
  const [monthlyTrend, setMonthlyTrend] = useState([]);

  useEffect(() => {
    fetchSafetyData();
  }, []);

  const fetchSafetyData = async () => {
    try {
      const projectId = localStorage.getItem('activeProjectId');
      if (!projectId) {
        toast.error('Please select a project');
        return;
      }

      // Fetch safety statistics
      const [incidentsRes, auditsRes] = await Promise.all([
        apiRequest(`/api/incidents/dashboard?project_id=${projectId}`),
        apiRequest(`/api/safety-audits?project_id=${projectId}&status=scheduled`)
      ]);

      // Update stats
      setStats({
        totalIncidents: incidentsRes.statistics?.total_incidents || 0,
        openIncidents: incidentsRes.statistics?.open_incidents || 0,
        nearMisses: incidentsRes.statistics?.by_type?.NEAR_MISS || 0,
        safetyScore: calculateSafetyScore(incidentsRes.statistics),
        daysWithoutIncident: incidentsRes.statistics?.days_since_last_incident || 0,
        lostTimeDays: incidentsRes.statistics?.total_lost_days || 0,
        upcomingAudits: auditsRes.audits?.length || 0,
        ppeCompliance: 85, // TODO: Calculate from PPE API
        criticalActions: incidentsRes.statistics?.open_corrective_actions || 0
      });

      setRecentIncidents(incidentsRes.recent_incidents || []);
      setUpcomingAudits(auditsRes.audits?.slice(0, 5) || []);

    } catch (error) {
      console.error('Failed to load safety data:', error);
      toast.error('Failed to load safety data');
    } finally {
      setLoading(false);
    }
  };

  const calculateSafetyScore = (statistics) => {
    if (!statistics) return 0;
    
    // Simple safety score calculation (customize as needed)
    const incidentPenalty = (statistics.total_incidents || 0) * 5;
    const nearMissPenalty = (statistics.by_type?.NEAR_MISS || 0) * 2;
    const fatalityPenalty = (statistics.by_type?.FATALITY || 0) * 50;
    
    const baseScore = 100;
    const finalScore = Math.max(0, baseScore - incidentPenalty - nearMissPenalty - fatalityPenalty);
    
    return Math.round(finalScore);
  };

  const getSeverityColor = (severity) => {
    const colors = {
      1: 'bg-blue-100 text-blue-800',
      2: 'bg-yellow-100 text-yellow-800',
      3: 'bg-orange-100 text-orange-800',
      4: 'bg-red-100 text-red-800',
      5: 'bg-purple-100 text-purple-800'
    };
    return colors[severity] || colors[3];
  };

  const getScoreColor = (score) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    if (score >= 50) return 'text-orange-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading safety data...</p>
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
            <Shield className="w-8 h-8 text-blue-600" />
            Safety Management Dashboard
          </h1>
          <p className="text-gray-600 mt-1">Monitor workplace safety and compliance</p>
        </div>
        <div className="flex gap-3">
          <Link
            href="/dashboard/incidents/new"
            className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            <AlertTriangle className="w-5 h-5" />
            Report Incident
          </Link>
          <Link
            href="/dashboard/safety-audits/new"
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <ClipboardCheck className="w-5 h-5" />
            Schedule Audit
          </Link>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Safety Score */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">Safety Score</p>
              <p className={`text-4xl font-bold mt-2 ${getScoreColor(stats.safetyScore)}`}>
                {stats.safetyScore}
              </p>
              <p className="text-xs text-gray-500 mt-1">out of 100</p>
            </div>
            <div className={`p-3 rounded-full ${stats.safetyScore >= 70 ? 'bg-green-100' : 'bg-red-100'}`}>
              <Shield className={`w-8 h-8 ${stats.safetyScore >= 70 ? 'text-green-600' : 'text-red-600'}`} />
            </div>
          </div>
        </div>

        {/* Days Without Incident */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">Days Without Incident</p>
              <p className="text-4xl font-bold text-green-600 mt-2">
                {stats.daysWithoutIncident}
              </p>
              <p className="text-xs text-gray-500 mt-1">Keep up the good work!</p>
            </div>
            <div className="p-3 rounded-full bg-green-100">
              <CheckCircle2 className="w-8 h-8 text-green-600" />
            </div>
          </div>
        </div>

        {/* Total Incidents */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">Total Incidents</p>
              <p className="text-4xl font-bold text-red-600 mt-2">
                {stats.totalIncidents}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {stats.openIncidents} open
              </p>
            </div>
            <div className="p-3 rounded-full bg-red-100">
              <AlertTriangle className="w-8 h-8 text-red-600" />
            </div>
          </div>
        </div>

        {/* Near Misses */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">Near Misses</p>
              <p className="text-4xl font-bold text-yellow-600 mt-2">
                {stats.nearMisses}
              </p>
              <p className="text-xs text-gray-500 mt-1">This month</p>
            </div>
            <div className="p-3 rounded-full bg-yellow-100">
              <FileWarning className="w-8 h-8 text-yellow-600" />
            </div>
          </div>
        </div>

        {/* Lost Time Days */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">Lost Time Days</p>
              <p className="text-4xl font-bold text-orange-600 mt-2">
                {stats.lostTimeDays}
              </p>
              <p className="text-xs text-gray-500 mt-1">This year</p>
            </div>
            <div className="p-3 rounded-full bg-orange-100">
              <Clock className="w-8 h-8 text-orange-600" />
            </div>
          </div>
        </div>

        {/* PPE Compliance */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">PPE Compliance</p>
              <p className="text-4xl font-bold text-blue-600 mt-2">
                {stats.ppeCompliance}%
              </p>
              <p className="text-xs text-gray-500 mt-1">Current rate</p>
            </div>
            <div className="p-3 rounded-full bg-blue-100">
              <HardHat className="w-8 h-8 text-blue-600" />
            </div>
          </div>
        </div>

        {/* Upcoming Audits */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">Upcoming Audits</p>
              <p className="text-4xl font-bold text-purple-600 mt-2">
                {stats.upcomingAudits}
              </p>
              <p className="text-xs text-gray-500 mt-1">Next 30 days</p>
            </div>
            <div className="p-3 rounded-full bg-purple-100">
              <ClipboardCheck className="w-8 h-8 text-purple-600" />
            </div>
          </div>
        </div>

        {/* Critical Actions */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">Critical Actions</p>
              <p className="text-4xl font-bold text-red-600 mt-2">
                {stats.criticalActions}
              </p>
              <p className="text-xs text-gray-500 mt-1">Pending</p>
            </div>
            <div className="p-3 rounded-full bg-red-100">
              <AlertOctagon className="w-8 h-8 text-red-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Quick Access Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Link
          href="/dashboard/incidents"
          className="bg-gradient-to-br from-red-500 to-red-600 text-white rounded-lg p-6 hover:shadow-lg transition-shadow"
        >
          <AlertTriangle className="w-10 h-10 mb-3" />
          <h3 className="font-semibold text-lg">Incident Reports</h3>
          <p className="text-sm opacity-90 mt-1">View and manage incidents</p>
        </Link>

        <Link
          href="/dashboard/safety-audits"
          className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-lg p-6 hover:shadow-lg transition-shadow"
        >
          <ClipboardCheck className="w-10 h-10 mb-3" />
          <h3 className="font-semibold text-lg">Safety Audits</h3>
          <p className="text-sm opacity-90 mt-1">Schedule and conduct audits</p>
        </Link>

        <Link
          href="/dashboard/ppe"
          className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-lg p-6 hover:shadow-lg transition-shadow"
        >
          <HardHat className="w-10 h-10 mb-3" />
          <h3 className="font-semibold text-lg">PPE Tracking</h3>
          <p className="text-sm opacity-90 mt-1">Manage PPE issuance</p>
        </Link>

        <Link
          href="/dashboard/geofence"
          className="bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-lg p-6 hover:shadow-lg transition-shadow"
        >
          <Activity className="w-10 h-10 mb-3" />
          <h3 className="font-semibold text-lg">Geofence</h3>
          <p className="text-sm opacity-90 mt-1">Location verification</p>
        </Link>
      </div>

      {/* Recent Incidents and Upcoming Audits */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Incidents */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-600" />
              Recent Incidents
            </h2>
            <Link
              href="/dashboard/incidents"
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              View All →
            </Link>
          </div>

          <div className="space-y-3">
            {recentIncidents.length === 0 ? (
              <p className="text-center text-gray-500 py-8">No recent incidents</p>
            ) : (
              recentIncidents.map((incident) => (
                <div
                  key={incident.id}
                  className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-medium text-gray-900">
                          {incident.incident_number}
                        </span>
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getSeverityColor(incident.severity)}`}>
                          Severity {incident.severity}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 line-clamp-2">
                        {incident.incident_description}
                      </p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {format(new Date(incident.incident_date), 'dd MMM yyyy')}
                        </span>
                        <span className="flex items-center gap-1">
                          <Users className="w-3 h-3" />
                          {incident.reported_by_name}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Upcoming Audits */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <ClipboardCheck className="w-5 h-5 text-blue-600" />
              Upcoming Audits
            </h2>
            <Link
              href="/dashboard/safety-audits"
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              View All →
            </Link>
          </div>

          <div className="space-y-3">
            {upcomingAudits.length === 0 ? (
              <p className="text-center text-gray-500 py-8">No upcoming audits</p>
            ) : (
              upcomingAudits.map((audit) => (
                <div
                  key={audit.id}
                  className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-medium text-gray-900">
                          {audit.audit_title}
                        </span>
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                          {audit.audit_type}
                        </span>
                      </div>
                      <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {format(new Date(audit.scheduled_date), 'dd MMM yyyy')}
                        </span>
                        <span className="flex items-center gap-1">
                          <Users className="w-3 h-3" />
                          {audit.lead_auditor_name}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
