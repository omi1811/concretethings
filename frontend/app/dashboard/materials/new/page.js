'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Plus } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Input, Select, Textarea } from '@/components/ui/Input';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Alert } from '@/components/ui/Alert';
import { materialTestAPI } from '@/lib/api';

export default function NewMaterialTestPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showCustomCategory, setShowCustomCategory] = useState(false);
  const [customCategory, setCustomCategory] = useState('');
  
  const [predefinedCategories] = useState([
    { id: '1', name: 'Cement' },
    { id: '2', name: 'Fine Aggregate (Sand)' },
    { id: '3', name: 'Coarse Aggregate' },
    { id: '4', name: 'Steel (TMT Bars)' },
    { id: '5', name: 'Ready Mix Concrete' },
    { id: '6', name: 'Admixtures' },
    { id: '7', name: 'Bricks' },
    { id: '8', name: 'Tiles' },
    { id: '9', name: 'Paint' },
    { id: '10', name: 'Waterproofing Materials' },
    { id: '11', name: 'Pipes & Fittings' },
    { id: '12', name: 'Electrical Materials' },
  ]);
  
  const [formData, setFormData] = useState({
    project_id: 1,
    material_category_id: '',
    material_description: '',
    supplier_name: '',
    supplier_contact: '',
    brand_name: '',
    grade_specification: '',
    quantity: '',
    unit: 'MT',
    test_date: new Date().toISOString().split('T')[0],
    test_agency: '',
    sample_id: '',
    pass_fail_status: 'Pending',
    remarks: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleCategoryChange = (e) => {
    const value = e.target.value;
    if (value === 'custom') {
      setShowCustomCategory(true);
      setFormData(prev => ({ ...prev, material_category_id: '' }));
    } else {
      setShowCustomCategory(false);
      setFormData(prev => ({ ...prev, material_category_id: value }));
    }
  };

  const handleCustomCategoryAdd = () => {
    if (customCategory.trim()) {
      // For custom categories, we'll use the category name as the ID
      // The backend should handle creating new categories
      setFormData(prev => ({ 
        ...prev, 
        material_category_id: customCategory.trim(),
        material_description: customCategory.trim() + (formData.material_description ? ' - ' + formData.material_description : '')
      }));
      setShowCustomCategory(false);
      setSuccess(`Custom category "${customCategory}" will be added`);
      setTimeout(() => setSuccess(''), 3000);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const result = await materialTestAPI.create(formData);
      
      if (result.success) {
        setSuccess('Material test recorded successfully!');
        setTimeout(() => router.push('/dashboard/materials'), 1500);
      } else {
        setError(result.error || result.message || 'Failed to record test');
      }
    } catch (err) {
      console.error('Error:', err);
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center gap-4">
        <Link href="/dashboard/materials">
          <Button variant="outline" size="sm"><ArrowLeft className="w-4 h-4 mr-2" />Back</Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">New Material Test</h1>
          <p className="text-gray-600 mt-1">Record material quality test results</p>
        </div>
      </div>

      {error && <Alert variant="danger" onClose={() => setError('')}>{error}</Alert>}
      {success && <Alert variant="success" onClose={() => setSuccess('')}>{success}</Alert>}

      <form onSubmit={handleSubmit} className="space-y-6">
        <Card>
          <CardHeader><CardTitle>Material Information</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Select 
                  label="Material Category" 
                  name="material_category_id" 
                  value={showCustomCategory ? 'custom' : formData.material_category_id} 
                  onChange={handleCategoryChange} 
                  required={!showCustomCategory}
                >
                  <option value="">Select Category</option>
                  {predefinedCategories.map(cat => (
                    <option key={cat.id} value={cat.id}>{cat.name}</option>
                  ))}
                  <option value="custom">➕ Add New Category</option>
                </Select>
                
                {showCustomCategory && (
                  <div className="flex gap-2 mt-2">
                    <Input
                      placeholder="Enter new category name"
                      value={customCategory}
                      onChange={(e) => setCustomCategory(e.target.value)}
                      className="flex-1"
                    />
                    <Button 
                      type="button" 
                      onClick={handleCustomCategoryAdd}
                      variant="outline"
                      size="sm"
                    >
                      <Plus className="w-4 h-4" />
                    </Button>
                    <Button 
                      type="button" 
                      onClick={() => {
                        setShowCustomCategory(false);
                        setCustomCategory('');
                      }}
                      variant="outline"
                      size="sm"
                    >
                      Cancel
                    </Button>
                  </div>
                )}
              </div>
              
              <Input 
                label="Material Description" 
                name="material_description" 
                value={formData.material_description} 
                onChange={handleChange} 
                required 
                placeholder="Detailed description of the material"
              />
              <Input 
                label="Brand Name" 
                name="brand_name" 
                value={formData.brand_name} 
                onChange={handleChange} 
                required 
                placeholder="e.g., ACC, Ultratech, Tata Steel"
              />
              <Input 
                label="Grade/Specification" 
                name="grade_specification" 
                value={formData.grade_specification} 
                onChange={handleChange} 
                required 
                placeholder="e.g., OPC 53, M30, Fe 500D" 
              />
              <Input 
                type="number" 
                label="Quantity" 
                name="quantity" 
                value={formData.quantity} 
                onChange={handleChange} 
                step="0.01" 
                required 
                placeholder="Enter quantity"
              />
              <Select label="Unit" name="unit" value={formData.unit} onChange={handleChange} required>
                <option value="MT">Metric Ton (MT)</option>
                <option value="cum">Cubic Meter (m³)</option>
                <option value="kg">Kilogram (kg)</option>
                <option value="ltr">Liter (L)</option>
                <option value="nos">Numbers (Nos)</option>
                <option value="sqm">Square Meter (m²)</option>
                <option value="rmt">Running Meter (RMT)</option>
              </Select>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Supplier Details</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input label="Supplier Name" name="supplier_name" value={formData.supplier_name} onChange={handleChange} required />
              <Input label="Supplier Contact" name="supplier_contact" value={formData.supplier_contact} onChange={handleChange} placeholder="Phone or email" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Test Information</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input type="date" label="Test Date" name="test_date" value={formData.test_date} onChange={handleChange} required />
              <Input label="Test Agency" name="test_agency" value={formData.test_agency} onChange={handleChange} required placeholder="e.g., Internal Lab, NABL Lab" />
              <Input label="Sample ID" name="sample_id" value={formData.sample_id} onChange={handleChange} required placeholder="e.g., SAMPLE-2025-001" />
              <Select label="Test Status" name="pass_fail_status" value={formData.pass_fail_status} onChange={handleChange} required>
                <option value="Pending">Pending</option>
                <option value="Pass">Pass</option>
                <option value="Fail">Fail</option>
              </Select>
            </div>
            <Textarea label="Remarks" name="remarks" value={formData.remarks} onChange={handleChange} rows={3} placeholder="Any additional observations or notes..." />
          </CardContent>
        </Card>

        <div className="flex justify-end gap-4">
          <Link href="/dashboard/materials">
            <Button type="button" variant="outline">Cancel</Button>
          </Link>
          <Button type="submit" disabled={loading}>
            {loading ? 'Saving...' : 'Save Test'}
          </Button>
        </div>
      </form>
    </div>
  );
}
