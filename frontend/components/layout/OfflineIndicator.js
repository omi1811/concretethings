'use client';

import { useState, useEffect } from 'react';
import { Badge } from '../ui/Badge';
import { Wifi, WifiOff } from 'lucide-react';

export function OfflineIndicator() {
  const [isOnline, setIsOnline] = useState(true);
  
  useEffect(() => {
    setIsOnline(navigator.onLine);
    
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);
  
  if (isOnline) {
    return (
      <Badge variant="synced" className="flex items-center gap-1">
        <Wifi className="w-3 h-3" />
        Online
      </Badge>
    );
  }
  
  return (
    <Badge variant="offline" className="flex items-center gap-1 animate-pulse">
      <WifiOff className="w-3 h-3" />
      Offline Mode
    </Badge>
  );
}
