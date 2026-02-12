/* Versioned cache names to safely manage updates */
const SW_VERSION = 'v2';
const STATIC_CACHE = `static-${SW_VERSION}`;
const OFFLINE_CACHE = `offline-${SW_VERSION}`;
const OFFLINE_URL = '/offline.html';

/* Minimal critical UI shell to precache */
const PRECACHE_URLS = [
  OFFLINE_URL,
  '/static/images/favicon_bg.png?v=2',
  '/static/images/logo.png',
];

/* Utility: Determine if request is for static assets */
const isStaticAsset = (req) => {
  const { destination, url, method } = req;
  if (method !== 'GET') return false;
  if (destination && ['style', 'script', 'image', 'font'].includes(destination)) return true;
  if (url.includes('/static/')) return true;
  return false;
};

/* Install: Pre-cache minimal UI shell (offline page, favicon, logo) */
self.addEventListener('install', (event) => {
  event.waitUntil(
    Promise.all([
      caches.open(OFFLINE_CACHE).then((cache) => cache.add(OFFLINE_URL)),
      caches.open(STATIC_CACHE).then((cache) => cache.addAll(PRECACHE_URLS)),
    ])
  );
  self.skipWaiting();
});

/* Activate: Clean up old caches and take control of clients */
self.addEventListener('activate', (event) => {
  const currentCaches = [STATIC_CACHE, OFFLINE_CACHE];
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => !currentCaches.includes(key))
          .map((key) => caches.delete(key))
      )
    ).then(() => self.clients.claim())
  );
});

/* Fetch: Hybrid strategy */
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const reqOrigin = new URL(request.url).origin;
  const swOrigin = self.location.origin;

  /* Bypass all cross-origin requests (e.g., Cloudinary, third-party CDNs) */
  if (reqOrigin !== swOrigin) {
    return;
  }

  /* Network-first for navigation (HTML) to avoid breaking Django auth/navigation */
  const isNavigation =
    request.mode === 'navigate' ||
    (request.headers.get('accept') || '').includes('text/html');

  if (isNavigation) {
    event.respondWith(
      (async () => {
        try {
          const networkResponse = await fetch(request);
          return networkResponse;
        } catch (err) {
          const cachedOffline = await caches.match(OFFLINE_URL, { ignoreSearch: true });
          return cachedOffline || new Response('Offline', { status: 503, statusText: 'Service Unavailable' });
        }
      })()
    );
    return;
  }

  /* Stale-While-Revalidate for static assets (CSS, JS, images, fonts) */
  if (isStaticAsset(request)) {
    event.respondWith(
      (async () => {
        const cache = await caches.open(STATIC_CACHE);
        const cached = await cache.match(request, { ignoreSearch: true });
        const fetchAndUpdate = fetch(request)
          .then((res) => {
            if (res && res.ok) {
              cache.put(request, res.clone());
            }
            return res;
          })
          .catch(() => null);
        return cached || (await fetchAndUpdate) || new Response('', { status: 504 });
      })()
    );
    return;
  }

  /* Default: pass-through for API or other requests to avoid interfering with Django */
  event.respondWith(fetch(request));
});
