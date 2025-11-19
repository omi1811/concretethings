'use client';

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { cubeTestAPI, handoverAPI, api, getStoredUser, getActiveProjectId } from '@/lib/api-optimized';

export default function DashboardPage() {
  const [user, setUser] = useState(() => getStoredUser());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [pendingCubeTests, setPendingCubeTests] = useState(0);
  const [todayReminders, setTodayReminders] = useState(0);
  const [pendingHandovers, setPendingHandovers] = useState(0);
  const [trainingStats, setTrainingStats] = useState(null);

  useEffect(() => {
    let mounted = true;
    async function loadOverview() {
      setLoading(true);
      setError(null);
      try {
        const projectId = getActiveProjectId();

        if (!projectId) {
          // If no active project is selected, avoid calling project-scoped endpoints
          // which require `project_id` and would return an error from the API.
          if (!mounted) return;
          setPendingCubeTests(0);
          setTodayReminders(0);
          setPendingHandovers(0);
          setTrainingStats(null);
          setError('No active project selected. Select a project to view project-specific overview.');
          setLoading(false);
          return;
        }

        // Pending cube tests
        const pendingResp = await cubeTestAPI.getAll({ projectId, status: 'pending' });
        const pendingCount = Array.isArray(pendingResp) ? pendingResp.length : (pendingResp?.count ?? 0);

        // Today's reminders (upcoming tests / reminders)
        const remindersResp = await cubeTestAPI.getRemindersToday();
        const remindersCount = Array.isArray(remindersResp) ? remindersResp.length : (remindersResp?.reminders?.length ?? (remindersResp?.count ?? 0));

        // Handover pending items
        const handoversResp = await handoverAPI.getAll(projectId);
        const handoverCount = Array.isArray(handoversResp) ? handoversResp.filter(h => !h.completed && !h.is_deleted).length : (handoversResp?.count ?? 0);

        // Training stats (if available)
        let training = null;
        try {
          training = await api.get('/api/training-records/stats', { project_id: projectId });
        } catch (e) {
          training = null;
        }

        if (!mounted) return;
        setPendingCubeTests(pendingCount);
        setTodayReminders(remindersCount);
        setPendingHandovers(handoverCount);
        setTrainingStats(training);
      } catch (err) {
        console.error('Dashboard overview load error', err);
        if (mounted) setError(err.message || 'Failed to load overview');
      } finally {
        if (mounted) setLoading(false);
      }
    }

    loadOverview();
    return () => { mounted = false; };
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Overview</h1>
        <p className="text-gray-600 mt-1">Welcome back{user?.full_name ? `, ${user.full_name}` : ''}.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Overview — Cube Tests & Related</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p>Loading overview…</p>
          ) : error ? (
            <p className="text-red-600">{error}</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center">
                <p className="text-3xl font-bold text-gray-900">{pendingCubeTests}</p>
                <p className="text-sm text-gray-600">Pending Cube Tests</p>
              </div>

              <div className="text-center">
                <p className="text-3xl font-bold text-blue-600">{todayReminders}</p>
                <p className="text-sm text-gray-600">Reminders Today</p>
              </div>

              <div className="text-center">
                <p className="text-3xl font-bold text-green-600">{pendingHandovers}</p>
                <p className="text-sm text-gray-600">Pending Handovers</p>
              </div>

              <div className="text-center">
                <p className="text-3xl font-bold text-orange-600">{trainingStats ? (trainingStats.pending ?? trainingStats.total ?? 0) : '—'}</p>
                <p className="text-sm text-gray-600">Training Pending</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
