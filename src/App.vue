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
}

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

// 侧边栏折叠:用户可手动 toggle(show-trigger 触发),初次按窗口宽度默认
// 窗口 resize 时:小屏(≤768)强制收起(避免 sider 把手机内容压扁),
// 大屏不强制改(让用户掌控手动 toggle)。
const collapsed = ref(typeof window !== 'undefined' ? window.innerWidth <= 768 : false)
function syncCollapsedToViewport() {
  if (window.innerWidth <= 768) collapsed.value = true
}
onMounted(() => {
  syncCollapsedToViewport()
  window.addEventListener('resize', syncCollapsedToViewport)
})
onUnmounted(() => {
  window.removeEventListener('resize', syncCollapsedToViewport)
})

// 全局自动结算自我对赌:应用启动即把达标契约落为 won(数据一致性),
// 新赢的 id 暂存到 sessionWins,Bets 页挂载时取走弹庆祝(避免漏庆祝)。
// ⚠️ 必须在 setup 同步调用(不能放 onMounted):Vue 中子组件 onMounted 先于父组件执行,
// 若放 onMounted,Bets 的 takeSessionWins() 会早于此处推入赢家 → 取到空 → 庆祝不弹。
const { autoResolve } = useContracts()
autoResolve()
</script>

<template>
  <NConfigProvider :theme="theme" :locale="naiveLocale" :date-locale="naiveDateLocale">
    <NMessageProvider>
      <NNotificationProvider>
        <NDialogProvider>
          <SaveFxLayer />
          <Onboarding v-if="needsOnboarding" />
          <NLayout v-else has-sider style="height: 100vh">
            <NLayoutSider
              bordered
              :collapsed-width="64"
              :width="232"
              v-model:collapsed="collapsed"
              show-trigger
              collapse-mode="width"
            >
              <div style="padding: 18px 14px 14px 14px; display: flex; align-items: center; gap: 10px">
                <FireLogo :size="collapsed ? 36 : 81" :show-wordmark="!collapsed" />
              </div>
              <NMenu
                :value="activeKey"
                :options="menuOptions"
                :render-label="(opt) => h('div', { style: 'display:inline-flex;align-items:center;gap:10px' }, [opt.iconRender(), h('span', {}, opt.label)])"
                @update:value="handleMenu"
                style="padding-top: 6px"
              />
              <div class="sider-foot">
                <!-- 语系 / 主题切换:两个 NSelect 横向并排(居中+gap),
                     隐私文字独立一行;浮层 z-index 在 menu-props 显式给以穿透 stacking context。 -->
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
              <!-- 顶部 banner 已移除:页面直接占满视口,不再有 60px 偏移 -->
              <NLayoutContent content-style="padding: 20px; overflow: auto" style="height: 100vh">
                <RouterView />
              </NLayoutContent>
            </NLayout>
          </NLayout>
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
}
.n-card { transition: transform .15s ease, box-shadow .15s ease; }

/* sider 底部控件栏:整体竖排,内部 .sider-controls 横向并排放两个 select;
   各 select 仍走 fit-content(不撑满);浮层 z-index 已在 menu-props 显式给。 */
.sider-foot {
  position: absolute;
  bottom: 14px;
  left: 0;
  right: 0;
  padding: 0 14px;
  display: flex;
  flex-direction: column;
  align-items: center;       /* 子层整体水平居中 */
  gap: 6px;
}
.sider-controls {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 8px;                  /* 两 select 之间间距 */
  flex-wrap: wrap;           /* 极窄时换行,避免溢出 */
}
.sider-foot .n-select {
  width: fit-content;        /* 跟随内容宽度,避免空荡拉伸 */
  min-width: 0;
}
.sider-foot .n-base-selection .n-base-selection-label,
.sider-foot .n-base-selection .n-base-selection-input__content {
  text-align: center;        /* 选中文字水平居中 */
}
.sider-foot .sider-privacy { text-align: center; }
.sider-privacy {
  font-size: 10px;
  line-height: 1.5;
  display: block;
  margin-top: 4px;
}

/* ====== 移动端适配(≤768px):让手机端排版正常 ======
   关键点:
   - sider 默认 64px(由 collapsed 双向绑定 + resize 监听保证)
   - 内容区 / 卡片 padding 收紧(腾出水平空间)
   - 数字 / 标题字号缩小(避免 ¥ 大数溢出)
   - ECharts 容器防溢出
   Dashboard 自身的 .hero/.hero-title 等由它自己 <style scoped> 末尾的媒体查询覆盖。 */
@media (max-width: 768px) {
  .n-layout-content { padding: 12px !important; }
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
