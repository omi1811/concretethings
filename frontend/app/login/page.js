'use client';

import { useState, useCallback, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authAPI } from '@/lib/api-optimized';
import { saveUserData } from '@/lib/db';

// Reusable Input Component
const FormInput = ({ label, error, ...props }) => (
  <div className="space-y-1">
    <label className="block text-sm font-medium text-gray-700">{label}</label>
    <input
      className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 transition-all ${
        error 
          ? 'border-red-300 focus:ring-red-500' 
          : 'border-gray-300 focus:ring-blue-500'
      }`}
      {...props}
    />
    {error && <p className="text-xs text-red-600">{error}</p>}
  </div>
);

// Reusable Button Component
const Button = ({ loading, children, ...props }) => (
  <button
    className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform active:scale-[0.98]"
    disabled={loading}
    {...props}
  >
    {loading ? (
      <span className="flex items-center justify-center gap-2">
        <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
        <span>Signing in...</span>
      </span>
    ) : children}
  </button>
);

// Alert Component
const Alert = ({ type = 'error', children, onClose }) => {
  const styles = {
    error: 'bg-red-50 border-red-200 text-red-800',
    success: 'bg-green-50 border-green-200 text-green-800',
  };
  
  return (
    <div className={`p-4 border rounded-lg flex items-start gap-3 ${styles[type]}`}>
      <span className="flex-1">{children}</span>
      {onClose && (
        <button onClick={onClose} className="text-current opacity-70 hover:opacity-100">×</button>
      )}
    </div>
  );
};

export default function LoginPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [errors, setErrors] = useState({});
  const [alert, setAlert] = useState(null);
  const [loading, setLoading] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);

  const validateForm = useCallback(() => {
    const newErrors = {};
    if (!formData.email.trim()) newErrors.email = 'Email is required';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) newErrors.email = 'Invalid email format';
    if (!formData.password) newErrors.password = 'Password is required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [formData]);

  const handleChange = useCallback((e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors(prev => ({ ...prev, [name]: '' }));
  }, [errors]);

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    setAlert(null);
    if (!validateForm()) return;
    setLoading(true);
    
    try {
      const credentials = {
        email: formData.email.trim().toLowerCase(),
        password: formData.password,
      };

      const response = await authAPI.login(credentials);

      if (!response?.access_token) {
        throw new Error(response?.error || 'Invalid credentials');
      }

      // Preserve legacy token key usage alongside the shared API helper storage.
      localStorage.setItem('auth_token', response.access_token);
      if (rememberMe) localStorage.setItem('remember_email', formData.email);
      else localStorage.removeItem('remember_email');

      if (response.user) {
        await saveUserData(response);
      }

      setAlert({ type: 'success', message: 'Login successful! Redirecting...' });
      setTimeout(() => router.push('/'), 500);
    } catch (err) {
      setAlert({ type: 'error', message: err.message || 'Login failed' });
    } finally {
      setLoading(false);
    }
  }, [formData, rememberMe, validateForm, router]);

  const demoCredentials = useMemo(() => [
    { label: 'System Admin', email: 'admin@prosite.com', password: 'Admin@2025' },
    { label: 'Project Manager', email: 'pm@prosite.com', password: 'PM@2025' },
    { label: 'Quality Manager', email: 'qm@prosite.com', password: 'QM@2025' },
  ], []);

  const fillDemo = useCallback((email, password) => {
    setFormData({ email, password });
    setErrors({});
  }, []);
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-gray-100 px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-600 to-blue-700 rounded-2xl mb-4 shadow-lg">
            <span className="text-white font-bold text-2xl">PS</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">ProSite</h1>
          <p className="text-gray-600 mt-2">Professional Site Management Platform</p>
        </div>
        
        {/* Login form */}
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Sign In</h2>
          
          {alert && (
            <Alert type={alert.type} onClose={() => setAlert(null)}>
              {alert.message}
            </Alert>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-5 mt-6">
            <FormInput
              type="email"
              name="email"
              label="Email Address"
              placeholder="your@email.com"
              value={formData.email}
              onChange={handleChange}
              error={errors.email}
              autoComplete="email"
            />
            
            <FormInput
              type="password"
              name="password"
              label="Password"
              placeholder="••••••••"
              value={formData.password}
              onChange={handleChange}
              error={errors.password}
              autoComplete="current-password"
            />
            
            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center gap-2 cursor-pointer">
                <input 
                  type="checkbox" 
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-gray-600">Remember me</span>
              </label>
              <Link href="/forgot-password" className="text-blue-600 hover:text-blue-700 font-medium">
                Forgot password?
              </Link>
            </div>
            
            <Button type="submit" loading={loading}>
              Sign In
            </Button>
          </form>
          
          {/* Demo credentials quick-fill */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-xs font-medium text-gray-500 text-center mb-3">Demo Accounts (Click to Fill)</p>
            <div className="grid grid-cols-3 gap-2">
              {demoCredentials.map((demo, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => fillDemo(demo.email, demo.password)}
                  className="px-2 py-2 text-xs bg-gray-50 hover:bg-blue-50 border border-gray-200 hover:border-blue-300 rounded-lg transition-colors text-gray-700 hover:text-blue-600 font-medium"
                >
                  {demo.label}
                </button>
              ))}
            </div>
            <p className="text-xs text-gray-500 text-center mt-3">
              Local seed users are created via <code>init_database.py</code>. Use these pre-filled accounts or create your own from the admin panel.
            </p>
          </div>
          
          <div className="mt-6 text-center text-sm text-gray-600">
            Don't have an account?{' '}
            <Link href="/signup" className="text-blue-600 hover:text-blue-700 font-medium">
              Sign up
            </Link>
          </div>
        </div>
        
        {/* Footer */}
        <p className="text-center text-xs text-gray-500 mt-6">
          ISO 9001:2015 Compliant Quality Management System
        </p>
      </div>
    </div>
  );
}
