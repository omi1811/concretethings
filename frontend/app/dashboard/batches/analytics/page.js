'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import KPICard from '@/components/analytics/KPICard';
import { TrendChart, ComparisonBarChart, DistributionPieChart } from '@/components/analytics/Charts';
import { PackageIcon, TrendingUpIcon, AlertCircleIcon, CheckCircleIcon } from 'lucide-react';

export default function BatchAnalyticsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/login');
        return;
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/batches`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (!response.ok) throw new Error('Failed to fetch');
      const result = await response.json();
      const batches = result.data || [];

      // Calculate analytics
      const analytics = {
        kpis: {
          total: batches.length,
          avgStrength: calculateAvgStrength(batches),
          compliance: calculateCompliance(batches),
          pending: batches.filter(b => b.status === 'pending').length,
        },
        strengthTrend: generateStrengthTrend(batches),
        gradeDistribution: generateGradeDistribution(batches),
        monthlyBatches: generateMonthlyBatches(batches),
      };

      setData(analytics);
      setLoading(false);
    } catch (error) {
      console.error('Error:', error);
      setLoading(false);
    }
  };

  const calculateAvgStrength = (batches) => {
    const withStrength = batches.filter(b => b.avg_strength);
    if (withStrength.length === 0) return 0;
    const sum = withStrength.reduce((acc, b) => acc + parseFloat(b.avg_strength || 0), 0);
    return (sum / withStrength.length).toFixed(2);
  };

  const calculateCompliance = (batches) => {
    if (batches.length === 0) return 100;
    const compliant = batches.filter(b => {
      if (!b.avg_strength || !b.design_strength) return false;
      return parseFloat(b.avg_strength) >= parseFloat(b.design_strength);
    }).length;
    return ((compliant / batches.length) * 100).toFixed(1);
  };

  const generateStrengthTrend = (batches) => {
    const last6Months = [];
    const now = new Date();
    
    for (let i = 5; i >= 0; i--) {
      const month = new Date(now.getFullYear(), now.getMonth() - i, 1);
      const monthName = month.toLocaleString('default', { month: 'short' });
      const monthBatches = batches.filter(b => {
        const batchDate = new Date(b.pour_date || b.created_at);
        return batchDate.getMonth() === month.getMonth() && 
               batchDate.getFullYear() === month.getFullYear();
      });
      
      const avgStrength = monthBatches.length > 0 
        ? monthBatches.reduce((acc, b) => acc + parseFloat(b.avg_strength || 0), 0) / monthBatches.length
        : 0;
      
      last6Months.push({ name: monthName, value: parseFloat(avgStrength.toFixed(2)) });
    }
    
    return last6Months;
  };

  const generateGradeDistribution = (batches) => {
    const grades = {};
    batches.forEach(b => {
      const grade = b.concrete_grade || 'Unknown';
      grades[grade] = (grades[grade] || 0) + 1;
    });
    
    return Object.entries(grades).map(([name, value]) => ({ name, value }));
  };

  const generateMonthlyBatches = (batches) => {
    const last6Months = [];
    const now = new Date();
    
    for (let i = 5; i >= 0; i--) {
      const month = new Date(now.getFullYear(), now.getMonth() - i, 1);
      const monthName = month.toLocaleString('default', { month: 'short' });
      const count = batches.filter(b => {
        const batchDate = new Date(b.pour_date || b.created_at);
        return batchDate.getMonth() === month.getMonth() && 
               batchDate.getFullYear() === month.getFullYear();
      }).length;
      
      last6Months.push({ name: monthName, value: count });
    }
    
    return last6Months;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto animate-pulse">
          <div className="h-12 bg-gray-200 rounded w-1/3 mb-8"></div>
          <div className="grid grid-cols-4 gap-6">
            {[1,2,3,4].map(i => <div key={i} className="h-32 bg-gray-200 rounded"></div>)}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Batch Analytics</h1>
          <p className="text-gray-600 mt-2">Concrete batch production insights</p>
        </div>

        {/* KPIs */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <KPICard
            title="Total Batches"
            value={data?.kpis.total || 0}
            change={12.5}
            trend="up"
            icon={PackageIcon}
            color="blue"
          />
          <KPICard
            title="Avg Strength (MPa)"
            value={data?.kpis.avgStrength || 0}
            change={3.2}
            trend="up"
            icon={TrendingUpIcon}
            color="green"
          />
          <KPICard
            title="Compliance Rate"
            value={`${data?.kpis.compliance || 0}%`}
            change={1.5}
            trend="up"
            icon={CheckCircleIcon}
            color="purple"
          />
          <KPICard
            title="Pending Tests"
            value={data?.kpis.pending || 0}
            change={-8.3}
            trend="down"
            icon={AlertCircleIcon}
            color="yellow"
          />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <TrendChart
            data={data?.strengthTrend || []}
            dataKey="value"
            title="Average Strength Trend (MPa)"
          />
          
          <TrendChart
            data={data?.monthlyBatches || []}
            dataKey="value"
            title="Monthly Batch Production"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <DistributionPieChart
            data={data?.gradeDistribution || []}
            title="Concrete Grade Distribution"
          />
          
          <ComparisonBarChart
            data={data?.gradeDistribution || []}
            title="Batches by Grade"
          />
        </div>
      </div>
    </div>
  );
}
