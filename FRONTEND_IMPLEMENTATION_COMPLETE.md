# ProSite Frontend - Complete Implementation Guide

**Status**: Ready for Implementation  
**Date**: November 17, 2025  
**Estimated Time**: 40-50 hours development  

---

## ✅ What's Already Complete

### Backend (100%)
- ✅ All 30+ API endpoints functional
- ✅ JWT authentication & authorization
- ✅ All 5 disabled modules now ENABLED:
  - `incident_investigation` - Incident reporting
  - `safety_audits` - ISO 45001 audits
  - `ppe_tracking` - PPE issuance
  - `geofence_api` - Location verification
  - `handover_register` - Work handovers
- ✅ Database compatibility layer added (`db.session` support)

### Frontend Structure (70%)
- ✅ Next.js 16 + React 19 setup
- ✅ Tailwind CSS 4 configured
- ✅ Dashboard layout with Sidebar/Header
- ✅ Login/Registration pages
- ✅ Password reset flow
- ✅ Basic dashboard page
- ✅ Folder structure for all modules

### What's Missing (30%)
- ⏳ Complete page implementations (placeholder pages exist)
- ⏳ Forms with validation
- ⏳ Data fetching & display
- ⏳ Hindi language support
- ⏳ UI Polish & consistency

---

## 📦 Step 1: Install Required Packages

```bash
cd frontend
npm install next-intl zod @hookform/resolvers react-hot-toast sonner
```

**Packages Added:**
- `next-intl` - i18n for Next.js App Router (Hindi support)
- `zod` - Form validation schemas
- `@hookform/resolvers` - Connect Zod with react-hook-form
- `react-hot-toast` or `sonner` - Toast notifications

---

## 🌐 Step 2: Setup Hindi Language Support

### 2.1 Create i18n Configuration

**File**: `frontend/i18n.js`
```javascript
import { getRequestConfig } from 'next-intl/server';

export default getRequestConfig(async ({ locale }) => ({
  messages: (await import(`./messages/${locale}.json`)).default
}));
```

### 2.2 Create Translation Files

**File**: `frontend/messages/en.json`
```json
{
  "nav": {
    "dashboard": "Dashboard",
    "batches": "Batches",
    "cubeTests": "Cube Tests",
    "vendors": "Vendors",
    "materials": "Materials",
    "safety": "Safety",
    "reports": "Reports",
    "settings": "Settings"
  },
  "dashboard": {
    "welcome": "Welcome back!",
    "overview": "Here's your quality management overview",
    "batches": "Batches",
    "cubeTests": "Cube Tests",
    "training": "Training Sessions",
    "materialTests": "Material Tests",
    "recentActivity": "Recent Activities"
  },
  "batches": {
    "title": "Batch Management",
    "newBatch": "New Batch",
    "batchNumber": "Batch Number",
    "vendor": "Vendor",
    "grade": "Grade",
    "quantity": "Quantity",
    "status": "Status",
    "actions": "Actions"
  },
  "forms": {
    "submit": "Submit",
    "cancel": "Cancel",
    "save": "Save",
    "delete": "Delete",
    "edit": "Edit",
    "loading": "Loading...",
    "required": "This field is required",
    "invalidEmail": "Invalid email address",
    "invalidPhone": "Invalid phone number"
  }
}
```

**File**: `frontend/messages/hi.json`
```json
{
  "nav": {
    "dashboard": "डैशबोर्ड",
    "batches": "बैच",
    "cubeTests": "क्यूब टेस्ट",
    "vendors": "विक्रेता",
    "materials": "सामग्री",
    "safety": "सुरक्षा",
    "reports": "रिपोर्ट",
    "settings": "सेटिंग्स"
  },
  "dashboard": {
    "welcome": "वापसी पर स्वागत है!",
    "overview": "यहाँ आपका गुणवत्ता प्रबंधन अवलोकन है",
    "batches": "बैच",
    "cubeTests": "क्यूब टेस्ट",
    "training": "प्रशिक्षण सत्र",
    "materialTests": "सामग्री परीक्षण",
    "recentActivity": "हाल की गतिविधियां"
  },
  "batches": {
    "title": "बैच प्रबंधन",
    "newBatch": "नया बैच",
    "batchNumber": "बैच नंबर",
    "vendor": "विक्रेता",
    "grade": "ग्रेड",
    "quantity": "मात्रा",
    "status": "स्थिति",
    "actions": "क्रियाएं"
  },
  "forms": {
    "submit": "जमा करें",
    "cancel": "रद्द करें",
    "save": "सहेजें",
    "delete": "हटाएं",
    "edit": "संपादित करें",
    "loading": "लोड हो रहा है...",
    "required": "यह फ़ील्ड आवश्यक है",
    "invalidEmail": "अमान्य ईमेल पता",
    "invalidPhone": "अमान्य फोन नंबर"
  }
}
```

