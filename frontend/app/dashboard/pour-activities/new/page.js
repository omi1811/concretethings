'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Save, MapPin, Layers } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { pourActivityAPI } from '@/lib/api';

export default function NewPourActivityPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    pourDate: new Date().toISOString().slice(0, 16),
    buildingName: '',
    floorLevel: '',
    zone: '',
    gridReference: '',
    structuralElementType: 'Slab',
    elementId: '',
    locationDescription: '',
    concreteType: 'Normal',
    designGrade: 'M30',
    totalQuantityPlanned: '',
    remarks: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const projectId = localStorage.getItem('currentProjectId') || '1';
      
      const payload = {
        projectId: parseInt(projectId),
        pourDate: formData.pourDate,
        location: {
          buildingName: formData.buildingName,
          floorLevel: formData.floorLevel,
          zone: formData.zone,
          gridReference: formData.gridReference,
          structuralElementType: formData.structuralElementType,
          elementId: formData.elementId,
          description: formData.locationDescription
        },
        concreteType: formData.concreteType,
        designGrade: formData.designGrade,
        totalQuantityPlanned: parseFloat(formData.totalQuantityPlanned),
        remarks: formData.remarks
      };

      const result = await pourActivityAPI.create(payload);
      
      if (result.success) {
        // Show success message
        alert('Pour activity created successfully!');
        // Redirect to pour detail page
        router.push(`/dashboard/pour-activities/${result.data.pourActivity.id}`);
      } else {
        alert('Error creating pour activity: ' + (result.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error creating pour activity:', error);
      alert('Error creating pour activity. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/dashboard/pour-activities">
          <Button variant="outline" size="sm">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">New Pour Activity</h1>
          <p className="text-gray-600 mt-1">Create a new concrete pouring activity</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Details */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Layers className="w-5 h-5" />
              Pour Details
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Pour Date & Time *
                </label>
                <input
                  type="datetime-local"
                  name="pourDate"
                  value={formData.pourDate}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Concrete Type *
                </label>
                <select
                  name="concreteType"
                  value={formData.concreteType}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="Normal">Normal Concrete</option>
                  <option value="PT">Post-Tensioned (PT) Concrete</option>
                </select>
                {formData.concreteType === 'PT' && (
                  <p className="mt-1 text-xs text-blue-600">
                    ℹ️ PT concrete will be tested at 5 days (instead of 3 days)
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Design Grade *
                </label>
                <select
                  name="designGrade"
                  value={formData.designGrade}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="M20">M20</option>
                  <option value="M25">M25</option>
                  <option value="M30">M30</option>
                  <option value="M35">M35</option>
                  <option value="M40">M40</option>
                  <option value="M45">M45</option>
                  <option value="M50">M50</option>
                  <option value="M40FF">M40 Free Flow</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Planned Quantity (m³) *
                </label>
                <input
                  type="number"
                  name="totalQuantityPlanned"
                  value={formData.totalQuantityPlanned}
                  onChange={handleChange}
                  step="0.1"
                  min="0.1"
                  required
                  placeholder="e.g., 4.0"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Location Details */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="w-5 h-5" />
              Location Details
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Building Name
                </label>
                <input
                  type="text"
                  name="buildingName"
                  value={formData.buildingName}
                  onChange={handleChange}
                  placeholder="e.g., Tower A"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Floor Level
                </label>
                <input
                  type="text"
                  name="floorLevel"
                  value={formData.floorLevel}
                  onChange={handleChange}
                  placeholder="e.g., Level 5"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Zone
                </label>
                <input
                  type="text"
                  name="zone"
                  value={formData.zone}
                  onChange={handleChange}
                  placeholder="e.g., North Wing"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Grid Reference *
                </label>
                <input
                  type="text"
                  name="gridReference"
                  value={formData.gridReference}
                  onChange={handleChange}
                  required
                  placeholder="e.g., A-12"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Structural Element Type *
                </label>
                <select
                  name="structuralElementType"
                  value={formData.structuralElementType}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="Beam">Beam</option>
                  <option value="Column">Column</option>
                  <option value="Slab">Slab</option>
                  <option value="Footing">Footing</option>
                  <option value="Wall">Wall</option>
                  <option value="Foundation">Foundation</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Element ID
                </label>
                <input
                  type="text"
                  name="elementId"
                  value={formData.elementId}
                  onChange={handleChange}
                  placeholder="e.g., S-A12-L5"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Location Description *
              </label>
              <textarea
                name="locationDescription"
                value={formData.locationDescription}
                onChange={handleChange}
                required
                rows={3}
                placeholder="e.g., Slab at Grid A-12, Level 5, North Wing"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </CardContent>
        </Card>

        {/* Remarks */}
        <Card>
          <CardContent className="pt-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Remarks
              </label>
              <textarea
                name="remarks"
                value={formData.remarks}
                onChange={handleChange}
                rows={3}
                placeholder="Additional notes about this pour activity..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex gap-4">
          <Button type="submit" disabled={loading} className="flex-1">
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                Creating...
              </>
            ) : (
              <>
                <Save className="w-4 h-4 mr-2" />
                Create Pour Activity
              </>
            )}
          </Button>
          <Link href="/dashboard/pour-activities">
            <Button type="button" variant="outline">
              Cancel
            </Button>
          </Link>
        </div>
      </form>
    </div>
  );
}
