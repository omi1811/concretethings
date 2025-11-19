'use client';

import { useState } from 'react';
import { 
  ClipboardCheck, Save, Calendar, Clock, Users, FileText, 
  CheckSquare, AlertTriangle
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';

export default function NewSafetyAuditPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    audit_type: 'SITE_INSPECTION',
    scheduled_date: new Date().toISOString().split('T')[0],
    scheduled_time: '09:00',
    location: '',
    scope: '',
    auditor_name: '',
    auditor_phone: '',
    checklist_items: [],
    special_focus_areas: ''
  });

  const auditTypes = [
    { 
      value: 'SITE_INSPECTION', 
      label: 'Site Safety Inspection', 
      icon: '🏗️',
      desc: 'General site safety walkthrough',
      duration: '2-3 hours'
    },
    { 
      value: 'PPE_COMPLIANCE', 
      label: 'PPE Compliance Check', 
      icon: '🦺',
      desc: 'Personal protective equipment audit',
      duration: '1-2 hours'
    },
    { 
      value: 'WORK_AT_HEIGHT', 
      label: 'Work at Height Audit', 
      icon: '🪜',
      desc: 'Scaffolding, ladders, fall protection',
      duration: '2-3 hours'
    },
    { 
      value: 'ELECTRICAL_SAFETY', 
      label: 'Electrical Safety Audit', 
      icon: '⚡',
      desc: 'Electrical installations and equipment',
      duration: '2-3 hours'
    },
    { 
      value: 'FIRE_SAFETY', 
      label: 'Fire Safety Audit', 
      icon: '🔥',
      desc: 'Fire extinguishers, exits, drills',
      duration: '1-2 hours'
    },
    { 
      value: 'EXCAVATION', 
      label: 'Excavation Safety Audit', 
      icon: '🚧',
      desc: 'Trenches, shoring, barricading',
      duration: '1-2 hours'
    },
    { 
      value: 'HOUSEKEEPING', 
      label: 'Housekeeping Audit', 
      icon: '🧹',
      desc: 'Site cleanliness and organization',
      duration: '1-2 hours'
    },
    { 
      value: 'ISO_45001', 
      label: 'ISO 45001 Audit', 
      icon: '📋',
      desc: 'Full ISO 45001:2018 compliance audit',
      duration: '4-6 hours'
    },
    { 
      value: 'CONTRACTOR_AUDIT', 
      label: 'Contractor Safety Audit', 
      icon: '👷',
      desc: 'Contractor safety management review',
      duration: '2-3 hours'
    }
  ];

  const standardChecklists = {
    'SITE_INSPECTION': [
      'All workers wearing proper PPE',
      'Work permits displayed and valid',
      'Emergency exits clear and marked',
      'Fire extinguishers accessible and inspected',
      'First aid kits available and stocked',
      'Safety signage properly displayed',
      'Housekeeping standards maintained',
      'Materials stored safely',
      'Electrical cords and equipment safe',
      'Scaffolding properly erected and tagged'
    ],
    'PPE_COMPLIANCE': [
      'Hard hats worn by all personnel',
      'Safety shoes in good condition',
      'High-visibility vests worn',
      'Safety glasses/goggles used where required',
      'Gloves appropriate for task',
      'Hearing protection in noisy areas',
      'Respiratory protection where needed',
      'Fall protection harness inspection records',
      'PPE storage and maintenance proper',
      'PPE training records available'
    ],
    'WORK_AT_HEIGHT': [
      'Scaffolding inspection tags current',
      'Guardrails installed on all open edges',
      'Toe boards in place',
      'Fall arrest systems properly anchored',
      'Ladder inspection and condition',
      'Personal fall arrest equipment inspected',
      'Rescue plan in place',
      'Workers trained in fall protection',
      'Debris nets installed where required',
      'Access and egress safe'
    ],
    'ELECTRICAL_SAFETY': [
      'ELCB/MCB functional',
      'Proper earthing of equipment',
      'Electrical panels locked and labeled',
      'Extension cords in good condition',
      'Lockout/tagout procedures followed',
      'Qualified electricians performing work',
      'Electrical permits displayed',
      'Proper cable routing and protection',
      'Emergency power off accessible',
      'Electrical tools double insulated'
    ],
    'FIRE_SAFETY': [
      'Fire extinguishers inspected monthly',
      'Fire extinguishers accessible',
      'Emergency assembly points marked',
      'Fire exit routes clear',
      'Emergency lighting functional',
      'Fire drill conducted (monthly)',
      'Hot work permits system in place',
      'Flammable materials stored properly',
      'Fire alarm system functional',
      'Fire warden trained and identified'
    ],
    'EXCAVATION': [
      'Excavation permit obtained',
      'Utility clearance obtained',
      'Shoring/shielding adequate',
      'Ladder access provided',
      'Edge protection installed',
      'Spoil pile away from edge',
      'Competent person inspected daily',
      'Benching/sloping per standard',
      'Water accumulation controlled',
      'Barricading around excavation'
    ],
    'HOUSEKEEPING': [
      'Work areas clean and organized',
      'Waste segregation bins available',
      'Debris removed daily',
      'Materials stacked safely',
      'Walkways clear of obstructions',
      'Spills cleaned immediately',
      'Tools and equipment stored properly',
      'Toilet and washing facilities clean',
      'Drinking water available',
      'Site entrance/exit clean'
    ]
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => {
      const updated = { ...prev, [name]: value };
      
      // Auto-populate checklist when audit type changes
      if (name === 'audit_type' && standardChecklists[value]) {
        updated.checklist_items = standardChecklists[value];
      }
      
      return updated;
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.location || !formData.auditor_name) {
      toast.error('Please fill in all required fields');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const projectId = localStorage.getItem('activeProjectId');
      
      const response = await fetch('/api/safety-audits', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          ...formData,
          project_id: parseInt(projectId),
          scheduled_by: parseInt(localStorage.getItem('userId'))
        })
      });

      if (!response.ok) throw new Error('Failed to schedule audit');

      const data = await response.json();
      toast.success('Safety audit scheduled successfully');
      router.push(`/dashboard/safety-audits/${data.audit.id}`);
    } catch (error) {
      console.error('Error scheduling audit:', error);
      toast.error('Failed to schedule audit');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
            <ClipboardCheck className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Schedule Safety Audit</h1>
            <p className="text-sm text-gray-600">Plan and organize safety inspection</p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Audit Type Selection */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <CheckSquare className="w-5 h-5 text-blue-600" />
            Audit Type*
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {auditTypes.map((type) => (
              <label
                key={type.value}
                className={`relative flex flex-col p-4 border-2 rounded-lg cursor-pointer transition ${
                  formData.audit_type === type.value
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-blue-300'
                }`}
              >
                <input
                  type="radio"
                  name="audit_type"
                  value={type.value}
                  checked={formData.audit_type === type.value}
                  onChange={handleChange}
                  className="sr-only"
                />
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl">{type.icon}</span>
                  <span className="font-medium text-gray-900 text-sm">{type.label}</span>
                </div>
                <p className="text-xs text-gray-600 mb-1">{type.desc}</p>
                <p className="text-xs text-gray-500">Duration: {type.duration}</p>
                {formData.audit_type === type.value && (
                  <div className="absolute top-2 right-2 w-5 h-5 bg-blue-600 rounded-full flex items-center justify-center">
                    <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                )}
              </label>
            ))}
          </div>
        </div>

        {/* Schedule & Location */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Calendar className="w-5 h-5 text-gray-600" />
            Schedule & Location
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <Calendar className="w-4 h-4 inline mr-1" />
                Audit Date*
              </label>
              <input
                type="date"
                name="scheduled_date"
                value={formData.scheduled_date}
                onChange={handleChange}
                min={new Date().toISOString().split('T')[0]}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <Clock className="w-4 h-4 inline mr-1" />
                Audit Time*
              </label>
              <input
                type="time"
                name="scheduled_time"
                value={formData.scheduled_time}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Location/Area*
              </label>
              <input
                type="text"
                name="location"
                value={formData.location}
                onChange={handleChange}
                placeholder="e.g., Block A, All Floors"
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Auditor Details */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Users className="w-5 h-5 text-gray-600" />
            Auditor Details
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Lead Auditor Name*
              </label>
              <input
                type="text"
                name="auditor_name"
                value={formData.auditor_name}
                onChange={handleChange}
                placeholder="e.g., Rajesh Kumar"
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Auditor Phone
              </label>
              <input
                type="tel"
                name="auditor_phone"
                value={formData.auditor_phone}
                onChange={handleChange}
                placeholder="e.g., +91 9876543210"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Audit Scope */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5 text-gray-600" />
            Audit Scope & Focus Areas
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Audit Scope
              </label>
              <textarea
                name="scope"
                value={formData.scope}
                onChange={handleChange}
                rows={3}
                placeholder="Define what will be covered in this audit..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Special Focus Areas
              </label>
              <textarea
                name="special_focus_areas"
                value={formData.special_focus_areas}
                onChange={handleChange}
                rows={2}
                placeholder="Any specific areas requiring extra attention..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Checklist Preview */}
        {formData.checklist_items.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <CheckSquare className="w-5 h-5 text-green-600" />
              Standard Checklist ({formData.checklist_items.length} items)
            </h2>
            <div className="bg-gray-50 rounded-lg p-4">
              <ul className="space-y-2">
                {formData.checklist_items.slice(0, 5).map((item, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-gray-700">
                    <CheckSquare className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
              {formData.checklist_items.length > 5 && (
                <p className="text-xs text-gray-500 mt-3">
                  + {formData.checklist_items.length - 5} more items will be included
                </p>
              )}
            </div>
          </div>
        )}

        {/* Info Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex gap-3">
            <AlertTriangle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">After scheduling this audit:</p>
              <ol className="list-decimal list-inside space-y-1">
                <li>Auditor will receive notification</li>
                <li>Standard checklist will be attached</li>
                <li>Audit can be conducted on scheduled date</li>
                <li>Findings will be recorded with photos</li>
                <li>Corrective actions will be assigned</li>
                <li>Audit report will be auto-generated</li>
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
            className="flex-1 flex items-center justify-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
          >
            {loading ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Scheduling...
              </>
            ) : (
              <>
                <Save className="w-5 h-5" />
                Schedule Audit
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
