'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Input, Select, Textarea } from '@/components/ui/Input';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Alert } from '@/components/ui/Alert';
import { labAPI } from '@/lib/api-optimized';

export default function NewLabPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const [formData, setFormData] = useState({
    company_id: 1,
    lab_name: '',
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    pincode: '',
    country: 'India',
    contact_person_name: '',
    contact_phone: '',
    contact_email: '',
    nabl_accredited: false,
    nabl_certificate_number: '',
    nabl_validity_from: '',
    nabl_validity_to: '',
    scope_of_testing: '',
    remarks: ''
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const result = await labAPI.create(formData);
      
      if (result.success) {
        setSuccess('Laboratory added successfully!');
        setTimeout(() => router.push('/dashboard/labs'), 1500);
      } else {
        setError(result.error || result.message || 'Failed to add laboratory');
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
        <Link href="/dashboard/labs">
          <Button variant="outline" size="sm"><ArrowLeft className="w-4 h-4 mr-2" />Back</Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Add Third-Party Lab</h1>
          <p className="text-gray-600 mt-1">Register external testing laboratory</p>
        </div>
      </div>

      {error && <Alert variant="danger" onClose={() => setError('')}>{error}</Alert>}
      {success && <Alert variant="success" onClose={() => setSuccess('')}>{success}</Alert>}

      <form onSubmit={handleSubmit} className="space-y-6">
        <Card>
          <CardHeader><CardTitle>Laboratory Information</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <Input label="Lab Name" name="lab_name" value={formData.lab_name} onChange={handleChange} required placeholder="e.g., XYZ Testing Laboratory" />
            <Input label="Address Line 1" name="address_line1" value={formData.address_line1} onChange={handleChange} required />
            <Input label="Address Line 2" name="address_line2" value={formData.address_line2} onChange={handleChange} placeholder="Optional" />
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Input label="City" name="city" value={formData.city} onChange={handleChange} required />
              <Input label="State" name="state" value={formData.state} onChange={handleChange} required />
              <Input label="Pincode" name="pincode" value={formData.pincode} onChange={handleChange} required />
            </div>
            <Input label="Country" name="country" value={formData.country} onChange={handleChange} required />
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Contact Information</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Input label="Contact Person" name="contact_person_name" value={formData.contact_person_name} onChange={handleChange} required />
              <Input type="tel" label="Phone" name="contact_phone" value={formData.contact_phone} onChange={handleChange} required />
              <Input type="email" label="Email" name="contact_email" value={formData.contact_email} onChange={handleChange} required />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Accreditation Details</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-2">
              <input type="checkbox" id="nabl" name="nabl_accredited" checked={formData.nabl_accredited} onChange={handleChange} className="w-5 h-5 text-blue-600 rounded" />
              <label htmlFor="nabl" className="font-medium">NABL Accredited</label>
            </div>
            {formData.nabl_accredited && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pl-7">
                <Input label="NABL Certificate Number" name="nabl_certificate_number" value={formData.nabl_certificate_number} onChange={handleChange} />
                <Input type="date" label="Validity From" name="nabl_validity_from" value={formData.nabl_validity_from} onChange={handleChange} />
                <Input type="date" label="Validity To" name="nabl_validity_to" value={formData.nabl_validity_to} onChange={handleChange} />
              </div>
            )}
            <Textarea label="Scope of Testing" name="scope_of_testing" value={formData.scope_of_testing} onChange={handleChange} rows={3} placeholder="e.g., Concrete cube testing, Cement testing, Aggregate testing..." />
            <Textarea label="Remarks" name="remarks" value={formData.remarks} onChange={handleChange} rows={2} placeholder="Any additional notes..." />
          </CardContent>
        </Card>

        <div className="flex justify-end gap-4">
          <Link href="/dashboard/labs">
            <Button type="button" variant="outline">Cancel</Button>
          </Link>
          <Button type="submit" disabled={loading}>
            {loading ? 'Saving...' : 'Add Laboratory'}
          </Button>
        </div>
      </form>
    </div>
  );
}
