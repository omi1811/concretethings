'use client';

import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/Card';
import { Building2, Shield, Layers } from 'lucide-react';
import React from 'react';
import { projectsAPI, getActiveProjectId } from '@/lib/api-optimized';

export default function ProjectModulesPage() {
  const [project, setProject] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);
  // Robustly get numeric projectId from URL (handles trailing slash)
  let projectId = null;
  if (typeof window !== 'undefined') {
    const path = window.location.pathname.replace(/\/+$/, ''); // remove trailing slash
    const last = path.split('/').pop();
    const parsed = parseInt(last, 10);
    projectId = Number.isNaN(parsed) ? null : parsed;
    // fallback to stored active project id if URL segment isn't numeric
    if (!projectId) {
      const stored = getActiveProjectId();
      if (stored) projectId = stored;
    }
  }

  // Optional: Map module names to icons and descriptions
  const moduleMeta = {
    concrete: {
      name: 'ConcreteThings',
      description: 'End-to-end quality management covering batch registers, cube tests, and material traceability.',
      icon: Building2,
      href: 'concretethings'
    },
    safety: {
      name: 'SafetyApp',
      description: 'Safety, PTW, and NCR scoring workflows kept ready for phased rollouts across job sites.',
      icon: Shield,
      href: 'safetyapp'
    },
    // 'Other Tools' remains available under Projects → Other Tools
  };

  React.useEffect(() => {
    let mounted = true;
    async function fetchProject() {
      try {
        const data = await projectsAPI.getById(projectId);
        if (!mounted) return;
        setProject(data?.project || data || null);
      } catch (err) {
        // Build a detailed error message when available
        let msg = err?.message || String(err);
        if (err && err.status) {
          msg = `Status ${err.status}: ${msg}`;
        }
        if (err && err.details) {
          try {
            msg += ` - ${JSON.stringify(err.details)}`;
          } catch (_) {
            msg += ` - ${String(err.details)}`;
          }
        }
        console.error('Failed to fetch project:', err);
        if (mounted) setError(msg);
      } finally {
        if (mounted) setLoading(false);
      }
    }
    if (projectId) {
      fetchProject();
    } else {
      setError('Project ID not found in URL or localStorage');
      setLoading(false);
    }
    return () => { mounted = false; };
  }, [projectId]);

  // Compute displayed modules from project's enabled modules
  let displayedModules = [];
  if (project && project.enabledModules && project.enabledModules.length > 0) {
    displayedModules = Array.from(new Set(project.enabledModules || []));
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Project Modules</h1>
        <p className="text-gray-600 mt-1">Select a module to access its features</p>
      </div>
      {loading ? (
        <div className="text-gray-500">Loading project modules...</div>
      ) : error ? (
        <div className="text-red-500">{error}</div>
      ) : project ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {displayedModules && displayedModules.length > 0 ? (
            displayedModules.map((mod) => {
              const meta = moduleMeta[mod] || { name: mod, description: '', icon: Layers, href: mod };
              const Icon = meta.icon;
              return (
                <Link key={mod} href={meta.href}>
                  <Card className="hover:shadow-xl transition-all cursor-pointer border-2 hover:border-blue-300 h-full">
                    <CardContent className="pt-6">
                      <div className="flex items-start gap-4 mb-4">
                        <div className="bg-blue-50 text-blue-600 p-4 rounded-xl">
                          <Icon className="w-8 h-8" />
                        </div>
                        <h3 className="text-xl font-bold text-gray-900">{meta.name}</h3>
                      </div>
                      <p className="text-gray-600 text-sm mb-4">{meta.description}</p>
                      {/* Features for this module */}
                      {project.enabledFeatures && project.enabledFeatures.length > 0 && (
                        <div className="mb-4">
                          <p className="text-xs font-semibold text-gray-500 uppercase mb-2">Features</p>
                              <div className="flex flex-wrap gap-2">
                                {(() => {
                                  // Prefer canonical module features when defined; otherwise fallback to project-provided features
                                  const canonical = meta.features && meta.features.length ? meta.features : [];
                                  const source = (canonical.length ? canonical : (project.enabledFeatures || []));
                                  // If project provides enabledFeatures, intersect with canonical to avoid showing unavailable items
                                  const finalList = (project.enabledFeatures && project.enabledFeatures.length && canonical.length)
                                    ? source.filter((f) => project.enabledFeatures.includes(f))
                                    : source;
                                  return finalList.map((feature) => (
                                    <span key={feature} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                                      {feature}
                                    </span>
                                  ));
                                })()}
                              </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </Link>
              );
            })
          ) : (
            <div className="text-gray-500">No modules enabled for this project.</div>
          )}
        </div>
      ) : null}
    </div>
  );
}
