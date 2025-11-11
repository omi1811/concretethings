'use client';

import { useState, useEffect } from 'react';
import { getSyncQueue } from '@/lib/db';
import syncManager from '@/lib/sync';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { RefreshCw, CheckCircle } from 'lucide-react';

export function SyncStatus() {
  const [pendingCount, setPendingCount] = useState(0);
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncProgress, setSyncProgress] = useState(null);
  
  useEffect(() => {
    loadPendingCount();
    
    // Listen to sync events
    syncManager.onSyncStatusChange((status) => {
      if (status.status === 'syncing') {
        setIsSyncing(true);
        setSyncProgress(status);
      } else if (status.status === 'complete') {
        setIsSyncing(false);
        setSyncProgress(null);
        loadPendingCount();
      } else if (status.status === 'error') {
        setIsSyncing(false);
        setSyncProgress(null);
      }
    });
    
    // Refresh count every 30 seconds
    const interval = setInterval(loadPendingCount, 30000);
    
    return () => clearInterval(interval);
  }, []);
  
  async function loadPendingCount() {
    try {
      const queue = await getSyncQueue();
      setPendingCount(queue.length);
    } catch (error) {
      console.error('Error loading sync queue:', error);
    }
  }
  
  async function handleManualSync() {
    try {
      await syncManager.forceSyncNow();
    } catch (error) {
      console.error('Manual sync failed:', error);
    }
  }
  
  if (pendingCount === 0 && !isSyncing) {
    return (
      <Badge variant="synced" className="flex items-center gap-1">
        <CheckCircle className="w-3 h-3" />
        All Synced
      </Badge>
    );
  }
  
  if (isSyncing && syncProgress) {
    return (
      <div className="flex items-center gap-2">
        <Badge variant="syncing" className="flex items-center gap-1">
          <RefreshCw className="w-3 h-3 animate-spin" />
          Syncing {syncProgress.completed}/{syncProgress.total}
        </Badge>
      </div>
    );
  }
  
  return (
    <div className="flex items-center gap-2">
      <Badge variant="warning" className="flex items-center gap-1">
        {pendingCount} Pending
      </Badge>
      <Button 
        size="sm" 
        variant="ghost" 
        onClick={handleManualSync}
        className="h-6 px-2 text-xs"
      >
        <RefreshCw className="w-3 h-3 mr-1" />
        Sync Now
      </Button>
    </div>
  );
}
