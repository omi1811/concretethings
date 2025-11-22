'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Plus, Search, Filter, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Spinner } from '@/components/ui/Spinner';
import { cubeTestAPI } from '@/lib/api-optimized';

export default function CubeTestsPage() {
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [dueToday, setDueToday] = useState([]);

  useEffect(() => {
    fetchTests();
  }, []);

  const fetchTests = async () => {
    try {
      const projectId = localStorage.getItem('currentProjectId') || '1';
      const result = await cubeTestAPI.list(projectId);
      if (result.data) {
        setTests(result.data);

        // Filter for due today (mock logic for now as backend might not return isDueToday flag yet)
        // In a real app, we'd compare dates.
        const today = new Date().toISOString().slice(0, 10);
        const due = result.data.filter(t => {
          // Check if expectedResultDate matches today and status is not completed
          return t.expectedResultDate && t.expectedResultDate.startsWith(today) && !t.averageStrengthMpa;
        });
        setDueToday(due);
      }
    } catch (error) {
      console.error('Error fetching tests:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      {/* Due Today Section */}
      {dueToday.length > 0 && (
        <Card className="border-orange-200 bg-orange-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-orange-800">
              <AlertCircle className="w-5 h-5" />
              Due for Testing Today
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4">
              {dueToday.map(test => (
                <div key={test.id} className="flex items-center justify-between bg-white p-4 rounded-lg border border-orange-100">
                  <div>
                    <p className="font-medium text-gray-900">{test.testId || `Test #${test.id}`}</p>
                    <p className="text-sm text-gray-500">{test.concreteType} - {test.testAgeDays} Days</p>
                  </div>
                  <Link href={`/dashboard/cube-tests/${test.id}/result`}>
                    <Button size="sm" variant="outline" className="border-orange-200 text-orange-700 hover:bg-orange-50">
                      Record Result
                    </Button>
                  </Link>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Search */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search by batch number or test ID..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            <Button variant="outline">
              <Filter className="w-4 h-4 mr-2" />
              Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Tests List */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : tests.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-gray-500">No cube tests found. Record your first test!</p>
            <Link href="/dashboard/cube-tests/new">
              <Button className="mt-4">
                <Plus className="w-4 h-4 mr-2" />
                Record Test
              </Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {tests.map((test) => (
            <Link key={test.id} href={`/dashboard/cube-tests/${test.id}`}>
              <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {test.testId || `Test #${test.id}`}
                        </h3>
                        {test.averageStrengthMpa ? (
                          <Badge variant={test.passFailStatus === 'pass' ? 'success' : 'danger'}>
                            {test.passFailStatus}
                          </Badge>
                        ) : (
                          <Badge variant="secondary">
                            <Clock className="w-3 h-3 mr-1" />
                            Planned
                          </Badge>
                        )}
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <p className="text-gray-500">Batch</p>
                          <p className="font-medium">{test.batch_number || 'Planned'}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Test Age</p>
                          <p className="font-medium">{test.testAgeDays} days</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Strength</p>
                          <p className="font-medium">{test.averageStrengthMpa ? `${test.averageStrengthMpa} MPa` : '-'}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Date</p>
                          <p className="font-medium">
                            {test.testingDate ? new Date(test.testingDate).toLocaleDateString() : (test.expectedResultDate ? new Date(test.expectedResultDate).toLocaleDateString() : '-')}
                          </p>
                        </div>
                      </div>
                    </div>
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
