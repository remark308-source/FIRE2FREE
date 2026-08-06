<script setup>
import { ref, computed, h, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute, RouterView } from 'vue-router'
import {
  NLayout, NLayoutSider, NLayoutContent,
  NMenu, NSpace, NSelect, NText, NConfigProvider,
  NMessageProvider, NDialogProvider, NNotificationProvider,
  darkTheme, useOsTheme,
  zhCN, enUS,
  dateZhCN, dateEnUS
} from 'naive-ui'
import { useI18n } from 'vue-i18n'
import { useAppStore } from '@/stores/app'

import FireLogo from '@/components/icons/FireLogo.vue'
import IconDashboard from '@/components/icons/IconDashboard.vue'
import IconIncome from '@/components/icons/IconIncome.vue'
import IconExpense from '@/components/icons/IconExpense.vue'
import IconInvest from '@/components/icons/IconInvest.vue'
import IconCalculator from '@/components/icons/IconCalculator.vue'
import IconReminders from '@/components/icons/IconReminders.vue'
import IconBet from '@/components/icons/IconBet.vue'
import IconLine from '@/components/icons/IconLine.vue'
import IconSettings from '@/components/icons/IconSettings.vue'
import SaveFxLayer from '@/components/SaveFxLayer.vue'
import QuickEntrySheet from '@/components/QuickEntrySheet.vue'
import SideSheet from '@/components/SideSheet.vue'
import Onboarding from '@/views/Onboarding.vue'
import { useContracts } from '@/composables/contracts'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const app = useAppStore()
const osTheme = useOsTheme()
// 首次进入(entryMode 未选) → 强制走 Onboarding,不可跳过
const needsOnboarding = computed(() => !app.profile.entryMode)
const theme = computed(() => {
  const eff = app.profile.theme === 'system' ? osTheme.value : app.profile.theme
  return eff === 'dark' ? darkTheme : null
})

// naive-ui 组件本地化跟随语系,影响 NDatePicker 的「确认/今日」等内置文案
// (注意:naive-ui 2.38.2 中日期 panel 的「此刻」按钮取自 zhCN.DatePicker.now,
//  不是 dateZhCN.panelNowBtn — 早期版本/文档的字段名已过时)
const naiveLocale = computed(() => {
  const isZh = app.profile.locale === 'zh-CN'
  const base = isZh ? zhCN : enUS
  return { ...base, DatePicker: { ...base.DatePicker, now: isZh ? '今日' : 'Today' } }
})
const naiveDateLocale = computed(() => (app.profile.locale === 'zh-CN' ? dateZhCN : dateEnUS))

// 注意:这里**不**给 menuOptions 加 `icon` 字段!
// NMenu 会自动渲染 option.icon,如果再加 render-label 就会双倍。
// 我们改为在 render-label 里直接把组件传上去(只渲一次)。
const menuOptions = computed(() => [
  { label: t('nav.dashboard'), key: 'dashboard', iconRender: () => h(IconDashboard) },
  { label: t('nav.income'), key: 'income', iconRender: () => h(IconIncome) },
  { label: t('nav.expense'), key: 'expense', iconRender: () => h(IconExpense) },
  { label: t('nav.invest'), key: 'invest', iconRender: () => h(IconInvest) },
  { label: t('nav.calculator'), key: 'calculator', iconRender: () => h(IconCalculator) },
  { label: t('nav.reminders'), key: 'reminders', iconRender: () => h(IconReminders) },
  { label: t('nav.bets'), key: 'bets', iconRender: () => h(IconBet) },
  { label: t('nav.report'), key: 'report', iconRender: () => h(IconLine) },
  { label: t('nav.settings'), key: 'settings', iconRender: () => h(IconSettings) }
])

const activeKey = computed(() => route.name)
function handleMenu(key) {
  router.push({ name: key })
  // 移动端:点选菜单后自动收起抽屉,让内容区占满全宽
  if (isMobile.value) mobileDrawerOpen.value = false
}

// 移动端:左上汉堡按钮点开左侧抽屉(替代原底部「更多」tab),
// 悬浮「记一笔」FAB 一步呼起底部录入抽屉,强化核心记账流程。
const quickOpen = ref(false)

const langOptions = computed(() => {
  const zh = app.profile.locale === 'zh-CN'
  return [
    { label: zh ? '中文' : 'Chinese', value: 'zh-CN' },
    { label: zh ? 'English' : 'English', value: 'en-US' }
  ]
})
const themeOptions = computed(() => [
  { label: t('theme.system'), value: 'system' },
  { label: t('theme.light'), value: 'light' },
  { label: t('theme.dark'), value: 'dark' }
])

