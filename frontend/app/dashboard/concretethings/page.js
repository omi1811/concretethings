'use client';

import Link from 'next/link';
import { useEffect, useState, Suspense } from 'react';
import { usePathname, useSearchParams } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Building2, FileText, Users, Clipboard, Box, CheckSquare, Loader2 } from 'lucide-react';

function ConcreteThingsContent() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [enabledFeatures, setEnabledFeatures] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // canonical features for ConcreteThings
  const allFeatures = [
    { name: 'Batch Register', href: '/dashboard/batches', icon: Clipboard, description: 'Manage concrete batches and delivery' },
    { name: 'Cube Testing', href: '/dashboard/cube-tests', icon: Box, description: 'Track cube tests and results' },
    { name: 'Material Tests', href: '/dashboard/material-tests', icon: CheckSquare, description: 'Quality control for raw materials' },
    { name: 'Mix Designs', href: '/dashboard/mix-designs', icon: Building2, description: 'Concrete mix design specifications' },
    { name: 'Third-Party Labs', href: '/dashboard/third-party-labs', icon: Building2, description: 'External laboratory management' },
    { name: 'Concrete NC', href: '/dashboard/concrete-nc', icon: FileText, description: 'Non-conformance reports' },
    { name: 'Training', href: '/dashboard/training', icon: Users, description: 'Staff training records' },
    { name: 'Handover Report', href: '/dashboard/handovers', icon: FileText, description: 'Project handover documentation' }
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
    <div className="space-y-8 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">ConcreteThings</h1>
        <p className="text-muted-foreground mt-1">Concrete quality management — batches, cube tests, training and handovers.</p>
        {projectId && (
          <p className="text-sm text-muted-foreground mt-1">Project ID: <span className="font-medium text-foreground">{projectId}</span></p>
        )}
      </div>

      {loading && (
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="w-4 h-4 animate-spin" />
          Loading project features...
        </div>
      )}

      {error && (
        <div className="bg-destructive/10 border border-destructive/20 text-destructive px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {visibleFeatures.map((f) => {
          const Icon = f.icon;
          // append project query param when present so downstream pages can be scoped
          const href = projectId ? `${f.href}?project=${projectId}` : f.href;
          return (
            <Link key={f.name} href={href} className="block group">
              <Card className="h-full transition-all duration-200 hover:shadow-md hover:border-primary/20 cursor-pointer">
                <CardHeader className="flex flex-row items-center gap-4 pb-2">
                  <div className="bg-primary/10 text-primary p-2 rounded-lg group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                    <Icon className="w-6 h-6" />
                  </div>
                  <CardTitle className="text-lg font-semibold text-foreground group-hover:text-primary transition-colors">
                    {f.name}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-sm text-muted-foreground">
                    {f.description}
                  </CardDescription>
                </CardContent>
              </Card>
            </Link>
          );
        })}
      </div>
    </div>
  );
}

export default function ConcreteThingsModulePage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
          <p className="text-muted-foreground">Loading module...</p>
        </div>
      </div>
    }>
      <ConcreteThingsContent />
    </Suspense>
  );
}
