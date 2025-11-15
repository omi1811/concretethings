'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import KPICard from '@/components/analytics/KPICard';
import { TrendChart, ComparisonBarChart, DistributionPieChart, MultiLineChart } from '@/components/analytics/Charts';
import { 
  TrendingUpIcon, 
  AlertTriangleIcon, 
  CheckCircleIcon, 
  ClockIcon,
  BarChart3Icon,
  ActivityIcon,
  PackageIcon,
  UsersIcon
} from 'lucide-react';

export default function AnalyticsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [dateRange, setDateRange] = useState('30d');

  useEffect(() => {
    fetchDashboardData();
  }, [dateRange]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      if (!token) {
        router.push('/login');
        return;
      }

      // Fetch data from multiple dashboard endpoints
      const endpoints = [
        '/api/batches',
        '/api/cube-tests',
        '/api/pour-activities',
        '/api/training',
        '/api/materials',
      ];

      const responses = await Promise.all(
        endpoints.map(endpoint =>
          fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
            headers: { Authorization: `Bearer ${token}` }
          }).then(res => res.ok ? res.json() : { data: [] })
        )
      );

      const [batches, cubeTests, pourActivities, trainings, materials] = responses;

      // Process data for analytics
      setDashboardData({
        kpis: {
          totalBatches: batches.data?.length || 0,
          totalTests: cubeTests.data?.length || 0,
          activePours: pourActivities.data?.filter(p => p.status === 'active').length || 0,
          upcomingTrainings: trainings.data?.filter(t => new Date(t.date) > new Date()).length || 0,
        },
        trends: generateTrendData(batches.data || []),
        testResults: generateTestResultsData(cubeTests.data || []),
        materials: generateMaterialsData(materials.data || []),
      });
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  };

  const generateTrendData = (batches) => {
    const last6Months = [];
    const now = new Date();
    
    for (let i = 5; i >= 0; i--) {
      const month = new Date(now.getFullYear(), now.getMonth() - i, 1);
      const monthName = month.toLocaleString('default', { month: 'short' });
      const count = batches.filter(b => {
        const batchDate = new Date(b.created_at);
        return batchDate.getMonth() === month.getMonth() && 
               batchDate.getFullYear() === month.getFullYear();
      }).length;
      
      last6Months.push({ name: monthName, value: count });
    }
    
    return last6Months;
  };

  const generateTestResultsData = (tests) => {
    if (!tests || tests.length === 0) {
      return [
        { name: 'Passed', value: 0 },
        { name: 'Failed', value: 0 },
        { name: 'Pending', value: 0 },
      ];
    }

    const passed = tests.filter(t => t.result === 'pass').length;
    const failed = tests.filter(t => t.result === 'fail').length;
    const pending = tests.filter(t => !t.result || t.result === 'pending').length;

    return [
      { name: 'Passed', value: passed },
      { name: 'Failed', value: failed },
      { name: 'Pending', value: pending },
    ];
  };

  const generateMaterialsData = (materials) => {
    const categories = {};
    
    materials.forEach(m => {
      const category = m.category || 'Other';
      categories[category] = (categories[category] || 0) + 1;
    });

    return Object.entries(categories).map(([name, value]) => ({ name, value }));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse space-y-8">
            <div className="h-12 bg-gray-200 rounded w-1/3"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="h-32 bg-gray-200 rounded"></div>
              ))}
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {[1, 2].map(i => (
                <div key={i} className="h-96 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Advanced Analytics</h1>
            <p className="text-gray-600 mt-2">Real-time insights across all modules</p>
          </div>
          
          <div className="flex items-center space-x-4">
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
            >
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
              <option value="1y">Last Year</option>
            </select>
            
            <button
              onClick={fetchDashboardData}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Refresh
            </button>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <KPICard
            title="Total Batches"
            value={dashboardData?.kpis.totalBatches || 0}
            change={12.5}
            trend="up"
            icon={PackageIcon}
            color="blue"
          />
          <KPICard
            title="Cube Tests"
            value={dashboardData?.kpis.totalTests || 0}
            change={8.3}
            trend="up"
            icon={BarChart3Icon}
            color="green"
          />
          <KPICard
            title="Active Pours"
            value={dashboardData?.kpis.activePours || 0}
            change={-5.2}
            trend="down"
            icon={ActivityIcon}
            color="yellow"
          />
          <KPICard
            title="Upcoming Training"
            value={dashboardData?.kpis.upcomingTrainings || 0}
            change={15.7}
            trend="up"
            icon={UsersIcon}
            color="purple"
          />
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <TrendChart
            data={dashboardData?.trends || []}
            dataKey="value"
            title="Batch Creation Trend (Last 6 Months)"
          />
          
          <DistributionPieChart
            data={dashboardData?.testResults || []}
            title="Cube Test Results Distribution"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ComparisonBarChart
            data={dashboardData?.materials || []}
            title="Materials by Category"
          />
          
          <MultiLineChart
            data={dashboardData?.trends || []}
            lines={[
              { key: 'value', name: 'Batches' },
            ]}
            title="Activity Comparison"
          />
        </div>

        {/* Quick Links */}
        <div className="bg-white rounded-lg border-2 border-gray-200 p-6">
          <h3 className="text-lg font-semibold mb-4">Module Analytics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Link
              href="/dashboard/batches"
              className="p-4 bg-blue-50 border-2 border-blue-200 rounded-lg hover:bg-blue-100 transition-colors text-center"
            >
              <PackageIcon className="w-8 h-8 mx-auto mb-2 text-blue-600" />
              <p className="font-semibold text-blue-900">Batches</p>
            </Link>
            
            <Link
              href="/dashboard/cube-tests"
              className="p-4 bg-green-50 border-2 border-green-200 rounded-lg hover:bg-green-100 transition-colors text-center"
            >
              <BarChart3Icon className="w-8 h-8 mx-auto mb-2 text-green-600" />
              <p className="font-semibold text-green-900">Cube Tests</p>
            </Link>
            
            <Link
              href="/dashboard/pour-activities"
              className="p-4 bg-yellow-50 border-2 border-yellow-200 rounded-lg hover:bg-yellow-100 transition-colors text-center"
            >
              <ActivityIcon className="w-8 h-8 mx-auto mb-2 text-yellow-600" />
              <p className="font-semibold text-yellow-900">Pour Activities</p>
            </Link>
            
            <Link
              href="/dashboard/training"
              className="p-4 bg-purple-50 border-2 border-purple-200 rounded-lg hover:bg-purple-100 transition-colors text-center"
            >
              <UsersIcon className="w-8 h-8 mx-auto mb-2 text-purple-600" />
              <p className="font-semibold text-purple-900">Training</p>
            </Link>
          </div>
        </div>

        {/* Critical Alerts */}
        <div className="bg-white rounded-lg border-2 border-red-200 p-6">
          <div className="flex items-center mb-4">
            <AlertTriangleIcon className="w-6 h-6 text-red-600 mr-2" />
            <h3 className="text-lg font-semibold text-red-900">Critical Alerts</h3>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
              <div className="flex items-center">
                <ClockIcon className="w-5 h-5 text-red-600 mr-3" />
                <div>
                  <p className="font-semibold text-red-900">Overdue Cube Tests</p>
                  <p className="text-sm text-red-700">3 tests pending results</p>
                </div>
              </div>
              <button className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700 transition-colors">
                Review
              </button>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
              <div className="flex items-center">
                <AlertTriangleIcon className="w-5 h-5 text-yellow-600 mr-3" />
                <div>
                  <p className="font-semibold text-yellow-900">Expiring Training</p>
                  <p className="text-sm text-yellow-700">5 certifications expiring soon</p>
                </div>
              </div>
              <button className="px-4 py-2 bg-yellow-600 text-white rounded-lg text-sm hover:bg-yellow-700 transition-colors">
                Review
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
