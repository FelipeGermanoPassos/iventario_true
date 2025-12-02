const CACHE_NAME = 'inventario-ti-v1';
const CORE_ASSETS = [
  '/',
  '/static/manifest.json',
  '/static/css/style.css',
  '/static/js/app.js',
  '/static/js/login.js',
  '/static/js/perfil.js',
  '/static/js/admin.js',
  '/static/js/relatorios.js'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(CORE_ASSETS)).then(self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(keys.map(k => k !== CACHE_NAME ? caches.delete(k) : null)))
      .then(() => self.clients.claim())
  );
});

// Simple routing: cache-first for static, network-first for navigation/API
self.addEventListener('fetch', event => {
  const req = event.request;
  const url = new URL(req.url);

  // Only handle same-origin
  if (url.origin !== location.origin) return;

  // Navigation requests -> network first, fallback to cache
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req).catch(() => caches.match('/'))
    );
    return;
  }

  // Static assets -> cache first
  if (req.destination === 'style' || req.destination === 'script' || req.destination === 'image' || req.url.includes('/static/')) {
    event.respondWith(
      caches.match(req).then(cached => cached || fetch(req).then(res => {
        const clone = res.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(req, clone));
        return res;
      }))
    );
    return;
  }

  // Default: try network then cache
  event.respondWith(
    fetch(req).then(res => {
      return res;
    }).catch(() => caches.match(req))
  );
});

// Push Notification Support
self.addEventListener('push', event => {
  const options = {
    icon: '/static/icons/icon-192.png',
    badge: '/static/icons/icon-192.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now()
    }
  };

  let data = { title: 'Inventário TI', body: 'Nova notificação' };
  
  if (event.data) {
    try {
      data = event.data.json();
    } catch (e) {
      data.body = event.data.text();
    }
  }

  options.body = data.body;
  options.data.url = data.url || '/';
  
  if (data.tag) options.tag = data.tag;
  if (data.requireInteraction) options.requireInteraction = data.requireInteraction;
  if (data.actions) options.actions = data.actions;

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  
  const urlToOpen = event.notification.data.url || '/';
  
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then(windowClients => {
        // Check if there's already a window open with this URL
        for (let client of windowClients) {
          if (client.url === urlToOpen && 'focus' in client) {
            return client.focus();
          }
        }
        // If no window is open, open a new one
        if (clients.openWindow) {
          return clients.openWindow(urlToOpen);
        }
      })
  );
});
