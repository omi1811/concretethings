'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { ArrowLeft, Upload, Camera, Layers } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Input, Select, Textarea } from '@/components/ui/Input';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Alert } from '@/components/ui/Alert';
import { Spinner, LoadingScreen } from '@/components/ui/Spinner';
import { batchAPI, cubeTestAPI, labAPI, pourActivityAPI, projectsAPI } from '@/lib/api-optimized';
import CubeCastingModal from '@/components/CubeCastingModal';

function NewBatchContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryProjectId = searchParams.get('project_id');
  const pourIdFromQuery = searchParams.get('pourId');

  const [activeProjectId, setActiveProjectId] = useState('');
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showCubeCastingModal, setShowCubeCastingModal] = useState(false);
  const [batchSummary, setBatchSummary] = useState(null);
  const [labs, setLabs] = useState([]);
  const [pourActivities, setPourActivities] = useState([]);
  const [selectedPour, setSelectedPour] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

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
    // vehicleNumber: '', // Removed as per requirement
    location: '',
    remarks: '',
    pourActivityId: pourIdFromQuery || ''
  });

  // Check authentication first
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token') ||
        localStorage.getItem('access_token') ||
        localStorage.getItem('auth_token');

      setIsAuthenticated(true);
    }
  }, [router]);

  useEffect(() => {
    // Only load projects if authenticated
    if (!isAuthenticated) return;

    if (queryProjectId) {
      setActiveProjectId(queryProjectId);
      if (typeof window !== 'undefined') {
        localStorage.setItem('currentProjectId', queryProjectId);
      }
      return;
    }

    if (typeof window !== 'undefined') {
      const storedProjectId =
        localStorage.getItem('currentProjectId') ||
        localStorage.getItem('project_id') ||
        localStorage.getItem('projectId');
      if (storedProjectId) {
        setActiveProjectId(storedProjectId);
      }
    }
  }, [queryProjectId, isAuthenticated]);

  useEffect(() => {
    // Only fetch projects if authenticated
    if (!isAuthenticated) return;

    let isMounted = true;

    async function fetchProjects() {
      try {
        const result = await projectsAPI.getAll();
        if (!isMounted) {
          return;
        }
        const projectList = Array.isArray(result?.projects)
          ? result.projects
          : Array.isArray(result?.data?.projects)
            ? result.data.projects
            : Array.isArray(result)
              ? result
              : [];
        setProjects(projectList);

        if (!queryProjectId && projectList.length > 0) {
          let resolvedId = '';
          setActiveProjectId((prev) => {
            if (prev) {
              return prev;
            }
            const firstProject = projectList[0] || {};
            const candidate =
              firstProject.id ??
              firstProject.projectId ??
              firstProject.project_id;
            if (!candidate) {
              return prev;
            }
            resolvedId = String(candidate);
            return resolvedId;
          });
          if (resolvedId && typeof window !== 'undefined') {
            localStorage.setItem('currentProjectId', resolvedId);
          }
        }
      } catch (fetchError) {
        console.error('Error loading projects:', fetchError);
      }
    }

    fetchProjects();

    return () => {
      isMounted = false;
    };
  }, [queryProjectId, isAuthenticated]);

  useEffect(() => {
    if (activeProjectId) {
      loadPourActivities(activeProjectId);
    } else {
      setPourActivities([]);
      setSelectedPour(null);
      setFormData((prev) => ({ ...prev, pourActivityId: '' }));
    }
  }, [activeProjectId]);

  useEffect(() => {
    if (pourIdFromQuery) {
      loadPourActivity(pourIdFromQuery);
    }
  }, [pourIdFromQuery]);

  const batchesListHref = activeProjectId
    ? `/dashboard/batches?project_id=${activeProjectId}`
    : '/dashboard/batches';
  const cubeTestsHref = activeProjectId
    ? `/dashboard/cube-tests?project_id=${activeProjectId}`
    : '/dashboard/cube-tests';

  async function loadPourActivities(projectIdToLoad) {
    if (!projectIdToLoad) {
      return;
    }
    try {
      const result = await pourActivityAPI.getAll({
        projectId: projectIdToLoad,
        status: 'in_progress'
      });
      if (result?.success) {
        setPourActivities(result.data.pourActivities || []);
      } else if (Array.isArray(result?.data?.pourActivities)) {
        setPourActivities(result.data.pourActivities);
      } else if (Array.isArray(result?.pourActivities)) {
        setPourActivities(result.pourActivities);
      } else {
        setPourActivities([]);
      }
    } catch (error) {
      console.error('Error loading pour activities:', error);
      setPourActivities([]);
    }
  }

  async function loadPourActivity(pourId) {
    try {
      const result = await pourActivityAPI.getById(pourId);
      const pour =
        result?.data?.pourActivity ??
        result?.pourActivity ??
        result?.data ??
        null;

      if (result?.success === false && !pour) {
        return;
      }

      if (pour) {
        setSelectedPour(pour);
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

  const handleProjectSelect = (event) => {
    const value = event.target.value;
    setActiveProjectId(value);
    if (typeof window !== 'undefined') {
      if (value) {
        localStorage.setItem('currentProjectId', value);
      } else {
        localStorage.removeItem('currentProjectId');
      }
    }
    setPourActivities([]);
    setSelectedPour(null);
    setFormData(prev => ({ ...prev, pourActivityId: '' }));
  };

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
    const numericProjectId = activeProjectId ? parseInt(activeProjectId, 10) : NaN;
    if (Number.isNaN(numericProjectId)) {
      setError('Select a project before creating a batch.');
      return;
    }

    setLoading(true);

    try {
      const result = await batchAPI.create({
        ...formData,
        projectId: numericProjectId
      });
      const creationSuccess = result?.success ?? !result?.error;
      if (creationSuccess) {
        setSuccess('Batch created successfully!');

        const batchPayload = result?.data ?? result;
        const batchId =
          batchPayload?.batch?.id ??
          batchPayload?.batchId ??
          batchPayload?.id;

        if (batchId) {
          // Set the batch summary and open the cube casting modal regardless of whether completion succeeds.
          const provisionalBatch = batchPayload?.batch ?? batchPayload ?? { id: batchId };
          setBatchSummary({
            ...(provisionalBatch || {}),
            batchId: batchId,
            projectId: numericProjectId
          });
          setShowCubeCastingModal(true);

          // Attempt to complete the batch (may fail for some backends) and fetch labs for modal
          (async () => {
            try {
              const completionResult = await batchAPI.complete(batchId, numericProjectId);
              const completionSuccess = completionResult?.success ?? !completionResult?.error;
              if (completionSuccess) {
                const completionData = completionResult?.data ?? completionResult;
                const completedBatch = completionData?.batch ?? completionData?.batchSummary ?? completionData;
                setBatchSummary({ ...(completedBatch || {}), projectId: numericProjectId });
              }
            } catch (completionError) {
              console.error('Error completing batch:', completionError);
            }

            try {
              const user = JSON.parse(localStorage.getItem('user') || '{}');
              if (user.companyId) {
                const labsResult = await labAPI.getAll(user.companyId);
                if (labsResult?.success) {
                  setLabs(labsResult.data.labs || []);
                } else if (Array.isArray(labsResult?.labs)) {
                  setLabs(labsResult.labs);
                }
              }
            } catch (labError) {
              console.error('Error loading labs:', labError);
            }
          })();
          return;
        }

        // No batchId available — redirect back to list after a short delay
        setTimeout(() => {
          router.push(batchesListHref);
        }, 1500);
      } else {
        setError(result?.error || result?.message || 'Failed to create batch');
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

      if (result?.success ?? !result?.error) {
        alert(`Successfully created ${result.data.cube_tests?.length || 0} cube test sets!`);
        router.push(cubeTestsHref);
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
    router.push(batchesListHref);
  };

  // Show loading while checking authentication
  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Spinner size="lg" />
          <p className="mt-4 text-gray-600">Checking authentication...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href={batchesListHref}>
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
        <Card>
          <CardHeader>
            <CardTitle>Project</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {projects.length > 0 ? (
              <Select
                label="Select Project"
                value={activeProjectId || ''}
                onChange={handleProjectSelect}
                required
              >
                <option value="">Select a project</option>
                {projects.map((project) => {
                  const idValue = project?.id ?? project?.projectId ?? project?.project_id;
                  if (!idValue) {
                    return null;
                  }
                  const idString = String(idValue);
                  const code = project?.projectCode ?? project?.project_code;
                  const label = code ? `${code} - ${project.name}` : project.name;
                  return (
                    <option key={idString} value={idString}>
                      {label}
                    </option>
                  );
                })}
              </Select>
            ) : (
              <p className="text-sm text-gray-600">
                No projects available yet. Ask your administrator to add one before creating batches.
              </p>
            )}
          </CardContent>
        </Card>

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
                {/* 💡 <strong>Tip:</strong> If this batch is part of a larger pour (e.g., multiple vehicles for one slab), */}
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
              {/* Driver Name removed from form intentionally */}
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
          <Link href={batchesListHref}>
            <Button type="button" variant="outline">
              Cancel
            </Button>
          </Link>
          <Button type="submit" disabled={loading || !activeProjectId}>
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

export default function NewBatchPage() {
  return (
    <Suspense fallback={<LoadingScreen message="Loading batch form..." />}>
      <NewBatchContent />
    </Suspense>
  );
}
