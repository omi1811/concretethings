'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { Building2, Users, DollarSign, TrendingUp, Plus, Search, Settings, Eye, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/Button';

const SUPPORT_API_BASE = '/api/support';

export default function SupportDashboard() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [overview, setOverview] = useState(null);
  const [companies, setCompanies] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [overviewRes, companiesRes] = await Promise.all([
        api.get(`${SUPPORT_API_BASE}/dashboard`),
        api.get(`${SUPPORT_API_BASE}/companies`)
      ]);
      
      const overviewData = overviewRes?.data?.data ?? overviewRes?.data ?? overviewRes;
      const companiesData = Array.isArray(companiesRes?.data)
        ? companiesRes.data
        : Array.isArray(companiesRes?.data?.data)
          ? companiesRes.data.data
          : Array.isArray(companiesRes)
            ? companiesRes
            : [];

      setOverview(overviewData);
      setCompanies(companiesData);
    } catch (error) {
      console.error('Error fetching support data:', error);
      if (error.response?.status === 403) {
        alert('Access denied. Support admin privileges required.');
        router.push('/dashboard');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    try {
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (statusFilter) params.append('status', statusFilter);

      const queryString = params.toString();
      const endpoint = queryString
        ? `${SUPPORT_API_BASE}/companies?${queryString}`
        : `${SUPPORT_API_BASE}/companies`;

      const res = await api.get(endpoint);
      const list = Array.isArray(res?.data)
        ? res.data
        : Array.isArray(res?.data?.data)
          ? res.data.data
          : Array.isArray(res)
            ? res
            : [];
      setCompanies(list);
    } catch (error) {
      console.error('Error searching companies:', error);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      handleSearch();
    }, 500);
    return () => clearTimeout(timer);
  }, [searchTerm, statusFilter]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading support dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Support Admin Dashboard</h1>
              <p className="text-gray-600 mt-1">Manage companies, projects, and billing</p>
            </div>
            <Button onClick={() => setShowCreateModal(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Create Company
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            icon={<Building2 className="w-6 h-6 text-blue-600" />}
            title="Total Companies"
            value={overview?.totalCompanies || 0}
            subtitle={`${overview?.activeCompanies || 0} active`}
            color="blue"
          />
          <StatCard
            icon={<Users className="w-6 h-6 text-green-600" />}
            title="Active Projects"
            value={overview?.activeProjects || 0}
            subtitle={`of ${overview?.totalProjects || 0} total`}
            color="green"
          />
          <StatCard
            icon={<DollarSign className="w-6 h-6 text-purple-600" />}
            title="Monthly Revenue"
            value={`₹${(overview?.monthlyRevenue || 0).toLocaleString()}`}
            subtitle="Recurring"
            color="purple"
          />
          <StatCard
            icon={<TrendingUp className="w-6 h-6 text-orange-600" />}
            title="New Signups"
            value={overview?.newSignupsThisMonth || 0}
            subtitle="This month"
            color="orange"
          />
        </div>

        {/* Suspended Companies Alert */}
        {overview?.suspendedCompanies > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-red-900">
                {overview.suspendedCompanies} {overview.suspendedCompanies === 1 ? 'company' : 'companies'} suspended
              </h3>
              <p className="text-sm text-red-700 mt-1">
                Review suspended companies and follow up on payments.
              </p>
            </div>
          </div>
        )}

        {/* Top Companies */}
        {overview?.topCompanies && overview.topCompanies.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Top Companies by Revenue</h2>
            <div className="space-y-3">
              {overview.topCompanies.map((company, index) => (
                <div key={company.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                  <div className="flex items-center gap-3">
                    <span className="font-bold text-2xl text-gray-400">#{index + 1}</span>
                    <div>
                      <p className="font-semibold text-gray-900">{company.name}</p>
                      <p className="text-sm text-gray-600">{company.activeProjects} active projects</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-lg text-green-600">₹{company.monthlyRevenue.toLocaleString()}/mo</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Companies List */}
        <div className="bg-white rounded-lg shadow-sm">
          <div className="p-6 border-b border-gray-200">
            <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">All Companies</h2>
              <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search companies..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent w-full sm:w-64"
                  />
                </div>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Status</option>
                  <option value="active">Active</option>
                  <option value="suspended">Suspended</option>
                  <option value="cancelled">Cancelled</option>
                  <option value="trial">Trial</option>
                </select>
              </div>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Company</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Projects</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Plan</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Revenue</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {companies.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="px-6 py-12 text-center text-gray-500">
                      No companies found. Create your first company to get started.
                    </td>
                  </tr>
                ) : (
                  companies.map((company) => (
                    <CompanyRow
                      key={company.id}
                      company={company}
                      onEdit={(comp) => {
                        setSelectedCompany(comp);
                        setShowEditModal(true);
                      }}
                      onRefresh={fetchData}
                    />
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Create Company Modal */}
      {showCreateModal && (
        <CreateCompanyModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false);
            fetchData();
          }}
        />
      )}

      {/* Edit Company Modal */}
      {showEditModal && selectedCompany && (
        <EditCompanyModal
          company={selectedCompany}
          onClose={() => {
            setShowEditModal(false);
            setSelectedCompany(null);
          }}
          onSuccess={() => {
            setShowEditModal(false);
            setSelectedCompany(null);
            fetchData();
          }}
        />
      )}
    </div>
  );
}

function StatCard({ icon, title, value, subtitle, color }) {
  const colorClasses = {
    blue: 'bg-blue-50',
    green: 'bg-green-50',
    purple: 'bg-purple-50',
    orange: 'bg-orange-50'
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="flex items-center gap-4">
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          {icon}
        </div>
        <div className="flex-1">
          <p className="text-sm text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
        </div>
      </div>
    </div>
  );
}

function CompanyRow({ company, onEdit, onRefresh }) {
  const statusColors = {
    active: 'bg-green-100 text-green-800',
    suspended: 'bg-red-100 text-red-800',
    cancelled: 'bg-gray-100 text-gray-800',
    trial: 'bg-blue-100 text-blue-800'
  };

  const planNames = {
    trial: 'Trial',
    starter: 'Starter',
    basic: 'Basic',
    professional: 'Pro',
    pro: 'Pro',
    enterprise: 'Enterprise'
  };

  return (
    <tr className="hover:bg-gray-50">
      <td className="px-6 py-4">
        <div>
          <p className="font-semibold text-gray-900">{company.name}</p>
          {company.companyEmail && (
            <p className="text-sm text-gray-600">{company.companyEmail}</p>
          )}
        </div>
      </td>
      <td className="px-6 py-4">
        <div className="text-sm">
          <span className="font-semibold text-gray-900">{company.activeProjects}</span>
          <span className="text-gray-600"> / {company.activeProjectsLimit}</span>
          <p className="text-xs text-gray-500 mt-1">
            ({company.totalProjects} total)
          </p>
        </div>
      </td>
      <td className="px-6 py-4">
        <span className="text-sm font-medium text-gray-900">
          {planNames[company.subscriptionPlan] || company.subscriptionPlan}
        </span>
      </td>
      <td className="px-6 py-4">
        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusColors[company.billingStatus] || 'bg-gray-100 text-gray-800'}`}>
          {company.billingStatus}
        </span>
      </td>
      <td className="px-6 py-4">
        <p className="font-semibold text-gray-900">₹{company.monthlyRevenue.toLocaleString()}/mo</p>
        <p className="text-xs text-gray-500">₹{company.pricePerProject.toLocaleString()} per project</p>
      </td>
      <td className="px-6 py-4">
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => onEdit(company)}
          >
            <Settings className="w-4 h-4" />
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => window.open(`/support/companies/${company.id}`, '_blank')}
          >
            <Eye className="w-4 h-4" />
          </Button>
        </div>
      </td>
    </tr>
  );
}

function CreateCompanyModal({ onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    name: '',
    subscriptionPlan: 'trial',
    activeProjectsLimit: 1,
    pricePerProject: 5000,
    billingStatus: 'active',
    companyEmail: '',
    companyPhone: '',
    companyAddress: '',
    gstin: ''
  });
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      const payload = {
        ...formData,
        activeProjectsLimit: Math.max(1, Number(formData.activeProjectsLimit) || 0),
        pricePerProject: Number(formData.pricePerProject) || 0,
      };

      await api.post(`${SUPPORT_API_BASE}/companies`, payload);
      alert('Company created successfully!');
      onSuccess();
    } catch (error) {
      console.error('Error creating company:', error);
      alert(error.response?.data?.error || 'Failed to create company');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold">Create New Company</h2>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Company Name *
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="ABC Construction Pvt Ltd"
            />
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="email"
                value={formData.companyEmail}
                onChange={(e) => setFormData({ ...formData, companyEmail: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="contact@company.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Phone
              </label>
              <input
                type="tel"
                value={formData.companyPhone}
                onChange={(e) => setFormData({ ...formData, companyPhone: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="+91 9876543210"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Subscription Plan
            </label>
            <select
              value={formData.subscriptionPlan}
              onChange={(e) => setFormData({ ...formData, subscriptionPlan: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="trial">Trial (30 days free)</option>
              <option value="starter">Starter</option>
              <option value="basic">Basic</option>
              <option value="professional">Professional</option>
              <option value="enterprise">Enterprise</option>
            </select>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Project Limit
              </label>
              <input
                type="number"
                min="1"
                required
                value={formData.activeProjectsLimit}
                onChange={(e) => {
                  const { value } = e.target;
                  setFormData((prev) => ({
                    ...prev,
                    activeProjectsLimit: value === '' ? '' : Number(value),
                  }));
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Price Per Project (₹)
              </label>
              <input
                type="number"
                min="0"
                step="500"
                required
                value={formData.pricePerProject}
                onChange={(e) => {
                  const { value } = e.target;
                  setFormData((prev) => ({
                    ...prev,
                    pricePerProject: value === '' ? '' : Number(value),
                  }));
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Billing Status
            </label>
            <select
              value={formData.billingStatus}
              onChange={(e) => setFormData({ ...formData, billingStatus: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="active">Active</option>
              <option value="suspended">Suspended</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>

          <div className="flex gap-3 pt-4">
            <Button type="submit" disabled={saving} className="flex-1">
              {saving ? 'Creating...' : 'Create Company'}
            </Button>
            <Button type="button" variant="outline" onClick={onClose} className="flex-1">
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

function EditCompanyModal({ company, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    name: company.name,
    subscriptionPlan: company.subscriptionPlan,
    activeProjectsLimit: company.activeProjectsLimit,
    pricePerProject: company.pricePerProject,
    billingStatus: company.billingStatus,
    companyEmail: company.companyEmail || '',
    companyPhone: company.companyPhone || '',
    companyAddress: company.companyAddress || '',
    gstin: company.gstin || '',
    isActive: company.isActive
  });
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      const payload = {
        ...formData,
        activeProjectsLimit: Math.max(1, Number(formData.activeProjectsLimit) || 0),
        pricePerProject: Number(formData.pricePerProject) || 0,
      };

      await api.put(`${SUPPORT_API_BASE}/companies/${company.id}`, payload);
      alert('Company updated successfully!');
      onSuccess();
    } catch (error) {
      console.error('Error updating company:', error);
      alert(error.response?.data?.error || 'Failed to update company');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold">Edit Company: {company.name}</h2>
          <p className="text-sm text-gray-600 mt-1">
            Active Projects: {company.activeProjects} / {company.activeProjectsLimit} | 
            Revenue: ₹{company.monthlyRevenue.toLocaleString()}/mo
          </p>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Company Name *
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="email"
                value={formData.companyEmail}
                onChange={(e) => setFormData({ ...formData, companyEmail: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Phone
              </label>
              <input
                type="tel"
                value={formData.companyPhone}
                onChange={(e) => setFormData({ ...formData, companyPhone: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Subscription Plan
            </label>
            <select
              value={formData.subscriptionPlan}
              onChange={(e) => setFormData({ ...formData, subscriptionPlan: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="trial">Trial</option>
              <option value="starter">Starter</option>
              <option value="basic">Basic</option>
              <option value="professional">Professional</option>
              <option value="enterprise">Enterprise</option>
            </select>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Project Limit *
              </label>
              <input
                type="number"
                min="1"
                required
                value={formData.activeProjectsLimit}
                onChange={(e) => {
                  const { value } = e.target;
                  setFormData((prev) => ({
                    ...prev,
                    activeProjectsLimit: value === '' ? '' : Number(value),
                  }));
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">
                Currently using: {company.activeProjects}
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Price Per Project (₹) *
              </label>
              <input
                type="number"
                min="0"
                step="500"
                required
                value={formData.pricePerProject}
                onChange={(e) => {
                  const { value } = e.target;
                  setFormData((prev) => ({
                    ...prev,
                    pricePerProject: value === '' ? '' : Number(value),
                  }));
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">
                New monthly: ₹{(company.activeProjects * (Number(formData.pricePerProject) || 0)).toLocaleString()}
              </p>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Billing Status *
            </label>
            <select
              value={formData.billingStatus}
              onChange={(e) => setFormData({ ...formData, billingStatus: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="active">Active</option>
              <option value="suspended">Suspended (Payment Overdue)</option>
              <option value="cancelled">Cancelled</option>
            </select>
            {formData.billingStatus === 'suspended' && (
              <p className="text-xs text-red-600 mt-1">
                ⚠️ Company will lose access to all features
              </p>
            )}
          </div>

          <div className="flex gap-3 pt-4">
            <Button type="submit" disabled={saving} className="flex-1">
              {saving ? 'Saving...' : 'Save Changes'}
            </Button>
            <Button type="button" variant="outline" onClick={onClose} className="flex-1">
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
