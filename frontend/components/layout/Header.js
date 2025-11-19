'use client';

import { useState, useEffect } from 'react';
import { Menu, Bell, User, ChevronDown, LogOut, Languages } from 'lucide-react';
import { OfflineIndicator } from './OfflineIndicator';
import { SyncStatus } from './SyncStatus';
import { Button } from '../ui/Button';
import { getUserData, clearUserData } from '@/lib/db';
import { clearTokens } from '@/lib/api-optimized';
import { useRouter, usePathname } from 'next/navigation';

export function Header({ onMenuClick }) {
  const [user, setUser] = useState(null);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showLangMenu, setShowLangMenu] = useState(false);
  const [currentLang, setCurrentLang] = useState('en');
  const router = useRouter();
  const pathname = usePathname();
  
  useEffect(() => {
    loadUserData();
    // Load saved language preference
    const savedLang = localStorage.getItem('language') || 'en';
    setCurrentLang(savedLang);
  }, []);
  
  async function loadUserData() {
    try {
      const userData = await getUserData();
      setUser(userData);
    } catch (error) {
      console.error('Error loading user data:', error);
    }
  }
  
  async function handleLogout() {
    clearTokens();
    await clearUserData();
    router.push('/login');
  }
  
  function handleLanguageChange(lang) {
    setCurrentLang(lang);
    localStorage.setItem('language', lang);
    setShowLangMenu(false);
    
    // Reload page to apply language change
    // In production, you would use next-intl's locale switching
    window.location.reload();
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
        
        {/* Language Switcher */}
        <div className="relative">
          <button
            onClick={() => setShowLangMenu(!showLangMenu)}
            className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition text-gray-600 hover:text-gray-900"
          >
            <Languages className="w-5 h-5" />
            <span className="hidden md:inline text-sm font-medium">
              {currentLang === 'en' ? 'English' : 'हिन्दी'}
            </span>
          </button>
          
          {showLangMenu && (
            <>
              <div 
                className="fixed inset-0 z-40"
                onClick={() => setShowLangMenu(false)}
              />
              <div className="absolute right-0 mt-2 w-40 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                <button
                  onClick={() => handleLanguageChange('en')}
                  className={`w-full flex items-center gap-2 px-4 py-2 text-sm hover:bg-gray-100 ${
                    currentLang === 'en' ? 'bg-blue-50 text-blue-600' : 'text-gray-700'
                  }`}
                >
                  🇬🇧 English
                </button>
                <button
                  onClick={() => handleLanguageChange('hi')}
                  className={`w-full flex items-center gap-2 px-4 py-2 text-sm hover:bg-gray-100 ${
                    currentLang === 'hi' ? 'bg-blue-50 text-blue-600' : 'text-gray-700'
                  }`}
                >
                  🇮🇳 हिन्दी
                </button>
              </div>
            </>
          )}
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
