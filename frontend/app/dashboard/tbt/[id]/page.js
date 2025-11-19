'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, QrCode, Users, CheckCircle, Calendar, Download, Plus } from 'lucide-react';
import toast from 'react-hot-toast';

export default function TBTSessionDetailsPage({ params }) {
  const [session, setSession] = useState(null);
  const [attendance, setAttendance] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showQRScanner, setShowQRScanner] = useState(false);
  const [workerIdInput, setWorkerIdInput] = useState('');

  useEffect(() => {
    fetchSession();
    fetchAttendance();
  }, [params.id]);

  const fetchSession = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/tbt/sessions/${params.id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSession(data.session || data);
      } else {
        toast.error('Failed to load TBT session');
      }
    } catch (error) {
      console.error('Error fetching session:', error);
      toast.error('Error loading session');
    } finally {
      setLoading(false);
    }
  };

  const fetchAttendance = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/tbt/sessions/${params.id}/attendance`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setAttendance(data.attendance || data || []);
      }
    } catch (error) {
      console.error('Error fetching attendance:', error);
    }
  };

  const handleMarkAttendance = async () => {
    if (!workerIdInput.trim()) {
      toast.error('Please enter worker ID');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/tbt/sessions/${params.id}/attendance`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          worker_id: workerIdInput.trim()
        })
      });

      if (response.ok) {
        toast.success('Attendance marked successfully');
        setWorkerIdInput('');
        fetchAttendance();
        fetchSession(); // Refresh to update attendance count
      } else {
        const error = await response.json();
        toast.error(error.error || 'Failed to mark attendance');
      }
    } catch (error) {
      console.error('Error marking attendance:', error);
      toast.error('Error marking attendance');
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatTime = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleTimeString('en-IN', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="p-6 text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Session not found</h2>
        <Link href="/dashboard/tbt" className="text-blue-600 hover:underline">
          Back to TBT Sessions
        </Link>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <Link
          href="/dashboard/tbt"
          className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to TBT Sessions
        </Link>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{session.topic}</h1>
            <p className="text-gray-600">{session.location}</p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-blue-600">{session.attendance_count || attendance.length}</div>
            <div className="text-sm text-gray-500">Attendees</div>
          </div>
        </div>
      </div>

      {/* Session Details */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Session Details</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Session Date & Time</label>
            <p className="text-gray-900">{formatDate(session.session_date)}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Duration</label>
            <p className="text-gray-900">{session.duration || 30} minutes</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Conductor</label>
            <p className="text-gray-900">{session.conductor_name}</p>
            {session.conductor_phone && (
              <p className="text-sm text-gray-500">{session.conductor_phone}</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Location</label>
            <p className="text-gray-900">{session.location}</p>
          </div>
        </div>

        {session.key_points && (
          <div className="mt-6">
            <label className="block text-sm font-medium text-gray-500 mb-1">Key Points</label>
            <p className="text-gray-900 whitespace-pre-wrap">{session.key_points}</p>
          </div>
        )}

        {session.hazards_discussed && (
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-500 mb-1">Hazards Discussed</label>
            <p className="text-gray-900 whitespace-pre-wrap">{session.hazards_discussed}</p>
          </div>
        )}

        {session.precautions_discussed && (
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-500 mb-1">Precautions Discussed</label>
            <p className="text-gray-900 whitespace-pre-wrap">{session.precautions_discussed}</p>
          </div>
        )}
      </div>

      {/* QR Attendance Scanner */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Mark Attendance</h2>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
          <h3 className="font-medium text-blue-900 mb-2">📱 QR Code Instructions</h3>
          <ol className="text-sm text-blue-700 space-y-1 list-decimal list-inside">
            <li>Workers should have QR codes printed on their safety helmets</li>
            <li>Use a QR scanner app or enter Worker ID manually below</li>
            <li>Each scan automatically marks attendance</li>
            <li>Duplicate scans are prevented</li>
          </ol>
        </div>

        <div className="flex gap-3">
          <input
            type="text"
            value={workerIdInput}
            onChange={(e) => setWorkerIdInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleMarkAttendance()}
            placeholder="Scan QR code or enter Worker ID..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleMarkAttendance}
            className="inline-flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <CheckCircle className="w-5 h-5" />
            Mark Present
          </button>
        </div>
      </div>

      {/* Attendance List */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Attendance List</h2>
          <button className="inline-flex items-center gap-2 px-4 py-2 text-sm text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50">
            <Download className="w-4 h-4" />
            Export
          </button>
        </div>

        {attendance.length === 0 ? (
          <div className="p-12 text-center">
            <Users className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <h3 className="text-lg font-medium text-gray-900 mb-1">No attendance marked yet</h3>
            <p className="text-gray-500">Start scanning worker QR codes to mark attendance</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    #
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Worker ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Worker Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Contractor
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Time Marked
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {attendance.map((record, index) => (
                  <tr key={record.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {index + 1}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{record.worker_id}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{record.worker_name || 'N/A'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{record.contractor_name || 'N/A'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{formatTime(record.marked_at || record.created_at)}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                        <CheckCircle className="w-3 h-3" />
                        Present
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Worker QR Code Generator */}
      <div className="mt-6 bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h3 className="font-medium text-gray-900 mb-2">Need Worker QR Codes?</h3>
        <p className="text-sm text-gray-600 mb-3">
          Generate and print QR codes for workers' helmets from the Workers Management module.
        </p>
        <Link
          href="/dashboard/workers"
          className="inline-flex items-center gap-2 px-4 py-2 text-sm bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          <QrCode className="w-4 h-4" />
          Manage Worker QR Codes
        </Link>
      </div>
    </div>
  );
}
