'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Plus, Search, Filter, MapPin, Layers, Calendar, CheckCircle, Clock, XCircle } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Spinner } from '@/components/ui/Spinner';
import { pourActivityAPI } from '@/lib/api';

export default function PourActivitiesPage() {
  const [pourActivities, setPourActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [concreteTypeFilter, setConcreteTypeFilter] = useState('all');

  useEffect(() => {
    loadPourActivities();
  }, [statusFilter, concreteTypeFilter]);

  async function loadPourActivities() {
    setLoading(true);
    try {
      const projectId = localStorage.getItem('currentProjectId') || '1';
      const params = { projectId };
      
      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }
      if (concreteTypeFilter !== 'all') {
        params.concreteType = concreteTypeFilter;
      }

      const result = await pourActivityAPI.getAll(params);
      if (result.success) {
        setPourActivities(result.data.pourActivities || []);
      }
    } catch (error) {
      console.error('Error loading pour activities:', error);
    } finally {
      setLoading(false);
    }
  }

  const filteredPours = pourActivities.filter(pour =>
    pour.pourId?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    pour.location?.gridReference?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    pour.location?.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusBadge = (status) => {
    const variants = {
      'in_progress': { variant: 'warning', icon: Clock, label: 'In Progress' },
      'completed': { variant: 'success', icon: CheckCircle, label: 'Completed' },
      'cancelled': { variant: 'error', icon: XCircle, label: 'Cancelled' }
    };
    const config = variants[status] || variants.in_progress;
    const Icon = config.icon;
    
    return (
      <Badge variant={config.variant}>
        <Icon className="w-3 h-3 mr-1" />
        {config.label}
      </Badge>
    );
  };

  const getConcreteTypeBadge = (type) => {
    return (
      <Badge variant={type === 'PT' ? 'info' : 'default'}>
        {type === 'PT' ? 'Post-Tensioned' : 'Normal'}
      </Badge>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Pour Activities</h1>
          <p className="text-gray-600 mt-1">Manage concrete pouring activities and batch consolidation</p>
        </div>
        <Link href="/dashboard/pour-activities/new">
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            New Pour Activity
          </Button>
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Pours</p>
                <p className="text-2xl font-bold text-gray-900">{pourActivities.length}</p>
              </div>
              <Layers className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">In Progress</p>
                <p className="text-2xl font-bold text-orange-600">
                  {pourActivities.filter(p => p.status === 'in_progress').length}
                </p>
              </div>
              <Clock className="w-8 h-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Completed</p>
                <p className="text-2xl font-bold text-green-600">
                  {pourActivities.filter(p => p.status === 'completed').length}
                </p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">PT Concrete</p>
                <p className="text-2xl font-bold text-purple-600">
                  {pourActivities.filter(p => p.concreteType === 'PT').length}
                </p>
              </div>
              <Layers className="w-8 h-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
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
                  placeholder="Search by pour ID or location..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Status</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
            
            <select
              value={concreteTypeFilter}
              onChange={(e) => setConcreteTypeFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Types</option>
              <option value="Normal">Normal</option>
              <option value="PT">Post-Tensioned</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Pour Activities List */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : filteredPours.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Layers className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 mb-2">No pour activities found.</p>
            <p className="text-sm text-gray-400 mb-4">
              Create a pour activity to group multiple batches for a single structural element.
            </p>
            <Link href="/dashboard/pour-activities/new">
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Create Pour Activity
              </Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {filteredPours.map((pour) => (
            <Link key={pour.id} href={`/dashboard/pour-activities/${pour.id}`}>
              <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardContent className="p-6">
                  <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                    {/* Left: Main Info */}
                    <div className="flex-1">
                      <div className="flex items-start gap-3 mb-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <h3 className="text-lg font-semibold text-gray-900">
                              {pour.pourId}
                            </h3>
                            {getStatusBadge(pour.status)}
                            {getConcreteTypeBadge(pour.concreteType)}
                          </div>
                          
                          <div className="flex items-center gap-4 text-sm text-gray-600 mb-2">
                            <div className="flex items-center gap-1">
                              <Calendar className="w-4 h-4" />
                              {new Date(pour.pourDate).toLocaleDateString()}
                            </div>
                            <div className="flex items-center gap-1">
                              <MapPin className="w-4 h-4" />
                              {pour.location?.gridReference || 'No grid reference'}
                            </div>
                          </div>
                          
                          <p className="text-sm text-gray-700">
                            <span className="font-medium">Location:</span> {pour.location?.description || 'No description'}
                          </p>
                          
                          {pour.location?.structuralElementType && (
                            <p className="text-sm text-gray-600 mt-1">
                              <span className="font-medium">Element:</span> {pour.location.structuralElementType}
                              {pour.location.elementId && ` (${pour.location.elementId})`}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Right: Quantity & Details */}
                    <div className="flex flex-col items-end gap-2">
                      <div className="text-right">
                        <p className="text-sm text-gray-600">Design Grade</p>
                        <p className="text-lg font-semibold text-blue-600">{pour.designGrade}</p>
                      </div>
                      
                      <div className="text-right">
                        <p className="text-sm text-gray-600">Quantity</p>
                        <p className="text-lg font-semibold text-gray-900">
                          {pour.status === 'completed' && pour.totalQuantityReceived 
                            ? `${pour.totalQuantityReceived} m³` 
                            : `${pour.totalQuantityPlanned} m³ (planned)`}
                        </p>
                      </div>
                      
                      {pour.batchCount !== undefined && (
                        <div className="text-right">
                          <p className="text-sm text-gray-600">Batches</p>
                          <p className="text-lg font-semibold text-gray-900">{pour.batchCount}</p>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {pour.remarks && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <p className="text-sm text-gray-600">
                        <span className="font-medium">Remarks:</span> {pour.remarks}
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
