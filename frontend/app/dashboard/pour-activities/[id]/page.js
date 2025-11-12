'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, CheckCircle, MapPin, Calendar, Truck, Layers, Plus, Edit } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Spinner } from '@/components/ui/Spinner';
import { pourActivityAPI } from '@/lib/api';
import { CubeCastingModal } from '@/components/CubeCastingModal';

export default function PourActivityDetailPage({ params }) {
  const router = useRouter();
  const [pour, setPour] = useState(null);
  const [loading, setLoading] = useState(true);
  const [completing, setCompleting] = useState(false);
  const [showCubeModal, setShowCubeModal] = useState(false);

  useEffect(() => {
    loadPourActivity();
  }, [params.id]);

  async function loadPourActivity() {
    setLoading(true);
    try {
      const result = await pourActivityAPI.getById(params.id);
      if (result.success) {
        setPour(result.data.pourActivity);
      }
    } catch (error) {
      console.error('Error loading pour activity:', error);
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

      if (result.success) {
        // Update local state
        setPour(result.data.pourActivity);
        // Show cube casting modal
        setShowCubeModal(true);
      } else {
        alert('Error completing pour: ' + (result.error || 'Unknown error'));
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
      'cancelled': { variant: 'error', label: 'Cancelled' }
    };
    const config = variants[status] || variants.in_progress;
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!pour) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Pour activity not found.</p>
        <Link href="/dashboard/pour-activities">
          <Button className="mt-4">Back to Pour Activities</Button>
        </Link>
      </div>
    );
  }

  const totalReceived = pour.batches?.reduce((sum, batch) => sum + (batch.quantityReceived || 0), 0) || 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/dashboard/pour-activities">
            <Button variant="outline" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
          </Link>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-bold text-gray-900">{pour.pourId}</h1>
              {getStatusBadge(pour.status)}
              <Badge variant={pour.concreteType === 'PT' ? 'info' : 'default'}>
                {pour.concreteType === 'PT' ? 'Post-Tensioned' : 'Normal'}
              </Badge>
            </div>
            <p className="text-gray-600 mt-1">{pour.location?.description}</p>
          </div>
        </div>

        <div className="flex gap-2">
          {pour.status === 'in_progress' && (
            <Button
              onClick={handleCompletePour}
              disabled={completing || !pour.batches || pour.batches.length === 0}
            >
              {completing ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
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
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <Calendar className="w-8 h-8 text-blue-500" />
              <div>
                <p className="text-sm text-gray-600">Pour Date</p>
                <p className="text-lg font-semibold text-gray-900">
                  {new Date(pour.pourDate).toLocaleDateString()}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <Layers className="w-8 h-8 text-purple-500" />
              <div>
                <p className="text-sm text-gray-600">Design Grade</p>
                <p className="text-lg font-semibold text-gray-900">{pour.designGrade}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <Truck className="w-8 h-8 text-green-500" />
              <div>
                <p className="text-sm text-gray-600">Quantity</p>
                <p className="text-lg font-semibold text-gray-900">
                  {pour.status === 'completed' 
                    ? `${totalReceived.toFixed(1)} m³`
                    : `${pour.totalQuantityPlanned} m³ (planned)`}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Location Details */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MapPin className="w-5 h-5" />
            Location Details
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {pour.location?.buildingName && (
              <div>
                <p className="text-sm text-gray-600">Building</p>
                <p className="font-medium text-gray-900">{pour.location.buildingName}</p>
              </div>
            )}
            {pour.location?.floorLevel && (
              <div>
                <p className="text-sm text-gray-600">Floor Level</p>
                <p className="font-medium text-gray-900">{pour.location.floorLevel}</p>
              </div>
            )}
            {pour.location?.zone && (
              <div>
                <p className="text-sm text-gray-600">Zone</p>
                <p className="font-medium text-gray-900">{pour.location.zone}</p>
              </div>
            )}
            {pour.location?.gridReference && (
              <div>
                <p className="text-sm text-gray-600">Grid Reference</p>
                <p className="font-medium text-gray-900">{pour.location.gridReference}</p>
              </div>
            )}
            {pour.location?.structuralElementType && (
              <div>
                <p className="text-sm text-gray-600">Element Type</p>
                <p className="font-medium text-gray-900">{pour.location.structuralElementType}</p>
              </div>
            )}
            {pour.location?.elementId && (
              <div>
                <p className="text-sm text-gray-600">Element ID</p>
                <p className="font-medium text-gray-900">{pour.location.elementId}</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Linked Batches */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Truck className="w-5 h-5" />
              Linked Batches ({pour.batches?.length || 0})
            </CardTitle>
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
            <div className="text-center py-8 text-gray-500">
              <Truck className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p>No batches linked to this pour yet.</p>
              {pour.status === 'in_progress' && (
                <Link href={`/dashboard/batches/new?pourId=${pour.id}`}>
                  <Button size="sm" className="mt-3">
                    <Plus className="w-4 h-4 mr-2" />
                    Add First Batch
                  </Button>
                </Link>
              )}
            </div>
          ) : (
            <div className="space-y-3">
              {pour.batches.map((batch, index) => (
                <Link key={batch.id} href={`/dashboard/batches/${batch.id}`}>
                  <div className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-sm transition-all cursor-pointer">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-semibold text-gray-900">Batch #{index + 1}</span>
                          <Badge variant="default">{batch.batchNumber || 'N/A'}</Badge>
                        </div>
                        <div className="text-sm text-gray-600">
                          <span className="font-medium">Vehicle:</span> {batch.vehicleNumber || 'N/A'}
                        </div>
                        {batch.vendorName && (
                          <div className="text-sm text-gray-600">
                            <span className="font-medium">Vendor:</span> {batch.vendorName}
                          </div>
                        )}
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-semibold text-blue-600">
                          {batch.quantityReceived || 0} m³
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(batch.deliveryDate).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
              
              {pour.status === 'completed' && (
                <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-green-900">Total Quantity Received</span>
                    <span className="text-xl font-bold text-green-600">{totalReceived.toFixed(1)} m³</span>
                  </div>
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
            <p className="text-gray-700">{pour.remarks}</p>
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
