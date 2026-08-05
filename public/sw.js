/**
 * F.I.R.E. 陪跑系统 — Service Worker
 *
 * 策略：
 *   - install: 预缓存 app shell + 关键静态资源（index.html / manifest / 图标 / favicon）
 *   - fetch:   cache-first（命中即返回，未命中走网络再回写缓存），离线时回 index.html
 *   - activate: 清掉旧版本缓存
 *
 * 注意：app 的全部业务数据存在 localStorage，本地依旧可用；SW 只缓存静态资源。
 * Bump CACHE_VERSION 强制全部客户端刷新缓存。
 */
const CACHE_VERSION = 'fire-companion-v1'
const CORE_ASSETS = [
  './',
  './index.html',
  './manifest.webmanifest',
  './favicon.png',
  './icon-192.png',
  './icon-512.png',
  './apple-touch-icon.png',
  './maskable-512.png'
]

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches
      .open(CACHE_VERSION)
      .then((cache) => cache.addAll(CORE_ASSETS))
      .then(() => self.skipWaiting())
  )
})

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(keys.filter((k) => k !== CACHE_VERSION).map((k) => caches.delete(k)))
      )
      .then(() => self.clients.claim())
  )
})

self.addEventListener('fetch', (event) => {
  const req = event.request
  // Only handle same-origin GET
  if (req.method !== 'GET') return
  const url = new URL(req.url)
  if (url.origin !== self.location.origin) return

  event.respondWith(
    caches.match(req).then((cached) => {
      if (cached) return cached
      return fetch(req)
        .then((res) => {
          // cache successful basic responses
          if (res && res.status === 200 && res.type === 'basic') {
            const copy = res.clone()
            caches.open(CACHE_VERSION).then((c) => c.put(req, copy))
          }
          return res
        })
        .catch(() => {
          // offline fallback: serve root index for navigation requests
          if (req.mode === 'navigate') return caches.match('./index.html')
          return new Response('', { status: 504, statusText: 'offline' })
        })
    })
  )
})