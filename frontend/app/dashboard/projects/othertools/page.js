'use client';

import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/Card';
import { Layers, FileText, Users } from 'lucide-react';

export default function OtherToolsPage() {
  const tools = [
    {
      name: 'Training',
      description: 'Access training modules and resources for site teams.',
      icon: Users,
      href: '/dashboard/projects/othertools/training',
    },
    {
      name: 'Handover Report',
      description: 'Generate and review handover reports for completed projects.',
      icon: FileText,
      href: '/dashboard/projects/othertools/handover',
    },
    // Add more tools as needed
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Other Tools</h1>
        <p className="text-gray-600 mt-1">Access additional modules and utilities</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {tools.map((tool) => {
          const Icon = tool.icon;
          return (
            <Link key={tool.name} href={tool.href}>
              <Card className="hover:shadow-xl transition-all cursor-pointer border-2 hover:border-blue-300 h-full">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-4 mb-4">
                    <div className="bg-blue-50 text-blue-600 p-4 rounded-xl">
                      <Icon className="w-8 h-8" />
                    </div>
                    <h3 className="text-xl font-bold text-gray-900">{tool.name}</h3>
                  </div>
                  <p className="text-gray-600 text-sm mb-4">{tool.description}</p>
                  <div className="flex items-center gap-2 text-blue-600 font-medium text-sm">
                    <span>Open Tool</span>
                  </div>
                </CardContent>
              </Card>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
