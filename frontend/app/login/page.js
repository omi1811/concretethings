'use client';

import { useState, useCallback, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authAPI } from '@/lib/api-optimized';
import { saveUserData } from '@/lib/db';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Alert } from '@/components/ui/Alert';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/Card';

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
      setAlert({ type: 'danger', message: err.message || 'Login failed' });
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
    <div className="min-h-screen flex items-center justify-center bg-muted/30 px-4 py-12">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary rounded-xl shadow-lg shadow-primary/20 mb-4">
            <span className="text-primary-foreground font-bold text-2xl">PS</span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">ProSite</h1>
          <p className="text-muted-foreground">Professional Site Management Platform</p>
        </div>

        <Card className="border-border shadow-xl">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl text-center">Sign in</CardTitle>
            <CardDescription className="text-center">
              Enter your email and password to access your account
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {alert && (
              <Alert variant={alert.type} onClose={() => setAlert(null)}>
                {alert.message}
              </Alert>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                type="email"
                name="email"
                label="Email"
                placeholder="name@example.com"
                value={formData.email}
                onChange={handleChange}
                error={errors.email}
                autoComplete="email"
                required
              />

              <Input
                type="password"
                name="password"
                label="Password"
                placeholder="••••••••"
                value={formData.password}
                onChange={handleChange}
                error={errors.password}
                autoComplete="current-password"
                required
              />

              <div className="flex items-center justify-between text-sm">
                <label className="flex items-center gap-2 cursor-pointer text-muted-foreground hover:text-foreground transition-colors">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="h-4 w-4 rounded border-input text-primary focus:ring-primary"
                  />
                  Remember me
                </label>
                <Link href="/forgot-password" className="font-medium text-primary hover:underline underline-offset-4">
                  Forgot password?
                </Link>
              </div>

              <Button type="submit" isLoading={loading} className="w-full">
                Sign In
              </Button>
            </form>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-border" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-card px-2 text-muted-foreground">Or continue with demo</span>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2">
              {demoCredentials.map((demo, idx) => (
                <Button
                  key={idx}
                  variant="outline"
                  size="sm"
                  type="button"
                  onClick={() => fillDemo(demo.email, demo.password)}
                  className="text-xs h-auto py-2 px-1"
                >
                  {demo.label}
                </Button>
              ))}
            </div>
          </CardContent>
          <CardFooter className="flex flex-col space-y-2 text-center text-sm text-muted-foreground">
            <div>
              Don&apos;t have an account?{' '}
              <Link href="/signup" className="font-medium text-primary hover:underline underline-offset-4">
                Sign up
              </Link>
            </div>
          </CardFooter>
        </Card>

        <p className="text-center text-xs text-muted-foreground">
          ISO 9001:2015 Compliant Quality Management System
        </p>
      </div>
    </div>
  );
}