### 2.3 Update Next.js Config

**File**: `frontend/next.config.js`
```javascript
const createNextIntlPlugin = require('next-intl/plugin');

const withNextIntl = createNextIntlPlugin();

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    appDir: true
  }
};

module.exports = withNextIntl(nextConfig);
```

### 2.4 Add Language Switcher to Header

**File**: `frontend/components/layout/Header.js` (Add this component)
```javascript
'use client';

import { useState } from 'react';
import { Globe } from 'lucide-react';
import { useRouter, usePathname } from 'next/navigation';

export function LanguageSwitcher() {
  const router = useRouter();
  const pathname = usePathname();
  const [locale, setLocale] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('locale') || 'en';
    }
    return 'en';
  });

  const switchLanguage = () => {
    const newLocale = locale === 'en' ? 'hi' : 'en';
    setLocale(newLocale);
    localStorage.setItem('locale', newLocale);
    
    // Reload the page to apply new translations
    window.location.reload();
  };

  return (
    <button
      onClick={switchLanguage}
      className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors"
    >
      <Globe className="w-5 h-5" />
      <span className="font-medium">{locale === 'en' ? 'हिंदी' : 'English'}</span>
    </button>
  );
}
```

---

## 📝 Step 3: Complete All Module Pages

### 3.1 Vendors Module

**File**: `frontend/app/dashboard/vendors/page.js`
```javascript
'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Plus, Edit, Trash2, Phone, Mail } from 'lucide-react';
import { apiRequest } from '@/lib/api-optimized';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import toast from 'react-hot-toast';

export default function VendorsPage() {
  const t = useTranslations('vendors');
  const [vendors, setVendors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    fetchVendors();
  }, []);

  const fetchVendors = async () => {
    try {
      const data = await apiRequest('/api/vendors');
      setVendors(data.vendors || []);
    } catch (error) {
      toast.error('Failed to load vendors');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{t('title')}</h1>
          <p className="text-gray-600 mt-1">{t('subtitle')}</p>
        </div>
        <Button onClick={() => setShowForm(true)}>
          <Plus className="w-5 h-5 mr-2" />
          {t('newVendor')}
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {vendors.map((vendor) => (
          <Card key={vendor.id} className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-semibold text-lg">{vendor.company_name}</h3>
                <p className="text-sm text-gray-600">{vendor.rmc_plant_name}</p>
              </div>
              <div className="flex gap-2">
                <button className="text-blue-600 hover:text-blue-700">
                  <Edit className="w-4 h-4" />
                </button>
                <button className="text-red-600 hover:text-red-700">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="mt-4 space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <Phone className="w-4 h-4 text-gray-400" />
                <span>{vendor.contact_phone}</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Mail className="w-4 h-4 text-gray-400" />
                <span>{vendor.contact_email}</span>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                vendor.status === 'active' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {vendor.status}
              </span>
            </div>
          </Card>
        ))}
      </div>

      {/* Add VendorForm modal here */}
    </div>
  );
}
```

### 3.2 Batches Module

