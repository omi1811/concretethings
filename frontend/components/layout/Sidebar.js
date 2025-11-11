'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { 
  LayoutDashboard, 
  Package, 
  FlaskConical, 
  GraduationCap, 
  TestTube2,
  Building2,
  FileCheck,
  FileText,
  Settings,
  X
} from 'lucide-react';

const menuItems = [
  {
    title: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard
  },
  {
    title: 'Batch Register',
    href: '/dashboard/batches',
    icon: Package
  },
  {
    title: 'Cube Tests',
    href: '/dashboard/cube-tests',
    icon: FlaskConical
  },
  {
    title: 'Training Register',
    href: '/dashboard/training',
    icon: GraduationCap
  },
  {
    title: 'Material Tests',
    href: '/dashboard/materials',
    icon: TestTube2
  },
  {
    title: 'Third-Party Labs',
    href: '/dashboard/labs',
    icon: Building2
  },
  {
    title: 'Handover Register',
    href: '/dashboard/handovers',
    icon: FileCheck
  },
  {
    title: 'Reports',
    href: '/dashboard/reports',
    icon: FileText
  },
  {
    title: 'Settings',
    href: '/dashboard/settings',
    icon: Settings
  }
];

export function Sidebar({ isOpen, onClose }) {
  const pathname = usePathname();
  
  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}
      
      {/* Sidebar */}
      <aside 
        className={cn(
          'fixed top-0 left-0 z-50 h-full w-64 bg-white border-r border-gray-200 transition-transform duration-300 lg:translate-x-0',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Logo */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">CQ</span>
            </div>
            <span className="font-bold text-gray-900">ConcreteQMS</span>
          </Link>
          <button 
            onClick={onClose}
            className="lg:hidden text-gray-500 hover:text-gray-700"
          >
            <X className="w-6 h-6" />
          </button>
        </div>
        
        {/* Navigation */}
        <nav className="px-3 py-4 space-y-1 overflow-y-auto h-[calc(100vh-73px)]">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
            
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                  isActive 
                    ? 'bg-blue-50 text-blue-700' 
                    : 'text-gray-700 hover:bg-gray-100'
                )}
                onClick={() => {
                  if (window.innerWidth < 1024) {
                    onClose();
                  }
                }}
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                <span>{item.title}</span>
              </Link>
            );
          })}
        </nav>
      </aside>
    </>
  );
}
