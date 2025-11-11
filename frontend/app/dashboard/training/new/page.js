'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Camera, UserPlus, X } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Input, Select, Textarea } from '@/components/ui/Input';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Alert } from '@/components/ui/Alert';

export default function NewTrainingPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [attendees, setAttendees] = useState(['']);
  
  const [formData, setFormData] = useState({
    topic: '',
    type: 'Toolbox Talk',
    date: new Date().toISOString().split('T')[0],
    time: '',
    duration: '30',
    location: '',
    conductor: '',
    description: '',
    remarks: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const addAttendee = () => {
    setAttendees([...attendees, '']);
  };

  const removeAttendee = (index) => {
    setAttendees(attendees.filter((_, i) => i !== index));
  };

  const updateAttendee = (index, value) => {
    const newAttendees = [...attendees];
    newAttendees[index] = value;
    setAttendees(newAttendees);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const validAttendees = attendees.filter(a => a.trim());
      if (validAttendees.length === 0) {
        setError('Please add at least one attendee');
        setLoading(false);
        return;
      }

      // API call will be implemented
      setTimeout(() => {
        router.push('/dashboard/training');
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
        <Link href="/dashboard/training">
          <Button variant="outline" size="sm">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">New Training Session</h1>
          <p className="text-gray-600 mt-1">Record worker training or toolbox talk</p>
        </div>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      <form onSubmit={handleSubmit} className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Session Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Topic"
                name="topic"
                value={formData.topic}
                onChange={handleChange}
                placeholder="e.g., Concrete Pouring Safety"
                required
                className="md:col-span-2"
              />
              <Select
                label="Type"
                name="type"
                value={formData.type}
                onChange={handleChange}
                required
              >
                <option value="Toolbox Talk">Toolbox Talk</option>
                <option value="Safety Training">Safety Training</option>
                <option value="Technical Training">Technical Training</option>
                <option value="Induction">Induction</option>
                <option value="Refresher">Refresher</option>
              </Select>
              <Input
                label="Conductor"
                name="conductor"
                value={formData.conductor}
                onChange={handleChange}
                placeholder="e.g., Site Engineer"
                required
              />
              <Input
                type="date"
                label="Date"
                name="date"
                value={formData.date}
                onChange={handleChange}
                required
              />
              <Input
                type="time"
                label="Time"
                name="time"
                value={formData.time}
                onChange={handleChange}
                required
              />
              <Input
                type="number"
                label="Duration (minutes)"
                name="duration"
                value={formData.duration}
                onChange={handleChange}
                required
              />
              <Input
                label="Location"
                name="location"
                value={formData.location}
                onChange={handleChange}
                placeholder="e.g., Site Office"
                required
              />
            </div>
            <Textarea
              label="Description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows={3}
              placeholder="Brief description of the training content..."
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Attendees</CardTitle>
              <Button type="button" size="sm" onClick={addAttendee}>
                <UserPlus className="w-4 h-4 mr-2" />
                Add Attendee
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {attendees.map((attendee, index) => (
              <div key={index} className="flex gap-2">
                <input
                  type="text"
                  value={attendee}
                  onChange={(e) => updateAttendee(index, e.target.value)}
                  placeholder={`Attendee ${index + 1} name`}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required={index === 0}
                />
                {attendees.length > 1 && (
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => removeAttendee(index)}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                )}
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Photos (Optional)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <Camera className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-2">Photo upload will be available soon</p>
              <p className="text-sm text-gray-500">You can add photos after creating the session</p>
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end gap-4">
          <Link href="/dashboard/training">
            <Button type="button" variant="outline">Cancel</Button>
          </Link>
          <Button type="submit" disabled={loading}>
            {loading ? 'Saving...' : 'Save Session'}
          </Button>
        </div>
      </form>
    </div>
  );
}
