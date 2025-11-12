'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { ArrowLeft, Upload, Camera, Layers } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Input, Select, Textarea } from '@/components/ui/Input';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Alert } from '@/components/ui/Alert';
import { batchAPI, cubeTestAPI, labAPI, pourActivityAPI } from '@/lib/api';
import CubeCastingModal from '@/components/CubeCastingModal';

export default function NewBatchPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const projectId = searchParams.get('project_id');
  const pourIdFromQuery = searchParams.get('pourId');
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showCubeCastingModal, setShowCubeCastingModal] = useState(false);
  const [batchSummary, setBatchSummary] = useState(null);
  const [labs, setLabs] = useState([]);
  const [pourActivities, setPourActivities] = useState([]);
  const [selectedPour, setSelectedPour] = useState(null);
  
  const [formData, setFormData] = useState({
    batchNumber: '',
    vendorId: '',
    vendorName: '',
    grade: 'M20',
    quantity: '',
    deliveryDate: new Date().toISOString().split('T')[0],
    deliveryTime: '',
    slump: '',
    temperature: '',
    vehicleNumber: '',
    driverName: '',
    location: '',
    remarks: '',
    pourActivityId: pourIdFromQuery || ''
  });

  useEffect(() => {
    if (projectId) {
      loadPourActivities();
    }
    if (pourIdFromQuery) {
      loadPourActivity(pourIdFromQuery);
    }
  }, [projectId, pourIdFromQuery]);

  async function loadPourActivities() {
    try {
      const result = await pourActivityAPI.getAll({
        projectId,
        status: 'in_progress'
      });
      if (result.success) {
        setPourActivities(result.data.pourActivities || []);
      }
    } catch (error) {
      console.error('Error loading pour activities:', error);
    }
  }

  async function loadPourActivity(pourId) {
    try {
      const result = await pourActivityAPI.getById(pourId);
      if (result.success) {
        const pour = result.data.pourActivity;
        setSelectedPour(pour);
        // Auto-populate fields from pour activity
        setFormData(prev => ({
          ...prev,
          grade: pour.designGrade || prev.grade,
          location: pour.location?.description || prev.location
        }));
      }
    } catch (error) {
      console.error('Error loading pour activity:', error);
    }
  }

  const handlePourChange = (e) => {
    const pourId = e.target.value;
    setFormData(prev => ({ ...prev, pourActivityId: pourId }));
    
    if (pourId) {
      const pour = pourActivities.find(p => p.id === parseInt(pourId));
      if (pour) {
        setSelectedPour(pour);
        // Auto-populate fields
        setFormData(prev => ({
          ...prev,
          grade: pour.designGrade || prev.grade,
          location: pour.location?.description || prev.location
        }));
      }
    } else {
      setSelectedPour(null);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const result = await batchAPI.create(formData);
      
      if (result.success) {
        setSuccess('Batch created successfully!');
        
        // Fetch batch completion summary
        const batchId = result.data.batch?.id || result.data.id;
        if (batchId && projectId) {
          const completionResult = await batchAPI.complete(batchId, projectId);
          
          if (completionResult.success) {
            // Fetch available labs
            const user = JSON.parse(localStorage.getItem('user') || '{}');
            if (user.companyId) {
              const labsResult = await labAPI.getAll(user.companyId);
              if (labsResult.success) {
                setLabs(labsResult.data.labs || []);
              }
            }
            
            // Show cube casting modal
            setBatchSummary({
              ...completionResult.data.batch,
              projectId: projectId
            });
            setShowCubeCastingModal(true);
          } else {
            // If completion fails, just redirect
            setTimeout(() => {
              router.push('/dashboard/batches?project_id=' + projectId);
            }, 1500);
          }
        } else {
          setTimeout(() => {
            router.push('/dashboard/batches?project_id=' + projectId);
          }, 1500);
        }
      } else {
        setError(result.error || result.message || 'Failed to create batch');
      }
    } catch (err) {
      console.error('Error creating batch:', err);
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleCubeCasting = async (cubeData) => {
    try {
      const result = await cubeTestAPI.bulkCreate(cubeData);
      
      if (result.success) {
        alert(`Successfully created ${result.data.cube_tests?.length || 0} cube test sets!`);
        router.push('/dashboard/cube-tests?project_id=' + projectId);
      } else {
        throw new Error(result.error || 'Failed to create cube tests');
      }
    } catch (err) {
      console.error('Error creating cube tests:', err);
      throw err;
    }
  };

  const handleSkipCubeCasting = () => {
    setShowCubeCastingModal(false);
    router.push('/dashboard/batches?project_id=' + projectId);
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/dashboard/batches">
          <Button variant="outline" size="sm">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">New Batch</h1>
          <p className="text-gray-600 mt-1">Register a new concrete batch delivery</p>
        </div>
      </div>

      {error && (
        <Alert variant="danger" onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert variant="success" onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Pour Activity Linking (NEW) */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Layers className="w-5 h-5" />
              Link to Pour Activity (Optional)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
              <p className="text-sm text-blue-800">
                💡 <strong>Tip:</strong> If this batch is part of a larger pour (e.g., multiple vehicles for one slab),
                link it to a pour activity. This groups batches together for single cube test sets.
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Select Pour Activity
              </label>
              <select
                value={formData.pourActivityId}
                onChange={handlePourChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Standalone Batch (No Pour Activity)</option>
                {pourActivities.map(pour => (
                  <option key={pour.id} value={pour.id}>
                    {pour.pourId} - {pour.location?.gridReference} ({pour.designGrade}, {pour.totalQuantityPlanned}m³)
                  </option>
                ))}
              </select>
              
              {pourActivities.length === 0 && (
                <p className="mt-2 text-sm text-gray-500">
                  No active pour activities. <Link href="/dashboard/pour-activities/new" className="text-blue-600 hover:underline">Create one</Link> to group batches.
                </p>
              )}
            </div>
            
            {selectedPour && (
              <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                <h4 className="font-semibold text-green-900 mb-2">Linked to Pour Activity</h4>
                <div className="text-sm text-green-800 space-y-1">
                  <p><strong>Pour ID:</strong> {selectedPour.pourId}</p>
                  <p><strong>Location:</strong> {selectedPour.location?.description}</p>
                  <p><strong>Concrete Type:</strong> {selectedPour.concreteType === 'PT' ? 'Post-Tensioned' : 'Normal'}</p>
                  <p><strong>Design Grade:</strong> {selectedPour.designGrade}</p>
                  <p><strong>Total Planned:</strong> {selectedPour.totalQuantityPlanned} m³</p>
                  {selectedPour.concreteType === 'PT' && (
                    <p className="text-blue-600 font-medium mt-2">
                      ℹ️ PT concrete: Tests will be at 5 days (not 3 days)
                    </p>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Basic Information */}
        <Card>
          <CardHeader>
            <CardTitle>Basic Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Batch Number"
                name="batchNumber"
                value={formData.batchNumber}
                onChange={handleChange}
                placeholder="e.g., BATCH-2025-001"
                required
              />
              <Input
                label="Vendor Name"
                name="vendorName"
                value={formData.vendorName}
                onChange={handleChange}
                placeholder="e.g., ABC Concrete"
                required
              />
              <Select
                label="Grade"
                name="grade"
                value={formData.grade}
                onChange={handleChange}
                required
              >
                <option value="M10">M10</option>
                <option value="M15">M15</option>
                <option value="M20">M20</option>
                <option value="M25">M25</option>
                <option value="M30">M30</option>
                <option value="M35">M35</option>
                <option value="M40">M40</option>
                <option value="M45">M45</option>
                <option value="M50">M50</option>
              </Select>
              <Input
                type="number"
                label="Quantity (m³)"
                name="quantity"
                value={formData.quantity}
                onChange={handleChange}
                placeholder="e.g., 10"
                step="0.1"
                required
              />
            </div>
          </CardContent>
        </Card>

        {/* Delivery Details */}
        <Card>
          <CardHeader>
            <CardTitle>Delivery Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                type="date"
                label="Delivery Date"
                name="deliveryDate"
                value={formData.deliveryDate}
                onChange={handleChange}
                required
              />
              <Input
                type="time"
                label="Delivery Time"
                name="deliveryTime"
                value={formData.deliveryTime}
                onChange={handleChange}
                required
              />
              <Input
                label="Vehicle Number"
                name="vehicleNumber"
                value={formData.vehicleNumber}
                onChange={handleChange}
                placeholder="e.g., DL-01-AB-1234"
              />
              <Input
                label="Driver Name"
                name="driverName"
                value={formData.driverName}
                onChange={handleChange}
                placeholder="e.g., John Doe"
              />
              <Input
                label="Location"
                name="location"
                value={formData.location}
                onChange={handleChange}
                placeholder="e.g., Site-A, Column C1"
              />
            </div>
          </CardContent>
        </Card>

        {/* Quality Parameters */}
        <Card>
          <CardHeader>
            <CardTitle>Quality Parameters</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                type="number"
                label="Slump (mm)"
                name="slump"
                value={formData.slump}
                onChange={handleChange}
                placeholder="e.g., 100"
                step="1"
              />
              <Input
                type="number"
                label="Temperature (°C)"
                name="temperature"
                value={formData.temperature}
                onChange={handleChange}
                placeholder="e.g., 32"
                step="0.1"
              />
            </div>
            <Textarea
              label="Remarks"
              name="remarks"
              value={formData.remarks}
              onChange={handleChange}
              placeholder="Any additional notes..."
              rows={3}
            />
          </CardContent>
        </Card>

        {/* Photo Upload */}
        <Card>
          <CardHeader>
            <CardTitle>Photos (Optional)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <Camera className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-2">Photo upload will be available soon</p>
              <p className="text-sm text-gray-500">You can add photos after creating the batch</p>
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex justify-end gap-4">
          <Link href={`/dashboard/batches?project_id=${projectId}`}>
            <Button type="button" variant="outline">
              Cancel
            </Button>
          </Link>
          <Button type="submit" disabled={loading}>
            {loading ? 'Creating...' : 'Create Batch'}
          </Button>
        </div>
      </form>

      {/* Cube Casting Modal */}
      <CubeCastingModal
        isOpen={showCubeCastingModal}
        onClose={handleSkipCubeCasting}
        batchData={batchSummary}
        onSubmit={handleCubeCasting}
        labs={labs}
      />
    </div>
  );
}
