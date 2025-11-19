'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Save } from 'lucide-react';
import toast from 'react-hot-toast';

export default function NewConcreteNCPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    description: '',
    issue_type: '',
    vendor_name: '',
    batch_number: '',
    cube_test_id: '',
    corrective_action_required: ''
  });

  const handleChange = (e) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.description || !formData.vendor_name) {
      toast.error('Please fill in all required fields');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/concrete/nc/issues', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        const data = await response.json();
        toast.success('Concrete NC raised successfully');
        router.push(`/dashboard/concrete-nc/${data.issue?.id || data.id}`);
      } else {
        const error = await response.json();
        toast.error(error.error || 'Failed to raise NC');
      }
    } catch (error) {
      console.error('Error:', error);
      toast.error('Error raising NC');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <Link href="/dashboard/concrete-nc" className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4">
          <ArrowLeft className="w-4 h-4" />
          Back to Concrete NCs
        </Link>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Raise Concrete Non-Conformance</h1>
        <p className="text-gray-600">Report a concrete quality issue</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-white rounded-lg border p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">NC Details</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Issue Type *</label>
              <select
                name="issue_type"
                value={formData.issue_type}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select issue type...</option>
                <option value="Cube Test Failure">Cube Test Failure</option>
                <option value="Slump Test Failure">Slump Test Failure</option>
                <option value="Wrong Mix Design">Wrong Mix Design</option>
                <option value="Delayed Supply">Delayed Supply</option>
                <option value="Quantity Shortage">Quantity Shortage</option>
                <option value="Segregation">Segregation</option>
                <option value="Cold Joints">Cold Joints</option>
                <option value="Honeycombing">Honeycombing</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description *</label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                required
                rows={4}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Describe the quality issue in detail..."
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Vendor Name *</label>
                <input
                  type="text"
                  name="vendor_name"
                  value={formData.vendor_name}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="RMC vendor name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Batch Number</label>
                <input
                  type="text"
                  name="batch_number"
                  value={formData.batch_number}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Related batch number"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Cube Test ID (if applicable)</label>
              <input
                type="text"
                name="cube_test_id"
                value={formData.cube_test_id}
                onChange={handleChange}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Related cube test ID"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Corrective Action Required</label>
              <textarea
                name="corrective_action_required"
                value={formData.corrective_action_required}
                onChange={handleChange}
                rows={3}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="What needs to be done to resolve this issue?"
              />
            </div>
          </div>
        </div>

        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h3 className="font-medium text-yellow-900 mb-2">📊 Vendor Scoring</h3>
          <p className="text-sm text-yellow-700">
            This NC will affect the vendor's performance score. The vendor will be notified and can respond with their corrective actions.
          </p>
        </div>

        <div className="flex gap-3 justify-end">
          <Link href="/dashboard/concrete-nc" className="px-6 py-2 border text-gray-700 rounded-lg hover:bg-gray-50">
            Cancel
          </Link>
          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            {loading ? 'Raising NC...' : 'Raise NC'}
          </button>
        </div>
      </form>
    </div>
  );
}