**File**: `frontend/app/dashboard/batches/page.js`
```javascript
'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Plus, Eye, Edit, FileText } from 'lucide-react';
import { apiRequest } from '@/lib/api-optimized';
import { format } from 'date-fns';
import toast from 'react-hot-toast';

export default function BatchesPage() {
  const t = useTranslations('batches');
  const [batches, setBatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchBatches();
  }, []);

  const fetchBatches = async () => {
    try {
      const projectId = localStorage.getItem('activeProjectId');
      const data = await apiRequest(`/api/batches?project_id=${projectId}`);
      setBatches(data.batches || []);
    } catch (error) {
      toast.error('Failed to load batches');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'draft': 'bg-gray-100 text-gray-800',
      'pending': 'bg-yellow-100 text-yellow-800',
      'approved': 'bg-green-100 text-green-800',
      'rejected': 'bg-red-100 text-red-800'
    };
    return colors[status] || colors.draft;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{t('title')}</h1>
          <p className="text-gray-600 mt-1">{t('subtitle')}</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          <Plus className="w-5 h-5" />
          {t('newBatch')}
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-2">
        {['all', 'pending', 'approved', 'rejected'].map((status) => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === status
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {t(`filter.${status}`)}
          </button>
        ))}
      </div>

      {/* Batches Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {t('batchNumber')}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {t('vendor')}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {t('grade')}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {t('quantity')}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {t('date')}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {t('status')}
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                {t('actions')}
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {batches
              .filter(batch => filter === 'all' || batch.status === filter)
              .map((batch) => (
                <tr key={batch.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {batch.batch_number}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {batch.vendor_company_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {batch.concrete_grade}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {batch.quantity_cubic_meters} m³
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {format(new Date(batch.delivery_date), 'dd MMM yyyy')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(batch.status)}`}>
                      {t(`status.${batch.status}`)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end gap-2">
                      <button className="text-blue-600 hover:text-blue-900">
                        <Eye className="w-4 h-4" />
                      </button>
                      <button className="text-gray-600 hover:text-gray-900">
                        <Edit className="w-4 h-4" />
                      </button>
                      <button className="text-green-600 hover:text-green-900">
                        <FileText className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

### 3.3 Cube Tests Module

**File**: `frontend/app/dashboard/cube-tests/page.js`
```javascript
'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Plus, FlaskConical, CheckCircle, XCircle } from 'lucide-react';
import { apiRequest } from '@/lib/api-optimized';
import { format } from 'date-fns';
import toast from 'react-hot-toast';

export default function CubeTestsPage() {
  const t = useTranslations('cubeTests');
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchTests();
  }, []);

  const fetchTests = async () => {
    try {
      const projectId = localStorage.getItem('activeProjectId');
      const data = await apiRequest(`/api/cube-tests?project_id=${projectId}`);
      setTests(data.cube_tests || []);
    } catch (error) {
      toast.error('Failed to load cube tests');
    } finally {
      setLoading(false);
    }
  };

  const getResultBadge = (result) => {
    if (!result) return null;
    
    return result === 'pass' ? (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
        <CheckCircle className="w-3 h-3" />
        {t('pass')}
      </span>
    ) : (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
        <XCircle className="w-3 h-3" />
        {t('fail')}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{t('title')}</h1>
          <p className="text-gray-600 mt-1">{t('subtitle')}</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
          <Plus className="w-5 h-5" />
          {t('newTest')}
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t('totalTests')}</p>
              <p className="text-3xl font-bold mt-1">{tests.length}</p>
            </div>
            <FlaskConical className="w-10 h-10 text-blue-600" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t('passed')}</p>
              <p className="text-3xl font-bold text-green-600 mt-1">
                {tests.filter(t => t.test_result === 'pass').length}
              </p>
            </div>
            <CheckCircle className="w-10 h-10 text-green-600" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t('failed')}</p>
              <p className="text-3xl font-bold text-red-600 mt-1">
                {tests.filter(t => t.test_result === 'fail').length}
              </p>
            </div>
            <XCircle className="w-10 h-10 text-red-600" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t('passRate')}</p>
              <p className="text-3xl font-bold text-blue-600 mt-1">
                {tests.length > 0 
                  ? Math.round((tests.filter(t => t.test_result === 'pass').length / tests.length) * 100)
                  : 0}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Tests Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {t('testNumber')}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {t('batchNumber')}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {t('grade')}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {t('testAge')}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {t('avgStrength')}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {t('required')}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {t('result')}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {t('date')}
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {tests.map((test) => (
              <tr key={test.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {test.test_number || `CT-${test.id}`}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {test.batch_number}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {test.concrete_grade}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {test.test_age_days} {t('days')}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {test.average_strength?.toFixed(2)} MPa
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {test.required_strength} MPa
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getResultBadge(test.test_result)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {test.test_date ? format(new Date(test.test_date), 'dd MMM yyyy') : '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

---

## 🎨 Step 4: UI/UX Polish

### 4.1 Consistent Color Scheme

**File**: `frontend/tailwind.config.js` (Update colors)
```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        success: {
          50: '#f0fdf4',
          100: '#dcfce7',
          500: '#22c55e',
          600: '#16a34a',
        },
        danger: {
          50: '#fef2f2',
          100: '#fee2e2',
          500: '#ef4444',
          600: '#dc2626',
        },
        warning: {
          50: '#fffbeb',
          100: '#fef3c7',
          500: '#f59e0b',
          600: '#d97706',
        }
      }
    }
  }
}
```

### 4.2 Loading States Component

**File**: `frontend/components/ui/Loading.js`
```javascript
export function LoadingSpinner({ size = 'md' }) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12'
  };

  return (
    <div className="flex items-center justify-center">
      <div className={`animate-spin rounded-full border-b-2 border-blue-600 ${sizeClasses[size]}`}></div>
    </div>
  );
}

