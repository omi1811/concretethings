'use client';

import { useState, useEffect } from 'react';
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
  const [loadingBatches, setLoadingBatches] = useState(true);
  const [error, setError] = useState('');
  const [batches, setBatches] = useState([]);
  
  const [formData, setFormData] = useState({
    batchId: '',
    batchNumber: '',
    testAge: '28',
    cubeId1: '',
    cubeId2: '',
    cubeId3: '',
    weight1: '',
    weight2: '',
    weight3: '',
    load1: '',
    load2: '',
    load3: '',
    testDate: new Date().toISOString().split('T')[0],
    testedBy: '',
    machineId: '',
    remarks: ''
  });

  // Fetch batches on component mount
  useEffect(() => {
    fetchBatches();
  }, []);

  const fetchBatches = async () => {
    try {
      setLoadingBatches(true);
      const projectId = localStorage.getItem('current_project_id') || '1';
      const token = localStorage.getItem('token');
      
      if (!token) {
        console.warn('No authentication token found');
        setLoadingBatches(false);
        return;
      }
      
      const response = await fetch(`http://localhost:8000/api/batches?project_id=${projectId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.batches) {
          setBatches(data.batches);
        } else {
          console.warn('No batches returned from API');
        }
      } else {
        const errorData = await response.json().catch(() => ({}));
        console.error('Failed to fetch batches:', response.status, errorData);
        // Don't show error to user if no batches exist - this is normal
        if (response.status !== 404) {
          setError(`Failed to load batches: ${errorData.error || response.statusText}`);
        }
      }
    } catch (err) {
      console.error('Error fetching batches:', err);
      // Don't show error for network issues - allow manual entry
      setError('');
    } finally {
      setLoadingBatches(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    
    // If batch is selected, update both batchId and batchNumber
    if (name === 'batchId') {
      const selectedBatch = batches.find(b => b.id === parseInt(value));
      setFormData(prev => ({
        ...prev,
        batchId: value,
        batchNumber: selectedBatch ? selectedBatch.batch_number : ''
      }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
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
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Batch Number <span className="text-red-500">*</span>
                </label>
                {loadingBatches ? (
                  <div className="px-3 py-2 border border-gray-300 rounded-lg text-gray-500">
                    Loading batches...
                  </div>
                ) : batches.length > 0 ? (
                  <select
                    name="batchId"
                    value={formData.batchId}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select a batch</option>
                    {batches.map(batch => (
                      <option key={batch.id} value={batch.id}>
                        {batch.batch_number} - {batch.mix_design_name || 'N/A'} ({new Date(batch.delivery_date).toLocaleDateString()})
                      </option>
                    ))}
                  </select>
                ) : (
                  <div>
                    <Input
                      name="batchNumber"
                      value={formData.batchNumber}
                      onChange={handleChange}
                      placeholder="Enter batch number manually"
                      required
                    />
                    <p className="mt-1 text-xs text-gray-500">
                      No registered batches found. Please enter manually.
                    </p>
                  </div>
                )}
              </div>
              <Select
                label="Test Age (days)"
                name="testAge"
                value={formData.testAge}
                onChange={handleChange}
                required
              >
                <option value="3">3 Days</option>
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
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Input
                  label="Cube ID"
                  name="cubeId1"
                  value={formData.cubeId1}
                  onChange={handleChange}
                  placeholder="A"
                  required
                />
                <Input
                  type="number"
                  label="Weight (kg)"
                  name="weight1"
                  value={formData.weight1}
                  onChange={handleChange}
                  step="0.01"
                  placeholder="8.2"
                  required
                />
                <Input
                  type="number"
                  label="Load (kN)"
                  name="load1"
                  value={formData.load1}
                  onChange={handleChange}
                  step="0.1"
                  placeholder="675"
                  required
                />
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Strength (MPa)
                  </label>
                  <div className="px-3 py-2 bg-blue-50 border border-blue-300 rounded-lg font-semibold text-blue-700">
                    {strength1}
                  </div>
                </div>
              </div>
            </div>

            {/* Cube 2 */}
            <div className="border-b pb-4">
              <h4 className="font-medium mb-3">Cube 2</h4>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Input
                  label="Cube ID"
                  name="cubeId2"
                  value={formData.cubeId2}
                  onChange={handleChange}
                  placeholder="B"
                  required
                />
                <Input
                  type="number"
                  label="Weight (kg)"
                  name="weight2"
                  value={formData.weight2}
                  onChange={handleChange}
                  step="0.01"
                  placeholder="8.1"
                  required
                />
                <Input
                  type="number"
                  label="Load (kN)"
                  name="load2"
                  value={formData.load2}
                  onChange={handleChange}
                  step="0.1"
                  placeholder="680"
                  required
                />
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Strength (MPa)
                  </label>
                  <div className="px-3 py-2 bg-blue-50 border border-blue-300 rounded-lg font-semibold text-blue-700">
                    {strength2}
                  </div>
                </div>
              </div>
            </div>

            {/* Cube 3 */}
            <div className="border-b pb-4">
              <h4 className="font-medium mb-3">Cube 3</h4>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Input
                  label="Cube ID"
                  name="cubeId3"
                  value={formData.cubeId3}
                  onChange={handleChange}
                  placeholder="C"
                  required
                />
                <Input
                  type="number"
                  label="Weight (kg)"
                  name="weight3"
                  value={formData.weight3}
                  onChange={handleChange}
                  step="0.01"
                  placeholder="8.3"
                  required
                />
                <Input
                  type="number"
                  label="Load (kN)"
                  name="load3"
                  value={formData.load3}
                  onChange={handleChange}
                  step="0.1"
                  placeholder="672"
                  required
                />
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Strength (MPa)
                  </label>
                  <div className="px-3 py-2 bg-blue-50 border border-blue-300 rounded-lg font-semibold text-blue-700">
                    {strength3}
                  </div>
                </div>
              </div>
            </div>

            {/* Average */}
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-300 rounded-lg p-6">
              <div className="flex justify-between items-center">
                <div>
                  <span className="text-sm text-gray-600 block mb-1">Calculated Average Strength</span>
                  <span className="text-lg font-semibold text-gray-900">Average of 3 Cubes</span>
                </div>
                <div className="text-right">
                  <span className="text-3xl font-bold text-blue-600">{avgStrength}</span>
                  <span className="text-xl font-semibold text-gray-600 ml-1">MPa</span>
                </div>
              </div>
              <div className="mt-3 pt-3 border-t border-blue-200 text-xs text-gray-600">
                Individual: {strength1} MPa, {strength2} MPa, {strength3} MPa
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
