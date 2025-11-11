'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Plus, Trash2, AlertCircle } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Input, Select, Textarea } from '@/components/ui/Input';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Alert } from '@/components/ui/Alert';
import { handoverAPI } from '@/lib/api';

export default function NewHandoverPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [categories, setCategories] = useState([]);

  const [formData, setFormData] = useState({
    project_id: 1,
    
    // Work Details
    work_description: '',
    work_location: '',
    work_category: '',
    floor_level: '',
    zone_area: '',
    work_scope: '',
    
    // Outgoing Contractor
    outgoing_contractor_name: '',
    outgoing_supervisor_name: '',
    outgoing_supervisor_phone: '',
    
    // Incoming Contractor (Optional)
    incoming_contractor_name: '',
    incoming_supervisor_name: '',
    incoming_supervisor_phone: '',
    
    // Engineer
    engineer_name: '',
    engineer_designation: '',
    engineer_remarks: '',
    
    // Dates
    work_start_date: '',
    work_completion_date: '',
    handover_date: new Date().toISOString().split('T')[0],
    target_rectification_date: '',
    
    // Quality & Inspection
    quality_standard_met: true,
    inspection_completed: false,
    inspection_date: '',
    
    // Warranty
    warranty_period_months: 12,
    warranty_start_date: '',
    
    // Remarks
    general_remarks: '',
    safety_notes: '',
    special_instructions: '',
    maintenance_instructions: '',
    
    // Status
    status: 'draft'
  });

  const [defects, setDefects] = useState([]);
  const [newDefect, setNewDefect] = useState({
    description: '',
    location: '',
    severity: 'minor',
    rectification_required: true
  });

  const [deliverables, setDeliverables] = useState([]);
  const [newDeliverable, setNewDeliverable] = useState('');

  const [materialsUsed, setMaterialsUsed] = useState([]);
  const [newMaterial, setNewMaterial] = useState({ name: '', quantity: '', unit: '' });

  const [inspectionChecklist, setInspectionChecklist] = useState([
    { item: 'Work completed as per specifications', checked: false },
    { item: 'Quality standards met', checked: false },
    { item: 'Safety measures implemented', checked: false },
    { item: 'Site cleaned and debris removed', checked: false },
    { item: 'Tools and equipment removed', checked: false },
    { item: 'Documentation complete', checked: false }
  ]);

  useEffect(() => {
    loadCategories();
  }, []);

  async function loadCategories() {
    try {
      const result = await handoverAPI.getCategories();
      if (result.success) {
        setCategories(result.data.categories || []);
      }
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  }

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const addDefect = () => {
    if (newDefect.description && newDefect.location) {
      setDefects([...defects, { ...newDefect, id: Date.now() }]);
      setNewDefect({ description: '', location: '', severity: 'minor', rectification_required: true });
    }
  };

  const removeDefect = (id) => {
    setDefects(defects.filter(d => d.id !== id));
  };

  const addDeliverable = () => {
    if (newDeliverable.trim()) {
      setDeliverables([...deliverables, newDeliverable.trim()]);
      setNewDeliverable('');
    }
  };

  const removeDeliverable = (index) => {
    setDeliverables(deliverables.filter((_, i) => i !== index));
  };

  const addMaterial = () => {
    if (newMaterial.name && newMaterial.quantity) {
      setMaterialsUsed([...materialsUsed, { ...newMaterial, id: Date.now() }]);
      setNewMaterial({ name: '', quantity: '', unit: '' });
    }
  };

  const removeMaterial = (id) => {
    setMaterialsUsed(materialsUsed.filter(m => m.id !== id));
  };

  const toggleChecklistItem = (index) => {
    const updated = [...inspectionChecklist];
    updated[index].checked = !updated[index].checked;
    setInspectionChecklist(updated);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Prepare submission data
      const submissionData = {
        ...formData,
        defects_list: defects.map(({ id, ...rest }) => rest),
        deliverables,
        materials_used: materialsUsed.map(({ id, ...rest }) => rest),
        inspection_checklist: inspectionChecklist
      };

      const result = await handoverAPI.create(submissionData);

      if (result.success) {
        setSuccess(true);
        setTimeout(() => {
          router.push('/dashboard/handovers');
        }, 1500);
      } else {
        setError(result.error || 'Failed to create handover record');
      }
    } catch (err) {
      setError('An error occurred while creating the handover record');
      console.error('Submission error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/dashboard/handovers">
          <Button variant="outline" size="sm">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">New Handover Record</h1>
          <p className="text-gray-600 mt-1">Create work completion handover certificate</p>
        </div>
      </div>

      {error && (
        <Alert variant="error">
          <AlertCircle className="w-4 h-4" />
          {error}
        </Alert>
      )}

      {success && (
        <Alert variant="success">
          Handover record created successfully! Redirecting...
        </Alert>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Work Details */}
        <Card>
          <CardHeader>
            <CardTitle>Work Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Textarea
              label="Work Description"
              name="work_description"
              value={formData.work_description}
              onChange={handleChange}
              required
              rows={3}
              placeholder="Describe the completed work in detail..."
            />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Work Location"
                name="work_location"
                value={formData.work_location}
                onChange={handleChange}
                required
                placeholder="e.g., Building A, Basement Level"
              />

              <Select
                label="Work Category"
                name="work_category"
                value={formData.work_category}
                onChange={handleChange}
                required
              >
                <option value="">Select Category</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </Select>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Floor Level"
                name="floor_level"
                value={formData.floor_level}
                onChange={handleChange}
                placeholder="e.g., Ground Floor, 2nd Floor"
              />

              <Input
                label="Zone/Area"
                name="zone_area"
                value={formData.zone_area}
                onChange={handleChange}
                placeholder="e.g., North Wing, Zone A"
              />
            </div>

            <Textarea
              label="Work Scope"
              name="work_scope"
              value={formData.work_scope}
              onChange={handleChange}
              rows={3}
              placeholder="Define the scope of work completed..."
            />
          </CardContent>
        </Card>

        {/* Dates */}
        <Card>
          <CardHeader>
            <CardTitle>Important Dates</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Input
                label="Work Start Date"
                name="work_start_date"
                type="date"
                value={formData.work_start_date}
                onChange={handleChange}
              />

              <Input
                label="Work Completion Date"
                name="work_completion_date"
                type="date"
                value={formData.work_completion_date}
                onChange={handleChange}
                required
              />

              <Input
                label="Handover Date"
                name="handover_date"
                type="date"
                value={formData.handover_date}
                onChange={handleChange}
                required
              />
            </div>
          </CardContent>
        </Card>

        {/* Outgoing Contractor */}
        <Card>
          <CardHeader>
            <CardTitle>Outgoing Contractor (Work Completed By)</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              label="Contractor Company Name"
              name="outgoing_contractor_name"
              value={formData.outgoing_contractor_name}
              onChange={handleChange}
              required
              placeholder="Company name"
            />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Supervisor Name"
                name="outgoing_supervisor_name"
                value={formData.outgoing_supervisor_name}
                onChange={handleChange}
                required
                placeholder="Full name of supervisor"
              />

              <Input
                label="Supervisor Phone"
                name="outgoing_supervisor_phone"
                type="tel"
                value={formData.outgoing_supervisor_phone}
                onChange={handleChange}
                placeholder="+1234567890"
              />
            </div>
          </CardContent>
        </Card>

        {/* Incoming Contractor */}
        <Card>
          <CardHeader>
            <CardTitle>Incoming Contractor (Next Work) - Optional</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              label="Contractor Company Name"
              name="incoming_contractor_name"
              value={formData.incoming_contractor_name}
              onChange={handleChange}
              placeholder="Company name"
            />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Supervisor Name"
                name="incoming_supervisor_name"
                value={formData.incoming_supervisor_name}
                onChange={handleChange}
                placeholder="Full name of supervisor"
              />

              <Input
                label="Supervisor Phone"
                name="incoming_supervisor_phone"
                type="tel"
                value={formData.incoming_supervisor_phone}
                onChange={handleChange}
                placeholder="+1234567890"
              />
            </div>
          </CardContent>
        </Card>

        {/* Building Engineer */}
        <Card>
          <CardHeader>
            <CardTitle>Building Engineer / Project Manager</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Engineer Name"
                name="engineer_name"
                value={formData.engineer_name}
                onChange={handleChange}
                required
                placeholder="Full name"
              />

              <Input
                label="Designation"
                name="engineer_designation"
                value={formData.engineer_designation}
                onChange={handleChange}
                placeholder="e.g., Project Engineer, Site Manager"
              />
            </div>

            <Textarea
              label="Engineer's Remarks"
              name="engineer_remarks"
              value={formData.engineer_remarks}
              onChange={handleChange}
              rows={3}
              placeholder="Any remarks or observations..."
            />
          </CardContent>
        </Card>

        {/* Quality & Inspection */}
        <Card>
          <CardHeader>
            <CardTitle>Quality Assurance & Inspection</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="quality_standard_met"
                  name="quality_standard_met"
                  checked={formData.quality_standard_met}
                  onChange={handleChange}
                  className="w-4 h-4 text-blue-600 rounded"
                />
                <label htmlFor="quality_standard_met" className="text-sm font-medium text-gray-700">
                  Quality Standards Met
                </label>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="inspection_completed"
                  name="inspection_completed"
                  checked={formData.inspection_completed}
                  onChange={handleChange}
                  className="w-4 h-4 text-blue-600 rounded"
                />
                <label htmlFor="inspection_completed" className="text-sm font-medium text-gray-700">
                  Inspection Completed
                </label>
              </div>

              {formData.inspection_completed && (
                <Input
                  label="Inspection Date"
                  name="inspection_date"
                  type="date"
                  value={formData.inspection_date}
                  onChange={handleChange}
                />
              )}
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-3">Inspection Checklist</h4>
              <div className="space-y-2">
                {inspectionChecklist.map((item, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={item.checked}
                      onChange={() => toggleChecklistItem(index)}
                      className="w-4 h-4 text-blue-600 rounded"
                    />
                    <span className="text-sm text-gray-700">{item.item}</span>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Defects/Snag List */}
        <Card>
          <CardHeader>
            <CardTitle>Defects / Snag List</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Add Defect Form */}
            <div className="p-4 bg-gray-50 rounded-lg space-y-3">
              <Textarea
                label="Defect Description"
                value={newDefect.description}
                onChange={(e) => setNewDefect({ ...newDefect, description: e.target.value })}
                placeholder="Describe the defect or issue..."
                rows={2}
              />

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <Input
                  label="Location"
                  value={newDefect.location}
                  onChange={(e) => setNewDefect({ ...newDefect, location: e.target.value })}
                  placeholder="Specific location"
                />

                <Select
                  label="Severity"
                  value={newDefect.severity}
                  onChange={(e) => setNewDefect({ ...newDefect, severity: e.target.value })}
                >
                  <option value="minor">Minor</option>
                  <option value="major">Major</option>
                  <option value="critical">Critical</option>
                </Select>

                <div className="flex items-end">
                  <Button type="button" onClick={addDefect} variant="outline" className="w-full">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Defect
                  </Button>
                </div>
              </div>
            </div>

            {/* Defects List */}
            {defects.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-gray-700">
                  Recorded Defects ({defects.length})
                </h4>
                {defects.map((defect) => (
                  <div key={defect.id} className="flex items-start gap-3 p-3 bg-white border border-gray-200 rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`px-2 py-0.5 text-xs font-medium rounded ${
                          defect.severity === 'critical' ? 'bg-red-100 text-red-700' :
                          defect.severity === 'major' ? 'bg-orange-100 text-orange-700' :
                          'bg-yellow-100 text-yellow-700'
                        }`}>
                          {defect.severity.toUpperCase()}
                        </span>
                        <span className="text-xs text-gray-500">{defect.location}</span>
                      </div>
                      <p className="text-sm text-gray-900">{defect.description}</p>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeDefect(defect.id)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {defects.length > 0 && (
              <Input
                label="Target Rectification Date"
                name="target_rectification_date"
                type="date"
                value={formData.target_rectification_date}
                onChange={handleChange}
              />
            )}
          </CardContent>
        </Card>

        {/* Deliverables */}
        <Card>
          <CardHeader>
            <CardTitle>Deliverables & Materials Used</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Add Deliverable */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Deliverables
              </label>
              <div className="flex gap-2">
                <Input
                  value={newDeliverable}
                  onChange={(e) => setNewDeliverable(e.target.value)}
                  placeholder="e.g., As-built drawings, Test certificates"
                  className="flex-1"
                />
                <Button type="button" onClick={addDeliverable} variant="outline">
                  <Plus className="w-4 h-4" />
                </Button>
              </div>
              {deliverables.length > 0 && (
                <div className="mt-2 space-y-1">
                  {deliverables.map((item, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <span className="text-sm text-gray-900">{item}</span>
                      <button
                        type="button"
                        onClick={() => removeDeliverable(index)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Add Material */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Materials Used
              </label>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-2">
                <Input
                  value={newMaterial.name}
                  onChange={(e) => setNewMaterial({ ...newMaterial, name: e.target.value })}
                  placeholder="Material name"
                  className="md:col-span-2"
                />
                <Input
                  value={newMaterial.quantity}
                  onChange={(e) => setNewMaterial({ ...newMaterial, quantity: e.target.value })}
                  placeholder="Quantity"
                />
                <div className="flex gap-2">
                  <Input
                    value={newMaterial.unit}
                    onChange={(e) => setNewMaterial({ ...newMaterial, unit: e.target.value })}
                    placeholder="Unit"
                    className="flex-1"
                  />
                  <Button type="button" onClick={addMaterial} variant="outline">
                    <Plus className="w-4 h-4" />
                  </Button>
                </div>
              </div>
              {materialsUsed.length > 0 && (
                <div className="mt-2 space-y-1">
                  {materialsUsed.map((material) => (
                    <div key={material.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <span className="text-sm text-gray-900">
                        {material.name} - {material.quantity} {material.unit}
                      </span>
                      <button
                        type="button"
                        onClick={() => removeMaterial(material.id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Warranty Information */}
        <Card>
          <CardHeader>
            <CardTitle>Warranty & Maintenance</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Warranty Period (Months)"
                name="warranty_period_months"
                type="number"
                value={formData.warranty_period_months}
                onChange={handleChange}
                min="0"
              />

              <Input
                label="Warranty Start Date"
                name="warranty_start_date"
                type="date"
                value={formData.warranty_start_date}
                onChange={handleChange}
              />
            </div>

            <Textarea
              label="Maintenance Instructions"
              name="maintenance_instructions"
              value={formData.maintenance_instructions}
              onChange={handleChange}
              rows={3}
              placeholder="Special maintenance requirements or instructions..."
            />
          </CardContent>
        </Card>

        {/* Additional Remarks */}
        <Card>
          <CardHeader>
            <CardTitle>Additional Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Textarea
              label="General Remarks"
              name="general_remarks"
              value={formData.general_remarks}
              onChange={handleChange}
              rows={3}
              placeholder="Any additional remarks..."
            />

            <Textarea
              label="Safety Notes"
              name="safety_notes"
              value={formData.safety_notes}
              onChange={handleChange}
              rows={2}
              placeholder="Safety considerations or precautions..."
            />

            <Textarea
              label="Special Instructions"
              name="special_instructions"
              value={formData.special_instructions}
              onChange={handleChange}
              rows={2}
              placeholder="Any special instructions for the next contractor..."
            />
          </CardContent>
        </Card>

        {/* Status Selection */}
        <Card>
          <CardHeader>
            <CardTitle>Record Status</CardTitle>
          </CardHeader>
          <CardContent>
            <Select
              label="Status"
              name="status"
              value={formData.status}
              onChange={handleChange}
              required
            >
              <option value="draft">Save as Draft</option>
              <option value="pending_approval">Submit for Approval</option>
            </Select>
          </CardContent>
        </Card>

        {/* Submit Buttons */}
        <div className="flex justify-end gap-4">
          <Link href="/dashboard/handovers">
            <Button type="button" variant="outline">
              Cancel
            </Button>
          </Link>
          <Button type="submit" disabled={loading}>
            {loading ? 'Creating...' : 'Create Handover Record'}
          </Button>
        </div>
      </form>
    </div>
  );
}
