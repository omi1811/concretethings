'use client';

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/Card';
import { cubeTestAPI, handoverAPI, api, getStoredUser, getActiveProjectId } from '@/lib/api-optimized';
import { Beaker, Bell, ClipboardCheck, GraduationCap, ArrowUpRight, Activity } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import Link from 'next/link';

export default function DashboardPage() {
  const [user, setUser] = useState(() => getStoredUser());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [stats, setStats] = useState({
    pendingCubeTests: 0,
    todayReminders: 0,
    pendingHandovers: 0,
    trainingPending: 0
  });

  useEffect(() => {
    let mounted = true;
    async function loadOverview() {
      setLoading(true);
      setError(null);
      try {
        const projectId = getActiveProjectId();

        if (!projectId) {
          if (!mounted) return;
          setStats({
            pendingCubeTests: 0,
            todayReminders: 0,
            pendingHandovers: 0,
            trainingPending: 0
          });
          setError('No active project selected. Please select a project to view the dashboard.');
          setLoading(false);
          return;
        }

        // Parallel data fetching for better performance
        const [pendingResp, remindersResp, handoversResp, trainingResp] = await Promise.allSettled([
          cubeTestAPI.getAll({ projectId, status: 'pending' }),
          cubeTestAPI.getRemindersToday(),
          handoverAPI.getAll(projectId),
          api.get('/api/training-records/stats', { project_id: projectId }).catch(() => null)
        ]);

        if (!mounted) return;

        // Process Pending Cube Tests
        const pendingCount = pendingResp.status === 'fulfilled'
          ? (Array.isArray(pendingResp.value) ? pendingResp.value.length : (pendingResp.value?.count ?? 0))
          : 0;

        // Process Today's Reminders
        const remindersCount = remindersResp.status === 'fulfilled'
          ? (Array.isArray(remindersResp.value) ? remindersResp.value.length : (remindersResp.value?.reminders?.length ?? (remindersResp.value?.count ?? 0)))
          : 0;

        // Process Pending Handovers
        const handoverCount = handoversResp.status === 'fulfilled'
          ? (Array.isArray(handoversResp.value) ? handoversResp.value.filter(h => !h.completed && !h.is_deleted).length : (handoversResp.value?.count ?? 0))
          : 0;

        // Process Training Stats
        const trainingCount = trainingResp.status === 'fulfilled' && trainingResp.value
          ? (trainingResp.value.pending ?? trainingResp.value.total ?? 0)
          : 0;

        setStats({
          pendingCubeTests: pendingCount,
          todayReminders: remindersCount,
          pendingHandovers: handoverCount,
          trainingPending: trainingCount
        });

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

  const statCards = [
    {
      title: 'Pending Cube Tests',
      value: stats.pendingCubeTests,
      icon: Beaker,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100/50 dark:bg-blue-900/20',
      href: '/dashboard/cube-tests?status=pending',
      description: 'Tests waiting for results'
    },
    {
      title: 'Reminders Today',
      value: stats.todayReminders,
      icon: Bell,
      color: 'text-amber-600',
      bgColor: 'bg-amber-100/50 dark:bg-amber-900/20',
      href: '/dashboard/reminders',
      description: 'Actions required today'
    },
    {
      title: 'Pending Handovers',
      value: stats.pendingHandovers,
      icon: ClipboardCheck,
      color: 'text-green-600',
      bgColor: 'bg-green-100/50 dark:bg-green-900/20',
      href: '/dashboard/handovers',
      description: 'Items to be handed over'
    },
    {
      title: 'Training Pending',
      value: stats.trainingPending,
      icon: GraduationCap,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100/50 dark:bg-purple-900/20',
      href: '/dashboard/training',
      description: 'Staff needing training'
    }
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Welcome Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">
            Dashboard
          </h1>
          <p className="text-muted-foreground mt-1">
            Welcome back, <span className="font-medium text-foreground">{user?.full_name || 'User'}</span>. Here's what's happening today.
          </p>
        </div>
        {/* Batch functionality temporarily disabled
        <div className="flex gap-2">
          <Link href="/dashboard/batches/new">
            <Button>
              <Activity className="w-4 h-4 mr-2" />
              New Batch
            </Button>
          </Link>
        </div>
        */}
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-destructive/10 border border-destructive/20 text-destructive px-4 py-3 rounded-lg flex items-center gap-2">
          <Activity className="w-5 h-5" />
          <p>{error}</p>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {loading ? (
          // Skeleton Loading
          Array.from({ length: 4 }).map((_, i) => (
            <Card key={i} className="h-32 animate-pulse bg-muted/50 border-none" />
          ))
        ) : (
          statCards.map((stat, index) => (
            <Link key={index} href={stat.href} className="block group">
              <Card className="h-full transition-all duration-200 hover:shadow-md hover:border-primary/20 cursor-pointer">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {stat.title}
                  </CardTitle>
                  <div className={`p-2 rounded-full ${stat.bgColor}`}>
                    <stat.icon className={`w-4 h-4 ${stat.color}`} />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-foreground group-hover:text-primary transition-colors">
                    {stat.value}
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {stat.description}
                  </p>
                </CardContent>
              </Card>
            </Link>
          ))
        )}
      </div>

      {/* Recent Activity / Quick Actions (Placeholder for future expansion) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common tasks you perform often</CardDescription>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-4">
            <Link href="/dashboard/pour-activities/new">
              <div className="flex flex-col items-center justify-center p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer text-center h-full">
                <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-full mb-3">
                  <Activity className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                </div>
                <span className="font-medium text-sm">Start Pour</span>
              </div>
            </Link>
            {/* Batch functionality temporarily disabled
            <Link href="/dashboard/batches/new">
              <div className="flex flex-col items-center justify-center p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer text-center h-full">
                <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-full mb-3">
                  <Beaker className="w-6 h-6 text-green-600 dark:text-green-400" />
                </div>
                <span className="font-medium text-sm">Register Batch</span>
              </div>
            </Link>
            */}
          </CardContent>
        </Card>

        <Card className="col-span-1">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>Latest updates from your project</CardDescription>
            </div>
            <Button variant="ghost" size="sm" className="text-xs">
              View All <ArrowUpRight className="w-3 h-3 ml-1" />
            </Button>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center h-40 text-center text-muted-foreground bg-muted/20 rounded-lg border border-dashed">
              <Activity className="w-8 h-8 mb-2 opacity-20" />
              <p className="text-sm">Activity feed coming soon</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
