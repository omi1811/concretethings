'use client';

import { useState, useEffect } from 'react';
import { 
  HardHat, Plus, Package, AlertTriangle, TrendingDown,
  Calendar, User, CheckCircle, XCircle, Search
} from 'lucide-react';
import { apiRequest } from '@/lib/api-optimized';
import toast from 'react-hot-toast';
import Link from 'next/link';
import { format } from 'date-fns';

export default function PPETrackingPage() {
  const [loading, setLoading] = useState(true);
  const [issuances, setIssuances] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [stats, setStats] = useState({
    totalIssued: 0,
    activeIssuances: 0,
    overdueReturns: 0,
    lowStock: 0,
    totalValue: 0
  });

  useEffect(() => {
    fetchPPEData();
  }, []);

  const fetchPPEData = async () => {
    try {
      const projectId = localStorage.getItem('activeProjectId');
      const [issuancesData, inventoryData] = await Promise.all([
        apiRequest(`/api/ppe/issuances?project_id=${projectId}`),
        apiRequest(`/api/ppe/inventory?project_id=${projectId}`)
      ]);

      setIssuances(issuancesData.issuances || []);
      setInventory(inventoryData.inventory || []);

      // Calculate stats
      const activeIssuances = issuancesData.issuances?.filter(i => i.issuance_status === 'issued').length || 0;
      const overdueReturns = issuancesData.issuances?.filter(i => {
        if (i.expected_return_date && i.issuance_status === 'issued') {
          return new Date(i.expected_return_date) < new Date();
        }
        return false;
      }).length || 0;

      setStats({
        totalIssued: issuancesData.issuances?.length || 0,
        activeIssuances,
        overdueReturns,
        lowStock: inventoryData.inventory?.filter(i => i.current_stock < i.minimum_stock).length || 0,
        totalValue: inventoryData.inventory?.reduce((sum, i) => sum + (i.current_stock * i.unit_cost), 0) || 0
      });

    } catch (error) {
      toast.error('Failed to load PPE data');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'issued': 'bg-blue-100 text-blue-800',
      'returned': 'bg-green-100 text-green-800',
      'damaged': 'bg-red-100 text-red-800',
      'lost': 'bg-gray-100 text-gray-800'
    };
    return colors[status] || colors.issued;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <HardHat className="w-8 h-8 text-green-600" />
            PPE Tracking
          </h1>
          <p className="text-gray-600 mt-1">Personal Protective Equipment Management</p>
        </div>
        <div className="flex gap-3">
          <Link
            href="/dashboard/ppe/issue"
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            <Plus className="w-5 h-5" />
            Issue PPE
          </Link>
          <Link
            href="/dashboard/ppe/inventory"
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Package className="w-5 h-5" />
            Manage Inventory
          </Link>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Total Issued</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{stats.totalIssued}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Active</p>
          <p className="text-2xl font-bold text-blue-600 mt-1">{stats.activeIssuances}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Overdue Returns</p>
          <p className="text-2xl font-bold text-red-600 mt-1">{stats.overdueReturns}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Low Stock Items</p>
          <p className="text-2xl font-bold text-orange-600 mt-1">{stats.lowStock}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Total Value</p>
          <p className="text-2xl font-bold text-green-600 mt-1">
            ₹{stats.totalValue.toLocaleString('en-IN')}
          </p>
        </div>
      </div>

      {/* Recent Issuances */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-6 border-b">
          <h2 className="text-xl font-bold text-gray-900">Recent PPE Issuances</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Issuance #
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Worker
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  PPE Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Issue Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Expected Return
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {issuances.slice(0, 10).map((issuance) => (
                <tr key={issuance.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {issuance.issuance_number}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {issuance.worker_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {issuance.ppe_type?.replace('_', ' ')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {format(new Date(issuance.issue_date), 'dd MMM yyyy')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {issuance.expected_return_date 
                      ? format(new Date(issuance.expected_return_date), 'dd MMM yyyy')
                      : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(issuance.issuance_status)}`}>
                      {issuance.issuance_status?.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                    <Link
                      href={`/dashboard/ppe/${issuance.id}`}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Low Stock Alerts */}
      {stats.lowStock > 0 && (
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-6 h-6 text-orange-600 mt-1" />
            <div>
              <h3 className="font-semibold text-orange-900">Low Stock Alert</h3>
              <p className="text-sm text-orange-700 mt-1">
                {stats.lowStock} PPE item(s) are running low on stock. Please reorder soon.
              </p>
              <Link
                href="/dashboard/ppe/inventory"
                className="inline-block mt-2 text-sm text-orange-600 hover:text-orange-700 font-medium"
              >
                View Inventory →
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
