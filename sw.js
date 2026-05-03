// Minimal service worker — its existence (with a fetch handler) is what
// unlocks Chrome's "Install app" prompt on Android. Caching is opportunistic:
// on first hit we cache the app shell so the form loads offline; on every
// fetch we try the network first and fall back to the cache.

const CACHE = 'daily-log-v1';
const SHELL = ['./', 'index.html', 'app.js', 'config.js', 'manifest.json'];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  // Don't cache POSTs to the Apps Script — those must always hit the network.
  if (req.method !== 'GET') return;
  event.respondWith(
    fetch(req).then((res) => {
      // Only cache same-origin responses; cross-origin (Apps Script JSON) skips cache.
      if (new URL(req.url).origin === self.location.origin && res.ok) {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copy));
      }
      return res;
    }).catch(() => caches.match(req))
  );
});
