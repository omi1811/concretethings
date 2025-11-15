'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Plus, Search, Building2, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Spinner } from '@/components/ui/Spinner';
import { labAPI } from '@/lib/api-optimized';

export default function LabsPage() {
  const [labs, setLabs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadLabs();
  }, []);

  async function loadLabs() {
    setLoading(true);
    try {
      const result = await labAPI.getAll(1);
      if (result.success) {
        setLabs(result.data.labs || []);
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  }

  const filteredLabs = labs.filter(lab => 
    lab.lab_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    lab.city?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Third-Party Labs</h1>
          <p className="text-gray-600 mt-1">Manage external testing laboratories</p>
        </div>
        <Link href="/dashboard/labs/new">
          <Button><Plus className="w-4 h-4 mr-2" />Add Lab</Button>
        </Link>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search labs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </CardContent>
      </Card>

      {loading ? (
        <div className="flex justify-center py-12"><Spinner size="lg" /></div>
      ) : filteredLabs.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Building2 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No labs found. Add your first laboratory!</p>
            <Link href="/dashboard/labs/new">
              <Button className="mt-4"><Plus className="w-4 h-4 mr-2" />Add Lab</Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {filteredLabs.map((lab) => (
            <Link key={lab.id} href={`/dashboard/labs/${lab.id}`}>
              <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-lg font-semibold">{lab.lab_name || 'N/A'}</h3>
                    {lab.nabl_accredited ? (
                      <Badge variant="success"><CheckCircle className="w-3 h-3 mr-1" />NABL Accredited</Badge>
                    ) : (
                      <Badge variant="warning">Not Accredited</Badge>
                    )}
                  </div>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500">Contact Person</p>
                      <p className="font-medium">{lab.contact_person_name || 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Phone</p>
                      <p className="font-medium">{lab.contact_phone || 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Location</p>
                      <p className="font-medium">{lab.city || 'N/A'}</p>
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
