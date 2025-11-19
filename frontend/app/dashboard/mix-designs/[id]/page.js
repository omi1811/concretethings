'use client';

import { useState, useEffect } from 'react';
import { 
  Beaker, ArrowLeft, User, Calendar, CheckCircle, 
  AlertCircle, Edit2, FileText, Package, Scale,
  Droplet, ThermometerSun, Clock, Shield, Info
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import Link from 'next/link';
import { format } from 'date-fns';

export default function MixDesignDetailsPage({ params }) {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [mixDesign, setMixDesign] = useState(null);
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  const [showEditMode, setShowEditMode] = useState(false);
  const [approvalComments, setApprovalComments] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchMixDesignDetails();
  }, [params.id]);

  const fetchMixDesignDetails = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/mix-designs/${params.id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) throw new Error('Failed to load mix design details');

      const data = await response.json();
      setMixDesign(data.mix_design);
    } catch (error) {
      console.error('Error loading mix design:', error);
      toast.error('Failed to load mix design details');
    } finally {
      setLoading(false);
    }
  };

  const handleApproval = async (approved) => {
    if (approved && !approvalComments) {
      toast.error('Please add approval comments');
      return;
    }

    setSubmitting(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/mix-designs/${params.id}/approve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          approved,
          comments: approvalComments
        })
      });

      if (!response.ok) throw new Error('Failed to submit approval');

      toast.success(approved ? 'Mix design approved successfully' : 'Mix design rejected');
      setShowApprovalModal(false);
      fetchMixDesignDetails();
    } catch (error) {
      console.error('Error submitting approval:', error);
      toast.error('Failed to submit approval');
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      draft: 'gray',
      pending_approval: 'yellow',
      approved: 'green',
      rejected: 'red',
      revised: 'blue'
    };
    return colors[status] || 'gray';
  };

  const getComplianceIcon = (compliant) => {
    return compliant ? (
      <CheckCircle className="w-5 h-5 text-green-600" />
    ) : (
      <AlertCircle className="w-5 h-5 text-red-600" />
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-16 h-16 border-4 border-gray-200 border-t-blue-600 rounded-full animate-spin" />
      </div>
    );
  }

  if (!mixDesign) {
    return (
      <div className="p-6 text-center">
        <Beaker className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Mix Design Not Found</h2>
        <p className="text-gray-600 mb-4">The requested mix design could not be found.</p>
        <Link href="/dashboard/mix-designs" className="text-blue-600 hover:underline">
          Back to Mix Designs
        </Link>
      </div>
    );
  }

  const statusColor = getStatusColor(mixDesign.status);

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <Link 
          href="/dashboard/mix-designs"
          className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Mix Designs
        </Link>

        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Beaker className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{mixDesign.mix_id}</h1>
              <p className="text-sm text-gray-600">Concrete Mix Design Details</p>
            </div>
          </div>

          <div className="flex gap-2 items-center">
            <span className={`px-3 py-1 rounded-full text-sm font-medium bg-${statusColor}-100 text-${statusColor}-700`}>
              {mixDesign.status.replace(/_/g, ' ').charAt(0).toUpperCase() + mixDesign.status.slice(1).replace(/_/g, ' ')}
            </span>
            {mixDesign.status === 'approved' && (
              <button
                onClick={() => setShowEditMode(true)}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition"
                title="Edit Mix Design"
              >
                <Edit2 className="w-5 h-5" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Mix Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Information */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5 text-gray-600" />
              Mix Specifications
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-600 mb-1">Concrete Grade</p>
                <p className="font-bold text-lg">{mixDesign.grade}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Design Strength</p>
                <p className="font-medium">{mixDesign.design_strength} MPa</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">W/C Ratio</p>
                <p className="font-medium">{mixDesign.water_cement_ratio}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Slump</p>
                <p className="font-medium">{mixDesign.slump} mm</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Max Aggregate</p>
                <p className="font-medium">{mixDesign.max_aggregate_size} mm</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Exposure</p>
                <p className="font-medium">{mixDesign.exposure_condition || 'Normal'}</p>
              </div>
            </div>
          </div>

          {/* Material Proportions */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Package className="w-5 h-5 text-gray-600" />
              Material Proportions (per m³)
            </h2>
            
            <div className="space-y-4">
              {/* Cement */}
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <Scale className="w-5 h-5 text-gray-600" />
                  <div>
                    <p className="font-medium">Cement</p>
                    <p className="text-sm text-gray-600">{mixDesign.cement_type || 'OPC 43'}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-bold text-lg">{mixDesign.cement_content} kg</p>
                </div>
              </div>

              {/* Water */}
              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <Droplet className="w-5 h-5 text-blue-600" />
                  <div>
                    <p className="font-medium">Water</p>
                    <p className="text-sm text-gray-600">Potable water</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-bold text-lg">{mixDesign.water_content} L</p>
                </div>
              </div>

              {/* Fine Aggregate */}
              <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <Package className="w-5 h-5 text-yellow-600" />
                  <div>
                    <p className="font-medium">Fine Aggregate</p>
                    <p className="text-sm text-gray-600">Sand</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-bold text-lg">{mixDesign.fine_aggregate} kg</p>
                </div>
              </div>

              {/* Coarse Aggregate */}
              <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <Package className="w-5 h-5 text-orange-600" />
                  <div>
                    <p className="font-medium">Coarse Aggregate</p>
                    <p className="text-sm text-gray-600">{mixDesign.max_aggregate_size}mm down</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-bold text-lg">{mixDesign.coarse_aggregate} kg</p>
                </div>
              </div>

              {/* Admixtures */}
              {mixDesign.admixture_type && (
                <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Beaker className="w-5 h-5 text-purple-600" />
                    <div>
                      <p className="font-medium">Admixture</p>
                      <p className="text-sm text-gray-600">{mixDesign.admixture_type}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-lg">{mixDesign.admixture_dosage} L</p>
                  </div>
                </div>
              )}
            </div>

            {/* Mix Ratio Summary */}
            <div className="mt-4 p-3 bg-gray-100 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Mix Ratio by Weight</p>
              <p className="font-bold text-xl">
                1 : {(mixDesign.fine_aggregate / mixDesign.cement_content).toFixed(2)} : {(mixDesign.coarse_aggregate / mixDesign.cement_content).toFixed(2)}
              </p>
              <p className="text-xs text-gray-600 mt-1">Cement : Sand : Coarse Aggregate</p>
            </div>
          </div>

          {/* Compliance Checks */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Shield className="w-5 h-5 text-gray-600" />
              Compliance Checks
            </h2>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  {getComplianceIcon(mixDesign.water_cement_ratio <= 0.5)}
                  <div>
                    <p className="font-medium">W/C Ratio</p>
                    <p className="text-sm text-gray-600">Must be ≤ 0.50 for normal exposure</p>
                  </div>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  mixDesign.water_cement_ratio <= 0.5 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                }`}>
                  {mixDesign.water_cement_ratio <= 0.5 ? 'PASS' : 'FAIL'}
                </span>
              </div>

              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  {getComplianceIcon(mixDesign.cement_content >= 300)}
                  <div>
                    <p className="font-medium">Minimum Cement Content</p>
                    <p className="text-sm text-gray-600">Must be ≥ 300 kg/m³</p>
                  </div>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  mixDesign.cement_content >= 300 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                }`}>
                  {mixDesign.cement_content >= 300 ? 'PASS' : 'FAIL'}
                </span>
              </div>

              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  {getComplianceIcon(mixDesign.slump >= 25 && mixDesign.slump <= 150)}
                  <div>
                    <p className="font-medium">Slump Range</p>
                    <p className="text-sm text-gray-600">Should be 25-150 mm</p>
                  </div>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  mixDesign.slump >= 25 && mixDesign.slump <= 150 ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                }`}>
                  {mixDesign.slump >= 25 && mixDesign.slump <= 150 ? 'PASS' : 'CHECK'}
                </span>
              </div>
            </div>
          </div>

          {/* Additional Notes */}
          {mixDesign.notes && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Info className="w-5 h-5 text-gray-600" />
                Additional Notes
              </h2>
              <p className="text-gray-700 whitespace-pre-wrap">{mixDesign.notes}</p>
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
                <p className="text-sm text-gray-600 mb-1">Created Date</p>
                <p className="font-medium">{format(new Date(mixDesign.created_date), 'PPP')}</p>
              </div>
              {mixDesign.approved_date && (
                <div>
                  <p className="text-sm text-gray-600 mb-1">Approved Date</p>
                  <p className="font-medium">{format(new Date(mixDesign.approved_date), 'PPP')}</p>
                </div>
              )}
              {mixDesign.revision_number > 0 && (
                <div>
                  <p className="text-sm text-gray-600 mb-1">Revision</p>
                  <p className="font-medium">Rev. {mixDesign.revision_number}</p>
                </div>
              )}
            </div>
          </div>

          {/* Created By */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <User className="w-5 h-5 text-gray-600" />
              Design Team
            </h2>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-600 mb-1">Designed By</p>
                <p className="font-medium">{mixDesign.designed_by_name || 'Unknown'}</p>
              </div>
              {mixDesign.approved_by_name && (
                <div>
                  <p className="text-sm text-gray-600 mb-1">Approved By</p>
                  <p className="font-medium">{mixDesign.approved_by_name}</p>
                </div>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold mb-4">Actions</h2>
            <div className="space-y-2">
              {mixDesign.status === 'pending_approval' && (
                <>
                  <button
                    onClick={() => setShowApprovalModal(true)}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
                  >
                    <CheckCircle className="w-4 h-4" />
                    Approve Mix Design
                  </button>
                  <button
                    onClick={() => {
                      setShowApprovalModal(true);
                    }}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
                  >
                    <AlertCircle className="w-4 h-4" />
                    Reject Mix Design
                  </button>
                </>
              )}

              {mixDesign.status === 'approved' && (
                <div className="flex items-center justify-center gap-2 px-4 py-2 bg-green-100 text-green-700 rounded-lg">
                  <CheckCircle className="w-4 h-4" />
                  Mix Design Approved
                </div>
              )}

              {mixDesign.status === 'draft' && (
                <button
                  onClick={() => router.push(`/dashboard/mix-designs/${params.id}/edit`)}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >
                  <Edit2 className="w-4 h-4" />
                  Edit Mix Design
                </button>
              )}
            </div>
          </div>

          {/* Application Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex gap-3">
              <ThermometerSun className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-blue-800">
                <p className="font-medium mb-1">Application</p>
                <p>This mix design is suitable for structural concrete work in normal exposure conditions.</p>
              </div>
            </div>
          </div>

          {/* Validity Period */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex gap-3">
              <Clock className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-yellow-800">
                <p className="font-medium mb-1">Validity</p>
                <p>Mix design valid for 1 year from approval date. Re-approval required after expiry.</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Approval Modal */}
      {showApprovalModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-lg w-full p-6">
            <h2 className="text-xl font-bold mb-4">Approve/Reject Mix Design</h2>
            
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Comments*
              </label>
              <textarea
                value={approvalComments}
                onChange={(e) => setApprovalComments(e.target.value)}
                rows={4}
                placeholder="Add approval/rejection comments..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setShowApprovalModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
              >
                Cancel
              </button>
              <button
                onClick={() => handleApproval(false)}
                disabled={submitting}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 transition"
              >
                Reject
              </button>
              <button
                onClick={() => handleApproval(true)}
                disabled={submitting}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition"
              >
                Approve
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
