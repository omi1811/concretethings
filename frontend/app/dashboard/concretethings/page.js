'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';
import { Card, CardContent } from '@/components/ui/Card';
import { Building2, FileText, Users, Clipboard, Box, CheckSquare } from 'lucide-react';

export default function ConcreteThingsModulePage() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [enabledFeatures, setEnabledFeatures] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // canonical features for ConcreteThings
  const allFeatures = [
    { name: 'Batch Register', href: '/dashboard/batches', icon: Clipboard },
    { name: 'Cube Testing', href: '/dashboard/cube-tests', icon: Box },
    { name: 'Material Tests', href: '/dashboard/material-tests', icon: CheckSquare },
    { name: 'Mix Designs', href: '/dashboard/mix-designs', icon: Building2 },
    { name: 'Third-Party Labs', href: '/dashboard/third-party-labs', icon: Building2 },
    { name: 'Concrete NC', href: '/dashboard/concrete-nc', icon: FileText },
    { name: 'Training', href: '/dashboard/training', icon: Users },
    { name: 'Handover Report', href: '/dashboard/handovers', icon: FileText }
  ];

  // try to extract projectId from the pathname (/dashboard/projects/[id]/...) or from ?project= query
  let projectId = null;
  if (pathname) {
    const parts = pathname.split('/').filter(Boolean);
    const idx = parts.indexOf('projects');
    if (idx !== -1 && parts.length > idx + 1) {
      projectId = parts[idx + 1];
    }
  }
  if (!projectId && searchParams) projectId = searchParams.get('project');

  useEffect(() => {
    if (!projectId) {
      // no project -> show all features
      setEnabledFeatures(null);
      return;
    }
    setLoading(true);
    setError(null);
    fetch(`/api/projects/${projectId}`)
      .then((r) => {
        if (!r.ok) throw new Error('Failed to fetch project');
        return r.json();
      })
      .then((data) => {
        setEnabledFeatures(data.enabledFeatures || []);
      })
      .catch((err) => {
        console.error('Error fetching project', err);
        setError('Could not load project features');
        setEnabledFeatures([]);
      })
      .finally(() => setLoading(false));
  }, [projectId]);

  // Always show Training and Handover Report so users can access them from ConcreteThings.
  // Other features follow the project's `enabledFeatures` list when present.
  const alwaysVisible = new Set(['Training', 'Handover Report']);
  const visibleFeatures = enabledFeatures && Array.isArray(enabledFeatures)
    ? allFeatures.filter((f) => enabledFeatures.includes(f.name) || alwaysVisible.has(f.name))
    : allFeatures;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">ConcreteThings</h1>
        <p className="text-gray-600 mt-1">Concrete quality management — batches, cube tests, training and handovers.</p>
        {projectId && (
          <p className="text-sm text-gray-500 mt-1">Project: {projectId}</p>
        )}
      </div>

      {loading && <div className="text-sm text-gray-600">Loading project features…</div>}
      {error && <div className="text-sm text-red-600">{error}</div>}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {visibleFeatures.map((f) => {
          const Icon = f.icon;
          // append project query param when present so downstream pages can be scoped
          const href = projectId ? `${f.href}?project=${projectId}` : f.href;
          return (
            <Link key={f.name} href={href}>
              <Card className="hover:shadow-xl transition-all cursor-pointer border-2 hover:border-blue-300 h-full">
                <CardContent className="pt-6">
                  <div className="flex items-start gap-4 mb-4">
                    <div className="bg-blue-50 text-blue-600 p-4 rounded-xl">
                      <Icon className="w-6 h-6" />
                    </div>
                    <h3 className="text-xl font-bold text-gray-900">{f.name}</h3>
                  </div>
                  <p className="text-gray-600 text-sm">Open the {f.name} section.</p>
                </CardContent>
              </Card>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
