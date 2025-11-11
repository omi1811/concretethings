'use client';

import { useState, useEffect } from 'react';
import { Menu, Bell, User, ChevronDown, LogOut } from 'lucide-react';
import { OfflineIndicator } from './OfflineIndicator';
import { SyncStatus } from './SyncStatus';
import { Button } from '../ui/Button';
import { getUserData } from '@/lib/db';
import { useRouter } from 'next/navigation';

export function Header({ onMenuClick }) {
  const [user, setUser] = useState(null);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const router = useRouter();
  
  useEffect(() => {
    loadUserData();
  }, []);
  
  async function loadUserData() {
    try {
      const userData = await getUserData('current_user');
      setUser(userData);
    } catch (error) {
      console.error('Error loading user data:', error);
    }
  }
  
  function handleLogout() {
    localStorage.removeItem('auth_token');
    router.push('/login');
  }
  
  return (
    <header className="sticky top-0 z-30 bg-white border-b border-gray-200 px-4 lg:px-6 h-16 flex items-center justify-between">
      {/* Left side */}
      <div className="flex items-center gap-4">
        <button
          onClick={onMenuClick}
          className="lg:hidden text-gray-600 hover:text-gray-900"
        >
          <Menu className="w-6 h-6" />
        </button>
        
        <div className="hidden lg:flex items-center gap-3">
          <OfflineIndicator />
          <SyncStatus />
        </div>
      </div>
      
      {/* Right side */}
      <div className="flex items-center gap-3">
        {/* Mobile status indicators */}
        <div className="lg:hidden flex items-center gap-2">
          <OfflineIndicator />
        </div>
        
        {/* Notifications */}
        <button className="relative text-gray-600 hover:text-gray-900">
          <Bell className="w-6 h-6" />
          <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full" />
        </button>
        
        {/* User menu */}
        <div className="relative">
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition"
          >
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-white" />
            </div>
            <div className="hidden md:block text-left">
              <p className="text-sm font-medium text-gray-900">
                {user?.full_name || 'User'}
              </p>
              <p className="text-xs text-gray-500">{user?.role || 'Engineer'}</p>
            </div>
            <ChevronDown className="w-4 h-4 text-gray-500" />
          </button>
          
          {/* Dropdown */}
          {showUserMenu && (
            <>
              <div 
                className="fixed inset-0 z-40"
                onClick={() => setShowUserMenu(false)}
              />
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  <LogOut className="w-4 h-4" />
                  Logout
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
