import { createI18n } from 'vue-i18n'
import zhCN from './locales/zh-CN'
import enUS from './locales/en-US'
import { loadDb } from '@/storage'

// 直接读本地存储,避免模块加载时依赖 Pinia 激活上下文
const locale = (loadDb().profile && loadDb().profile.locale) || 'zh-CN'

const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale,
  fallbackLocale: 'en-US',
  messages: {
    'zh-CN': zhCN,
    'en-US': enUS
  }
})

export default i18n
