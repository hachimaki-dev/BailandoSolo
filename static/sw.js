/**
 * Bailando Solo — Service Worker v3.1
 * 
 * Offline-first strategy:
 * - PRECACHE: All critical shell assets are cached on install (HTML, fonts, icons, JS)
 * - NAVIGATION: Always serve cached shell, update in background (stale-while-revalidate)
 * - API: Network-first with cache fallback (so offline library data works)
 * - STATIC: Cache-first with network fallback
 * - AUDIO: Pass-through (audio blobs are stored in IndexedDB by the app)
 */

const CACHE_NAME = 'bailandosolo-mobile-v4.0';

// Critical shell assets — ALL must be cached for offline to work
const PRECACHE_URLS = [
  '/mobile',
  '/manifest.json',
  '/static/js/jszip.min.js',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
  '/static/icons/apple-touch-icon.png',
  '/static/icons/favicon.png',
  // Local fonts (essential for correct UI rendering offline)
  '/static/fonts/press-start-2p.ttf',
  '/static/fonts/jetbrains-mono-400.ttf',
  '/static/fonts/jetbrains-mono-600.ttf',
  '/static/fonts/jetbrains-mono-700.ttf'
];

// ─── INSTALL ────────────────────────────────────────────────────────────────────
// Cache all critical assets. If any CRITICAL asset fails, installation still
// proceeds but we log warnings. The app can still work with partial cache.
self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(async (cache) => {
      const results = await Promise.allSettled(
        PRECACHE_URLS.map(async (url) => {
          try {
            const response = await fetch(url, { cache: 'no-cache' });
            if (response.ok) {
              await cache.put(url, response);
              return { url, status: 'cached' };
            }
            throw new Error(`HTTP ${response.status}`);
          } catch (err) {
            console.warn(`[SW] Failed to precache: ${url}`, err.message);
            return { url, status: 'failed', error: err.message };
          }
        })
      );

      const cached = results.filter(r => r.value?.status === 'cached').length;
      const failed = results.filter(r => r.value?.status === 'failed').length;
      console.log(`[SW] Precache complete: ${cached} cached, ${failed} failed out of ${PRECACHE_URLS.length}`);
    })
  );
});

// ─── ACTIVATE ───────────────────────────────────────────────────────────────────
// Clean up old cache versions and take control of all clients immediately
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys
          .filter((key) => key !== CACHE_NAME)
          .map((key) => {
            console.log(`[SW] Deleting old cache: ${key}`);
            return caches.delete(key);
          })
      );
    }).then(() => self.clients.claim())
  );
});

// ─── FETCH ──────────────────────────────────────────────────────────────────────
self.addEventListener('fetch', (event) => {
  const request = event.request;

  // Only handle GET requests
  if (request.method !== 'GET') return;

  const url = new URL(request.url);

  // Skip cross-origin requests entirely (CDNs, external APIs, etc.)
  if (url.origin !== self.location.origin) return;

  // ── 1. Audio Streams & Downloads → Pass-through (handled by IndexedDB in app)
  if (url.pathname.startsWith('/api/stream') ||
      url.pathname.startsWith('/api/mobile/download')) {
    return;
  }

  // ── 2. Navigation requests (user opening /mobile or refreshing)
  //    Strategy: Cache-first, network-update-in-background
  //    This guarantees the app ALWAYS loads offline if it was cached once
  if (request.mode === 'navigate' ||
      url.pathname === '/mobile' ||
      url.pathname === '/') {
    event.respondWith(
      caches.match('/mobile').then((cachedResponse) => {
        // Always try to update cache in the background
        const networkUpdate = fetch(request)
          .then((networkResponse) => {
            if (networkResponse && networkResponse.ok) {
              const clone = networkResponse.clone();
              caches.open(CACHE_NAME).then((cache) => {
                cache.put('/mobile', clone);
              });
            }
            return networkResponse;
          })
          .catch(() => null);

        // If we have a cached version, return it immediately
        if (cachedResponse) {
          return cachedResponse;
        }

        // No cache? Wait for network
        return networkUpdate.then((networkResponse) => {
          if (networkResponse) return networkResponse;
          // Complete offline with no cache — return a basic offline page
          return new Response(
            generateOfflineFallbackHTML(),
            { headers: { 'Content-Type': 'text/html; charset=utf-8' } }
          );
        });
      })
    );
    return;
  }

  // ── 3. API endpoints → Network-first with cache fallback
  //    Caches successful responses so library data is available offline
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response && response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
          }
          return response;
        })
        .catch(() => {
          return caches.match(request).then((cached) => {
            if (cached) return cached;
            // Return empty JSON for API calls with no cache
            return new Response(
              JSON.stringify({ error: 'offline', message: 'No cached data available' }),
              { status: 503, headers: { 'Content-Type': 'application/json' } }
            );
          });
        })
    );
    return;
  }

  // ── 4. Static assets (fonts, JS, icons, images) → Cache-first
  event.respondWith(
    caches.match(request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }
      return fetch(request)
        .then((networkResponse) => {
          if (networkResponse && networkResponse.ok) {
            const clone = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
          }
          return networkResponse;
        })
        .catch(() => {
          console.warn('[SW] Offline fetch failed for:', url.pathname);
          // Return empty response rather than throwing
          return new Response('', { status: 404 });
        });
    })
  );
});

// ─── OFFLINE FALLBACK HTML ──────────────────────────────────────────────────────
// Minimal fallback page shown only when the app was NEVER cached (first visit offline)
function generateOfflineFallbackHTML() {
  return `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Bailando Solo — Sin Conexión</title>
  <style>
    body {
      font-family: -apple-system, system-ui, sans-serif;
      background: #0f0f1a;
      color: #ffffff;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      margin: 0;
      text-align: center;
      padding: 20px;
    }
    .container { max-width: 400px; }
    h1 { font-size: 48px; margin-bottom: 8px; }
    h2 { color: #00f0ff; font-size: 18px; margin-bottom: 16px; }
    p { color: #a0a0b8; line-height: 1.6; margin-bottom: 20px; }
    button {
      background: #5a5aff;
      color: white;
      border: none;
      padding: 14px 28px;
      font-size: 16px;
      font-weight: 700;
      border-radius: 4px;
      cursor: pointer;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>💿</h1>
    <h2>BAILANDO SOLO</h2>
    <p>No hay conexión a internet y la app no se ha cacheado todavía.</p>
    <p>Conecta tu teléfono a la misma red WiFi que tu PC con Bailando Solo y abre esta página para cachearla por primera vez.</p>
    <button onclick="location.reload()">🔄 Reintentar</button>
  </div>
</body>
</html>`;
}
