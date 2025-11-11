'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Plus, Search, FileCheck, AlertCircle, CheckCircle, Clock, XCircle } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { handoverAPI } from '@/lib/api';
import { Spinner } from '@/components/ui/Spinner';

export default function HandoverRegisterPage() {
  const [handovers, setHandovers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadHandovers();
  }, []);

  async function loadHandovers() {
    setLoading(true);
    try {
      const result = await handoverAPI.getAll(1); // Default project ID
      if (result.success) {
        setHandovers(result.data.handovers || []);
      }
    } catch (error) {
      console.error('Error loading handovers:', error);
    } finally {
      setLoading(false);
    }
  }

  const filteredHandovers = handovers.filter(handover =>
    handover.handover_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    handover.work_description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    handover.work_location?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    handover.outgoing_contractor_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusBadge = (status) => {
    const statusConfig = {
      'draft': { color: 'gray', icon: Clock, label: 'Draft' },
      'pending_approval': { color: 'yellow', icon: Clock, label: 'Pending Approval' },
      'approved': { color: 'green', icon: CheckCircle, label: 'Approved' },
      'rejected': { color: 'red', icon: XCircle, label: 'Rejected' },
      'completed': { color: 'blue', icon: CheckCircle, label: 'Completed' }
    };

    const config = statusConfig[status] || statusConfig['draft'];
    const Icon = config.icon;

    return (
      <Badge variant={config.color} className="flex items-center gap-1">
        <Icon className="w-3 h-3" />
        {config.label}
      </Badge>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Handover Register</h1>
          <p className="text-gray-600 mt-1">Work completion & handover certificates</p>
        </div>
        <Link href="/dashboard/handovers/new">
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            New Handover
          </Button>
        </Link>
      </div>

      {/* Search */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <Input
                placeholder="Search by handover number, work description, location, or contractor..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full"
              />
            </div>
            <Button variant="outline">
              <Search className="w-4 h-4 mr-2" />
              Search
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Handover List */}
      {loading ? (
        <div className="flex justify-center items-center py-12">
          <Spinner size="lg" />
        </div>
      ) : filteredHandovers.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <FileCheck className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {searchTerm ? 'No handovers found' : 'No handovers yet'}
            </h3>
            <p className="text-gray-600 mb-6">
              {searchTerm
                ? 'Try adjusting your search terms'
                : 'Start by creating your first work handover record'}
            </p>
            {!searchTerm && (
              <Link href="/dashboard/handovers/new">
                <Button>
                  <Plus className="w-4 h-4 mr-2" />
                  Create Handover
                </Button>
              </Link>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {filteredHandovers.map((handover) => (
            <Card key={handover.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {handover.handover_number}
                      </h3>
                      {getStatusBadge(handover.status)}
                      {handover.has_defects && (
                        <Badge variant="red" className="flex items-center gap-1">
                          <AlertCircle className="w-3 h-3" />
                          {handover.defects_count} Defect{handover.defects_count !== 1 ? 's' : ''}
                        </Badge>
                      )}
                      {handover.quality_standard_met && !handover.has_defects && (
                        <Badge variant="green" className="flex items-center gap-1">
                          <CheckCircle className="w-3 h-3" />
                          Quality Met
                        </Badge>
                      )}
                    </div>
                    <p className="text-gray-700 font-medium mb-1">
                      {handover.work_description}
                    </p>
                    <p className="text-sm text-gray-600">
                      Location: {handover.work_location}
                      {handover.floor_level && ` • Floor: ${handover.floor_level}`}
                      {handover.zone_area && ` • Zone: ${handover.zone_area}`}
                    </p>
                  </div>
                  <Link href={`/dashboard/handovers/${handover.id}`}>
                    <Button variant="outline" size="sm">
                      View Details
                    </Button>
                  </Link>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-gray-200">
                  {/* Work Category */}
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Work Category</p>
                    <Badge variant="blue">{handover.work_category}</Badge>
                  </div>

                  {/* Outgoing Contractor */}
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Outgoing Contractor</p>
                    <p className="text-sm font-medium text-gray-900">
                      {handover.outgoing_contractor_name}
                    </p>
                    <p className="text-xs text-gray-600">
                      {handover.outgoing_supervisor_name}
                      {handover.outgoing_signed_date && (
                        <CheckCircle className="w-3 h-3 inline ml-1 text-green-600" />
                      )}
                    </p>
                  </div>

                  {/* Incoming Contractor */}
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Incoming Contractor</p>
                    <p className="text-sm font-medium text-gray-900">
                      {handover.incoming_contractor_name || 'Not specified'}
                    </p>
                    {handover.incoming_supervisor_name && (
                      <p className="text-xs text-gray-600">
                        {handover.incoming_supervisor_name}
                        {handover.incoming_signed_date && (
                          <CheckCircle className="w-3 h-3 inline ml-1 text-green-600" />
                        )}
                      </p>
                    )}
                  </div>

                  {/* Dates */}
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Handover Date</p>
                    <p className="text-sm text-gray-900">
                      {new Date(handover.handover_date).toLocaleDateString()}
                    </p>
                  </div>

                  {/* Engineer */}
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Building Engineer</p>
                    <p className="text-sm font-medium text-gray-900">
                      {handover.engineer_name}
                      {handover.engineer_signed_date && (
                        <CheckCircle className="w-3 h-3 inline ml-1 text-green-600" />
                      )}
                    </p>
                  </div>

                  {/* Warranty */}
                  {handover.warranty_period_months > 0 && (
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Warranty Period</p>
                      <p className="text-sm text-gray-900">
                        {handover.warranty_period_months} months
                      </p>
                    </div>
                  )}
                </div>

                {/* Engineer Remarks */}
                {handover.engineer_remarks && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <p className="text-xs text-gray-500 mb-1">Engineer's Remarks</p>
                    <p className="text-sm text-gray-700">{handover.engineer_remarks}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