// ====== 响应式布局:桌面 vs 移动 =================================
// 桌面:左侧固定 sider(可手动折叠 64px / 展开 232px)。
// 移动(≤768):**没有持久 sider**,改成抽屉式 —
//   - 默认完全隐藏(translateX(-100%))
//   - 右上角汉堡按钮打开,触屏从左侧滑入覆盖整个内容区
//   - 点击菜单项 → 自动关闭抽屉
// 优势:内容区永远占满全屏宽度,不再被 64px 侧栏挤压。
const isMobile = ref(typeof window !== 'undefined' ? window.innerWidth <= 768 : false)
const mobileDrawerOpen = ref(false)
const desktopCollapsed = ref(false)

function syncLayout() {
  const m = window.innerWidth <= 768
  const was = isMobile.value
  isMobile.value = m
  if (was && !m) {
    // 从移动切到桌面:关闭抽屉(桌面没有抽屉)
    mobileDrawerOpen.value = false
  }
  if (!was && m) {
    // 从桌面切到移动:确保抽屉关闭,desktopCollapsed 在桌面无意义
    desktopCollapsed.value = false
    mobileDrawerOpen.value = false
  }
}

onMounted(() => {
  syncLayout()
  window.addEventListener('resize', syncLayout)
})
onUnmounted(() => {
  window.removeEventListener('resize', syncLayout)
})

// 全局自动结算自我对赌:应用启动即把达标契约落为 won(数据一致性),
// 新赢的 id 暂存到 sessionWins,Bets 页挂载时取走弹庆祝(避免漏庆祝)。
// ⚠️ 必须在 setup 同步调用(不能放 onMounted):Vue 中子组件 onMounted 先于父组件执行,
// 若放 onMounted,Bets 的 takeSessionWins() 会早于此处推入赢家 → 取到空 → 庆祝不弹。
const { autoResolve } = useContracts()
autoResolve()
</script>

<template>
  <NConfigProvider :theme="theme" :locale="naiveLocale" :date-locale="naiveDateLocale" :class="theme ? 'theme-dark' : 'theme-light'">
    <NMessageProvider>
      <NNotificationProvider>
        <NDialogProvider>
          <SaveFxLayer />
          <Onboarding v-if="needsOnboarding" />
          <template v-else>
            <!-- 桌面布局:固定左侧 sider -->
            <NLayout v-if="!isMobile" has-sider style="height: 100vh">
              <NLayoutSider
                bordered
                :collapsed-width="64"
                :width="232"
                v-model:collapsed="desktopCollapsed"
                show-trigger
                collapse-mode="width"
              >
                <div style="padding: 18px 14px 14px 14px; display: flex; align-items: center; gap: 10px">
                  <FireLogo :size="desktopCollapsed ? 36 : 81" :show-wordmark="!desktopCollapsed" />
                </div>
                <NMenu
                  :value="activeKey"
                  :options="menuOptions"
                  :render-label="(opt) => h('div', { style: 'display:inline-flex;align-items:center;gap:10px' }, [opt.iconRender(), h('span', {}, opt.label)])"
                  @update:value="handleMenu"
                  style="padding-top: 6px"
                />
                <div class="sider-foot">
                  <div class="sider-controls">
                    <NSelect
                      size="small"
                      :value="app.profile.locale"
                      :options="langOptions"
                      :menu-props="{ style: 'min-width: 140px; z-index: 9999' }"
                      @update:value="(v) => app.updateProfile({ locale: v })"
                    />
                    <NSelect
                      size="small"
                      :value="app.profile.theme"
                      :options="themeOptions"
                      :menu-props="{ style: 'min-width: 140px; z-index: 9999' }"
                      @update:value="(v) => app.updateProfile({ theme: v })"
                    />
                  </div>
                  <NText depth="3" class="sider-privacy">
                    🔒 {{ $t('app.privacyFooter') }}
                  </NText>
                </div>
              </NLayoutSider>

              <NLayout>
                <NLayoutContent content-style="padding: 20px; overflow: auto" style="height: 100vh">
                  <RouterView />
                </NLayoutContent>
              </NLayout>
            </NLayout>

            <!-- 移动布局:全宽内容,无持久 sider(抽屉浮层另起) -->
            <template v-else>
              <NLayout style="height: 100vh">
                <NLayoutContent content-style="padding: 0; overflow: auto" style="height: 100vh">
                  <div class="mobile-content">
                    <RouterView />
                  </div>
                </NLayoutContent>
              </NLayout>

              <!-- 左上角汉堡按钮:替代原底部「更多」tab,仅移动端渲染,点开左侧抽屉 -->
              <button class="menu-fab" type="button" :aria-label="t('nav.menu')" @click="mobileDrawerOpen = true">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">
                  <line x1="4" y1="7" x2="20" y2="7" />
                  <line x1="4" y1="12" x2="20" y2="12" />
                  <line x1="4" y1="17" x2="20" y2="17" />
                </svg>
              </button>

              <!-- 悬浮记账按钮(核心记账流程一步呼起) -->
              <button class="fab" type="button" :aria-label="t('quick.title')" @click="quickOpen = true">
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              </button>

              <!-- 记一笔 底部抽屉 -->
              <QuickEntrySheet v-model:show="quickOpen" />
            </template>

            <!-- 移动抽屉:从左侧滑入,带遮罩,点选菜单自动关闭
                 用自定义 SideSheet 替代 NDrawer(naive-ui 2.38 NDrawerContent
                 在 mobile 下偶发渲染空白,见 SideSheet.vue 顶部说明) -->
            <SideSheet
              v-if="isMobile"
              v-model:show="mobileDrawerOpen"
              placement="left"
              :width="280"
            >
              <template #header>
                <div class="drawer-head">
                  <FireLogo :size="42" :show-wordmark="true" />
                </div>
              </template>
              <NMenu
                :value="activeKey"
                :options="menuOptions"
                :render-label="(opt) => h('div', { style: 'display:inline-flex;align-items:center;gap:10px' }, [opt.iconRender(), h('span', {}, opt.label)])"
                @update:value="handleMenu"
              />
              <div class="drawer-foot">
                <div class="drawer-foot-title">{{ $t('settings.title') }}</div>
                <div class="sider-controls">
                  <NSelect
                    size="small"
                    :value="app.profile.locale"
                    :options="langOptions"
                    :menu-props="{ style: 'min-width: 140px; z-index: 9999' }"
                    @update:value="(v) => app.updateProfile({ locale: v })"
                  />
                  <NSelect
                    size="small"
                    :value="app.profile.theme"
                    :options="themeOptions"
                    :menu-props="{ style: 'min-width: 140px; z-index: 9999' }"
                    @update:value="(v) => app.updateProfile({ theme: v })"
                  />
                </div>
                <NText depth="3" class="sider-privacy">
                  🔒 {{ $t('app.privacyFooter') }}
                </NText>
              </div>
            </SideSheet>
          </template>
        </NDialogProvider>
      </NNotificationProvider>
    </NMessageProvider>
  </NConfigProvider>
