import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import i18n from './i18n'
import './style.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(i18n)
app.mount('#app')

// PWA Service Worker — 仅生产构建注册,避免开发态被缓存搅局
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => {
    const swUrl = (import.meta.env.BASE_URL || './') + 'sw.js'
    navigator.serviceWorker
      .register(swUrl)
      .then((reg) => {
        if (reg.waiting) {
          // 有新版本等待激活，不强制刷新以免打断用户
          console.info('[SW] update waiting, will activate on next load')
        }
      })
      .catch((err) => console.warn('[SW] registration failed', err))
  })
}
