const CACHE_NAME = 'bailandosolo-mobile-v2.2';
const PRECACHE_URLS = [
  '/',
  '/mobile',
  '/manifest.json',
  '/static/js/jszip.min.js',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
  '/static/icons/apple-touch-icon.png',
  '/static/icons/favicon.png'
];

// Install: Cache all critical assets individually to guarantee installation succeeds
self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(async (cache) => {
      for (const url of PRECACHE_URLS) {
        try {
          await cache.add(url);
        } catch (err) {
          console.warn(`[SW] Precache item failed (${url}):`, err);
        }
      }
    })
  );
});

// Activate: Clean up previous cache versions immediately
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch: Strategy depending on request type
self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);

  // 1. Audio Streaming or Big Downloads -> Let browser/network handle directly
  if (url.pathname.startsWith('/api/stream') || url.pathname.startsWith('/api/mobile/download')) {
    return;
  }

  // 2. API Endpoints -> Network-First (Do NOT cache failed responses)
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
          }
          return response;
        })
        .catch(() => {
          return caches.match(request);
        })
    );
    return;
  }

  // 3. Navigation Requests (User opening /mobile or refreshing) -> Cache-First with Network fallback
  if (request.mode === 'navigate' || url.pathname === '/mobile' || url.pathname === '/') {
    event.respondWith(
      caches.match('/mobile').then((cachedMobile) => {
        if (cachedMobile) {
          // Attempt network update in background if online
          fetch(request).then((netRes) => {
            if (netRes && netRes.status === 200) {
              caches.open(CACHE_NAME).then((cache) => cache.put('/mobile', netRes.clone()));
            }
          }).catch(() => {});
          return cachedMobile;
        }

        // If not in cache yet, fetch from network
        return fetch(request).then((netRes) => {
          if (netRes && netRes.status === 200) {
            const clone = netRes.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put('/mobile', clone));
          }
          return netRes;
        }).catch(() => {
          return caches.match('/mobile');
        });
      })
    );
    return;
  }

  // 4. Static Assets (JS, CSS, Icons, Images) -> Cache-First
  event.respondWith(
    caches.match(request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }
      return fetch(request).then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200) {
          const clone = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
        }
        return networkResponse;
      }).catch((err) => {
        console.warn('[SW] Offline asset fetch failed:', url.pathname);
      });
    })
  );
});
