'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Plus, Search, Filter } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { batchAPI } from '@/lib/api';
import { Spinner } from '@/components/ui/Spinner';

export default function BatchesPage() {
  const [batches, setBatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadBatches();
  }, []);

  async function loadBatches() {
    setLoading(true);
    try {
      // Try to get from API (will use offline cache if available)
      const result = await batchAPI.getAll(1); // Default project ID
      if (result.success) {
        setBatches(result.data.batches || []);
      }
    } catch (error) {
      console.error('Error loading batches:', error);
    } finally {
      setLoading(false);
    }
  }

  const filteredBatches = batches.filter(batch => 
    batch.batchNumber?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    batch.vendorName?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Batch Register</h1>
          <p className="text-gray-600 mt-1">Manage concrete batch deliveries</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Link href="/dashboard/batches/quick-entry">
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Quick Entry
            </Button>
          </Link>
          <Link href="/dashboard/batches/import">
            <Button variant="outline">
              Import
            </Button>
          </Link>
          <Link href="/dashboard/batches/new">
            <Button variant="outline">
              Full Form
            </Button>
          </Link>
        </div>
      </div>

      {/* Search and Filter */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search by batch number or vendor..."
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

      {/* Batches List */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : filteredBatches.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-gray-500">No batches found. Create your first batch!</p>
            <Link href="/dashboard/batches/new">
              <Button className="mt-4">
                <Plus className="w-4 h-4 mr-2" />
                Create Batch
              </Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {filteredBatches.map((batch) => (
            <Link key={batch.id} href={`/dashboard/batches/${batch.id}`}>
              <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {batch.batchNumber || 'N/A'}
                        </h3>
                        <Badge variant={batch.status === 'approved' ? 'success' : 'warning'}>
                          {batch.status || 'Pending'}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <p className="text-gray-500">Vendor</p>
                          <p className="font-medium">{batch.vendorName || 'N/A'}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Grade</p>
                          <p className="font-medium">{batch.grade || 'N/A'}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Quantity</p>
                          <p className="font-medium">{batch.quantity || 0} m³</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Date</p>
                          <p className="font-medium">
                            {batch.deliveryDate ? new Date(batch.deliveryDate).toLocaleDateString() : 'N/A'}
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
