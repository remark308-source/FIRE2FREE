/**
 * F.I.R.E. 陪跑系统 — Service Worker
 *
 * 策略：
 *   - install:  预缓存 app shell（离线兜底）
 *   - fetch:
 *       * 导航请求（index.html）: network-first
 *         —— 保证每次部署用户立即拿到新 HTML，新 HTML 引用新 hash 的
 *            JS/CSS，从而自动加载新版。彻底解决「推了新版手机却看旧版」。
 *       * 静态资源（JS/CSS/图片）: cache-first
 *         —— 这些资源构建时带内容 hash，URL 唯一，旧版不会污染新版，安全缓存。
 *   - activate: 清掉旧版本缓存
 *
 * 注意：app 业务数据存在 localStorage，本地依旧可用；SW 只缓存静态资源。
 * 每次发版若想强制所有客户端刷新，bump CACHE_VERSION 即可（本文件字节变化
 * 也会触发 SW 重新安装，从而应用新策略）。
 */
const CACHE_VERSION = 'fire-companion-v2'
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

  // 导航请求：network-first，确保新部署立即生效
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req)
        .then((res) => {
          if (res && res.status === 200) {
            const copy = res.clone()
            caches.open(CACHE_VERSION).then((c) => c.put('./index.html', copy))
          }
          return res
        })
        .catch(() => caches.match('./index.html'))
    )
    return
  }

  // 静态资源：cache-first（带 hash，URL 唯一，安全）
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
        .catch(() => new Response('', { status: 504, statusText: 'offline' }))
    })
  )
})
