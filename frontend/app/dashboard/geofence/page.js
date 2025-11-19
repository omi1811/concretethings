'use client';

import { useState, useEffect } from 'react';
import { 
  MapPin, Plus, Activity, CheckCircle, XCircle,
  AlertCircle, MapPinned, Navigation, Settings
} from 'lucide-react';
import { apiRequest } from '@/lib/api-optimized';
import toast from 'react-hot-toast';
import { format } from 'date-fns';

export default function GeofencePage() {
  const [loading, setLoading] = useState(true);
  const [geofence, setGeofence] = useState(null);
  const [verifications, setVerifications] = useState([]);
  const [showSetupForm, setShowSetupForm] = useState(false);
  const [formData, setFormData] = useState({
    location_name: '',
    center_latitude: '',
    center_longitude: '',
    radius_meters: 100,
    tolerance_meters: 20,
    strict_mode: true,
    address: '',
    city: '',
    state: '',
    pincode: ''
  });

  useEffect(() => {
    fetchGeofenceData();
  }, []);

  const fetchGeofenceData = async () => {
    try {
      const projectId = localStorage.getItem('activeProjectId');
      const [geofenceData, verificationsData] = await Promise.all([
        apiRequest(`/api/geofence?project_id=${projectId}`),
        apiRequest(`/api/geofence/verifications?project_id=${projectId}&limit=20`)
      ]);

      setGeofence(geofenceData.geofence);
      setVerifications(verificationsData.verifications || []);

      if (geofenceData.geofence) {
        setFormData({
          location_name: geofenceData.geofence.location_name || '',
          center_latitude: geofenceData.geofence.center_latitude || '',
          center_longitude: geofenceData.geofence.center_longitude || '',
          radius_meters: geofenceData.geofence.radius_meters || 100,
          tolerance_meters: geofenceData.geofence.tolerance_meters || 20,
          strict_mode: geofenceData.geofence.strict_mode ?? true,
          address: geofenceData.geofence.address || '',
          city: geofenceData.geofence.city || '',
          state: geofenceData.geofence.state || '',
          pincode: geofenceData.geofence.pincode || ''
        });
      }
    } catch (error) {
      console.error('Failed to load geofence data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const projectId = localStorage.getItem('activeProjectId');
      await apiRequest('/api/geofence', {
        method: 'POST',
        body: JSON.stringify({
          project_id: parseInt(projectId),
          ...formData
        })
      });

      toast.success('Geofence setup successfully');
      setShowSetupForm(false);
      fetchGeofenceData();
    } catch (error) {
      toast.error('Failed to setup geofence');
    }
  };

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setFormData(prev => ({
            ...prev,
            center_latitude: position.coords.latitude.toFixed(6),
            center_longitude: position.coords.longitude.toFixed(6)
          }));
          toast.success('Location captured successfully');
        },
        (error) => {
          toast.error('Failed to get current location');
        }
      );
    } else {
      toast.error('Geolocation is not supported by this browser');
    }
  };

  const stats = {
    totalVerifications: verifications.length,
    withinGeofence: verifications.filter(v => v.is_verified).length,
    outsideGeofence: verifications.filter(v => !v.is_verified).length,
    complianceRate: verifications.length > 0 
      ? Math.round((verifications.filter(v => v.is_verified).length / verifications.length) * 100)
      : 0
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <MapPin className="w-8 h-8 text-purple-600" />
            Geofence Management
          </h1>
          <p className="text-gray-600 mt-1">Manage project location boundaries</p>
        </div>
        {geofence && (
          <button
            onClick={() => setShowSetupForm(!showSetupForm)}
            className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          >
            <Settings className="w-5 h-5" />
            {showSetupForm ? 'Cancel' : 'Update Geofence'}
          </button>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Total Verifications</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{stats.totalVerifications}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Within Geofence</p>
          <p className="text-2xl font-bold text-green-600 mt-1">{stats.withinGeofence}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Outside Geofence</p>
          <p className="text-2xl font-bold text-red-600 mt-1">{stats.outsideGeofence}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Compliance Rate</p>
          <p className="text-2xl font-bold text-blue-600 mt-1">{stats.complianceRate}%</p>
        </div>
      </div>

      {/* Setup Form or Geofence Info */}
      {!geofence || showSetupForm ? (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6">
            {geofence ? 'Update Geofence' : 'Setup Geofence'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Location Name *
                </label>
                <input
                  type="text"
                  value={formData.location_name}
                  onChange={(e) => setFormData({...formData, location_name: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  required
                />
              </div>

              <div className="flex gap-2">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Radius (meters) *
                  </label>
                  <input
                    type="number"
                    value={formData.radius_meters}
                    onChange={(e) => setFormData({...formData, radius_meters: parseInt(e.target.value)})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    required
                  />
                </div>
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tolerance (meters)
                  </label>
                  <input
                    type="number"
                    value={formData.tolerance_meters}
                    onChange={(e) => setFormData({...formData, tolerance_meters: parseInt(e.target.value)})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Center Latitude *
                </label>
                <input
                  type="text"
                  value={formData.center_latitude}
                  onChange={(e) => setFormData({...formData, center_latitude: e.target.value})}
                  placeholder="19.0760"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Center Longitude *
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={formData.center_longitude}
                    onChange={(e) => setFormData({...formData, center_longitude: e.target.value})}
                    placeholder="72.8777"
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    required
                  />
                  <button
                    type="button"
                    onClick={getCurrentLocation}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                  >
                    <Navigation className="w-4 h-4" />
                    Current
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Address
                </label>
                <input
                  type="text"
                  value={formData.address}
                  onChange={(e) => setFormData({...formData, address: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  City
                </label>
                <input
                  type="text"
                  value={formData.city}
                  onChange={(e) => setFormData({...formData, city: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  State
                </label>
                <input
                  type="text"
                  value={formData.state}
                  onChange={(e) => setFormData({...formData, state: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Pincode
                </label>
                <input
                  type="text"
                  value={formData.pincode}
                  onChange={(e) => setFormData({...formData, pincode: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                />
              </div>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="strict_mode"
                checked={formData.strict_mode}
                onChange={(e) => setFormData({...formData, strict_mode: e.target.checked})}
                className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
              />
              <label htmlFor="strict_mode" className="text-sm text-gray-700">
                Strict Mode (Reject entries outside geofence)
              </label>
            </div>

            <div className="flex gap-3">
              <button
                type="submit"
                className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
              >
                {geofence ? 'Update Geofence' : 'Setup Geofence'}
              </button>
              {showSetupForm && (
                <button
                  type="button"
                  onClick={() => setShowSetupForm(false)}
                  className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                >
                  Cancel
                </button>
              )}
            </div>
          </form>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Current Geofence</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Location Name</p>
              <p className="font-medium text-gray-900">{geofence.location_name}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Center Coordinates</p>
              <p className="font-medium text-gray-900">
                {geofence.center_latitude}, {geofence.center_longitude}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Radius</p>
              <p className="font-medium text-gray-900">{geofence.radius_meters} meters</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Mode</p>
              <p className="font-medium text-gray-900">
                {geofence.strict_mode ? 'Strict' : 'Warning Only'}
              </p>
            </div>
            {geofence.address && (
              <div className="md:col-span-2">
                <p className="text-sm text-gray-600">Address</p>
                <p className="font-medium text-gray-900">{geofence.address}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Recent Verifications */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-6 border-b">
          <h2 className="text-xl font-bold text-gray-900">Recent Location Verifications</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Action
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Location
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Distance
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {verifications.map((verification) => (
                <tr key={verification.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {format(new Date(verification.verified_at), 'dd MMM yyyy HH:mm')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {verification.user_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {verification.action_type}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {verification.latitude}, {verification.longitude}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {verification.distance_from_center} m
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {verification.is_verified ? (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        <CheckCircle className="w-3 h-3 mr-1" />
                        Within Geofence
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        <XCircle className="w-3 h-3 mr-1" />
                        Outside Geofence
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
