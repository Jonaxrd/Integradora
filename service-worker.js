const CACHE_NAME = "scope-v1";

const ARCHIVOS = [
    "./",
    "./index.html",
    "./pwa.html",
    "./manifest.json",
    "./img/logo.png"
];

self.addEventListener("install", event => {

    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(ARCHIVOS))
    );

});

self.addEventListener("fetch", event => {

    event.respondWith(
        caches.match(event.request)
            .then(response => {
                return response || fetch(event.request);
            })
    );

});