'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { Building2, Users, Plus, Search, Settings, Eye, AlertCircle, CheckCircle2, XCircle, Clock } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { Modal } from '@/components/ui/Modal';

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
      <div className="flex items-center justify-center min-h-screen bg-muted/30">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Loading support dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-muted/30 p-6 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Support Admin Dashboard</h1>
          <p className="text-muted-foreground mt-1">Manage companies and system access</p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Create Company
        </Button>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <StatCard
          icon={<Building2 className="w-6 h-6 text-blue-600" />}
          title="Total Companies"
          value={overview?.totalCompanies || 0}
          subtitle={`${overview?.activeCompanies || 0} active`}
          className="bg-blue-50 dark:bg-blue-900/20 border-blue-100 dark:border-blue-800"
        />
        <StatCard
          icon={<Users className="w-6 h-6 text-green-600" />}
          title="Active Projects"
          value={overview?.activeProjects || 0}
          subtitle={`of ${overview?.totalProjects || 0} total`}
          className="bg-green-50 dark:bg-green-900/20 border-green-100 dark:border-green-800"
        />
        <StatCard
          icon={<AlertCircle className="w-6 h-6 text-orange-600" />}
          title="Suspended Companies"
          value={overview?.suspendedCompanies || 0}
          subtitle="Requires attention"
          className="bg-orange-50 dark:bg-orange-900/20 border-orange-100 dark:border-orange-800"
        />
      </div>

      {/* Companies List */}
      <Card>
        <CardHeader className="border-b">
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
            <CardTitle>All Companies</CardTitle>
            <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
              <div className="relative w-full sm:w-64">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="Search companies..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-4 py-2 border border-input rounded-md bg-background focus:ring-2 focus:ring-ring focus:border-transparent"
              >
                <option value="">All Status</option>
                <option value="active">Active</option>
                <option value="suspended">Suspended</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
          </div>
        </CardHeader>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-muted/50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Company</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Projects</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-card divide-y divide-border">
              {companies.length === 0 ? (
                <tr>
                  <td colSpan="4" className="px-6 py-12 text-center text-muted-foreground">
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
                    onView={(comp) => router.push(`/support/companies/${comp.id}`)}
                  />
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

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

function StatCard({ icon, title, value, subtitle, className }) {
  return (
    <div className={`rounded-lg shadow-sm p-6 border ${className}`}>
      <div className="flex items-center gap-4">
        <div className="p-3 rounded-lg bg-white/50 dark:bg-black/20">
          {icon}
        </div>
        <div className="flex-1">
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <p className="text-2xl font-bold text-foreground mt-1">{value}</p>
          <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
        </div>
      </div>
    </div>
  );
}

function CompanyRow({ company, onEdit, onView }) {
  const getStatusBadge = (status) => {
    const variants = {
      active: { variant: 'success', icon: CheckCircle2, label: 'Active' },
      suspended: { variant: 'destructive', icon: XCircle, label: 'Suspended' },
      cancelled: { variant: 'secondary', icon: XCircle, label: 'Cancelled' },
      trial: { variant: 'info', icon: Clock, label: 'Trial' }
    };
    const config = variants[status] || variants.active;
    const Icon = config.icon;

    return (
      <Badge variant={config.variant} className="flex items-center gap-1 w-fit">
        <Icon className="w-3 h-3" />
        {config.label}
      </Badge>
    );
  };

  return (
    <tr className="hover:bg-muted/50 transition-colors">
      <td className="px-6 py-4">
        <div>
          <p className="font-semibold text-foreground">{company.name}</p>
          {company.companyEmail && (
            <p className="text-sm text-muted-foreground">{company.companyEmail}</p>
          )}
        </div>
      </td>
      <td className="px-6 py-4">
        <div className="text-sm">
          <span className="font-semibold text-foreground">{company.activeProjects}</span>
          <span className="text-muted-foreground"> / {company.activeProjectsLimit}</span>
          <p className="text-xs text-muted-foreground mt-1">
            ({company.totalProjects} total)
          </p>
        </div>
      </td>
      <td className="px-6 py-4">
        {getStatusBadge(company.billingStatus)}
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
            onClick={() => onView(company)}
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
    activeProjectsLimit: 1,
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
        // Default values for removed fields to satisfy backend if needed
        subscriptionPlan: 'enterprise',
        pricePerProject: 0
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
    <Modal isOpen={true} onClose={onClose} title="Create New Company">
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Company Name *"
          required
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          placeholder="ABC Construction Pvt Ltd"
        />

        <div className="grid md:grid-cols-2 gap-4">
          <Input
            label="Email"
            type="email"
            value={formData.companyEmail}
            onChange={(e) => setFormData({ ...formData, companyEmail: e.target.value })}
            placeholder="contact@company.com"
          />
          <Input
            label="Phone"
            type="tel"
            value={formData.companyPhone}
            onChange={(e) => setFormData({ ...formData, companyPhone: e.target.value })}
            placeholder="+91 9876543210"
          />
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <Input
            label="Project Limit *"
            type="number"
            min="1"
            required
            value={formData.activeProjectsLimit}
            onChange={(e) => setFormData({ ...formData, activeProjectsLimit: e.target.value })}
          />

          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Status *
            </label>
            <select
              value={formData.billingStatus}
              onChange={(e) => setFormData({ ...formData, billingStatus: e.target.value })}
              className="w-full px-3 py-2 border border-input rounded-md bg-background focus:ring-2 focus:ring-ring focus:border-transparent"
            >
              <option value="active">Active</option>
              <option value="suspended">Suspended</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
        </div>

        <Input
          label="Address"
          value={formData.companyAddress}
          onChange={(e) => setFormData({ ...formData, companyAddress: e.target.value })}
          placeholder="Registered Office Address"
        />

        <Input
          label="GSTIN"
          value={formData.gstin}
          onChange={(e) => setFormData({ ...formData, gstin: e.target.value })}
          placeholder="GSTIN Number"
        />

        <div className="flex gap-3 pt-4 justify-end">
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={saving}>
            {saving ? 'Creating...' : 'Create Company'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

function EditCompanyModal({ company, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    name: company.name,
    activeProjectsLimit: company.activeProjectsLimit,
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
        // Preserve existing values or default
        subscriptionPlan: company.subscriptionPlan || 'enterprise',
        pricePerProject: company.pricePerProject || 0
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
    <Modal isOpen={true} onClose={onClose} title={`Edit Company: ${company.name}`}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Company Name *"
          required
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        />

        <div className="grid md:grid-cols-2 gap-4">
          <Input
            label="Email"
            type="email"
            value={formData.companyEmail}
            onChange={(e) => setFormData({ ...formData, companyEmail: e.target.value })}
          />
          <Input
            label="Phone"
            type="tel"
            value={formData.companyPhone}
            onChange={(e) => setFormData({ ...formData, companyPhone: e.target.value })}
          />
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <Input
              label="Project Limit *"
              type="number"
              min="1"
              required
              value={formData.activeProjectsLimit}
              onChange={(e) => setFormData({ ...formData, activeProjectsLimit: e.target.value })}
            />
            <p className="text-xs text-muted-foreground mt-1">
              Currently using: {company.activeProjects}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Status *
            </label>
            <select
              value={formData.billingStatus}
              onChange={(e) => setFormData({ ...formData, billingStatus: e.target.value })}
              className="w-full px-3 py-2 border border-input rounded-md bg-background focus:ring-2 focus:ring-ring focus:border-transparent"
            >
              <option value="active">Active</option>
              <option value="suspended">Suspended</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
        </div>

        <Input
          label="Address"
          value={formData.companyAddress}
          onChange={(e) => setFormData({ ...formData, companyAddress: e.target.value })}
        />

        <Input
          label="GSTIN"
          value={formData.gstin}
          onChange={(e) => setFormData({ ...formData, gstin: e.target.value })}
        />

        <div className="flex gap-3 pt-4 justify-end">
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={saving}>
            {saving ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
