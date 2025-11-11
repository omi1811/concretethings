# Offline-First Architecture for ConcreteThings QMS

## 🔌 Offline Strategy Overview

Your app will work **completely offline** with automatic sync when online!

```
┌────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                          │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  Online Mode:                 Offline Mode:                │
│  ✅ Real-time API calls       ✅ Read from IndexedDB       │
│  ✅ Instant updates           ✅ Write to local queue      │
│  ✅ Server validation         ✅ Show offline indicator    │
│                               ✅ Photos stored locally     │
│                                                             │
├────────────────────────────────────────────────────────────┤
│              SERVICE WORKER (Background)                   │
│  • Cache API responses                                     │
│  • Store photos in Cache Storage                           │
│  • Intercept network requests                              │
│  • Queue failed requests                                   │
├────────────────────────────────────────────────────────────┤
│              INDEXEDDB (Local Database)                    │
│  • Batches, Cube Tests, Training Records                   │
│  • Photos (Base64 or Blob)                                 │
│  • Pending sync queue                                      │
│  • Offline timestamps                                      │
├────────────────────────────────────────────────────────────┤
│              BACKGROUND SYNC                               │
│  • Auto-sync when online                                   │
│  • Retry failed requests                                   │
│  • Conflict resolution                                     │
│  • Progress tracking                                       │
└────────────────────────────────────────────────────────────┘
```

---

## 📦 Storage Strategy

### 1. **IndexedDB** (Primary Local Database)

```javascript
// Database Schema
ConcreteQMS_DB
  ├── batches (project_id, batch_data, photos, sync_status)
  ├── cube_tests (project_id, test_data, photos, sync_status)
  ├── training_records (project_id, training_data, photos, sync_status)
  ├── materials (project_id, material_data, sync_status)
  ├── vendors (project_id, vendor_data, sync_status)
  ├── sync_queue (id, type, data, timestamp, retries)
  ├── photos_cache (id, photo_blob, associated_id, timestamp)
  └── user_data (user_id, company_id, projects, token)
```

**Storage Limits:**
- Chrome/Edge: ~60% of available disk space
- Firefox: ~50% of available disk space
- Safari: 1GB (can request more)
- Mobile: Usually 50-100MB (expandable to ~500MB)

### 2. **Cache Storage** (Service Worker Cache)

```javascript
// Cache Strategy
Caches:
  ├── static-v1 (HTML, CSS, JS files)
  ├── api-cache (GET API responses)
  ├── photos-cache (Uploaded photos)
  └── fonts-cache (Web fonts)
```

**Cache Strategies:**
- **Network First**: API calls (try online, fallback to cache)
- **Cache First**: Static assets (fast load from cache)
- **Cache & Update**: Read from cache, update in background
- **Online Only**: Auth endpoints (must be online)

### 3. **LocalStorage** (Small Data)

```javascript
// Quick access data
localStorage:
  ├── auth_token (JWT)
  ├── user_preference (theme, language)
  ├── last_sync_timestamp
  ├── offline_mode (boolean)
  └── selected_project_id
```

---

## 🔄 Sync Strategy

### When User Creates Data Offline:

```
1. User creates batch entry (no internet)
   ↓
2. Save to IndexedDB with status: "pending_sync"
   ↓
3. Add to sync_queue with timestamp
   ↓
4. Show in UI with 🔴 Offline badge
   ↓
5. When internet returns:
   ↓
6. Background sync triggers
   ↓
7. POST to server API
   ↓
8. If success:
   - Update IndexedDB with server ID
   - Mark as "synced" ✅
   - Show 🟢 Synced badge
   ↓
9. If conflict (e.g., duplicate):
   - Show conflict resolution UI
   - Let user choose: Keep local / Use server / Merge
```

### Conflict Resolution:

```javascript
Scenario 1: Same record edited offline and online
  → Last-Write-Wins (server timestamp)
  → Or: Show merge UI to user

Scenario 2: Photo uploaded offline, different photo online
  → Keep both with suffix: photo_1_local, photo_1_server
  → Let user choose

Scenario 3: Record deleted online, edited offline
  → Server wins (deleted)
  → Notify user: "Record was deleted by another user"
```

---

## 📱 PWA Configuration

### manifest.json

```json
{
  "name": "ConcreteThings QMS",
  "short_name": "ConcreteQMS",
  "description": "Construction Quality Management System",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#1E40AF",
  "orientation": "portrait-primary",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ],
  "screenshots": [
    {
      "src": "/screenshot-mobile.png",
      "sizes": "540x720",
      "type": "image/png",
      "form_factor": "narrow"
    }
  ],
  "categories": ["productivity", "business"],
  "shortcuts": [
    {
      "name": "New Batch",
      "url": "/batches/new",
      "icons": [{ "src": "/icon-batch.png", "sizes": "96x96" }]
    },
    {
      "name": "New Cube Test",
      "url": "/cube-tests/new",
      "icons": [{ "src": "/icon-cube.png", "sizes": "96x96" }]
    }
  ]
}
```

