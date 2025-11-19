'use client';

import React from 'react';
import { projectsAPI } from '@/lib/api-optimized';

import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/Card';
import { Building2, Shield, ArrowRight, CheckCircle, FolderOpen } from 'lucide-react';

export default function ProjectsPage() {
  const [projects, setProjects] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    let mounted = true;
    async function fetchProjects() {
      try {
        const data = await projectsAPI.getAll();
        if (!mounted) return;
        // projectsAPI returns { projects: [...], total }
        setProjects(data?.projects || data || []);
      } catch (err) {
        setError(err?.message || String(err));
      } finally {
        if (mounted) setLoading(false);
      }
    }
    fetchProjects();
    return () => { mounted = false; };
  }, []);

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Projects</h1>
        <p className="text-gray-600 mt-1">Select a project to access its modules and features</p>
      </div>

      {loading ? (
        <div className="text-gray-500">Loading projects...</div>
      ) : error ? (
        <div className="text-red-500">{error}</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <Link key={project.id} href={`/dashboard/projects/${project.id}`}>
              <Card className="hover:shadow-xl transition-all cursor-pointer border-2 hover:border-blue-300 h-full">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-4 mb-4">
                    <div className="bg-blue-50 text-blue-600 p-4 rounded-xl">
                      <FolderOpen className="w-8 h-8" />
                    </div>
                    <h3 className="text-xl font-bold text-gray-900">{project.name}</h3>
                  </div>
                  <p className="text-gray-600 text-sm mb-4">{project.description}</p>
                  {/* Enabled Modules */}
                  {project.enabledModules && project.enabledModules.length > 0 && (
                    <div className="mb-2">
                      <span className="font-semibold text-gray-700 text-xs">Enabled Modules:</span>
                      <ul className="list-disc ml-5 text-xs text-blue-700">
                        {project.enabledModules.map((mod) => (
                          <li key={mod}>{mod}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {/* Enabled Features */}
                  {project.enabledFeatures && project.enabledFeatures.length > 0 && (
                    <div className="mb-2">
                      <span className="font-semibold text-gray-700 text-xs">Enabled Features:</span>
                      <ul className="list-disc ml-5 text-xs text-green-700">
                        {project.enabledFeatures.map((feat) => (
                          <li key={feat}>{feat}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  <div className="flex items-center gap-2 text-blue-600 font-medium text-sm">
                    <span>Open Project</span>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
