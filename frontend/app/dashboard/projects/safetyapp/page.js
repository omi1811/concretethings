'use client';

import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { 
  Shield,
  AlertTriangle,
  ClipboardCheck,
  HardHat,
  MapPin,
  FileWarning,
  Clipboard,
  UserCheck,
  MessageSquareWarning,
  ArrowRight
} from 'lucide-react';

export default function SafetyAppPage() {
  const modules = [
    {
      title: 'Safety Dashboard',
      description: 'Overview of safety metrics and incident trends',
      href: '/dashboard/safety',
      icon: Shield,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      stats: { total: '95%', recent: 'Compliance' }
    },
    {
      title: 'Incident Reports',
      description: 'Log and track safety incidents and near misses',
      href: '/dashboard/incidents',
      icon: AlertTriangle,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
      stats: { total: '12', recent: '3 Open' }
    },
    {
      title: 'Safety Audits',
      description: 'Conduct and manage safety inspection audits',
      href: '/dashboard/safety-audits',
      icon: ClipboardCheck,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      stats: { total: '45', recent: '8 This Month' }
    },
    {
      title: 'PPE Tracking',
      description: 'Monitor PPE distribution and compliance',
      href: '/dashboard/ppe',
      icon: HardHat,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      stats: { total: '234', recent: '98% Compliance' }
    },
    {
      title: 'Geofence',
      description: 'Manage site boundaries and access control',
      href: '/dashboard/geofence',
      icon: MapPin,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      stats: { total: '5', recent: '3 Active Zones' }
    },
    {
      title: 'Permit to Work',
      description: 'Issue and track work permits for high-risk tasks',
      href: '/dashboard/ptw',
      icon: FileWarning,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
      stats: { total: '67', recent: '15 Active' }
    },
    {
      title: 'Toolbox Talks',
      description: 'Schedule and record daily safety briefings',
      href: '/dashboard/tbt',
      icon: Clipboard,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
      stats: { total: '89', recent: '23 This Week' }
    },
    {
      title: 'Safety Inductions',
      description: 'Manage worker safety induction training',
      href: '/dashboard/safety-inductions',
      icon: UserCheck,
      color: 'text-teal-600',
      bgColor: 'bg-teal-50',
      stats: { total: '156', recent: '12 Pending' }
    },
    {
      title: 'Safety NC',
      description: 'Track safety non-conformances and actions',
      href: '/dashboard/safety-nc',
      icon: MessageSquareWarning,
      color: 'text-pink-600',
      bgColor: 'bg-pink-50',
      stats: { total: '18', recent: '5 Open' }
    }
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-green-600 text-white p-3 rounded-xl">
              <Shield className="w-6 h-6" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900">SafetyApp</h1>
          </div>
          <p className="text-gray-600">Comprehensive safety management and compliance monitoring</p>
        </div>
        <Link href="/dashboard/projects">
          <span className="text-blue-600 hover:text-blue-700 font-medium text-sm">← Back to Projects</span>
        </Link>
      </div>

      {/* Stats Overview */}
      <Card>
        <CardHeader>
          <CardTitle>Safety Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-3xl font-bold text-green-600">95%</p>
              <p className="text-sm text-gray-600">Compliance Rate</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-red-600">12</p>
              <p className="text-sm text-gray-600">Incidents</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-blue-600">45</p>
              <p className="text-sm text-gray-600">Safety Audits</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-orange-600">67</p>
              <p className="text-sm text-gray-600">Active PTW</p>
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
                <Card className="hover:shadow-xl transition-all cursor-pointer border-2 hover:border-green-300 h-full">
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
