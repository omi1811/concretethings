'use client';

import { useState, useEffect } from 'react';
import {
  Beaker, ArrowLeft, User, Calendar, CheckCircle,
  AlertCircle, Edit2, FileText, Package, Scale,
  Droplet, ThermometerSun, Clock, Shield, Info,
  Loader2, X
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import Link from 'next/link';
import { format } from 'date-fns';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Modal } from '@/components/ui/Modal';
import { Textarea } from '@/components/ui/Input';
import { Alert } from '@/components/ui/Alert';
import { CONCRETE_EXPOSURE_LIMITS, getGradeValue } from '@/utils/standards';

export default function MixDesignDetailsPage({ params }) {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [mixDesign, setMixDesign] = useState(null);
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  const [showEditMode, setShowEditMode] = useState(false);
  const [approvalComments, setApprovalComments] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const exposure = mixDesign?.exposure_condition || 'Mild';
  const normalizedExposure = Object.keys(CONCRETE_EXPOSURE_LIMITS).find(
    k => k.toLowerCase() === exposure.toLowerCase()
  ) || 'Mild';
  const limits = CONCRETE_EXPOSURE_LIMITS[normalizedExposure];
  const gradeValue = mixDesign ? getGradeValue(mixDesign.grade) : 0;

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

  const getStatusBadge = (status) => {
    const variants = {
      draft: { variant: 'secondary', label: 'Draft' },
      pending_approval: { variant: 'warning', label: 'Pending Approval' },
      approved: { variant: 'success', label: 'Approved' },
      rejected: { variant: 'destructive', label: 'Rejected' },
      revised: { variant: 'info', label: 'Revised' }
    };
    const config = variants[status] || variants.draft;
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  const getComplianceIcon = (compliant) => {
    return compliant ? (
      <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
    ) : (
      <AlertCircle className="w-5 h-5 text-destructive" />
    );
  };

  if (loading) {
    return (
      <div className="flex flex-col justify-center items-center min-h-[60vh] gap-4">
        <Loader2 className="w-10 h-10 animate-spin text-primary" />
        <p className="text-muted-foreground">Loading mix design...</p>
      </div>
    );
  }

  if (!mixDesign) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4 text-center">
        <div className="bg-muted p-4 rounded-full">
          <Beaker className="w-10 h-10 text-muted-foreground" />
        </div>
        <h2 className="text-xl font-semibold text-foreground">Mix Design Not Found</h2>
        <p className="text-muted-foreground">The requested mix design could not be found.</p>
        <Link href="/dashboard/mix-designs">
          <Button variant="outline">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Mix Designs
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-muted-foreground mb-2">
            <Link href="/dashboard/mix-designs" className="hover:text-foreground transition-colors flex items-center gap-1 text-sm">
              <ArrowLeft className="w-4 h-4" />
              Back to List
            </Link>
          </div>
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="text-3xl font-bold tracking-tight text-foreground">{mixDesign.mix_id}</h1>
            {getStatusBadge(mixDesign.status)}
          </div>
          <p className="text-muted-foreground flex items-center gap-2">
            Concrete Mix Design Details
          </p>
        </div>

        <div className="flex gap-2">
          {mixDesign.status === 'approved' && (
            <Button
              variant="outline"
              onClick={() => setShowEditMode(true)}
            >
              <Edit2 className="w-4 h-4 mr-2" />
              Edit
            </Button>
          )}
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Mix Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-primary" />
                Mix Specifications
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-1">Concrete Grade</p>
                  <p className="font-bold text-lg text-foreground">{mixDesign.grade}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-1">Design Strength</p>
                  <p className="font-medium text-foreground">{mixDesign.design_strength} MPa</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-1">W/C Ratio</p>
                  <p className="font-medium text-foreground">{mixDesign.water_cement_ratio}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-1">Slump</p>
                  <p className="font-medium text-foreground">{mixDesign.slump} mm</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-1">Max Aggregate</p>
                  <p className="font-medium text-foreground">{mixDesign.max_aggregate_size} mm</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-1">Exposure</p>
                  <p className="font-medium text-foreground">{mixDesign.exposure_condition || 'Normal'}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Material Proportions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Package className="w-5 h-5 text-primary" />
                Material Proportions (per m³)
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Cement */}
              <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                <div className="flex items-center gap-3">
                  <Scale className="w-5 h-5 text-muted-foreground" />
                  <div>
                    <p className="font-medium text-foreground">Cement</p>
                    <p className="text-sm text-muted-foreground">{mixDesign.cement_type || 'OPC 43'}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-bold text-lg text-foreground">{mixDesign.cement_content} kg</p>
                </div>
              </div>

              {/* Water */}
              <div className="flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div className="flex items-center gap-3">
                  <Droplet className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  <div>
                    <p className="font-medium text-foreground">Water</p>
                    <p className="text-sm text-muted-foreground">Potable water</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-bold text-lg text-foreground">{mixDesign.water_content} L</p>
                </div>
              </div>

              {/* Fine Aggregate */}
              <div className="flex items-center justify-between p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                <div className="flex items-center gap-3">
                  <Package className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
                  <div>
                    <p className="font-medium text-foreground">Fine Aggregate</p>
                    <p className="text-sm text-muted-foreground">Sand</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-bold text-lg text-foreground">{mixDesign.fine_aggregate} kg</p>
                </div>
              </div>

              {/* Coarse Aggregate */}
              <div className="flex items-center justify-between p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                <div className="flex items-center gap-3">
                  <Package className="w-5 h-5 text-orange-600 dark:text-orange-400" />
                  <div>
                    <p className="font-medium text-foreground">Coarse Aggregate</p>
                    <p className="text-sm text-muted-foreground">{mixDesign.max_aggregate_size}mm down</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-bold text-lg text-foreground">{mixDesign.coarse_aggregate} kg</p>
                </div>
              </div>

              {/* Admixtures */}
              {mixDesign.admixture_type && (
                <div className="flex items-center justify-between p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Beaker className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                    <div>
                      <p className="font-medium text-foreground">Admixture</p>
                      <p className="text-sm text-muted-foreground">{mixDesign.admixture_type}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-lg text-foreground">{mixDesign.admixture_dosage} L</p>
                  </div>
                </div>
              )}

              {/* Mix Ratio Summary */}
              <div className="mt-4 p-4 bg-muted rounded-lg text-center">
                <p className="text-sm font-medium text-muted-foreground mb-1">Mix Ratio by Weight</p>
                <p className="font-bold text-xl text-foreground tracking-wide">
                  1 : {(mixDesign.fine_aggregate / mixDesign.cement_content).toFixed(2)} : {(mixDesign.coarse_aggregate / mixDesign.cement_content).toFixed(2)}
                </p>
                <p className="text-xs text-muted-foreground mt-1">Cement : Sand : Coarse Aggregate</p>
              </div>
            </CardContent>
          </Card>



          {/* Compliance Checks */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-primary" />
                Compliance Checks (IS 456:2000)
              </CardTitle>
              <CardDescription>
                Based on {normalizedExposure} exposure condition
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {/* W/C Ratio Check */}
              <div className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center gap-3">
                  {getComplianceIcon(mixDesign.water_cement_ratio <= limits.maxWaterCementRatio)}
                  <div>
                    <p className="font-medium text-foreground">W/C Ratio</p>
                    <p className="text-sm text-muted-foreground">
                      Must be ≤ {limits.maxWaterCementRatio.toFixed(2)}
                    </p>
                  </div>
                </div>
                <Badge variant={mixDesign.water_cement_ratio <= limits.maxWaterCementRatio ? 'success' : 'destructive'}>
                  {mixDesign.water_cement_ratio <= limits.maxWaterCementRatio ? 'PASS' : 'FAIL'}
                </Badge>
              </div>

              {/* Min Cement Content Check */}
              <div className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center gap-3">
                  {getComplianceIcon(mixDesign.cement_content >= limits.minCementContent)}
                  <div>
                    <p className="font-medium text-foreground">Min Cement Content</p>
                    <p className="text-sm text-muted-foreground">
                      Must be ≥ {limits.minCementContent} kg/m³
                    </p>
                  </div>
                </div>
                <Badge variant={mixDesign.cement_content >= limits.minCementContent ? 'success' : 'destructive'}>
                  {mixDesign.cement_content >= limits.minCementContent ? 'PASS' : 'FAIL'}
                </Badge>
              </div>

              {/* Min Grade Check */}
              <div className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center gap-3">
                  {getComplianceIcon(gradeValue >= limits.minGrade)}
                  <div>
                    <p className="font-medium text-foreground">Minimum Grade</p>
                    <p className="text-sm text-muted-foreground">
                      Must be ≥ M{limits.minGrade}
                    </p>
                  </div>
                </div>
                <Badge variant={gradeValue >= limits.minGrade ? 'success' : 'destructive'}>
                  {gradeValue >= limits.minGrade ? 'PASS' : 'FAIL'}
                </Badge>
              </div>

              {/* Slump Check (Standard Range) */}
              <div className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center gap-3">
                  {getComplianceIcon(mixDesign.slump >= 25 && mixDesign.slump <= 150)}
                  <div>
                    <p className="font-medium text-foreground">Slump Range</p>
                    <p className="text-sm text-muted-foreground">Should be 25-150 mm</p>
                  </div>
                </div>
                <Badge variant={mixDesign.slump >= 25 && mixDesign.slump <= 150 ? 'success' : 'warning'}>
                  {mixDesign.slump >= 25 && mixDesign.slump <= 150 ? 'PASS' : 'CHECK'}
                </Badge>
              </div>
            </CardContent>
          </Card>

          {/* Additional Notes */}
          {mixDesign.notes && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Info className="w-5 h-5 text-primary" />
                  Additional Notes
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground whitespace-pre-wrap">{mixDesign.notes}</p>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right Column - Timeline & Actions */}
        <div className="space-y-6">
          {/* Timeline */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="w-5 h-5 text-primary" />
                Timeline
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-1">Created Date</p>
                <p className="font-medium text-foreground">{format(new Date(mixDesign.created_date), 'PPP')}</p>
              </div>
              {mixDesign.approved_date && (
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-1">Approved Date</p>
                  <p className="font-medium text-foreground">{format(new Date(mixDesign.approved_date), 'PPP')}</p>
                </div>
              )}
              {mixDesign.revision_number > 0 && (
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-1">Revision</p>
                  <p className="font-medium text-foreground">Rev. {mixDesign.revision_number}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Created By */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="w-5 h-5 text-primary" />
                Design Team
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-1">Designed By</p>
                <p className="font-medium text-foreground">{mixDesign.designed_by_name || 'Unknown'}</p>
              </div>
              {mixDesign.approved_by_name && (
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-1">Approved By</p>
                  <p className="font-medium text-foreground">{mixDesign.approved_by_name}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {mixDesign.status === 'pending_approval' && (
                <>
                  <Button
                    onClick={() => setShowApprovalModal(true)}
                    className="w-full bg-green-600 hover:bg-green-700"
                  >
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Approve Mix Design
                  </Button>
                  <Button
                    onClick={() => setShowApprovalModal(true)}
                    variant="destructive"
                    className="w-full"
                  >
                    <AlertCircle className="w-4 h-4 mr-2" />
                    Reject Mix Design
                  </Button>
                </>
              )}

              {mixDesign.status === 'approved' && (
                <div className="flex items-center justify-center gap-2 px-4 py-3 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-lg font-medium">
                  <CheckCircle className="w-4 h-4" />
                  Mix Design Approved
                </div>
              )}

              {mixDesign.status === 'draft' && (
                <Button
                  onClick={() => router.push(`/dashboard/mix-designs/${params.id}/edit`)}
                  className="w-full"
                >
                  <Edit2 className="w-4 h-4 mr-2" />
                  Edit Mix Design
                </Button>
              )}
            </CardContent>
          </Card>

          {/* Application Info */}
          <Alert variant="info" className="bg-blue-50/50 dark:bg-blue-900/10 border-blue-200 dark:border-blue-800">
            <ThermometerSun className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            <div>
              <p className="font-medium text-blue-900 dark:text-blue-300">Application</p>
              <p className="text-sm mt-1 text-blue-700 dark:text-blue-400">
                This mix design is suitable for structural concrete work in normal exposure conditions.
              </p>
            </div>
          </Alert>

          {/* Validity Period */}
          <Alert variant="warning" className="bg-yellow-50/50 dark:bg-yellow-900/10 border-yellow-200 dark:border-yellow-800">
            <Clock className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />
            <div>
              <p className="font-medium text-yellow-900 dark:text-yellow-300">Validity</p>
              <p className="text-sm mt-1 text-yellow-700 dark:text-yellow-400">
                Mix design valid for 1 year from approval date. Re-approval required after expiry.
              </p>
            </div>
          </Alert>
        </div>
      </div>

      {/* Approval Modal */}
      <Modal
        isOpen={showApprovalModal}
        onClose={() => setShowApprovalModal(false)}
        title="Approve/Reject Mix Design"
      >
        <div className="space-y-4">
          <Textarea
            label="Comments"
            value={approvalComments}
            onChange={(e) => setApprovalComments(e.target.value)}
            rows={4}
            placeholder="Add approval/rejection comments..."
            required
          />

          <div className="flex gap-3 justify-end mt-4">
            <Button
              variant="outline"
              onClick={() => setShowApprovalModal(false)}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => handleApproval(false)}
              disabled={submitting}
            >
              Reject
            </Button>
            <Button
              className="bg-green-600 hover:bg-green-700"
              onClick={() => handleApproval(true)}
              disabled={submitting}
            >
              Approve
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