</template>

<style>
/* 全局微动效提升视觉 */
:root {
  --fire-grad-primary: linear-gradient(135deg, #FFC857 0%, #FF8A3D 50%, #E9533B 100%);
  --fire-grad-blue: linear-gradient(135deg, #5B8DEF 0%, #7B61FF 100%);
  --fire-grad-green: linear-gradient(135deg, #18a058 0%, #36ad6a 100%);
  --fire-grad-pink: linear-gradient(135deg, #FF6B9D 0%, #C147E9 100%);
  --fire-grad-orange: linear-gradient(135deg, #FFA94D 0%, #FF6B35 100%);
  --fire-grad-violet: linear-gradient(135deg, #312E81 0%, #5B21B6 100%);
  --fire-grad-rose: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);

  /* 统一字体栈 + 移动端字号阶梯(离线优先,不依赖网络字体) */
  --ff-font: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif;
  --ff-num: "SF Pro Display", system-ui, -apple-system, "Roboto", sans-serif;
  --fs-xs: 11px;
  --fs-sm: 12px;
  --fs-base: 14px;
  --fs-md: 16px;
  --fs-lg: 18px;
  --fs-xl: 22px;
  /* 底部 Tab 栏高度(含安全区) */
  /* 记一笔抽屉默认深色文字(浅色主题由组件内 .qs-light 覆盖) */
  --qs-text: #e6e8f0;
  /* FIRE 进度环中心文字颜色:浅/深主题各一套,
     Vue scoped 不会给 SVG <text> 加 data-hash 所以 :deep 不穿透,
     改用 CSS 变量在 SVG 子元素继承。外层 .theme-dark 覆盖 */
  --ring-text-label: rgba(0, 0, 0, 0.55);
  --ring-text-main:  #1a1a1a;
  --ring-text-sr:    #FF8A3D;
}
.theme-dark {
  --ring-text-label: rgba(255, 255, 255, 0.65);
  --ring-text-main:  rgba(255, 255, 255, 0.95);
  --ring-text-sr:    #FFB36B;
}
* { font-family: var(--ff-font); }
.n-card { transition: transform .15s ease, box-shadow .15s ease; }

/* ===== sider 底部控件(桌面 sider / 移动抽屉 都复用这套) ===== */
.sider-foot {
  position: absolute;
  bottom: 14px;
  left: 0;
  right: 0;
  padding: 0 14px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}
.sider-controls {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
}
.sider-foot .n-select,
.drawer-foot .n-select { width: fit-content; min-width: 0; }
.sider-foot .n-base-selection .n-base-selection-label,
.sider-foot .n-base-selection .n-base-selection-input__content,
.drawer-foot .n-base-selection .n-base-selection-label,
.drawer-foot .n-base-selection .n-base-selection-input__content { text-align: center; }
.sider-foot .sider-privacy,
.drawer-foot .sider-privacy { text-align: center; }
.sider-privacy {
  font-size: 10px;
  line-height: 1.5;
  display: block;
  margin-top: 4px;
}

/* ===== 移动抽屉内部布局 ===== */
.drawer-head { padding: 0 0 14px 0; display: flex; align-items: center; gap: 10px; }
.drawer-foot { margin-top: 18px; padding: 16px 0 8px; display: flex; flex-direction: column; align-items: center; gap: 8px; border-top: 1px solid rgba(125,125,140,0.18); }
.drawer-foot-title { font-size: 11px; font-weight: 700; opacity: 0.55; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 2px; }

/* ===== 移动端内容区:顶部避让汉堡按钮 + 状态栏安全区,底部避让 FAB ===== */
.mobile-content {
  padding: calc(32px + env(safe-area-inset-top)) 12px calc(90px + env(safe-area-inset-bottom)) 12px;
}

/* (移动端底部 Tab 栏已移除,改由左上汉堡按钮打开抽屉) */

/* ===== 左上角汉堡按钮:替代原底部「更多」tab,仅移动端渲染 ===== */
.menu-fab {
  position: fixed;
  left: 28px;                                                 /* hero 卡距屏左 14 + 卡内 padding 14 = 28,贴 hero 卡左上内角 */
  top: calc(26px + env(safe-area-inset-top));                 /* 同上,卡内顶约 12 + 卡外 14 = 26 */
  z-index: 860;
  width: 32px;                                                /* 缩小一档,从 40 → 32 */
  height: 32px;
  border-radius: 50%;
  border: 1px solid rgba(125, 125, 140, 0.22);
  background: rgba(17, 20, 38, 0.72);
  -webkit-backdrop-filter: blur(10px);
  backdrop-filter: blur(10px);
  color: #e6e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 6px 18px -8px rgba(0, 0, 0, 0.5);
  transition: transform 0.12s ease, background 0.15s ease;
}
.menu-fab :deep(svg) { width: 18px; height: 18px; }
.menu-fab:active { transform: scale(0.9); }

/* ===== 悬浮记账按钮(核心记账流程一步呼起) ===== */
.fab {
  position: fixed;
  right: 18px;
  bottom: calc(18px + env(safe-area-inset-bottom));
  z-index: 850;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: none;
  background: var(--fire-grad-blue);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 10px 24px -6px rgba(91, 141, 239, 0.6);
  transition: transform 0.12s ease;
}
.fab:active { transform: scale(0.9); }

/* 卡片点击微反馈(提升触感) */
.n-card:active { transform: scale(0.99); }

/* 浅色主题:FAB 与汉堡按钮适配 */
.theme-light .menu-fab {
  background: rgba(255, 255, 255, 0.82);
  border-color: rgba(0, 0, 0, 0.10);
  color: #1a1a1a;
  box-shadow: 0 6px 18px -8px rgba(0, 0, 0, 0.25);
}
.theme-light .fab { box-shadow: 0 10px 24px -6px rgba(91, 141, 239, 0.4); }

/* ===== 移动端适配(≤768px)全局收尾 ===== */
@media (max-width: 768px) {
  .n-card { padding: 12px !important; }
  .n-statistic .n-statistic-value { font-size: 1.4rem !important; }
  .echarts-wrap,
  .chart-box,
  .n-card :deep(.echarts),
  .n-card :deep(canvas) {
    width: 100% !important;
    max-width: 100% !important;
  }
}

/* 新录入行高亮闪动(NDataTable rowProps 注入 class) */
.row-just-added > td {
  animation: rowFlash 1.6s ease;
}
@keyframes rowFlash {
  0% { background: rgba(54, 173, 106, 0.28); }
  100% { background: transparent; }
}
</style>