'use client';

import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { 
  Package, 
  FlaskConical, 
  TestTube2, 
  Beaker, 
  Building2, 
  XCircle,
  ArrowRight,
  TrendingUp
} from 'lucide-react';

export default function ConcreteThingsPage() {
  const modules = [
    {
      title: 'Batch Register',
      description: 'Record and track RMC batch deliveries with complete traceability',
      href: '/dashboard/batches',
      icon: Package,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      stats: { total: '47', recent: '+3 today' }
    },
    {
      title: 'Cube Tests',
      description: 'Manage concrete cube testing and strength analysis',
      href: '/dashboard/cube-tests',
      icon: FlaskConical,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      stats: { total: '124', recent: '98% Pass' }
    },
    {
      title: 'Material Tests',
      description: 'Track material quality tests and approvals',
      href: '/dashboard/materials',
      icon: TestTube2,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      stats: { total: '89', recent: '12 Pending' }
    },
    {
      title: 'Mix Designs',
      description: 'Manage concrete mix designs and specifications',
      href: '/dashboard/mix-designs',
      icon: Beaker,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      stats: { total: '23', recent: '5 Active' }
    },
    {
      title: 'Third-Party Labs',
      description: 'Manage external laboratory test results',
      href: '/dashboard/labs',
      icon: Building2,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
      stats: { total: '15', recent: '3 Labs' }
    },
    {
      title: 'Concrete NC',
      description: 'Track non-conformances and corrective actions',
      href: '/dashboard/concrete-nc',
      icon: XCircle,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
      stats: { total: '8', recent: '2 Open' }
    }
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-blue-600 text-white p-3 rounded-xl">
              <Building2 className="w-6 h-6" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900">ConcreteThings</h1>
          </div>
          <p className="text-gray-600">Quality management for concrete operations</p>
        </div>
        <Link href="/dashboard/projects">
          <span className="text-blue-600 hover:text-blue-700 font-medium text-sm">← Back to Projects</span>
        </Link>
      </div>

      {/* Stats Overview */}
      <Card>
        <CardHeader>
          <CardTitle>Project Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-3xl font-bold text-blue-600">47</p>
              <p className="text-sm text-gray-600">Total Batches</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-green-600">124</p>
              <p className="text-sm text-gray-600">Cube Tests</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-orange-600">89</p>
              <p className="text-sm text-gray-600">Material Tests</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-purple-600">98%</p>
              <p className="text-sm text-gray-600">Pass Rate</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Modules Grid */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Modules</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {modules.map((module) => {
            const Icon = module.icon;
            return (
              <Link key={module.title} href={module.href}>
                <Card className="hover:shadow-xl transition-all cursor-pointer border-2 hover:border-blue-300 h-full">
                  <CardContent className="pt-6">
                    <div className={`${module.bgColor} ${module.color} p-4 rounded-xl w-fit mb-4`}>
                      <Icon className="w-6 h-6" />
                    </div>
                    
                    <h3 className="text-lg font-bold text-gray-900 mb-2">{module.title}</h3>
                    <p className="text-gray-600 text-sm mb-4">{module.description}</p>
                    
                    <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                      <div className="text-sm">
                        <p className="font-bold text-gray-900">{module.stats.total}</p>
                        <p className="text-gray-500 text-xs">{module.stats.recent}</p>
                      </div>
                      <ArrowRight className="w-5 h-5 text-gray-400" />
                    </div>
                  </CardContent>
                </Card>
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}
