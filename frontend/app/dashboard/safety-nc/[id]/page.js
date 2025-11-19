'use client';

import { useState, useEffect } from 'react';
import { 
  MessageSquareWarning, ArrowLeft, User, Calendar, MapPin, 
  AlertTriangle, CheckCircle, Clock, FileText, Upload, Send
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import Link from 'next/link';
import { format } from 'date-fns';

export default function SafetyNCDetailsPage({ params }) {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [nc, setNc] = useState(null);
  const [showResponseModal, setShowResponseModal] = useState(false);
  const [responseData, setResponseData] = useState({
    response_description: '',
    corrective_action_taken: '',
    evidence_photos: []
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchNCDetails();
  }, [params.id]);

  const fetchNCDetails = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/safety/nc/${params.id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) throw new Error('Failed to load NC details');

      const data = await response.json();
      setNc(data.nc);
    } catch (error) {
      console.error('Error loading NC:', error);
      toast.error('Failed to load NC details');
    } finally {
      setLoading(false);
    }
  };

  const handleResponse = async () => {
    if (!responseData.response_description || !responseData.corrective_action_taken) {
      toast.error('Please fill in all required fields');
      return;
    }

    setSubmitting(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/safety/nc/${params.id}/response`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(responseData)
      });

      if (!response.ok) throw new Error('Failed to submit response');

      toast.success('Response submitted successfully');
      setShowResponseModal(false);
      fetchNCDetails();
    } catch (error) {
      console.error('Error submitting response:', error);
      toast.error('Failed to submit response');
    } finally {
      setSubmitting(false);
    }
  };

  const handleVerify = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/safety/nc/${params.id}/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ verified: true })
      });

      if (!response.ok) throw new Error('Failed to verify NC closure');

      toast.success('NC closure verified successfully');
      fetchNCDetails();
    } catch (error) {
      console.error('Error verifying NC:', error);
      toast.error('Failed to verify NC closure');
    }
  };

  const getSeverityColor = (severity) => {
    const colors = {
      minor: 'yellow',
      major: 'orange',
      critical: 'red'
    };
    return colors[severity] || 'gray';
  };

  const getStatusColor = (status) => {
    const colors = {
      open: 'red',
      in_progress: 'yellow',
      pending_verification: 'blue',
      closed: 'green'
    };
    return colors[status] || 'gray';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-16 h-16 border-4 border-gray-200 border-t-red-600 rounded-full animate-spin" />
      </div>
    );
  }

  if (!nc) {
    return (
      <div className="p-6 text-center">
        <AlertTriangle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">NC Not Found</h2>
        <p className="text-gray-600 mb-4">The requested non-conformance could not be found.</p>
        <Link href="/dashboard/safety-nc" className="text-red-600 hover:underline">
          Back to Safety NCs
        </Link>
      </div>
    );
  }

  const severityColor = getSeverityColor(nc.severity);
  const statusColor = getStatusColor(nc.status);

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <Link 
          href="/dashboard/safety-nc"
          className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Safety NCs
        </Link>

        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
              <MessageSquareWarning className="w-6 h-6 text-red-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{nc.nc_number}</h1>
              <p className="text-sm text-gray-600">Safety Non-Conformance Details</p>
            </div>
          </div>

          <div className="flex gap-2">
            <span className={`px-3 py-1 rounded-full text-sm font-medium bg-${severityColor}-100 text-${severityColor}-700`}>
              {nc.severity.charAt(0).toUpperCase() + nc.severity.slice(1)}
            </span>
            <span className={`px-3 py-1 rounded-full text-sm font-medium bg-${statusColor}-100 text-${statusColor}-700`}>
              {nc.status.replace('_', ' ').charAt(0).toUpperCase() + nc.status.slice(1).replace('_', ' ')}
            </span>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Main Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* NC Description */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5 text-gray-600" />
              NC Description
            </h2>
            <p className="text-gray-700 whitespace-pre-wrap">{nc.description}</p>
          </div>

          {/* Location & Details */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <MapPin className="w-5 h-5 text-gray-600" />
              Location & Details
            </h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600 mb-1">Location</p>
                <p className="font-medium">{nc.location}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Category</p>
                <p className="font-medium">{nc.category || 'Not specified'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Contractor</p>
                <p className="font-medium">{nc.contractor_name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Severity</p>
                <span className={`px-2 py-1 rounded-full text-xs font-medium bg-${severityColor}-100 text-${severityColor}-700`}>
                  {nc.severity.toUpperCase()}
                </span>
              </div>
            </div>
          </div>

          {/* Corrective Action Required */}
          {nc.corrective_action_required && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold mb-4">Corrective Action Required</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{nc.corrective_action_required}</p>
            </div>
          )}

          {/* Contractor Response */}
          {nc.response_description && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Send className="w-5 h-5 text-blue-600" />
                Contractor Response
              </h2>
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Response Description</p>
                  <p className="text-gray-700 whitespace-pre-wrap">{nc.response_description}</p>
                </div>
                {nc.corrective_action_taken && (
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Corrective Action Taken</p>
                    <p className="text-gray-700 whitespace-pre-wrap">{nc.corrective_action_taken}</p>
                  </div>
                )}
                {nc.response_date && (
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Response Date</p>
                    <p className="text-gray-700">{format(new Date(nc.response_date), 'PPP')}</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right Column - Timeline & Actions */}
        <div className="space-y-6">
          {/* Timeline */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Calendar className="w-5 h-5 text-gray-600" />
              Timeline
            </h2>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-600 mb-1">Raised Date</p>
                <p className="font-medium">{format(new Date(nc.raised_date), 'PPP')}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Due Date</p>
                <p className="font-medium">{format(new Date(nc.due_date), 'PPP')}</p>
              </div>
              {nc.closed_date && (
                <div>
                  <p className="text-sm text-gray-600 mb-1">Closed Date</p>
                  <p className="font-medium">{format(new Date(nc.closed_date), 'PPP')}</p>
                </div>
              )}
            </div>
          </div>

          {/* Raised By */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <User className="w-5 h-5 text-gray-600" />
              Raised By
            </h2>
            <p className="font-medium">{nc.raised_by_name || 'Unknown'}</p>
            <p className="text-sm text-gray-600">{nc.raised_by_role || 'Safety Officer'}</p>
          </div>

          {/* Actions */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold mb-4">Actions</h2>
            <div className="space-y-2">
              {nc.status === 'open' && (
                <button
                  onClick={() => setShowResponseModal(true)}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >
                  <Send className="w-4 h-4" />
                  Submit Response
                </button>
              )}

              {nc.status === 'in_progress' && (
                <button
                  onClick={() => setShowResponseModal(true)}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >
                  <Upload className="w-4 h-4" />
                  Update Response
                </button>
              )}

              {nc.status === 'pending_verification' && (
                <button
                  onClick={handleVerify}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
                >
                  <CheckCircle className="w-4 h-4" />
                  Verify & Close NC
                </button>
              )}

              {nc.status === 'closed' && (
                <div className="flex items-center justify-center gap-2 px-4 py-2 bg-green-100 text-green-700 rounded-lg">
                  <CheckCircle className="w-4 h-4" />
                  NC Closed
                </div>
              )}
            </div>
          </div>

          {/* Contractor Scoring Impact */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex gap-3">
              <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-yellow-800">
                <p className="font-medium mb-1">Scoring Impact</p>
                <p>This NC affects contractor safety compliance score. Timely resolution improves rating.</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Response Modal */}
      {showResponseModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full p-6">
            <h2 className="text-xl font-bold mb-4">Submit Response to NC</h2>
            
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Response Description*
                </label>
                <textarea
                  value={responseData.response_description}
                  onChange={(e) => setResponseData({ ...responseData, response_description: e.target.value })}
                  rows={4}
                  placeholder="Explain what caused the NC and current status..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Corrective Action Taken*
                </label>
                <textarea
                  value={responseData.corrective_action_taken}
                  onChange={(e) => setResponseData({ ...responseData, corrective_action_taken: e.target.value })}
                  rows={4}
                  placeholder="Detail the actions taken to resolve the issue..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setShowResponseModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
              >
                Cancel
              </button>
              <button
                onClick={handleResponse}
                disabled={submitting}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
              >
                {submitting ? 'Submitting...' : 'Submit Response'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
