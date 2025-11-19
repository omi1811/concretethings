'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Save } from 'lucide-react';
import toast from 'react-hot-toast';

const COMMON_GRADES = ['M10', 'M15', 'M20', 'M25', 'M30', 'M35', 'M40', 'M45', 'M50', 'M55', 'M60'];

export default function NewMixDesignPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    grade: '',
    mix_id: '',
    description: '',
    target_strength: '',
    wc_ratio: '',
    cement_content: '',
    water_content: '',
    fine_aggregate: '',
    coarse_aggregate: '',
    slump: '',
    admixture_type: '',
    admixture_dosage: ''
  });

  const handleChange = (e) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.grade || !formData.target_strength) {
      toast.error('Please fill in all required fields');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/mix-designs', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        const data = await response.json();
        toast.success('Mix design created successfully');
        router.push(`/dashboard/mix-designs/${data.mix_design?.id || data.id}`);
      } else {
        const error = await response.json();
        toast.error(error.error || 'Failed to create mix design');
      }
    } catch (error) {
      console.error('Error:', error);
      toast.error('Error creating mix design');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <Link href="/dashboard/mix-designs" className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4">
          <ArrowLeft className="w-4 h-4" />
          Back to Mix Designs
        </Link>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">New Mix Design</h1>
        <p className="text-gray-600">Create concrete mix design per IS 456:2000 & IS 10262:2019</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Info */}
        <div className="bg-white rounded-lg border p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Grade *</label>
                <select
                  name="grade"
                  value={formData.grade}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select grade...</option>
                  {COMMON_GRADES.map(grade => (
                    <option key={grade} value={grade}>{grade}</option>
                  ))}
                  <option value="custom">Custom Grade</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Mix ID</label>
                <input
                  type="text"
                  name="mix_id"
                  value={formData.mix_id}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., MIX-2024-001"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={2}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Purpose and application of this mix design..."
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Target Strength (MPa) *</label>
                <input
                  type="number"
                  name="target_strength"
                  value={formData.target_strength}
                  onChange={handleChange}
                  required
                  step="0.1"
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., 30"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">W/C Ratio</label>
                <input
                  type="number"
                  name="wc_ratio"
                  value={formData.wc_ratio}
                  onChange={handleChange}
                  step="0.01"
                  max="0.70"
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., 0.45"
                />
                <p className="mt-1 text-xs text-gray-500">Max 0.70 per IS 456:2000</p>
              </div>
            </div>
          </div>
        </div>

        {/* Material Proportions */}
        <div className="bg-white rounded-lg border p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Material Proportions (per m³)</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Cement Content (kg)</label>
              <input
                type="number"
                name="cement_content"
                value={formData.cement_content}
                onChange={handleChange}
                step="0.1"
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., 350"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Water Content (liters)</label>
              <input
                type="number"
                name="water_content"
                value={formData.water_content}
                onChange={handleChange}
                step="0.1"
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., 157.5"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Fine Aggregate (kg)</label>
              <input
                type="number"
                name="fine_aggregate"
                value={formData.fine_aggregate}
                onChange={handleChange}
                step="0.1"
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., 650"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Coarse Aggregate (kg)</label>
              <input
                type="number"
                name="coarse_aggregate"
                value={formData.coarse_aggregate}
                onChange={handleChange}
                step="0.1"
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., 1200"
              />
            </div>
          </div>
        </div>

        {/* Properties */}
        <div className="bg-white rounded-lg border p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Fresh Concrete Properties</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Slump (mm)</label>
              <input
                type="number"
                name="slump"
                value={formData.slump}
                onChange={handleChange}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., 100"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Admixture Type</label>
              <select
                name="admixture_type"
                value={formData.admixture_type}
                onChange={handleChange}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">None</option>
                <option value="Superplasticizer">Superplasticizer</option>
                <option value="Retarder">Retarder</option>
                <option value="Accelerator">Accelerator</option>
                <option value="Air Entraining">Air Entraining</option>
              </select>
            </div>
            {formData.admixture_type && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Admixture Dosage (% by cement wt)</label>
                <input
                  type="number"
                  name="admixture_dosage"
                  value={formData.admixture_dosage}
                  onChange={handleChange}
                  step="0.01"
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., 0.8"
                />
              </div>
            )}
          </div>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-medium text-blue-900 mb-2">📋 Standards Compliance</h3>
          <ul className="text-sm text-blue-700 space-y-1 list-disc list-inside">
            <li>IS 456:2000 - Plain and Reinforced Concrete</li>
            <li>IS 10262:2019 - Concrete Mix Proportioning Guidelines</li>
            <li>IS 383:2016 - Coarse and Fine Aggregates Specification</li>
          </ul>
        </div>

        <div className="flex gap-3 justify-end">
          <Link href="/dashboard/mix-designs" className="px-6 py-2 border text-gray-700 rounded-lg hover:bg-gray-50">
            Cancel
          </Link>
          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            {loading ? 'Creating...' : 'Create Mix Design'}
          </button>
        </div>
      </form>
    </div>
  );
}
