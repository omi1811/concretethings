'use client';

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Alert } from '@/components/ui/Alert';
import { getUserData } from '@/lib/db';

export default function SettingsPage() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    phone: '',
    companyName: ''
  });

  useEffect(() => {
    loadUserData();
  }, []);

  async function loadUserData() {
    try {
      const userData = await getUserData('current_user');
      if (userData) {
        setUser(userData);
        setFormData({
          fullName: userData.fullName || '',
          email: userData.email || '',
          phone: userData.phone || '',
          companyName: userData.companyName || ''
        });
      }
    } catch (error) {
      console.error('Error loading user data:', error);
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      // API call will be implemented
      setTimeout(() => {
        setSuccess('Settings saved successfully!');
        setLoading(false);
      }, 1000);
    } catch (err) {
      setError('Failed to save settings');
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-1">Manage your account and preferences</p>
      </div>

      {success && (
        <Alert variant="success" onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      {error && (
        <Alert variant="danger" onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Profile Settings */}
        <Card>
          <CardHeader>
            <CardTitle>Profile Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              label="Full Name"
              name="fullName"
              value={formData.fullName}
              onChange={handleChange}
              required
            />
            <Input
              type="email"
              label="Email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              disabled
            />
            <Input
              type="tel"
              label="Phone"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
            />
            <Input
              label="Company Name"
              name="companyName"
              value={formData.companyName}
              onChange={handleChange}
              disabled
            />
          </CardContent>
        </Card>

        {/* Password Change */}
        <Card>
          <CardHeader>
            <CardTitle>Change Password</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              type="password"
              label="Current Password"
              name="currentPassword"
              placeholder="Enter current password"
            />
            <Input
              type="password"
              label="New Password"
              name="newPassword"
              placeholder="Enter new password"
            />
            <Input
              type="password"
              label="Confirm New Password"
              name="confirmPassword"
              placeholder="Confirm new password"
            />
          </CardContent>
        </Card>

        {/* Notification Preferences */}
        <Card>
          <CardHeader>
            <CardTitle>Notification Preferences</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Email Notifications</p>
                <p className="text-sm text-gray-600">Receive email updates for important events</p>
              </div>
              <input type="checkbox" className="w-5 h-5 text-blue-600 rounded" defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">WhatsApp Notifications</p>
                <p className="text-sm text-gray-600">Get instant updates on WhatsApp</p>
              </div>
              <input type="checkbox" className="w-5 h-5 text-blue-600 rounded" defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Sync Reminders</p>
                <p className="text-sm text-gray-600">Remind me to sync offline data</p>
              </div>
              <input type="checkbox" className="w-5 h-5 text-blue-600 rounded" defaultChecked />
            </div>
          </CardContent>
        </Card>

        {/* App Settings */}
        <Card>
          <CardHeader>
            <CardTitle>App Settings</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Offline Mode</p>
                <p className="text-sm text-gray-600">Enable offline data storage</p>
              </div>
              <input type="checkbox" className="w-5 h-5 text-blue-600 rounded" defaultChecked disabled />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Auto-Sync</p>
                <p className="text-sm text-gray-600">Automatically sync when online</p>
              </div>
              <input type="checkbox" className="w-5 h-5 text-blue-600 rounded" defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Photo Compression</p>
                <p className="text-sm text-gray-600">Compress photos to save storage</p>
              </div>
              <input type="checkbox" className="w-5 h-5 text-blue-600 rounded" defaultChecked />
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end">
          <Button type="submit" disabled={loading}>
            {loading ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </form>
    </div>
  );
}
