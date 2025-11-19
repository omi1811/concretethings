'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, CheckCircle, XCircle, Clock, AlertTriangle, Download, Edit } from 'lucide-react';
import toast from 'react-hot-toast';

const PERMIT_TYPES = {
  'hot_work': 'Hot Work',
  'confined_space': 'Confined Space',
  'height_work': 'Height Work',
  'electrical': 'Electrical Work',
  'excavation': 'Excavation'
};

export default function PermitDetailsPage({ params }) {
  const router = useRouter();
  const [permit, setPermit] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [rejectReason, setRejectReason] = useState('');
  const [userRole, setUserRole] = useState('');

  useEffect(() => {
    fetchPermit();
    fetchUserRole();
  }, [params.id]);

  const fetchUserRole = () => {
    const role = localStorage.getItem('user_role') || 'contractor';
    setUserRole(role);
  };

  const fetchPermit = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/safety/permits/${params.id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setPermit(data.permit || data);
      } else {
        toast.error('Failed to load permit');
      }
    } catch (error) {
      console.error('Error fetching permit:', error);
      toast.error('Error loading permit');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    setActionLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/safety/permits/${params.id}/approve`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        toast.success('Permit approved successfully');
        setShowApprovalModal(false);
        fetchPermit();
      } else {
        const error = await response.json();
        toast.error(error.error || 'Failed to approve permit');
      }
    } catch (error) {
      console.error('Error approving permit:', error);
      toast.error('Error approving permit');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!rejectReason.trim()) {
      toast.error('Please provide a reason for rejection');
      return;
    }

    setActionLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/safety/permits/${params.id}/reject`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ reason: rejectReason })
      });

      if (response.ok) {
        toast.success('Permit rejected');
        setShowRejectModal(false);
        fetchPermit();
      } else {
        const error = await response.json();
        toast.error(error.error || 'Failed to reject permit');
      }
    } catch (error) {
      console.error('Error rejecting permit:', error);
      toast.error('Error rejecting permit');
    } finally {
      setActionLoading(false);
    }
  };

  const handleClose = async () => {
    if (!confirm('Are you sure you want to close this permit?')) return;

    setActionLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/safety/permits/${params.id}/close`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        toast.success('Permit closed successfully');
        fetchPermit();
      } else {
        const error = await response.json();
        toast.error(error.error || 'Failed to close permit');
      }
    } catch (error) {
      console.error('Error closing permit:', error);
      toast.error('Error closing permit');
    } finally {
      setActionLoading(false);
    }
  };

  const canApprove = () => {
    if (!permit) return false;
    if (permit.status === 'pending_engineer' && (userRole === 'site_engineer' || userRole === 'admin')) {
      return true;
    }
    if (permit.status === 'pending_safety' && (userRole === 'safety_officer' || userRole === 'admin')) {
      return true;
    }
    return false;
  };

  const canClose = () => {
    if (!permit) return false;
    return permit.status === 'active' || permit.status === 'approved';
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status) => {
    const colors = {
      'draft': 'bg-gray-100 text-gray-800',
      'pending_engineer': 'bg-yellow-100 text-yellow-800',
      'pending_safety': 'bg-orange-100 text-orange-800',
      'approved': 'bg-green-100 text-green-800',
      'rejected': 'bg-red-100 text-red-800',
      'active': 'bg-blue-100 text-blue-800',
      'closed': 'bg-gray-100 text-gray-800',
      'expired': 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!permit) {
    return (
      <div className="p-6 text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Permit not found</h2>
        <Link href="/dashboard/ptw" className="text-blue-600 hover:underline">
          Back to Permits
        </Link>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <Link
          href="/dashboard/ptw"
          className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Permits
        </Link>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Permit #{permit.permit_number || 'Draft'}
            </h1>
            <p className="text-gray-600">{PERMIT_TYPES[permit.permit_type]}</p>
          </div>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(permit.status)}`}>
            {permit.status?.replace('_', ' ').toUpperCase()}
          </span>
        </div>
      </div>

      {/* Action Buttons */}
      {canApprove() && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6 flex items-start gap-4">
          <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="font-medium text-yellow-900 mb-1">Approval Required</h3>
            <p className="text-sm text-yellow-700 mb-3">
              This permit is pending your approval as {userRole === 'site_engineer' ? 'Site Engineer' : 'Safety Officer'}.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowApprovalModal(true)}
                disabled={actionLoading}
                className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
              >
                <CheckCircle className="w-4 h-4" />
                Approve Permit
              </button>
              <button
                onClick={() => setShowRejectModal(true)}
                disabled={actionLoading}
                className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
              >
                <XCircle className="w-4 h-4" />
                Reject Permit
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Work Details */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Work Details</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Work Description</label>
            <p className="text-gray-900">{permit.work_description || 'N/A'}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Location</label>
            <p className="text-gray-900">{permit.location || 'N/A'}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Valid From</label>
            <p className="text-gray-900">{formatDate(permit.valid_from)}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Valid Until</label>
            <p className="text-gray-900">{formatDate(permit.valid_until)}</p>
          </div>
        </div>
      </div>

      {/* Contractor Details */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Contractor Details</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Contractor Name</label>
            <p className="text-gray-900">{permit.contractor_name || 'N/A'}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Contact Number</label>
            <p className="text-gray-900">{permit.contractor_contact || 'N/A'}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">License Number</label>
            <p className="text-gray-900">{permit.contractor_license || 'N/A'}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Number of Workers</label>
            <p className="text-gray-900">{permit.number_of_workers || 'N/A'}</p>
          </div>
        </div>
      </div>

      {/* Safety Requirements */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Safety Requirements</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Equipment Required</label>
            <p className="text-gray-900 whitespace-pre-wrap">{permit.equipment_required || 'N/A'}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Hazards Identified</label>
            <p className="text-gray-900 whitespace-pre-wrap">{permit.hazards_identified || 'N/A'}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Control Measures</label>
            <p className="text-gray-900 whitespace-pre-wrap">{permit.control_measures || 'N/A'}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Emergency Procedures</label>
            <p className="text-gray-900 whitespace-pre-wrap">{permit.emergency_procedures || 'N/A'}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">PPE Required</label>
            <p className="text-gray-900">{permit.ppe_required || 'N/A'}</p>
          </div>
        </div>
      </div>

      {/* Approval History */}
      {(permit.engineer_approved_at || permit.safety_approved_at) && (
        <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Approval History</h2>
          <div className="space-y-3">
            {permit.engineer_approved_at && (
              <div className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                <div>
                  <p className="font-medium text-gray-900">Site Engineer Approved</p>
                  <p className="text-sm text-gray-500">{formatDate(permit.engineer_approved_at)}</p>
                  {permit.engineer_signature && <p className="text-xs text-gray-400 mt-1">Signature: {permit.engineer_signature}</p>}
                </div>
              </div>
            )}
            {permit.safety_approved_at && (
              <div className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                <div>
                  <p className="font-medium text-gray-900">Safety Officer Approved</p>
                  <p className="text-sm text-gray-500">{formatDate(permit.safety_approved_at)}</p>
                  {permit.safety_signature && <p className="text-xs text-gray-400 mt-1">Signature: {permit.safety_signature}</p>}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Close Button */}
      {canClose() && (
        <div className="flex justify-end">
          <button
            onClick={handleClose}
            disabled={actionLoading}
            className="inline-flex items-center gap-2 px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors disabled:opacity-50"
          >
            <CheckCircle className="w-4 h-4" />
            Close Permit
          </button>
        </div>
      )}

      {/* Approval Modal */}
      {showApprovalModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Confirm Approval</h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to approve this permit? This action cannot be undone.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowApprovalModal(false)}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleApprove}
                disabled={actionLoading}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
              >
                {actionLoading ? 'Approving...' : 'Approve'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Reject Modal */}
      {showRejectModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Reject Permit</h3>
            <p className="text-gray-600 mb-4">
              Please provide a reason for rejecting this permit:
            </p>
            <textarea
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 mb-4"
              placeholder="Enter rejection reason..."
            />
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowRejectModal(false);
                  setRejectReason('');
                }}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleReject}
                disabled={actionLoading || !rejectReason.trim()}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
              >
                {actionLoading ? 'Rejecting...' : 'Reject'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
