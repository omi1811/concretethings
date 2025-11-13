'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Alert } from '@/components/ui/Alert';
import { authAPI } from '@/lib/api';
import { saveUserData } from '@/lib/db';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  
  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      console.log('Attempting login with:', email);
      const result = await authAPI.login(email, password);
      console.log('Login result:', result);
      
      if (result.success) {
        // Save token
        localStorage.setItem('auth_token', result.data.access_token);
        
        // Save user data to IndexedDB
        await saveUserData('current_user', result.data.user);
        
        console.log('Login successful, redirecting to dashboard...');
        // Redirect to dashboard
        router.push('/dashboard');
      } else {
        const errorMsg = result.error || result.message || 'Login failed';
        console.error('Login failed:', errorMsg);
        setError(errorMsg);
      }
    } catch (err) {
      console.error('Login exception:', err);
      setError(err.message || 'An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  }
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-gray-100 px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-2xl mb-4">
            <span className="text-white font-bold text-2xl">PS</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">ProSite</h1>
          <p className="text-gray-600 mt-2">Professional Site Management Platform</p>
        </div>
        
        {/* Login form */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Sign In</h2>
          
          {error && (
            <Alert variant="danger" className="mb-4" onClose={() => setError('')}>
              {error}
            </Alert>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              type="email"
              label="Email"
              placeholder="your@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            
            <Input
              type="password"
              label="Password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            
            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center gap-2">
                <input type="checkbox" className="rounded" />
                <span className="text-gray-600">Remember me</span>
              </label>
              <Link href="/forgot-password" className="text-blue-600 hover:text-blue-700">
                Forgot password?
              </Link>
            </div>
            
            <Button
              type="submit"
              className="w-full"
              disabled={loading}
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </Button>
          </form>
          
          <div className="mt-6 text-center text-sm text-gray-600">
            Don't have an account?{' '}
            <Link href="/signup" className="text-blue-600 hover:text-blue-700 font-medium">
              Sign up
            </Link>
          </div>
          
          {/* Demo credentials */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-xs text-gray-500 text-center mb-2">Demo Credentials:</p>
            <p className="text-xs text-gray-600 text-center">
              Email: <span className="font-mono">admin@demo.com</span><br />
              Password: <span className="font-mono">adminpass</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
