'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState, useEffect } from 'react';
import { initDB } from '@/lib/db';
import syncManager from '@/lib/sync';

export function Providers({ children }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 5 * 60 * 1000, // 5 minutes
        retry: 1,
        refetchOnWindowFocus: false
      }
    }
  }));

  useEffect(() => {
    // Initialize IndexedDB
    initDB().catch(console.error);

    // Register sync listener
    const handleOnline = () => {
      console.log('App is online');
      syncManager.startSync();
    };

    window.addEventListener('online', handleOnline);

    return () => {
      window.removeEventListener('online', handleOnline);
    };
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
