'use client';

import { useState } from 'react';
import { 
  AlertTriangle, Save, Clock, MapPin, Users, FileText, 
  Upload, AlertOctagon, User, Calendar
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';

export default function NewIncidentPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    incident_type: 'NEAR_MISS',
    incident_date: new Date().toISOString().split('T')[0],
    incident_time: new Date().toTimeString().split(' ')[0].substring(0, 5),
    location: '',
    severity: 'minor',
    description: '',
    immediate_action: '',
    witnesses: '',
    injured_persons: '',
    reportable: false,
    lost_time_days: 0,
    medical_cost: 0,
    property_cost: 0
  });

  const incidentTypes = [
    { value: 'INJURY', label: 'Injury', icon: '🤕', desc: 'Physical injury to a person' },
    { value: 'NEAR_MISS', label: 'Near Miss', icon: '⚠️', desc: 'Incident with no injury but potential for harm' },
    { value: 'PROPERTY_DAMAGE', label: 'Property Damage', icon: '🏗️', desc: 'Damage to equipment or infrastructure' },
    { value: 'ENVIRONMENTAL', label: 'Environmental', icon: '🌍', desc: 'Environmental impact or spill' },
    { value: 'EQUIPMENT_FAILURE', label: 'Equipment Failure', icon: '⚙️', desc: 'Machinery or equipment malfunction' },
    { value: 'FIRE', label: 'Fire', icon: '🔥', desc: 'Fire incident' },
    { value: 'CHEMICAL_SPILL', label: 'Chemical Spill', icon: '☣️', desc: 'Hazardous chemical release' },
    { value: 'FALL_FROM_HEIGHT', label: 'Fall from Height', icon: '🪜', desc: 'Fall from elevated position' },
    { value: 'ELECTRIC_SHOCK', label: 'Electric Shock', icon: '⚡', desc: 'Electrical hazard incident' },
    { value: 'VEHICLE_ACCIDENT', label: 'Vehicle Accident', icon: '🚗', desc: 'Vehicle collision or accident' },
    { value: 'FATALITY', label: 'Fatality', icon: '💀', desc: 'Fatal incident (CRITICAL)' }
  ];

  const severityLevels = [
    { value: 'minor', label: 'Minor', color: 'yellow', desc: 'First aid only, no lost time' },
    { value: 'major', label: 'Major', color: 'orange', desc: 'Medical treatment required, some lost time' },
    { value: 'critical', label: 'Critical', color: 'red', desc: 'Serious injury, significant lost time' },
    { value: 'fatal', label: 'Fatal', color: 'red', desc: 'Fatality or permanent disability' }
  ];

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.location || !formData.description) {
      toast.error('Please fill in all required fields');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const projectId = localStorage.getItem('activeProjectId');
      
      const response = await fetch('/api/incidents', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          ...formData,
          project_id: parseInt(projectId),
          reported_by: parseInt(localStorage.getItem('userId'))
        })
      });

      if (!response.ok) throw new Error('Failed to create incident');

      const data = await response.json();
      toast.success('Incident reported successfully');
      router.push(`/dashboard/incidents/${data.incident.id}`);
    } catch (error) {
      console.error('Error creating incident:', error);
      toast.error('Failed to create incident');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
            <AlertTriangle className="w-6 h-6 text-red-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Report New Incident</h1>
            <p className="text-sm text-gray-600">Document workplace incident for investigation</p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Incident Type Selection */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <AlertOctagon className="w-5 h-5 text-red-600" />
            Incident Type*
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {incidentTypes.map((type) => (
              <label
                key={type.value}
                className={`relative flex items-start p-4 border-2 rounded-lg cursor-pointer transition ${
                  formData.incident_type === type.value
                    ? 'border-red-500 bg-red-50'
                    : 'border-gray-200 hover:border-red-300'
                }`}
              >
                <input
                  type="radio"
                  name="incident_type"
                  value={type.value}
                  checked={formData.incident_type === type.value}
                  onChange={handleChange}
                  className="sr-only"
                />
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-2xl">{type.icon}</span>
                    <span className="font-medium text-gray-900">{type.label}</span>
                  </div>
                  <p className="text-xs text-gray-600">{type.desc}</p>
                </div>
                {formData.incident_type === type.value && (
                  <div className="absolute top-2 right-2 w-5 h-5 bg-red-600 rounded-full flex items-center justify-center">
                    <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                )}
              </label>
            ))}
          </div>
        </div>

        {/* Date, Time & Location */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Calendar className="w-5 h-5 text-gray-600" />
            When & Where
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <Calendar className="w-4 h-4 inline mr-1" />
                Incident Date*
              </label>
              <input
                type="date"
                name="incident_date"
                value={formData.incident_date}
                onChange={handleChange}
                max={new Date().toISOString().split('T')[0]}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <Clock className="w-4 h-4 inline mr-1" />
                Incident Time*
              </label>
              <input
                type="time"
                name="incident_time"
                value={formData.incident_time}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <MapPin className="w-4 h-4 inline mr-1" />
                Location*
              </label>
              <input
                type="text"
                name="location"
                value={formData.location}
                onChange={handleChange}
                placeholder="e.g., Block A, Ground Floor"
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
              />
            </div>
          </div>
        </div>

        {/* Severity */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-orange-600" />
            Severity*
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            {severityLevels.map((severity) => (
              <label
                key={severity.value}
                className={`relative flex flex-col p-4 border-2 rounded-lg cursor-pointer transition ${
                  formData.severity === severity.value
                    ? `border-${severity.color}-500 bg-${severity.color}-50`
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <input
                  type="radio"
                  name="severity"
                  value={severity.value}
                  checked={formData.severity === severity.value}
                  onChange={handleChange}
                  className="sr-only"
                />
                <span className="font-medium text-gray-900 mb-1">{severity.label}</span>
                <span className="text-xs text-gray-600">{severity.desc}</span>
                {formData.severity === severity.value && (
                  <div className={`absolute top-2 right-2 w-5 h-5 bg-${severity.color}-600 rounded-full flex items-center justify-center`}>
                    <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                )}
              </label>
            ))}
          </div>
        </div>

        {/* Description & Immediate Action */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5 text-gray-600" />
            Incident Details
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Incident Description*
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={4}
                placeholder="Describe what happened in detail..."
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Immediate Action Taken*
              </label>
              <textarea
                name="immediate_action"
                value={formData.immediate_action}
                onChange={handleChange}
                rows={3}
                placeholder="What immediate actions were taken to secure the area and help victims?"
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
              />
            </div>
          </div>
        </div>

        {/* Witnesses & Injured Persons */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Users className="w-5 h-5 text-gray-600" />
            People Involved
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Witnesses (Names, separated by commas)
              </label>
              <textarea
                name="witnesses"
                value={formData.witnesses}
                onChange={handleChange}
                rows={3}
                placeholder="e.g., Rajesh Kumar, Amit Singh, Priya Sharma"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Injured Persons (Names & injuries)
              </label>
              <textarea
                name="injured_persons"
                value={formData.injured_persons}
                onChange={handleChange}
                rows={3}
                placeholder="e.g., Mohan Lal - Hand injury, Suresh - Minor cut"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
              />
            </div>
          </div>
        </div>

        {/* Cost & Impact */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">Cost & Impact</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Lost Time (Days)
              </label>
              <input
                type="number"
                name="lost_time_days"
                value={formData.lost_time_days}
                onChange={handleChange}
                min="0"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Medical Cost (₹)
              </label>
              <input
                type="number"
                name="medical_cost"
                value={formData.medical_cost}
                onChange={handleChange}
                min="0"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Property Damage Cost (₹)
              </label>
              <input
                type="number"
                name="property_cost"
                value={formData.property_cost}
                onChange={handleChange}
                min="0"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
              />
            </div>
          </div>
          <div className="mt-4">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                name="reportable"
                checked={formData.reportable}
                onChange={handleChange}
                className="w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
              />
              <span className="text-sm font-medium text-gray-700">
                Reportable to Authority (DGFASLI, Labour Department)
              </span>
            </label>
          </div>
        </div>

        {/* Info Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex gap-3">
            <AlertTriangle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">What happens next?</p>
              <ol className="list-decimal list-inside space-y-1">
                <li>Safety Officer will be automatically notified</li>
                <li>Investigation team will be assigned</li>
                <li>Root cause analysis will be conducted</li>
                <li>Corrective actions will be defined</li>
                <li>Incident will be reviewed and closed</li>
              </ol>
            </div>
          </div>
        </div>

        {/* Submit Buttons */}
        <div className="flex gap-3">
          <button
            type="button"
            onClick={() => router.back()}
            className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 transition"
          >
            {loading ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Creating...
              </>
            ) : (
              <>
                <Save className="w-5 h-5" />
                Report Incident
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