export function PageLoading() {
  return (
    <div className="flex items-center justify-center h-screen">
      <div className="text-center">
        <LoadingSpinner size="lg" />
        <p className="mt-4 text-gray-600">Loading...</p>
      </div>
    </div>
  );
}
```

### 4.3 Empty State Component

**File**: `frontend/components/ui/EmptyState.js`
```javascript
import { InboxIcon } from 'lucide-react';

export function EmptyState({ 
  icon: Icon = InboxIcon,
  title = "No data found",
  description = "Get started by creating a new item",
  action,
  actionLabel = "Create New"
}) {
  return (
    <div className="text-center py-12">
      <Icon className="mx-auto h-12 w-12 text-gray-400" />
      <h3 className="mt-2 text-sm font-medium text-gray-900">{title}</h3>
      <p className="mt-1 text-sm text-gray-500">{description}</p>
      {action && (
        <div className="mt-6">
          <button
            onClick={action}
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            {actionLabel}
          </button>
        </div>
      )}
    </div>
  );
}
```

### 4.4 Toast Notifications

**File**: `frontend/app/layout.js` (Add Toaster)
```javascript
import { Toaster } from 'react-hot-toast';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        {children}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
              iconTheme: {
                primary: '#22c55e',
                secondary: '#fff',
              },
            },
            error: {
              duration: 4000,
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fff',
              },
            },
          }}
        />
      </body>
    </html>
  );
}
```

---

## ✅ Step 5: Testing Checklist

### Before Deployment

- [ ] All pages load without errors
- [ ] Hindi translations work correctly
- [ ] Language switcher toggles properly
- [ ] Forms validate correctly
- [ ] API calls handle errors gracefully
- [ ] Loading states show during API calls
- [ ] Toast notifications appear on success/error
- [ ] Mobile responsive on all pages
- [ ] Images/photos upload successfully
- [ ] Tables paginate properly
- [ ] Filters work on list pages
- [ ] Search functionality works
- [ ] Date pickers show correct format (DD/MM/YYYY for India)
- [ ] Currency shows ₹ symbol
- [ ] Phone numbers validate +91 format

---

## 📊 Implementation Timeline

### Week 1 (40 hours)
- **Day 1-2** (16hrs): Setup i18n, create all translation files
- **Day 3-4** (16hrs): Complete Concrete QMS pages (Vendors, Batches, Cube Tests)
- **Day 5** (8hrs): Complete Material Testing pages

### Week 2 (30 hours)
- **Day 6-7** (16hrs): Complete Safety Management pages
- **Day 8** (8hrs): Complete Supporting Modules pages
- **Day 9** (6hrs): UI Polish & consistency

### Week 3 (10 hours)
- **Day 10** (6hrs): End-to-end testing
- **Day 11** (4hrs): Bug fixes & final touches

**Total**: ~80 hours (10 working days)

---

## 🚀 Quick Start Commands

```bash
# 1. Install dependencies
cd frontend
npm install next-intl zod @hookform/resolvers react-hot-toast

# 2. Create translation files
mkdir messages
# Create en.json and hi.json as shown above

# 3. Start development
npm run dev

# 4. Build for production
npm run build
npm start
```

---

## 📝 Notes

1. **All backend APIs are ready** - Just call them from frontend
2. **Authentication is working** - JWT tokens stored in localStorage
3. **File uploads** - Use FormData for multipart uploads
4. **Date formatting** - Use `date-fns` with `dd/MM/yyyy` format
5. **Number formatting** - Use Indian numbering system (lakhs/crores)

---

## 🎯 Priority Order

If time is limited, implement in this order:

1. **High Priority** (Critical for MVP):
   - ✅ Vendors page
   - ✅ Batches page
   - ✅ Cube Tests page
   - ✅ Hindi language
   - ✅ Dashboard with real data

2. **Medium Priority** (Important but can wait):
   - Material Testing pages
   - Safety pages
   - Reports page

3. **Low Priority** (Nice to have):
   - Advanced filters
   - Charts/graphs
   - Export to PDF
   - Email notifications UI

---

**Ready to implement! Follow steps 1-5 in order. All backend APIs are functional and tested.**
