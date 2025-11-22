'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Save, MapPin, Layers } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { pourActivityAPI } from '@/lib/api-optimized';

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
    concreteType: 'Conventional',
    designGrade: 'M30',
    totalQuantityPlanned: '',
    remarks: ''
  });

  const [cubeSchedule, setCubeSchedule] = useState([
    { age: 7, sets: 1 },
    { age: 28, sets: 1 }
  ]);

  const updateSchedule = (type) => {
    let newSchedule = [];
    if (type === 'Conventional') {
      newSchedule = [{ age: 7, sets: 1 }, { age: 28, sets: 1 }];
    } else if (type === 'Free Flow Aluform') {
      newSchedule = [{ age: 3, sets: 1 }, { age: 7, sets: 1 }, { age: 28, sets: 1 }];
    } else if (type === 'PT') {
      newSchedule = [{ age: 5, sets: 1 }, { age: 7, sets: 1 }, { age: 28, sets: 1 }];
    }
    setCubeSchedule(newSchedule);
  };

  const handleScheduleChange = (index, field, value) => {
    const newSchedule = [...cubeSchedule];
    newSchedule[index][field] = parseInt(value) || 0;
    setCubeSchedule(newSchedule);
  };

  const addScheduleItem = () => {
    setCubeSchedule([...cubeSchedule, { age: 0, sets: 1 }]);
  };

  const removeScheduleItem = (index) => {
    setCubeSchedule(cubeSchedule.filter((_, i) => i !== index));
  };

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
          description: formData.locationDescription,
        },
        concreteType: formData.concreteType,
        designGrade: formData.designGrade,
        totalQuantityPlanned: parseFloat(formData.totalQuantityPlanned),
        remarks: formData.remarks,
        cubeSchedule: cubeSchedule
      };
      const result = await pourActivityAPI.create(payload);
      const pourActivity = result?.data?.pourActivity || result?.pourActivity;

      if (pourActivity) {
        alert('Pour activity created successfully!');
        router.push(`/dashboard/pour-activities/${pourActivity.id}`);
        return;
      }

      const message = result?.error || result?.message || 'Unknown error creating pour activity';
      alert(`Error creating pour activity: ${message}`);
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
    if (name === 'concreteType') {
      updateSchedule(value);
    }
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
                  <option value="Conventional">Conventional Concrete</option>
                  <option value="Free Flow Aluform">Free Flow Aluform Concrete</option>
                  <option value="PT">Post-Tensioned (PT) Concrete</option>
                </select>
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
                  <optgroup label="Conventional">
                    <option value="M10">M10</option>
                    <option value="M15">M15</option>
                    <option value="M20">M20</option>
                    <option value="M25">M25</option>
                    <option value="M30">M30</option>
                    <option value="M35">M35</option>
                    <option value="M40">M40</option>
                    <option value="M45">M45</option>
                    <option value="M50">M50</option>
                    <option value="M55">M55</option>
                    <option value="M60">M60</option>
                  </optgroup>
                  <optgroup label="Free Flow Aluform">
                    <option value="M20FF">M20FF</option>
                    <option value="M25FF">M25FF</option>
                    <option value="M30FF">M30FF</option>
                    <option value="M35FF">M35FF</option>
                    <option value="M40FF">M40FF</option>
                    <option value="M45FF">M45FF</option>
                    <option value="M50FF">M50FF</option>
                    <option value="M60FF">M60FF</option>
                  </optgroup>
                  <optgroup label="Post-Tensioned (PT)">
                    <option value="M30PT">M30PT</option>
                    <option value="M35PT">M35PT</option>
                    <option value="M40PT">M40PT</option>
                    <option value="M50PT">M50PT</option>
                  </optgroup>
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

        {/* Testing Schedule */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Layers className="w-5 h-5" />
              Cube Testing Schedule
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-gray-500">
              Define the planned testing schedule. Reminders will be sent automatically.
            </p>
            <div className="space-y-2">
              {cubeSchedule.map((item, index) => (
                <div key={index} className="flex gap-4 items-center">
                  <div className="flex-1">
                    <label className="block text-xs font-medium text-gray-500 mb-1">Test Age (Days)</label>
                    <input
                      type="number"
                      value={item.age}
                      onChange={(e) => handleScheduleChange(index, 'age', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div className="flex-1">
                    <label className="block text-xs font-medium text-gray-500 mb-1">Number of Sets</label>
                    <input
                      type="number"
                      value={item.sets}
                      onChange={(e) => handleScheduleChange(index, 'sets', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                  <div className="pt-5">
                    <Button type="button" variant="ghost" size="sm" onClick={() => removeScheduleItem(index)} className="text-red-500">
                      Remove
                    </Button>
                  </div>
                </div>
              ))}
              <Button type="button" variant="outline" size="sm" onClick={addScheduleItem} className="mt-2">
                + Add Test Age
              </Button>
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