### Features:
- ✅ Install to home screen (Android/iOS)
- ✅ Fullscreen app experience
- ✅ Splash screen
- ✅ App shortcuts
- ✅ Badge notifications
- ✅ Share target (share photos to app)

---

## 🚀 Service Worker Lifecycle

```javascript
// Service Worker Events

Install Event:
  → Cache static assets (HTML, CSS, JS)
  → Precache API routes
  → Initialize IndexedDB

Activate Event:
  → Delete old caches
  → Claim clients
  → Ready to intercept requests

Fetch Event:
  → Intercept all network requests
  → Apply cache strategy
  → Return cached response if offline

Sync Event:
  → Trigger when online
  → Process sync_queue
  → Upload pending data
  → Update UI with results

Message Event:
  → Communication between SW and main thread
  → Send sync progress updates
  → Notify about new cache available
```

---

## 📸 Photo Handling Offline

### Strategy:

```javascript
1. User captures photo
   ↓
2. Convert to Base64 or Blob
   ↓
3. Compress image (reduce size)
   - JPEG quality: 80%
   - Max dimension: 1920px
   - Typical size: 200-500KB
   ↓
4. Store in IndexedDB photos_cache
   ↓
5. Display thumbnail from IndexedDB
   ↓
6. When online: Upload to server
   ↓
7. Server returns photo URL
   ↓
8. Update IndexedDB with server URL
   ↓
9. Clear local Blob (save space)
```

### Photo Compression:

```javascript
// Using canvas to compress
function compressImage(file, maxWidth = 1920, quality = 0.8) {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        let width = img.width;
        let height = img.height;
        
        if (width > maxWidth) {
          height = (maxWidth / width) * height;
          width = maxWidth;
        }
        
        canvas.width = width;
        canvas.height = height;
        
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);
        
        canvas.toBlob(resolve, 'image/jpeg', quality);
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  });
}
```

---

## 🔔 Background Sync

### Native Background Sync API:

```javascript
// Register sync when offline
if ('serviceWorker' in navigator && 'SyncManager' in window) {
  navigator.serviceWorker.ready.then((registration) => {
    return registration.sync.register('sync-batches');
  });
}

// In Service Worker
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-batches') {
    event.waitUntil(syncPendingBatches());
  }
});

async function syncPendingBatches() {
  const db = await openDB();
  const pending = await db.getAll('sync_queue');
  
  for (const item of pending) {
    try {
      const response = await fetch(item.url, {
        method: item.method,
        body: JSON.stringify(item.data),
        headers: item.headers
      });
      
      if (response.ok) {
        await db.delete('sync_queue', item.id);
        // Notify UI
        self.clients.matchAll().then(clients => {
          clients.forEach(client => {
            client.postMessage({
              type: 'SYNC_SUCCESS',
              id: item.id
            });
          });
        });
      }
    } catch (error) {
      // Retry later
      await db.put('sync_queue', { ...item, retries: item.retries + 1 });
    }
  }
}
```

---

## 📊 Storage Usage Monitoring

```javascript
// Check storage quota
async function checkStorageQuota() {
  if (navigator.storage && navigator.storage.estimate) {
    const estimate = await navigator.storage.estimate();
    const percentUsed = (estimate.usage / estimate.quota) * 100;
    
    console.log(`Using ${percentUsed.toFixed(2)}% of available storage`);
    console.log(`${formatBytes(estimate.usage)} of ${formatBytes(estimate.quota)}`);
    
    if (percentUsed > 80) {
      // Warn user: "Storage almost full. Clear old data?"
      showStorageWarning();
    }
  }
}

// Request persistent storage (won't be evicted)
async function requestPersistentStorage() {
  if (navigator.storage && navigator.storage.persist) {
    const isPersisted = await navigator.storage.persist();
    console.log(`Persistent storage granted: ${isPersisted}`);
  }
}
```

---

## 🔍 Data Sync Status Indicators

### UI Indicators:

```
🟢 Synced        - Data saved to server
🟡 Syncing...    - Upload in progress
🔴 Offline       - Saved locally, pending sync
⚠️  Conflict     - Needs user action
❌ Failed        - Sync error (retry)
```

### Example UI:

```
┌─────────────────────────────────────────────┐
│ Batch #B-047              🔴 Offline        │
│ Created: 10/11/2025 14:30 (Local)           │
│ Will sync when online                       │
│                                              │
│ [Retry Sync Now]  [View Details]            │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ Batch #B-048              🟢 Synced         │
│ Created: 10/11/2025 15:00                   │
│ Server ID: 12345                            │
└─────────────────────────────────────────────┘
```

---

## ⚡ Performance Optimizations

### 1. **Lazy Loading**
```javascript
// Load components only when needed
const BatchModule = lazy(() => import('./components/modules/batches'));
const CubeTestModule = lazy(() => import('./components/modules/cube-tests'));
```

