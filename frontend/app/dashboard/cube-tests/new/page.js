'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Input, Select, Textarea } from '@/components/ui/Input';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Alert } from '@/components/ui/Alert';

export default function NewCubeTestPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState({
    batchNumber: '',
    testAge: '28',
    cubeId1: '',
    cubeId2: '',
    cubeId3: '',
    load1: '',
    load2: '',
    load3: '',
    testDate: new Date().toISOString().split('T')[0],
    testedBy: '',
    machineId: '',
    remarks: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const calculateStrength = (load) => {
    // Assuming 150mm x 150mm cube (22500 mm²)
    const area = 22500;
    return load ? ((load * 1000) / area).toFixed(2) : '0';
  };

  const strength1 = calculateStrength(formData.load1);
  const strength2 = calculateStrength(formData.load2);
  const strength3 = calculateStrength(formData.load3);
  const avgStrength = ((parseFloat(strength1) + parseFloat(strength2) + parseFloat(strength3)) / 3).toFixed(2);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // API call will be implemented
      setTimeout(() => {
        router.push('/dashboard/cube-tests');
      }, 1000);
    } catch (err) {
      setError('An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center gap-4">
        <Link href="/dashboard/cube-tests">
          <Button variant="outline" size="sm">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">New Cube Test</h1>
          <p className="text-gray-600 mt-1">Record concrete cube compression test</p>
        </div>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      <form onSubmit={handleSubmit} className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Test Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Batch Number"
                name="batchNumber"
                value={formData.batchNumber}
                onChange={handleChange}
                required
              />
              <Select
                label="Test Age (days)"
                name="testAge"
                value={formData.testAge}
                onChange={handleChange}
                required
              >
                <option value="7">7 Days</option>
                <option value="28">28 Days</option>
                <option value="56">56 Days</option>
              </Select>
              <Input
                type="date"
                label="Test Date"
                name="testDate"
                value={formData.testDate}
                onChange={handleChange}
                required
              />
              <Input
                label="Tested By"
                name="testedBy"
                value={formData.testedBy}
                onChange={handleChange}
                required
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Cube Test Results</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Cube 1 */}
            <div className="border-b pb-4">
              <h4 className="font-medium mb-3">Cube 1</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Input
                  label="Cube ID"
                  name="cubeId1"
                  value={formData.cubeId1}
                  onChange={handleChange}
                  required
                />
                <Input
                  type="number"
                  label="Load (kN)"
                  name="load1"
                  value={formData.load1}
                  onChange={handleChange}
                  step="0.1"
                  required
                />
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Strength (MPa)
                  </label>
                  <div className="px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg font-medium">
                    {strength1}
                  </div>
                </div>
              </div>
            </div>

            {/* Cube 2 */}
            <div className="border-b pb-4">
              <h4 className="font-medium mb-3">Cube 2</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Input
                  label="Cube ID"
                  name="cubeId2"
                  value={formData.cubeId2}
                  onChange={handleChange}
                  required
                />
                <Input
                  type="number"
                  label="Load (kN)"
                  name="load2"
                  value={formData.load2}
                  onChange={handleChange}
                  step="0.1"
                  required
                />
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Strength (MPa)
                  </label>
                  <div className="px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg font-medium">
                    {strength2}
                  </div>
                </div>
              </div>
            </div>

            {/* Cube 3 */}
            <div className="border-b pb-4">
              <h4 className="font-medium mb-3">Cube 3</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Input
                  label="Cube ID"
                  name="cubeId3"
                  value={formData.cubeId3}
                  onChange={handleChange}
                  required
                />
                <Input
                  type="number"
                  label="Load (kN)"
                  name="load3"
                  value={formData.load3}
                  onChange={handleChange}
                  step="0.1"
                  required
                />
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Strength (MPa)
                  </label>
                  <div className="px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg font-medium">
                    {strength3}
                  </div>
                </div>
              </div>
            </div>

            {/* Average */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex justify-between items-center">
                <span className="text-lg font-semibold text-gray-900">Average Strength</span>
                <span className="text-2xl font-bold text-blue-600">{avgStrength} MPa</span>
              </div>
            </div>

            <Textarea
              label="Remarks"
              name="remarks"
              value={formData.remarks}
              onChange={handleChange}
              rows={3}
            />
          </CardContent>
        </Card>

        <div className="flex justify-end gap-4">
          <Link href="/dashboard/cube-tests">
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
