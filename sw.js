/* Nijer Khata — অফলাইন শেল ক্যাশ (Android-এ ইন্সটল করার জন্য দরকার)।
   এনক্রিপ্টেড ভল্টের ফাইল কখনো ক্যাশ হয় না। */
const CACHE = 'nijer-khata-v2';
const SHELL = ['./', 'index.html', 'manifest.webmanifest', 'private/', 'private/index.html',
  'private/app.js', 'terminal/', 'terminal/index.html', 'assets/menu.js', 'assets/install.js',
  'assets/branding/logos/app-icons/android-icon-192.png', 'assets/branding/logos/app-icons/android-icon-512.png'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => Promise.all(SHELL.map((u) => c.add(u).catch(() => {})))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin || url.pathname.includes('/vault/')) return;

  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).then((r) => {
      const copy = r.clone();
      caches.open(CACHE).then((c) => c.put(req, copy));
      return r;
    }).catch(() => caches.match(req).then((m) => m || caches.match('index.html'))));
    return;
  }
  e.respondWith(caches.match(req).then((m) => m || fetch(req).then((r) => {
    if (r.ok) { const copy = r.clone(); caches.open(CACHE).then((c) => c.put(req, copy)); }
    return r;
  })));
});