### 2. **Virtual Scrolling**
```javascript
// For large lists (1000+ items)
import { FixedSizeList } from 'react-window';
```

### 3. **Image Lazy Loading**
```javascript
<img src={photo} loading="lazy" alt="Batch photo" />
```

### 4. **Code Splitting**
```javascript
// Next.js automatic code splitting by route
app/
  batches/page.js       → batches.chunk.js
  cube-tests/page.js    → cube-tests.chunk.js
```

### 5. **Debounce Search**
```javascript
// Wait 300ms before searching
const debouncedSearch = debounce(searchBatches, 300);
```

---

## 🧪 Testing Offline Mode

### In Chrome DevTools:

1. Open DevTools (F12)
2. Network tab → Throttling dropdown
3. Select "Offline"
4. Test app functionality
5. Check IndexedDB (Application tab)
6. Check Service Worker (Application → Service Workers)

### Simulate Scenarios:

```javascript
// Scenario 1: Go offline mid-upload
1. Start uploading batch with photo
2. Turn off network mid-upload
3. Check: Photo saved to IndexedDB?
4. Turn on network
5. Check: Auto-resume upload?

// Scenario 2: Create multiple records offline
1. Go offline
2. Create 5 batches with photos
3. Check: All in sync_queue?
4. Go online
5. Check: All sync in order?

// Scenario 3: Conflict resolution
1. Edit batch #B-047 offline
2. Another user edits same batch online
3. Go online with your changes
4. Check: Conflict UI shown?
```

---

## 📱 Mobile-Specific Optimizations

### 1. **Network Information API**
```javascript
// Detect connection type
if ('connection' in navigator) {
  const connection = navigator.connection;
  
  if (connection.effectiveType === '4g') {
    // High quality photos
  } else if (connection.effectiveType === '3g') {
    // Compressed photos
  } else {
    // Minimal data mode
  }
}
```

### 2. **Battery Status API**
```javascript
// Reduce background sync when battery low
if ('getBattery' in navigator) {
  navigator.getBattery().then(battery => {
    if (battery.level < 0.2 && !battery.charging) {
      // Pause non-critical syncs
    }
  });
}
```

### 3. **Visibility API**
```javascript
// Pause sync when app in background
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    // Pause UI updates
  } else {
    // Resume, check for new data
  }
});
```

---

## 🎯 Recommended Offline Features Priority

### Phase 1: Basic Offline (MVP)
- [x] Service Worker setup
- [x] Cache static assets
- [x] IndexedDB for data storage
- [x] Offline indicator in UI
- [x] Read-only offline mode

### Phase 2: Offline CRUD
- [x] Create records offline
- [x] Update records offline
- [x] Delete (soft delete) offline
- [x] Sync queue management
- [x] Auto-sync when online

### Phase 3: Photo Support
- [x] Capture photos offline
- [x] Store photos in IndexedDB
- [x] Compress before upload
- [x] Background photo sync
- [x] Thumbnail generation

### Phase 4: Advanced Features
- [ ] Conflict resolution UI
- [ ] Partial sync (priority records)
- [ ] Bandwidth-aware sync
- [ ] P2P sync (share data between devices)
- [ ] Backup to local file

---

## 🔧 Debugging Tools

### 1. **Chrome DevTools**
- Application → Storage (IndexedDB, Cache, LocalStorage)
- Application → Service Workers (status, update, unregister)
- Network → Offline simulation
- Lighthouse → PWA audit

### 2. **Workbox Tools**
```bash
# Analyze service worker
npx workbox wizard

# Generate service worker
npx workbox generateSW workbox-config.js
```

### 3. **Custom Debug Panel**
```javascript
// Add debug panel in dev mode
if (process.env.NODE_ENV === 'development') {
  <DebugPanel>
    - Storage used: 12.5 MB
    - Pending syncs: 3
    - Last sync: 2 min ago
    - Network: Online
    - [Clear Cache] [Force Sync] [Export Data]
  </DebugPanel>
}
```

---

## ✅ Checklist for Going Offline-First

- [ ] Install next-pwa package
- [ ] Configure service worker
- [ ] Set up IndexedDB schema
- [ ] Implement sync queue
- [ ] Add offline indicator
- [ ] Test offline create/read/update
- [ ] Test photo capture offline
- [ ] Test auto-sync when online
- [ ] Test conflict scenarios
- [ ] Add storage quota monitoring
- [ ] Implement cache cleanup
- [ ] Test on real mobile devices
- [ ] PWA installability check
- [ ] Performance audit (Lighthouse)
- [ ] User documentation

---

## 📚 Libraries Used

```json
{
  "next-pwa": "^5.6.0",           // PWA support
  "idb": "^8.0.0",                 // IndexedDB wrapper
  "workbox-window": "^7.0.0",      // Service Worker helpers
  "react-query": "^5.0.0",         // Cache & sync management
  "localforage": "^1.10.0"         // Alternative to raw IndexedDB
}
```

---

Your app will now work **completely offline** like Google Docs or Gmail! 🚀

