'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Plus, Search, CheckCircle, XCircle } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Spinner } from '@/components/ui/Spinner';
import { materialTestAPI } from '@/lib/api';

export default function MaterialTestsPage() {
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadTests();
  }, []);

  async function loadTests() {
    setLoading(true);
    try {
      const result = await materialTestAPI.getAll(1);
      if (result.success) {
        setTests(result.data.tests || []);
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  }

  const filteredTests = tests.filter(test => 
    test.material_description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    test.supplier_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Material Tests</h1>
          <p className="text-gray-600 mt-1">Test results for cement, aggregate, and steel</p>
        </div>
        <Link href="/dashboard/materials/new">
          <Button><Plus className="w-4 h-4 mr-2" />New Test</Button>
        </Link>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search material tests..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </CardContent>
      </Card>

      {loading ? (
        <div className="flex justify-center py-12"><Spinner size="lg" /></div>
      ) : filteredTests.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-gray-500">No material tests found. Record your first test!</p>
            <Link href="/dashboard/materials/new">
              <Button className="mt-4"><Plus className="w-4 h-4 mr-2" />Record Test</Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {filteredTests.map((test) => (
            <Link key={test.id} href={`/dashboard/materials/${test.id}`}>
              <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-lg font-semibold">{test.material_description || 'N/A'}</h3>
                    {test.pass_fail_status === 'Pass' ? (
                      <Badge variant="success"><CheckCircle className="w-3 h-3 mr-1" />Pass</Badge>
                    ) : test.pass_fail_status === 'Fail' ? (
                      <Badge variant="danger"><XCircle className="w-3 h-3 mr-1" />Fail</Badge>
                    ) : (
                      <Badge variant="warning">Pending</Badge>
                    )}
                  </div>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500">Brand</p>
                      <p className="font-medium">{test.brand_name || 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Supplier</p>
                      <p className="font-medium">{test.supplier_name || 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Date</p>
                      <p className="font-medium">{test.test_date ? new Date(test.test_date).toLocaleDateString() : 'N/A'}</p>
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
