'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Package, FlaskConical, GraduationCap, TestTube2, TrendingUp, AlertTriangle, Shield } from 'lucide-react';
import TodaysTestsWidget from '@/components/TodaysTestsWidget';

export default function DashboardPage() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    try {
      const userStr = localStorage.getItem('user');
      if (userStr) {
        setUser(JSON.parse(userStr));
      }
    } catch (error) {
      console.error('Error loading user:', error);
    }
  }, []);

  const stats = [
    {
      title: 'Batches',
      value: '47',
      change: '+3 today',
      icon: Package,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100'
    },
    {
      title: 'Cube Tests',
      value: '124',
      change: '98% Pass',
      icon: FlaskConical,
      color: 'text-green-600',
      bgColor: 'bg-green-100'
    },
    {
      title: 'Training Sessions',
      value: '23',
      change: '156 Trainees',
      icon: GraduationCap,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100'
    },
    {
      title: 'Material Tests',
      value: '89',
      change: '12 Pending',
      icon: TestTube2,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100'
    }
  ];
  
  const recentActivities = [
    { type: 'success', message: 'Batch #B-2025-047 approved by QM', time: '10 mins ago' },
    { type: 'danger', message: 'Cube Test #CT-124 failed (18.5 MPa < 20 MPa)', time: '1 hour ago' },
    { type: 'info', message: 'Training session completed - 15 workers trained', time: '2 hours ago' },
    { type: 'warning', message: 'Material Test #MT-089 pending approval', time: '3 hours ago' }
  ];
  
  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600 mt-1">Welcome back! Here's your quality management overview.</p>
          </div>
          
          {/* Support Admin Link (Only for Support Admins) */}
          {(user?.isSupportAdmin || user?.isSystemAdmin) && (
            <Link href="/support">
              <div className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors cursor-pointer">
                <Shield className="w-5 h-5" />
                <span className="font-semibold">Support Admin</span>
              </div>
            </Link>
          )}
        </div>
      </div>
      
      {/* Stats grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card key={index} className="hover:shadow-lg transition-shadow">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 font-medium">{stat.title}</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">{stat.value}</p>
                    <p className="text-sm text-gray-500 mt-1">{stat.change}</p>
                  </div>
                  <div className={`${stat.bgColor} ${stat.color} p-3 rounded-lg`}>
                    <Icon className="w-6 h-6" />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
      
      {/* Today's Cube Tests Widget */}
      <TodaysTestsWidget />
      
      {/* Recent activities */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activities</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentActivities.map((activity, index) => (
              <div key={index} className="flex items-start gap-3 pb-4 border-b border-gray-100 last:border-0 last:pb-0">
                <div className="flex-shrink-0">
                  {activity.type === 'success' && <div className="w-2 h-2 bg-green-500 rounded-full mt-2" />}
                  {activity.type === 'danger' && <div className="w-2 h-2 bg-red-500 rounded-full mt-2" />}
                  {activity.type === 'info' && <div className="w-2 h-2 bg-blue-500 rounded-full mt-2" />}
                  {activity.type === 'warning' && <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2" />}
                </div>
                <div className="flex-1">
                  <p className="text-sm text-gray-900">{activity.message}</p>
                  <p className="text-xs text-gray-500 mt-1">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
      
      {/* Quick actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="hover:shadow-lg transition-shadow cursor-pointer">
          <CardContent className="pt-6 text-center">
            <Package className="w-12 h-12 text-blue-600 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-900">New Batch Entry</h3>
            <p className="text-sm text-gray-600 mt-1">Record RMC delivery</p>
          </CardContent>
        </Card>
        
        <Card className="hover:shadow-lg transition-shadow cursor-pointer">
          <CardContent className="pt-6 text-center">
            <FlaskConical className="w-12 h-12 text-green-600 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-900">Record Cube Test</h3>
            <p className="text-sm text-gray-600 mt-1">Add test results</p>
          </CardContent>
        </Card>
        
        <Card className="hover:shadow-lg transition-shadow cursor-pointer">
          <CardContent className="pt-6 text-center">
            <GraduationCap className="w-12 h-12 text-purple-600 mx-auto mb-3" />
            <h3 className="font-semibold text-gray-900">Training Session</h3>
            <p className="text-sm text-gray-600 mt-1">Log training activity</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
