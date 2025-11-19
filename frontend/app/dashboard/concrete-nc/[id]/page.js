'use client';

import { useState, useEffect } from 'react';
import { 
  AlertCircle, ArrowLeft, User, Calendar, MapPin, 
  Package, TestTube, TrendingDown, CheckCircle, Send,
  Building2, FileText, Clock, ArrowRight
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import Link from 'next/link';
import { format } from 'date-fns';

export default function ConcreteNCDetailsPage({ params }) {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [nc, setNc] = useState(null);
  const [vendorScore, setVendorScore] = useState(null);
  const [linkedRecords, setLinkedRecords] = useState({ batch: null, test: null });
  const [showTransferModal, setShowTransferModal] = useState(false);
  const [transferData, setTransferData] = useState({
    transfer_to: '',
    transfer_reason: '',
    transfer_comments: ''
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchNCDetails();
  }, [params.id]);

  const fetchNCDetails = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/concrete/nc/${params.id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) throw new Error('Failed to load NC details');

      const data = await response.json();
      setNc(data.nc);
      setVendorScore(data.vendor_score);
      setLinkedRecords({
        batch: data.linked_batch,
        test: data.linked_test
      });
    } catch (error) {
      console.error('Error loading NC:', error);
      toast.error('Failed to load NC details');
    } finally {
      setLoading(false);
    }
  };

  const handleTransfer = async () => {
    if (!transferData.transfer_to || !transferData.transfer_reason) {
      toast.error('Please fill in all required fields');
      return;
    }

    setSubmitting(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/concrete/nc/${params.id}/transfer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(transferData)
      });

      if (!response.ok) throw new Error('Failed to transfer NC');

      toast.success('NC transferred successfully');
      setShowTransferModal(false);
      fetchNCDetails();
    } catch (error) {
      console.error('Error transferring NC:', error);
      toast.error('Failed to transfer NC');
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/concrete/nc/${params.id}/close`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) throw new Error('Failed to close NC');

      toast.success('NC closed successfully');
      fetchNCDetails();
    } catch (error) {
      console.error('Error closing NC:', error);
      toast.error('Failed to close NC');
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
      under_investigation: 'yellow',
      vendor_response_pending: 'orange',
      resolved: 'green',
      closed: 'gray'
    };
    return colors[status] || 'gray';
  };

  const getScoreColor = (score) => {
    if (score >= 90) return 'green';
    if (score >= 70) return 'yellow';
    if (score >= 50) return 'orange';
    return 'red';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-16 h-16 border-4 border-gray-200 border-t-orange-600 rounded-full animate-spin" />
      </div>
    );
  }

  if (!nc) {
    return (
      <div className="p-6 text-center">
        <AlertCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">NC Not Found</h2>
        <p className="text-gray-600 mb-4">The requested non-conformance could not be found.</p>
        <Link href="/dashboard/concrete-nc" className="text-orange-600 hover:underline">
          Back to Concrete NCs
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
          href="/dashboard/concrete-nc"
          className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Concrete NCs
        </Link>

        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
              <AlertCircle className="w-6 h-6 text-orange-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{nc.nc_number}</h1>
              <p className="text-sm text-gray-600">Concrete Quality Non-Conformance</p>
            </div>
          </div>

          <div className="flex gap-2">
            <span className={`px-3 py-1 rounded-full text-sm font-medium bg-${severityColor}-100 text-${severityColor}-700`}>
              {nc.severity.charAt(0).toUpperCase() + nc.severity.slice(1)}
            </span>
            <span className={`px-3 py-1 rounded-full text-sm font-medium bg-${statusColor}-100 text-${statusColor}-700`}>
              {nc.status.replace(/_/g, ' ').charAt(0).toUpperCase() + nc.status.slice(1).replace(/_/g, ' ')}
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
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-600 mb-1">Issue Type</p>
                <p className="font-medium">{nc.issue_type}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Description</p>
                <p className="text-gray-700 whitespace-pre-wrap">{nc.description}</p>
              </div>
            </div>
          </div>

          {/* Test & Batch Linkage */}
          {(linkedRecords.batch || linkedRecords.test) && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <TestTube className="w-5 h-5 text-gray-600" />
                Linked Records
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {linkedRecords.batch && (
                  <div className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <Package className="w-5 h-5 text-blue-600" />
                      <h3 className="font-semibold">Concrete Batch</h3>
                    </div>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Batch No:</span>
                        <span className="font-medium">{linkedRecords.batch.batch_number}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Grade:</span>
                        <span className="font-medium">{linkedRecords.batch.grade}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Quantity:</span>
                        <span className="font-medium">{linkedRecords.batch.quantity} m³</span>
                      </div>
                      <Link 
                        href={`/dashboard/rmc-register/${linkedRecords.batch.id}`}
                        className="flex items-center gap-1 text-blue-600 hover:underline mt-2"
                      >
                        View Batch Details
                        <ArrowRight className="w-4 h-4" />
                      </Link>
                    </div>
                  </div>
                )}

                {linkedRecords.test && (
                  <div className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <TestTube className="w-5 h-5 text-purple-600" />
                      <h3 className="font-semibold">Cube Test</h3>
                    </div>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Test Date:</span>
                        <span className="font-medium">{format(new Date(linkedRecords.test.test_date), 'PP')}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Days:</span>
                        <span className="font-medium">{linkedRecords.test.age_days} days</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Result:</span>
                        <span className={`font-medium ${linkedRecords.test.status === 'pass' ? 'text-green-600' : 'text-red-600'}`}>
                          {linkedRecords.test.strength_achieved} MPa
                        </span>
                      </div>
                      <Link 
                        href={`/dashboard/cube-testing/${linkedRecords.test.id}`}
                        className="flex items-center gap-1 text-purple-600 hover:underline mt-2"
                      >
                        View Test Details
                        <ArrowRight className="w-4 h-4" />
                      </Link>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Vendor Information */}
          {nc.vendor_name && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Building2 className="w-5 h-5 text-gray-600" />
                Vendor Information
              </h2>
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Vendor Name</p>
                  <p className="font-medium">{nc.vendor_name}</p>
                </div>
                {vendorScore && (
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Quality Score</p>
                    <div className="flex items-center gap-3">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full bg-${getScoreColor(vendorScore.quality_score)}-500`}
                          style={{ width: `${vendorScore.quality_score}%` }}
                        />
                      </div>
                      <span className={`font-bold text-${getScoreColor(vendorScore.quality_score)}-600`}>
                        {vendorScore.quality_score}/100
                      </span>
                    </div>
                    <div className="mt-2 grid grid-cols-3 gap-2 text-xs">
                      <div>
                        <p className="text-gray-600">Total NCs</p>
                        <p className="font-semibold">{vendorScore.total_ncs}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Open NCs</p>
                        <p className="font-semibold text-red-600">{vendorScore.open_ncs}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Resolved</p>
                        <p className="font-semibold text-green-600">{vendorScore.resolved_ncs}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* NC Transfer History */}
          {nc.transferred_to && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <ArrowRight className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div className="text-sm">
                  <p className="font-medium text-blue-900 mb-1">NC Transferred</p>
                  <p className="text-blue-700 mb-2">
                    Transferred to: <span className="font-semibold">{nc.transferred_to}</span>
                  </p>
                  {nc.transfer_reason && (
                    <p className="text-blue-600">Reason: {nc.transfer_reason}</p>
                  )}
                </div>
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
                <p className="text-sm text-gray-600 mb-1">Target Resolution</p>
                <p className="font-medium">{format(new Date(nc.target_closure_date), 'PPP')}</p>
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
            <p className="text-sm text-gray-600">{nc.raised_by_role || 'Quality Engineer'}</p>
          </div>

          {/* Actions */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold mb-4">Actions</h2>
            <div className="space-y-2">
              {(nc.status === 'open' || nc.status === 'under_investigation') && (
                <button
                  onClick={() => setShowTransferModal(true)}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >
                  <ArrowRight className="w-4 h-4" />
                  Transfer NC
                </button>
              )}

              {nc.status === 'resolved' && (
                <button
                  onClick={handleClose}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
                >
                  <CheckCircle className="w-4 h-4" />
                  Close NC
                </button>
              )}

              {nc.status === 'closed' && (
                <div className="flex items-center justify-center gap-2 px-4 py-2 bg-gray-100 text-gray-600 rounded-lg">
                  <CheckCircle className="w-4 h-4" />
                  NC Closed
                </div>
              )}
            </div>
          </div>

          {/* Vendor Impact Notice */}
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
            <div className="flex gap-3">
              <TrendingDown className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-orange-800">
                <p className="font-medium mb-1">Vendor Scoring</p>
                <p>This NC impacts vendor quality rating. Resolution time and severity affect future vendor selection.</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Transfer Modal */}
      {showTransferModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full p-6">
            <h2 className="text-xl font-bold mb-4">Transfer NC</h2>
            
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Transfer To*
                </label>
                <select
                  value={transferData.transfer_to}
                  onChange={(e) => setTransferData({ ...transferData, transfer_to: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select department/person...</option>
                  <option value="vendor">RMC Vendor</option>
                  <option value="quality_team">Quality Team</option>
                  <option value="site_engineer">Site Engineer</option>
                  <option value="project_manager">Project Manager</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Reason for Transfer*
                </label>
                <select
                  value={transferData.transfer_reason}
                  onChange={(e) => setTransferData({ ...transferData, transfer_reason: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select reason...</option>
                  <option value="vendor_responsibility">Vendor Responsibility</option>
                  <option value="requires_investigation">Requires Further Investigation</option>
                  <option value="material_issue">Material Quality Issue</option>
                  <option value="design_related">Design Related</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Additional Comments
                </label>
                <textarea
                  value={transferData.transfer_comments}
                  onChange={(e) => setTransferData({ ...transferData, transfer_comments: e.target.value })}
                  rows={3}
                  placeholder="Add any additional notes..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setShowTransferModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
              >
                Cancel
              </button>
              <button
                onClick={handleTransfer}
                disabled={submitting}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
              >
                {submitting ? 'Transferring...' : 'Transfer NC'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
