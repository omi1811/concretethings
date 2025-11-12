'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Upload, Download, FileSpreadsheet, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Alert } from '@/components/ui/Alert';
import { pourActivityAPI } from '@/lib/api';
import axios from 'axios';

export default function BatchImportPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [pourActivities, setPourActivities] = useState([]);
  const [selectedPourId, setSelectedPourId] = useState('');

  useEffect(() => {
    const projectId = localStorage.getItem('currentProjectId') || '1';
    loadPourActivities(projectId);
  }, []);

  async function loadPourActivities(projectId) {
    try {
      const result = await pourActivityAPI.getAll({
        projectId,
        status: 'in_progress'
      });
      if (result.success) {
        setPourActivities(result.data.pourActivities || []);
      }
    } catch (error) {
      console.error('Error loading pour activities:', error);
    }
  }

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // Validate file type
      const validTypes = [
        'text/csv',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      ];
      
      if (!validTypes.includes(selectedFile.type) && 
          !selectedFile.name.endsWith('.csv') && 
          !selectedFile.name.endsWith('.xlsx') && 
          !selectedFile.name.endsWith('.xls')) {
        setError('Please upload a CSV or Excel file (.csv, .xlsx, .xls)');
        return;
      }
      
      setFile(selectedFile);
      setError('');
      setResult(null);
    }
  };

  const handleDownloadTemplate = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await axios.get('/api/batches/import-template?format=xlsx', {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        responseType: 'blob'
      });

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'batch_import_template.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Error downloading template:', err);
      setError('Failed to download template');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const projectId = localStorage.getItem('currentProjectId') || '1';
      const token = localStorage.getItem('auth_token');
      
      const formData = new FormData();
      formData.append('file', file);
      formData.append('projectId', projectId);
      if (selectedPourId) {
        formData.append('pourActivityId', selectedPourId);
      }

      const response = await axios.post('/api/batches/bulk-import', formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.data) {
        setResult(response.data);
        setFile(null);
        // Reset file input
        document.getElementById('file-input').value = '';
      }
    } catch (err) {
      console.error('Error uploading file:', err);
      setError(err.response?.data?.error || err.message || 'Failed to import batches');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/dashboard/batches">
          <Button variant="outline" size="sm">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Bulk Import Batches</h1>
          <p className="text-gray-600 mt-1">Import multiple batches from Excel/CSV file</p>
        </div>
      </div>

      {/* Instructions */}
      <Alert variant="info">
        <FileSpreadsheet className="w-4 h-4" />
        <div>
          <p className="font-medium">For sites where security maintains vehicle register</p>
          <p className="text-sm mt-1">
            Download the template, fill in vehicle details from security register, and upload to create multiple batches at once.
          </p>
        </div>
      </Alert>

      {error && (
        <Alert variant="danger" onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Step 1: Download Template */}
      <Card>
        <CardHeader>
          <CardTitle>Step 1: Download Template</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600 mb-4">
            Download the Excel template with sample data and required column headers.
          </p>
          <Button onClick={handleDownloadTemplate} variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Download Excel Template
          </Button>
          
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <p className="text-sm font-medium text-gray-700 mb-2">Required Columns:</p>
            <div className="text-xs text-gray-600 space-y-1">
              <p><strong>vehicleNumber</strong> - Vehicle registration (e.g., MH-01-1234)</p>
              <p><strong>vendorName</strong> - RMC vendor name (e.g., ABC Concrete)</p>
              <p><strong>grade</strong> - Concrete grade (e.g., M30, M40)</p>
              <p><strong>quantity</strong> - Quantity in m³ (e.g., 1.5)</p>
              <p className="text-gray-500 italic">Optional: deliveryDate, deliveryTime, slump, temperature, location, remarks</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Step 2: Select Pour (Optional) */}
      {pourActivities.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Step 2: Link to Pour Activity (Optional)</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600 mb-3">
              Link all imported batches to a pour activity for batch consolidation.
            </p>
            <select
              value={selectedPourId}
              onChange={(e) => setSelectedPourId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">No pour activity (standalone batches)</option>
              {pourActivities.map(pour => (
                <option key={pour.id} value={pour.id}>
                  {pour.pourId} - {pour.location?.gridReference} ({pour.designGrade}, {pour.totalQuantityPlanned}m³)
                </option>
              ))}
            </select>
          </CardContent>
        </Card>
      )}

      {/* Step 3: Upload File */}
      <Card>
        <CardHeader>
          <CardTitle>Step {pourActivities.length > 0 ? '3' : '2'}: Upload Filled File</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Excel or CSV File
            </label>
            <input
              id="file-input"
              type="file"
              accept=".csv,.xlsx,.xls"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
            {file && (
              <p className="mt-2 text-sm text-green-600">
                <CheckCircle className="w-4 h-4 inline mr-1" />
                Selected: {file.name} ({(file.size / 1024).toFixed(2)} KB)
              </p>
            )}
          </div>

          <Button 
            onClick={handleUpload} 
            disabled={!file || loading}
            className="w-full"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                Importing...
              </>
            ) : (
              <>
                <Upload className="w-4 h-4 mr-2" />
                Upload and Import
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Results */}
      {result && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {result.summary.errors > 0 ? (
                <AlertTriangle className="w-5 h-5 text-orange-500" />
              ) : (
                <CheckCircle className="w-5 h-5 text-green-500" />
              )}
              Import Results
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Summary */}
            <div className="grid grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
              <div className="text-center">
                <p className="text-2xl font-bold text-gray-900">{result.summary.total_rows}</p>
                <p className="text-sm text-gray-600">Total Rows</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">{result.summary.success}</p>
                <p className="text-sm text-gray-600">Success</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-red-600">{result.summary.errors}</p>
                <p className="text-sm text-gray-600">Errors</p>
              </div>
            </div>

            {/* Success Message */}
            {result.summary.success > 0 && (
              <Alert variant="success">
                <CheckCircle className="w-4 h-4" />
                <p>Successfully imported {result.summary.success} batch(es)!</p>
              </Alert>
            )}

            {/* Created Batches */}
            {result.batches_created && result.batches_created.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Created Batches:</h4>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {result.batches_created.map((batch, idx) => (
                    <div key={idx} className="p-3 bg-green-50 border border-green-200 rounded text-sm">
                      <span className="font-medium text-green-900">Row {batch.row}:</span>{' '}
                      {batch.batchNumber} - {batch.vehicleNumber} ({batch.quantity}m³)
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Errors */}
            {result.errors && result.errors.length > 0 && (
              <div>
                <h4 className="font-medium text-red-900 mb-2">Errors:</h4>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {result.errors.map((err, idx) => (
                    <div key={idx} className="p-3 bg-red-50 border border-red-200 rounded text-sm">
                      <p className="font-medium text-red-900">Row {err.row}:</p>
                      <p className="text-red-700">{err.error}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-4 pt-4 border-t border-gray-200">
              <Link href="/dashboard/batches" className="flex-1">
                <Button className="w-full">
                  View All Batches
                </Button>
              </Link>
              <Button 
                variant="outline" 
                onClick={() => {
                  setResult(null);
                  setFile(null);
                  setError('');
                }}
              >
                Import More
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
