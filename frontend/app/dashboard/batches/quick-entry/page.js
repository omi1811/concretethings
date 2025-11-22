'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { ArrowLeft, Save, Truck, Clock, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/Card';
import { Alert } from '@/components/ui/Alert';
import { Input, Select, Textarea } from '@/components/ui/Input';
import { pourActivityAPI } from '@/lib/api-optimized';
import axios from 'axios';

function QuickEntryContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const pourIdFromQuery = searchParams.get('pourId');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [pourActivities, setPourActivities] = useState([]);
  const [selectedPour, setSelectedPour] = useState(null);

  const [formData, setFormData] = useState({
    vehicleNumber: '',
    vendorName: '',
    grade: 'M30',
    quantityReceived: '',
    deliveryDate: new Date().toISOString().split('T')[0],
    deliveryTime: new Date().toTimeString().slice(0, 5),
    slump: '',
    temperature: '',
    location: '',
    remarks: '',
    pourActivityId: pourIdFromQuery || ''
  });

  useEffect(() => {
    const projectId = localStorage.getItem('currentProjectId') || '1';
    loadPourActivities(projectId);

    if (pourIdFromQuery) {
      loadPourActivity(pourIdFromQuery);
    }
  }, [pourIdFromQuery]);

  async function loadPourActivities(projectId) {
    try {
      const result = await pourActivityAPI.getAll({
        projectId,
        status: 'in_progress'
      });
      const activities = result?.data?.pourActivities || result?.pourActivities || [];
      setPourActivities(Array.isArray(activities) ? activities : []);
    } catch (error) {
      console.error('Error loading pour activities:', error);
    }
  }

  async function loadPourActivity(pourId) {
    try {
      const result = await pourActivityAPI.getById(pourId);
      const pour = result?.data?.pourActivity || result?.pourActivity;
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

  const handlePourChange = (e) => {
    const pourId = e.target.value;
    setFormData(prev => ({ ...prev, pourActivityId: pourId }));

    if (pourId) {
      const pour = pourActivities.find(p => p.id === parseInt(pourId));
      if (pour) {
        setSelectedPour(pour);
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
      const projectId = localStorage.getItem('currentProjectId') || '1';
      const token = localStorage.getItem('auth_token');

      const payload = {
        projectId: parseInt(projectId),
        pourActivityId: formData.pourActivityId ? parseInt(formData.pourActivityId) : undefined,
        vehicleNumber: formData.vehicleNumber,
        vendorName: formData.vendorName,
        grade: formData.grade,
        quantityReceived: parseFloat(formData.quantityReceived),
        deliveryDate: formData.deliveryDate,
        deliveryTime: formData.deliveryTime,
        slump: formData.slump ? parseInt(formData.slump) : undefined,
        temperature: formData.temperature ? parseInt(formData.temperature) : undefined,
        location: formData.location,
        remarks: formData.remarks || 'Quick entry - vehicle register maintained by security'
      };

      const response = await axios.post('/api/batches/quick-entry', payload, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.data) {
        setSuccess('Batch created successfully via quick entry!');

        // Reset form
        setFormData({
          vehicleNumber: '',
          vendorName: formData.vendorName, // Keep vendor name
          grade: formData.grade, // Keep grade
          quantityReceived: '',
          deliveryDate: new Date().toISOString().split('T')[0],
          deliveryTime: new Date().toTimeString().slice(0, 5),
          slump: '',
          temperature: '',
          location: formData.location, // Keep location
          remarks: '',
          pourActivityId: formData.pourActivityId // Keep pour selection
        });

        // Show success for 2 seconds then optionally redirect
        setTimeout(() => {
          setSuccess('');
        }, 2000);
      }
    } catch (err) {
      console.error('Error creating batch:', err);
      setError(err.response?.data?.error || err.message || 'Failed to create batch');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto animate-in fade-in duration-500">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/dashboard/batches">
          <Button variant="outline" size="sm">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
        </Link>
        <div className="flex-1">
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Quick Batch Entry</h1>
          <p className="text-muted-foreground mt-1">Fast entry for sites with external vehicle registers</p>
        </div>
        <Link href="/dashboard/batches/new">
          <Button variant="outline" size="sm">
            Full Form
          </Button>
        </Link>
      </div>

      {/* Info Alert */}
      <Alert variant="info" className="bg-blue-50/50 dark:bg-blue-900/10 border-blue-200 dark:border-blue-800">
        <AlertCircle className="w-4 h-4 text-blue-600 dark:text-blue-400" />
        <div>
          <p className="font-medium text-blue-900 dark:text-blue-300">Simplified Entry Mode</p>
          <p className="text-sm mt-1 text-blue-700 dark:text-blue-400">
            This form captures only QC-relevant data. Use this when vehicle entry details are maintained separately by security.
          </p>
        </div>
      </Alert>

      {error && (
        <Alert variant="danger" onClose={() => setError('')}>
          <AlertCircle className="w-4 h-4" />
          {error}
        </Alert>
      )}

      {success && (
        <Alert variant="success" onClose={() => setSuccess('')}>
          <CheckCircle2 className="w-4 h-4" />
          {success}
        </Alert>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Pour Activity (Optional) */}
        {pourActivities.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Link to Pour Activity (Optional)</CardTitle>
            </CardHeader>
            <CardContent>
              <Select
                label="Select Pour Activity"
                value={formData.pourActivityId}
                onChange={handlePourChange}
              >
                <option value="">No pour activity</option>
                {pourActivities.map(pour => (
                  <option key={pour.id} value={pour.id}>
                    {pour.pourId} - {pour.location?.gridReference} ({pour.designGrade})
                  </option>
                ))}
              </Select>

              {selectedPour && (
                <div className="mt-3 p-3 bg-primary/5 border border-primary/10 rounded-md text-sm text-primary">
                  <strong>Linked to:</strong> {selectedPour.location?.description}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Essential Details */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Truck className="w-5 h-5 text-primary" />
              Vehicle & Delivery
            </CardTitle>
            <CardDescription>Enter the delivery details as per the challan.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Vehicle Number"
                name="vehicleNumber"
                value={formData.vehicleNumber}
                onChange={handleChange}
                required
                placeholder="e.g., MH-01-1234"
              />

              <Input
                label="Vendor Name"
                name="vendorName"
                value={formData.vendorName}
                onChange={handleChange}
                required
                placeholder="e.g., ABC Concrete"
              />

              <Select
                label="Grade"
                name="grade"
                value={formData.grade}
                onChange={handleChange}
                required
              >
                <option value="M20">M20</option>
                <option value="M25">M25</option>
                <option value="M30">M30</option>
                <option value="M35">M35</option>
                <option value="M40">M40</option>
                <option value="M45">M45</option>
                <option value="M50">M50</option>
              </Select>

              <Input
                label="Quantity (m³)"
                type="number"
                name="quantityReceived"
                value={formData.quantityReceived}
                onChange={handleChange}
                step="0.1"
                min="0.1"
                required
                placeholder="e.g., 1.5"
              />
            </div>
          </CardContent>
        </Card>

        {/* Delivery Time */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Clock className="w-5 h-5 text-primary" />
              Delivery Time
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Date"
                type="date"
                name="deliveryDate"
                value={formData.deliveryDate}
                onChange={handleChange}
                required
              />

              <Input
                label="Time"
                type="time"
                name="deliveryTime"
                value={formData.deliveryTime}
                onChange={handleChange}
                required
              />
            </div>
          </CardContent>
        </Card>

        {/* Optional QC Data */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Quality Control (Optional)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Slump (mm)"
                type="number"
                name="slump"
                value={formData.slump}
                onChange={handleChange}
                placeholder="e.g., 100"
              />

              <Input
                label="Temperature (°C)"
                type="number"
                name="temperature"
                value={formData.temperature}
                onChange={handleChange}
                placeholder="e.g., 32"
              />

              <div className="md:col-span-2">
                <Input
                  label="Location"
                  name="location"
                  value={formData.location}
                  onChange={handleChange}
                  placeholder="e.g., Grid A-12, Slab"
                />
              </div>

              <div className="md:col-span-2">
                <Textarea
                  label="Remarks"
                  name="remarks"
                  value={formData.remarks}
                  onChange={handleChange}
                  rows={2}
                  placeholder="Additional notes..."
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex gap-4">
          <Button type="submit" disabled={loading} className="flex-1">
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
                Saving...
              </>
            ) : (
              <>
                <Save className="w-4 h-4 mr-2" />
                Save & Continue
              </>
            )}
          </Button>
          <Link href="/dashboard/batches">
            <Button type="button" variant="outline">
              Done
            </Button>
          </Link>
        </div>
      </form>
    </div>
  );
}

export default function QuickEntryBatchPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
          <p className="text-muted-foreground">Loading form...</p>
        </div>
      </div>
    }>
      <QuickEntryContent />
    </Suspense>
  );
}
