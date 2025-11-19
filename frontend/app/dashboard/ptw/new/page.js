'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Save, Send } from 'lucide-react';
import toast from 'react-hot-toast';

const PERMIT_TYPES = [
  { value: 'hot_work', label: 'Hot Work', description: 'Welding, grinding, cutting, brazing' },
  { value: 'confined_space', label: 'Confined Space', description: 'Tanks, vessels, manholes, sewers' },
  { value: 'height_work', label: 'Height Work', description: 'Work above 1.8m height' },
  { value: 'electrical', label: 'Electrical Work', description: 'Live electrical work' },
  { value: 'excavation', label: 'Excavation', description: 'Digging, trenching, earth moving' }
];

export default function NewPermitPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    permit_type: '',
    work_description: '',
    location: '',
    contractor_name: '',
    contractor_contact: '',
    contractor_license: '',
    valid_from: '',
    valid_until: '',
    number_of_workers: '',
    equipment_required: '',
    hazards_identified: '',
    control_measures: '',
    emergency_procedures: '',
    ppe_required: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e, submitForApproval = false) => {
    e.preventDefault();
    
    // Validation
    if (!formData.permit_type) {
      toast.error('Please select permit type');
      return;
    }
    if (!formData.work_description || !formData.location) {
      toast.error('Please fill in all required fields');
      return;
    }
    if (!formData.contractor_name) {
      toast.error('Please enter contractor name');
      return;
    }
    if (!formData.valid_from || !formData.valid_until) {
      toast.error('Please specify permit validity dates');
      return;
    }

    // Check valid_from is not in the past
    if (new Date(formData.valid_from) < new Date()) {
      toast.error('Valid from date cannot be in the past');
      return;
    }

    // Check valid_until is after valid_from
    if (new Date(formData.valid_until) <= new Date(formData.valid_from)) {
      toast.error('Valid until date must be after valid from date');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      
      // Create permit
      const response = await fetch('/api/safety/permits', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        const data = await response.json();
        const permitId = data.permit?.id || data.id;

        // If submit for approval, call submit endpoint
        if (submitForApproval && permitId) {
          const submitResponse = await fetch(`/api/safety/permits/${permitId}/submit`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          });

          if (submitResponse.ok) {
            toast.success('Permit created and submitted for approval');
          } else {
            toast.success('Permit created but failed to submit');
          }
        } else {
          toast.success('Permit saved as draft');
        }

        router.push(`/dashboard/ptw/${permitId}`);
      } else {
        const error = await response.json();
        toast.error(error.error || 'Failed to create permit');
      }
    } catch (error) {
      console.error('Error creating permit:', error);
      toast.error('Error creating permit');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <Link
          href="/dashboard/ptw"
          className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Permits
        </Link>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">New Permit to Work</h1>
        <p className="text-gray-600">Create a new work permit for high-risk activities</p>
      </div>

      {/* Form */}
      <form onSubmit={(e) => handleSubmit(e, false)} className="space-y-6">
        {/* Permit Type */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Permit Type</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {PERMIT_TYPES.map((type) => (
              <label
                key={type.value}
                className={`relative flex flex-col p-4 border-2 rounded-lg cursor-pointer transition-all ${
                  formData.permit_type === type.value
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <input
                  type="radio"
                  name="permit_type"
                  value={type.value}
                  checked={formData.permit_type === type.value}
                  onChange={handleChange}
                  className="sr-only"
                  required
                />
                <span className="font-medium text-gray-900">{type.label}</span>
                <span className="text-sm text-gray-500 mt-1">{type.description}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Work Details */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Work Details</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Work Description *
              </label>
              <textarea
                name="work_description"
                value={formData.work_description}
                onChange={handleChange}
                rows={3}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Describe the work to be performed..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Location *
              </label>
              <input
                type="text"
                name="location"
                value={formData.location}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Work location on site"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Valid From *
                </label>
                <input
                  type="datetime-local"
                  name="valid_from"
                  value={formData.valid_from}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Valid Until *
                </label>
                <input
                  type="datetime-local"
                  name="valid_until"
                  value={formData.valid_until}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Contractor Details */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Contractor Details</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Contractor Name *
              </label>
              <input
                type="text"
                name="contractor_name"
                value={formData.contractor_name}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Contractor company name"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Contact Number
                </label>
                <input
                  type="tel"
                  name="contractor_contact"
                  value={formData.contractor_contact}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="+91 XXXXX XXXXX"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  License Number
                </label>
                <input
                  type="text"
                  name="contractor_license"
                  value={formData.contractor_license}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="License/Registration number"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Number of Workers
              </label>
              <input
                type="number"
                name="number_of_workers"
                value={formData.number_of_workers}
                onChange={handleChange}
                min="1"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="0"
              />
            </div>
          </div>
        </div>

        {/* Safety Requirements */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Safety Requirements</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Equipment Required
              </label>
              <textarea
                name="equipment_required"
                value={formData.equipment_required}
                onChange={handleChange}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="List all equipment and tools required..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Hazards Identified
              </label>
              <textarea
                name="hazards_identified"
                value={formData.hazards_identified}
                onChange={handleChange}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Identify potential hazards..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Control Measures
              </label>
              <textarea
                name="control_measures"
                value={formData.control_measures}
                onChange={handleChange}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Describe control measures to mitigate hazards..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Emergency Procedures
              </label>
              <textarea
                name="emergency_procedures"
                value={formData.emergency_procedures}
                onChange={handleChange}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Emergency contact numbers, first aid location..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                PPE Required
              </label>
              <input
                type="text"
                name="ppe_required"
                value={formData.ppe_required}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Safety helmet, gloves, goggles, harness"
              />
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 justify-end">
          <Link
            href="/dashboard/ptw"
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-center"
          >
            Cancel
          </Link>
          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center justify-center gap-2 px-6 py-2 border border-gray-300 text-gray-700 bg-white rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            {loading ? 'Saving...' : 'Save as Draft'}
          </button>
          <button
            type="button"
            onClick={(e) => handleSubmit(e, true)}
            disabled={loading}
            className="inline-flex items-center justify-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            <Send className="w-4 h-4" />
            {loading ? 'Submitting...' : 'Submit for Approval'}
          </button>
        </div>
      </form>
    </div>
  );
}
