'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Download, CheckCircle, Upload } from 'lucide-react';
import toast from 'react-hot-toast';

export default function InductionDetailsPage({ params }) {
  const [induction, setInduction] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInduction();
  }, [params.id]);

  const fetchInduction = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/safety-inductions/${params.id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setInduction(data.induction || data);
      } else {
        toast.error('Failed to load induction');
      }
    } catch (error) {
      console.error('Error:', error);
      toast.error('Error loading induction');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!induction) {
    return (
      <div className="p-6 text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Induction not found</h2>
        <Link href="/dashboard/safety-inductions" className="text-blue-600 hover:underline">
          Back to Inductions
        </Link>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="mb-6">
        <Link href="/dashboard/safety-inductions" className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4">
          <ArrowLeft className="w-4 h-4" />
          Back to Inductions
        </Link>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{induction.worker_name}</h1>
            <p className="text-gray-600">Worker ID: {induction.worker_id}</p>
          </div>
          {induction.status === 'completed' && induction.certificate_url && (
            <a
              href={induction.certificate_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              <Download className="w-4 h-4" />
              Download Certificate
            </a>
          )}
        </div>
      </div>

      {/* Worker Details */}
      <div className="bg-white rounded-lg border p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Worker Details</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Aadhar Number</label>
            <p className="text-gray-900">{induction.aadhar_number || 'N/A'}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Contractor</label>
            <p className="text-gray-900">{induction.contractor_name || 'N/A'}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Trade</label>
            <p className="text-gray-900">{induction.trade || 'N/A'}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Phone</label>
            <p className="text-gray-900">{induction.phone_number || 'N/A'}</p>
          </div>
        </div>
      </div>

      {/* Progress */}
      <div className="bg-white rounded-lg border p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Induction Progress</h2>
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <CheckCircle className={`w-6 h-6 ${induction.aadhar_verified ? 'text-green-600' : 'text-gray-300'}`} />
            <div>
              <p className="font-medium text-gray-900">Aadhar Verification</p>
              <p className="text-sm text-gray-500">{induction.aadhar_verified ? 'Completed' : 'Pending'}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <CheckCircle className={`w-6 h-6 ${induction.video_completed ? 'text-green-600' : 'text-gray-300'}`} />
            <div>
              <p className="font-medium text-gray-900">Safety Video</p>
              <p className="text-sm text-gray-500">
                {induction.video_progress ? `${induction.video_progress}% watched` : 'Not started'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <CheckCircle className={`w-6 h-6 ${induction.quiz_passed ? 'text-green-600' : 'text-gray-300'}`} />
            <div>
              <p className="font-medium text-gray-900">Safety Quiz</p>
              <p className="text-sm text-gray-500">
                {induction.quiz_score ? `Score: ${induction.quiz_score}/10 (${induction.quiz_passed ? 'Passed' : 'Failed'})` : 'Not attempted'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <CheckCircle className={`w-6 h-6 ${induction.status === 'completed' ? 'text-green-600' : 'text-gray-300'}`} />
            <div>
              <p className="font-medium text-gray-900">Certificate Issued</p>
              <p className="text-sm text-gray-500">
                {induction.status === 'completed' ? `Valid until ${formatDate(induction.expiry_date)}` : 'Pending completion'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Dates */}
      <div className="bg-white rounded-lg border p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Important Dates</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Induction Date</label>
            <p className="text-gray-900">{formatDate(induction.induction_date)}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Completion Date</label>
            <p className="text-gray-900">{formatDate(induction.completed_at)}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Expiry Date</label>
            <p className="text-gray-900">{formatDate(induction.expiry_date)}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
