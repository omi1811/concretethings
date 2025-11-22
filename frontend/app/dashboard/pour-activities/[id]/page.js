'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, CheckCircle, MapPin, Calendar, Truck, Layers, Plus, Edit, Building2, Grid, Box, AlertCircle, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Spinner } from '@/components/ui/Spinner';
import { Alert } from '@/components/ui/Alert';
import { pourActivityAPI } from '@/lib/api-optimized';
import { getRequiredSamples } from '@/utils/standards';
import CubeCastingModal from '@/components/CubeCastingModal';

export default function PourActivityDetailPage({ params }) {
  const router = useRouter();
  const [pour, setPour] = useState(null);
  const [loading, setLoading] = useState(true);
  const [completing, setCompleting] = useState(false);
  const [showCubeModal, setShowCubeModal] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadPourActivity();
  }, [params.id]);

  async function loadPourActivity() {
    setLoading(true);
    setError(null);
    try {
      const result = await pourActivityAPI.getById(params.id);
      const pourData = result?.data?.pourActivity || result?.pourActivity;
      if (pourData) {
        setPour(pourData);
      } else {
        setError('Pour activity not found');
      }
    } catch (error) {
      console.error('Error loading pour activity:', error);
      setError('Failed to load pour activity details');
    } finally {
      setLoading(false);
    }
  }

  async function handleCompletePour() {
    if (!pour.batches || pour.batches.length === 0) {
      alert('Cannot complete pour with no batches linked. Please add at least one batch.');
      return;
    }

    if (!confirm('Are you sure you want to complete this pour? This will trigger cube test creation.')) {
      return;
    }

    setCompleting(true);
    try {
      const result = await pourActivityAPI.complete(params.id, {
        remarks: 'Pour completed successfully'
      });

      const pourData = result?.data?.pourActivity || result?.pourActivity;
      if (pourData) {
        setPour(pourData);
      }

      const showModal = result?.showCubeModal ?? result?.data?.showCubeModal ?? false;
      if (showModal) {
        setShowCubeModal(true);
      }

      if (!pourData && !showModal) {
        alert('Error completing pour: ' + (result?.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error completing pour:', error);
      alert('Error completing pour. Please try again.');
    } finally {
      setCompleting(false);
    }
  }

  const getStatusBadge = (status) => {
    const variants = {
      'in_progress': { variant: 'warning', label: 'In Progress' },
      'completed': { variant: 'success', label: 'Completed' },
      'cancelled': { variant: 'destructive', label: 'Cancelled' }
    };
    const config = variants[status] || variants.in_progress;
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  if (loading) {
    return (
      <div className="flex flex-col justify-center items-center min-h-[60vh] gap-4">
        <Loader2 className="w-10 h-10 animate-spin text-primary" />
        <p className="text-muted-foreground">Loading pour details...</p>
      </div>
    );
  }

  if (error || !pour) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4 text-center">
        <div className="bg-destructive/10 p-4 rounded-full">
          <AlertCircle className="w-10 h-10 text-destructive" />
        </div>
        <h2 className="text-xl font-semibold text-foreground">{error || 'Pour activity not found'}</h2>
        <Link href="/dashboard/pour-activities">
          <Button variant="outline">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Pour Activities
          </Button>
        </Link>
      </div>
    );
  }

  const totalReceived = pour.batches?.reduce((sum, batch) => sum + (batch.quantityReceived || 0), 0) || 0;

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-muted-foreground mb-2">
            <Link href="/dashboard/pour-activities" className="hover:text-foreground transition-colors flex items-center gap-1 text-sm">
              <ArrowLeft className="w-4 h-4" />
              Back to List
            </Link>
          </div>
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="text-3xl font-bold tracking-tight text-foreground">{pour.pourId}</h1>
            {getStatusBadge(pour.status)}
            <Badge variant={pour.concreteType === 'PT' ? 'secondary' : 'outline'}>
              {pour.concreteType === 'PT' ? 'Post-Tensioned' : 'Normal Concrete'}
            </Badge>
          </div>
          <p className="text-muted-foreground flex items-center gap-2">
            <MapPin className="w-4 h-4" />
            {pour.location?.description || 'No location description'}
          </p>
        </div>

        <div className="flex gap-2">
          {pour.status === 'in_progress' && (
            <Button
              onClick={handleCompletePour}
              disabled={completing || !pour.batches || pour.batches.length === 0}
              className="w-full md:w-auto"
            >
              {completing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  Completing...
                </>
              ) : (
                <>
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Complete Pour
                </>
              )}
            </Button>
          )}
        </div>
      </div>

      {/* Details Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6 flex items-center gap-4">
            <div className="bg-blue-100 dark:bg-blue-900/30 p-3 rounded-lg">
              <Calendar className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Pour Date</p>
              <p className="text-xl font-bold text-foreground">
                {new Date(pour.pourDate).toLocaleDateString()}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6 flex items-center gap-4">
            <div className="bg-purple-100 dark:bg-purple-900/30 p-3 rounded-lg">
              <Layers className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Design Grade</p>
              <p className="text-xl font-bold text-foreground">{pour.designGrade}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6 flex items-center gap-4">
            <div className="bg-green-100 dark:bg-green-900/30 p-3 rounded-lg">
              <Truck className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Quantity</p>
              <p className="text-xl font-bold text-foreground">
                {pour.status === 'completed'
                  ? `${totalReceived.toFixed(1)} m³`
                  : `${pour.totalQuantityPlanned} m³ (planned)`}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Sampling Frequency Compliance */}
        <Card>
          <CardContent className="pt-6 flex items-center gap-4">
            <div className="bg-orange-100 dark:bg-orange-900/30 p-3 rounded-lg">
              <Layers className="w-6 h-6 text-orange-600 dark:text-orange-400" />
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Required Samples</p>
              <p className="text-xl font-bold text-foreground">{getRequiredSamples(totalReceived)} sample{getRequiredSamples(totalReceived) > 1 ? 's' : ''}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Location Details */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MapPin className="w-5 h-5 text-primary" />
            Location Details
          </CardTitle>
          <CardDescription>Specific location information for this pour.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {pour.location?.buildingName && (
              <div className="flex items-start gap-3">
                <Building2 className="w-5 h-5 text-muted-foreground mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Building</p>
                  <p className="font-medium text-foreground">{pour.location.buildingName}</p>
                </div>
              </div>
            )}
            {pour.location?.floorLevel && (
              <div className="flex items-start gap-3">
                <Layers className="w-5 h-5 text-muted-foreground mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Floor Level</p>
                  <p className="font-medium text-foreground">{pour.location.floorLevel}</p>
                </div>
              </div>
            )}
            {pour.location?.zone && (
              <div className="flex items-start gap-3">
                <MapPin className="w-5 h-5 text-muted-foreground mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Zone</p>
                  <p className="font-medium text-foreground">{pour.location.zone}</p>
                </div>
              </div>
            )}
            {pour.location?.gridReference && (
              <div className="flex items-start gap-3">
                <Grid className="w-5 h-5 text-muted-foreground mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Grid Reference</p>
                  <p className="font-medium text-foreground">{pour.location.gridReference}</p>
                </div>
              </div>
            )}
            {pour.location?.structuralElementType && (
              <div className="flex items-start gap-3">
                <Box className="w-5 h-5 text-muted-foreground mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Element Type</p>
                  <p className="font-medium text-foreground">{pour.location.structuralElementType}</p>
                </div>
              </div>
            )}
            {pour.location?.elementId && (
              <div className="flex items-start gap-3">
                <Box className="w-5 h-5 text-muted-foreground mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Element ID</p>
                  <p className="font-medium text-foreground">{pour.location.elementId}</p>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Linked Batches */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Truck className="w-5 h-5 text-primary" />
                Linked Batches
              </CardTitle>
              <CardDescription>Batches associated with this pour activity.</CardDescription>
            </div>
            {pour.status === 'in_progress' && (
              <Link href={`/dashboard/batches/new?pourId=${pour.id}`}>
                <Button size="sm">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Batch
                </Button>
              </Link>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {!pour.batches || pour.batches.length === 0 ? (
            <div className="text-center py-12 border-2 border-dashed rounded-lg bg-muted/20">
              <Truck className="w-12 h-12 text-muted-foreground/50 mx-auto mb-3" />
              <p className="text-muted-foreground font-medium">No batches linked yet</p>
              <p className="text-sm text-muted-foreground mb-4">Start adding batches to track concrete usage.</p>
              {pour.status === 'in_progress' && (
                <Link href={`/dashboard/batches/new?pourId=${pour.id}`}>
                  <Button size="sm" variant="outline">
                    <Plus className="w-4 h-4 mr-2" />
                    Add First Batch
                  </Button>
                </Link>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              <div className="grid grid-cols-1 gap-4">
                {pour.batches.map((batch, index) => (
                  <Link key={batch.id} href={`/dashboard/batches/${batch.id}`}>
                    <div className="group flex flex-col md:flex-row md:items-center justify-between p-4 border rounded-lg hover:bg-muted/50 hover:border-primary/30 transition-all cursor-pointer bg-card">
                      <div className="flex-1 space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-foreground group-hover:text-primary transition-colors">Batch #{index + 1}</span>
                          <Badge variant="outline" className="text-xs font-normal">{batch.batchNumber || 'N/A'}</Badge>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <Truck className="w-3 h-3" />
                            {batch.vehicleNumber || 'N/A'}
                          </span>
                          {batch.vendorName && (
                            <span className="flex items-center gap-1">
                              <Building2 className="w-3 h-3" />
                              {batch.vendorName}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="mt-2 md:mt-0 text-right">
                        <p className="text-lg font-bold text-primary">
                          {batch.quantityReceived || 0} m³
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(batch.deliveryDate).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>

              {pour.status === 'completed' && (
                <div className="mt-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg flex items-center justify-between">
                  <span className="font-medium text-green-900 dark:text-green-300">Total Quantity Received</span>
                  <span className="text-2xl font-bold text-green-700 dark:text-green-400">{totalReceived.toFixed(1)} m³</span>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Remarks */}
      {pour.remarks && (
        <Card>
          <CardHeader>
            <CardTitle>Remarks</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground italic">{pour.remarks}</p>
          </CardContent>
        </Card>
      )}

      {/* Cube Casting Modal */}
      {showCubeModal && pour.status === 'completed' && (
        <CubeCastingModal
          isOpen={showCubeModal}
          onClose={() => {
            setShowCubeModal(false);
            // Reload to show updated data
            loadPourActivity();
          }}
          pourActivity={pour}
          projectId={pour.projectId}
        />
      )}
    </div>
  );
}
