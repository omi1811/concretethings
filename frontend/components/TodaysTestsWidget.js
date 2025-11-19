'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Beaker, Calendar, Building2, ExternalLink, RefreshCw } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/Card';
import Button from './ui/Button';
import Badge from './ui/Badge';
import { cubeTestAPI } from '@/lib/api';

/**
 * Today's Cube Tests Widget
 * 
 * Displays all cube tests due for testing today.
 * Shown on dashboard with quick access to test entry.
 */
export default function TodaysTestsWidget() {
  const router = useRouter();
  const [reminders, setReminders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchReminders();
  }, []);

  const fetchReminders = async () => {
    try {
      setLoading(true);
      setError('');
      
      const result = await cubeTestAPI.getRemindersToday();

      if (result?.success === false) {
        setError(result?.error || 'Failed to load reminders');
        setReminders([]);
        return;
      }

      const remindersData = result?.reminders || result?.data?.reminders || [];
      setReminders(Array.isArray(remindersData) ? remindersData : []);
    } catch (err) {
      console.error('Error fetching reminders:', err);
      setError('Error loading test reminders');
    } finally {
      setLoading(false);
    }
  };

  const getAgeColor = (days) => {
    if (days === 3) return 'blue';
    if (days === 7) return 'green';
    if (days === 28) return 'purple';
    if (days === 56) return 'orange';
    return 'gray';
  };

  const handleViewTest = (reminder) => {
    router.push(`/dashboard/cube-tests/${reminder.cubeTestId}?project_id=${reminder.project.id}`);
  };

  const handleViewAll = () => {
    router.push('/dashboard/cube-tests');
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Beaker className="w-5 h-5 text-blue-600" />
              <CardTitle>Today's Cube Tests</CardTitle>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <RefreshCw className="w-6 h-6 text-gray-400 animate-spin" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Beaker className="w-5 h-5 text-blue-600" />
            <CardTitle>Today's Cube Tests</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-red-600">
            <p>{error}</p>
            <Button
              variant="outline"
              size="sm"
              onClick={fetchReminders}
              className="mt-4"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Beaker className="w-5 h-5 text-blue-600" />
            <CardTitle>Today's Cube Tests</CardTitle>
            <Badge variant={reminders.length > 0 ? 'danger' : 'success'}>
              {reminders.length}
            </Badge>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleViewAll}
          >
            View All
            <ExternalLink className="w-4 h-4 ml-2" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {reminders.length === 0 ? (
          <div className="text-center py-8">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Beaker className="w-8 h-8 text-green-600" />
            </div>
            <p className="text-gray-600 font-medium">No tests due today</p>
            <p className="text-sm text-gray-500 mt-1">You're all caught up! 🎉</p>
          </div>
        ) : (
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {reminders.map((reminder) => (
              <div
                key={reminder.reminderId}
                className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:bg-blue-50 transition-all cursor-pointer"
                onClick={() => handleViewTest(reminder)}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    {/* Test Info */}
                    <div className="flex items-center gap-2 mb-2">
                      <Badge variant={getAgeColor(reminder.testAgeDays)}>
                        {reminder.testAgeDays}-Day Test
                      </Badge>
                      <span className="text-sm font-medium text-gray-900">
                        Set #{reminder.setNumber}
                      </span>
                      {reminder.thirdPartyLab && (
                        <Badge variant="warning">
                          🏢 {reminder.thirdPartyLab.name}
                        </Badge>
                      )}
                    </div>

                    {/* Batch & Location */}
                    <div className="flex items-center gap-2 mb-2">
                      <Building2 className="w-4 h-4 text-gray-400 flex-shrink-0" />
                      <div className="text-sm text-gray-700 truncate">
                        {reminder.batch?.location?.buildingName && (
                          <span className="font-medium">
                            {reminder.batch.location.buildingName}
                          </span>
                        )}
                        {reminder.batch?.location?.floorLevel && (
                          <span className="text-gray-500">
                            {' · '}{reminder.batch.location.floorLevel}
                          </span>
                        )}
                        {reminder.batch?.location?.elementId && (
                          <span className="text-gray-500">
                            {' · '}{reminder.batch.location.elementId}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Batch Number */}
                    <div className="text-xs text-gray-500">
                      Batch: {reminder.batch?.batchNumber || 'N/A'}
                    </div>

                    {/* Cubes */}
                    <div className="flex items-center gap-2 mt-2">
                      <span className="text-xs text-gray-600">Cubes:</span>
                      {reminder.cubes.map((cube, idx) => (
                        <span
                          key={idx}
                          className="inline-flex items-center justify-center w-6 h-6 text-xs font-medium bg-gray-100 text-gray-700 rounded border border-gray-300"
                        >
                          {cube}
                        </span>
                      ))}
                    </div>

                    {/* Casting Date */}
                    <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                      <Calendar className="w-3 h-3" />
                      Cast on: {new Date(reminder.castingDate).toLocaleDateString('en-IN', {
                        day: 'numeric',
                        month: 'short'
                      })}
                    </div>
                  </div>

                  {/* Arrow Icon */}
                  <ExternalLink className="w-4 h-4 text-gray-400 flex-shrink-0 mt-1" />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Refresh Button */}
        {reminders.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <Button
              variant="outline"
              size="sm"
              onClick={fetchReminders}
              className="w-full"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
