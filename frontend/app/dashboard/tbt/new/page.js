'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Save, Calendar, Users } from 'lucide-react';
import toast from 'react-hot-toast';

const DEFAULT_TOPICS = [
  'Personal Protective Equipment (PPE) Usage',
  'Fire Safety and Prevention',
  'Working at Heights',
  'Electrical Safety',
  'Manual Handling and Lifting',
  'Excavation Safety',
  'Confined Space Entry',
  'Hot Work Precautions',
  'Vehicle and Equipment Safety',
  'First Aid and Emergency Response',
  'Housekeeping and Cleanliness',
  'Hazard Identification and Reporting',
  'Scaffold Safety',
  'Fall Protection',
  'Chemical Handling and Storage'
];

export default function NewTBTSessionPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [topics, setTopics] = useState([]);
  const [formData, setFormData] = useState({
    topic: '',
    custom_topic: '',
    session_date: '',
    location: '',
    conductor_name: '',
    conductor_phone: '',
    duration: '30',
    key_points: '',
    hazards_discussed: '',
    precautions_discussed: ''
  });

  useEffect(() => {
    fetchTopics();
  }, []);

  const fetchTopics = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/tbt/topics', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setTopics(data.topics || DEFAULT_TOPICS);
      } else {
        setTopics(DEFAULT_TOPICS);
      }
    } catch (error) {
      setTopics(DEFAULT_TOPICS);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Use custom topic if "Other" is selected
    const finalTopic = formData.topic === 'custom' ? formData.custom_topic : formData.topic;
    
    if (!finalTopic || !formData.session_date || !formData.location || !formData.conductor_name) {
      toast.error('Please fill in all required fields');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/tbt/sessions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...formData,
          topic: finalTopic
        })
      });

      if (response.ok) {
        const data = await response.json();
        const sessionId = data.session?.id || data.id;
        toast.success('TBT session created successfully');
        router.push(`/dashboard/tbt/${sessionId}`);
      } else {
        const error = await response.json();
        toast.error(error.error || 'Failed to create TBT session');
      }
    } catch (error) {
      console.error('Error creating TBT session:', error);
      toast.error('Error creating TBT session');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <Link
          href="/dashboard/tbt"
          className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to TBT Sessions
        </Link>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">New Toolbox Talk Session</h1>
        <p className="text-gray-600">Schedule a new safety briefing with QR attendance</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Session Details */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Session Details</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Topic *
              </label>
              <select
                name="topic"
                value={formData.topic}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select a topic...</option>
                {topics.map((topic, index) => (
                  <option key={index} value={topic}>{topic}</option>
                ))}
                <option value="custom">Other (Custom Topic)</option>
              </select>
            </div>

            {formData.topic === 'custom' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Custom Topic *
                </label>
                <input
                  type="text"
                  name="custom_topic"
                  value={formData.custom_topic}
                  onChange={handleChange}
                  required={formData.topic === 'custom'}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter custom topic..."
                />
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Session Date & Time *
                </label>
                <input
                  type="datetime-local"
                  name="session_date"
                  value={formData.session_date}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Duration (minutes)
                </label>
                <input
                  type="number"
                  name="duration"
                  value={formData.duration}
                  onChange={handleChange}
                  min="15"
                  max="120"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Location *
              </label>
              <input
                type="text"
                name="location"
                value={formData.location}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Site Office, Main Gate, Block A"
              />
            </div>
          </div>
        </div>

        {/* Conductor Details */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Conductor Details</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Conductor Name *
              </label>
              <input
                type="text"
                name="conductor_name"
                value={formData.conductor_name}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Safety officer or supervisor name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Conductor Phone
              </label>
              <input
                type="tel"
                name="conductor_phone"
                value={formData.conductor_phone}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="+91 XXXXX XXXXX"
              />
            </div>
          </div>
        </div>

        {/* Content Details */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Discussion Content</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Key Points to Cover
              </label>
              <textarea
                name="key_points"
                value={formData.key_points}
                onChange={handleChange}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Main safety points to discuss..."
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Hazards to Discuss
              </label>
              <textarea
                name="hazards_discussed"
                value={formData.hazards_discussed}
                onChange={handleChange}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Specific hazards related to today's work..."
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Precautions to Discuss
              </label>
              <textarea
                name="precautions_discussed"
                value={formData.precautions_discussed}
                onChange={handleChange}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Safety precautions and control measures..."
              />
            </div>
          </div>
        </div>

        {/* Info Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-medium text-blue-900 mb-2">📱 QR Code Attendance</h3>
          <p className="text-sm text-blue-700">
            After creating this session, you'll be able to generate QR codes for workers' helmets. 
            During the TBT, scan each worker's QR code to mark their attendance automatically.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 justify-end">
          <Link
            href="/dashboard/tbt"
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-center"
          >
            Cancel
          </Link>
          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center justify-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            {loading ? 'Creating...' : 'Create TBT Session'}
          </button>
        </div>
      </form>
    </div>
  );
}
