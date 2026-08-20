// Macht das Quiz offline lauffaehig.
//
// Beim Aendern des Quiz die Zahl in SPEICHER hochzaehlen — sonst zeigen
// Geraete, die die App schon einmal geoeffnet haben, weiter den alten Stand.
const SPEICHER = 'quiz-v2';

const DATEIEN = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icon-192.png',
  './icon-512.png',
  './icon-maskable-512.png',
  './apple-touch-icon.png',
  './favicon.png'
];

self.addEventListener('install', function (e) {
  // skipWaiting: eine neue Fassung uebernimmt sofort. Ohne das bleibt der
  // neue Worker auf "waiting" stehen und das Tablet zeigt nach einem Upload
  // tagelang die alte Fassung — der Klassiker.
  e.waitUntil(caches.open(SPEICHER).then(function (s) { return s.addAll(DATEIEN); }));
  self.skipWaiting();
});

self.addEventListener('activate', function (e) {
  e.waitUntil(
    caches.keys()
      .then(function (namen) {
        return Promise.all(namen
          .filter(function (n) { return n !== SPEICHER; })
          .map(function (n) { return caches.delete(n); }));
      })
      .then(function () { return self.clients.claim(); })
  );
});

self.addEventListener('fetch', function (e) {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    caches.match(e.request).then(function (treffer) {
      return treffer || fetch(e.request).catch(function () {
        // Ohne Netz und nicht im Speicher: Startseite ausliefern, damit ein
        // versehentlicher Aufruf einer Unteradresse nicht ins Leere laeuft.
        return caches.match('./index.html');
      });
    })
  );
});
