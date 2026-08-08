<script setup>
/**
 * F.I.R.E. Dashboard v2 — 设计感、视觉冲击、信息密度平衡
 *
 * 区段:
 *   1. Hero (欢迎语 + FIRE 进度环 + 关键元数据)
 *   2. 4 张渐变统计卡(净资产/FIRE目标/本月收入/本月支出)
 *   3. 投资账户区块(累计市值 / 累计浮盈 / 市值走势)
 *   4. 3 张核心图表(净资产走势 / 月度收支 / 支出结构)
 *   5. 现金流 + 投资盈亏走势
 *   6. 快捷入口
 */
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import dayjs from 'dayjs'
import {
  NCard, NGrid, NGi, NStatistic, NText, NSpace, NTag,
  NButton, NProgress
} from 'naive-ui'

import ChartBox from '@/components/ChartBox.vue'
import FireProgressRing from '@/components/FireProgressRing.vue'
import StreakGrid from '@/components/StreakGrid.vue'
import BadgesStrip from '@/components/BadgesStrip.vue'

import IconMoney from '@/components/icons/IconMoney.vue'
import IconRocket from '@/components/icons/IconRocket.vue'
import IconIncome from '@/components/icons/IconIncome.vue'
import IconExpense from '@/components/icons/IconExpense.vue'
import IconReminders from '@/components/icons/IconReminders.vue'
import IconBet from '@/components/icons/IconBet.vue'
import IconTrendUp from '@/components/icons/IconTrendUp.vue'
import IconTrendDown from '@/components/icons/IconTrendDown.vue'
import FireLogo from '@/components/icons/FireLogo.vue'

import { useAggregate } from '@/composables/aggregate'
import { useStreak } from '@/composables/streak'
import { useBadges } from '@/composables/badges'
import { useContracts } from '@/composables/contracts'
import { useAppStore } from '@/stores/app'
import { fmtCompact, fmtPct, fmtMoney } from '@/composables/format'

const { t, locale } = useI18n()
const router = useRouter()
const app = useAppStore()
const agg = useAggregate()
const {
  monthly, netWorthSeries, fireState,
  totalInvestValue, investPLTotal, cashFlowDelta
} = agg
const streak = useStreak()
const badges = useBadges(agg, streak)
const base = computed(() => app.baseCurrency)

// 当前语系下的紧凑货币(避免每个 fmtCompact 调用都重复传 locale)
const fmtL = (v, c) => fmtCompact(v, c, app.profile.locale)

// 月版:隐藏 Streak,改显「本月月结完成度」三格卡(动机替代)
const isMonthly = computed(() => app.profile.entryMode === 'monthly')
const curYm = dayjs().format('YYYY-MM')
const curMonth = computed(() => agg.monthly.value.find((m) => m.ym === curYm))
const incomeDone = computed(() => !!(curMonth.value && curMonth.value.totalIncome > 0))
const expenseDone = computed(() => !!(curMonth.value && curMonth.value.totalExpense > 0))
const snapDone = computed(() => app.db.snapshots.some((s) => s.yearMonth === curYm))
const allDone = computed(() => incomeDone.value && expenseDone.value && snapDone.value)
const monthlyBadges = computed(() => badges.value.filter((b) => b.id !== 'streak_6'))

// 自我对赌:仅展示活跃契约的迷你进度
const bets = useContracts()
const betViews = computed(() => bets.activeContracts.value.map((c) => ({ c, ev: bets.evaluate(c) })))
function betGoalLabel(c) {
  const map = { streak: t('bets.goalTypeStreak'), savingsRate: t('bets.goalTypeSavingsRate'), expenseCap: t('bets.goalTypeExpenseCap') }
  return map[c.goalType] || c.goalType
}
function betStatusKey(s) {
  return { onTrack: 'bets.statusOnTrack', atRisk: 'bets.statusAtRisk', won: 'bets.statusWon', lost: 'bets.statusLost' }[s] || s
}
function betStatusType(s) {
  return { onTrack: 'info', atRisk: 'warning', won: 'success', lost: 'error' }[s] || 'default'
}
function betStatusColor(s) {
  return { onTrack: '#5B8DEF', atRisk: '#FF8A3D', won: '#18a058', lost: '#E9533B' }[s] || '#5B8DEF'
}
function betCurrent(c, ev) {
  if (c.goalType === 'streak') return `${ev.current} ${t('bets.unitMonths')}`
  if (c.goalType === 'savingsRate') return `${ev.current.toFixed(1)}%`
  return fmtMoney(ev.current, base.value)
}
function betTarget(c) {
  if (c.goalType === 'streak') return `${Number(c.target)} ${t('bets.unitMonths')}`
  if (c.goalType === 'savingsRate') return `${Number(c.target).toFixed(1)}%`
  return fmtMoney(Number(c.target), base.value)
}
const fs = fireState
const statement = computed(() => app.profile.fireStatement || '')

const hasData = computed(() => monthly.value.length > 0)
const lastMonth = computed(
  () => monthly.value[monthly.value.length - 1] || {
    activeIncome: 0, passiveIncome: 0, investPL: 0,
    totalIncome: 0, totalExpense: 0, netCashFlow: 0
  }
)
// 展示月份:优先「当前月」,当前月无数据则回退到最后一个有数据月份。
// 否则当最后一个数据月份不是本月时(如有一笔更晚的净值快照),顶部会误显示 ¥0。
const displayMonth = computed(() => curMonth.value || lastMonth.value)

// === ChartBox 数据适配器 ============================================
const netWorthData = computed(() => ({
  x: netWorthSeries.value.map((d) => d.ym),
  series: [{
    key: 'net', label: t('dashboard.netAssets'), color: '#18a058',
    data: netWorthSeries.value.map((d) => Math.round(d.value))
  }]
}))

const incomeExpenseData = computed(() => ({
  x: monthly.value.map((m) => m.ym),
  series: [
    {
      key: 'income', label: t('dashboard.income'), color: '#5B8DEF',
      data: monthly.value.map((m) => Math.round(m.totalIncome))
    },
    {
      key: 'expense', label: t('dashboard.expense'), color: '#E9533B',
      data: monthly.value.map((m) => Math.round(m.totalExpense))
    }
  ]
}))

const expenseStructureData = computed(() => {
  const last = monthly.value[monthly.value.length - 1] || null
  if (!last) return { x: [], series: [] }
  return {
    x: [t('dashboard.dailyExpense')],
    series: [{
      key: 'expense', label: '', data: [Math.round(last.dailyExpense)]
    }]
  }
})

const investPLData = computed(() => ({
  x: monthly.value.map((m) => m.ym),
  series: [{
    key: 'pl', label: t('dashboard.investPL'), color: '#FF8A3D',
    data: monthly.value.map((m) => Math.round(m.investPL))
  }]
}))

const cashFlowData = computed(() => ({
  x: monthly.value.map((m) => m.ym),
  series: [{
    key: 'cf', label: t('dashboard.netCashFlow'), color: '#5B8DEF',
    data: monthly.value.map((m) => Math.round(m.netCashFlow))
  }]
}))

// === UI 杂项 ========================================================
const heroTags = computed(() => {
  const arr = []
  arr.push({
    text: `${t('common.thisMonth')} ${t('dashboard.netCashFlow')}: ${fmtMoney(displayMonth.value.netCashFlow, base.value)}`,
    type: displayMonth.value.netCashFlow >= 0 ? 'success' : 'error'
  })
  if (cashFlowDelta.value !== 0) {
    arr.push({
      text: `${t('common.change')} ${cashFlowDelta.value >= 0 ? '+' : ''}${fmtMoney(cashFlowDelta.value, base.value)}`,
      type: cashFlowDelta.value >= 0 ? 'success' : 'error'
    })
  }
  return arr
})

const langGreeting = computed(() => (locale.value.startsWith('zh') ? '你好' : 'Hello'))
const userName = computed(() => app.profile.name || '')
const etaText = computed(() => {
  if (fs.eta == null) return '∞'
  if (fs.eta < 1) return `~${Math.round(fs.eta * 12)} mo`
  return `${fs.eta.toFixed(1)} yr`
})
/* 本月净现金流(收入 - 支出),用于 hero 左列 chip */
const monthNet = computed(() => displayMonth.value.totalIncome - displayMonth.value.totalExpense)

const incomeTrendIsActive = computed(() => displayMonth.value.activeIncome >= displayMonth.value.passiveIncome)

// 财务自由度 = 近 12 月滚动 被动收入 / 主动收入 (口径:平滑单月奖金/分红/失业空窗)
const finFreedom = computed(() => {
  const ms = monthly.value
  if (!ms.length) return { pct: null, hasData: false }
  const last12 = ms.slice(-12)
  const passive = last12.reduce((s, m) => s + (m.passiveIncome || 0), 0)
  const active = last12.reduce((s, m) => s + (m.activeIncome || 0), 0)
  if (active <= 0) return { pct: null, hasData: true } // 失业/裸辞:主动=0 → 不硬算
  return { pct: passive / active, hasData: true }
})
// 财务自由度进度条分段:0–100% 橘色 #FF8A3D,>100% 溢出段红色 #E9533B,100% 刻度线
const ffBar = computed(() => {
  const pct = finFreedom.value.pct
  if (pct == null) return { display: '—', fillW: 0, overW: 0, color: '#FF8A3D' }
  const fillW = Math.min(pct, 1) * 100
  const overW = pct > 1 ? Math.min((pct - 1) * 100, 35) : 0 // 溢出段(封顶 35% 防裁切)
  const color = pct >= 1 ? '#E9533B' : '#FF8A3D'
  return { display: (pct * 100).toFixed(0) + '%', fillW, overW, color }
})
// 本月收入/支出 环比(用于 2×2 卡脚注「较上月」)
const prevMonth = computed(() => monthly.value[monthly.value.length - 2] || null)
const incomeMoM = computed(() => displayMonth.value.totalIncome - (prevMonth.value ? prevMonth.value.totalIncome : 0))
const expenseMoM = computed(() => displayMonth.value.totalExpense - (prevMonth.value ? prevMonth.value.totalExpense : 0))

function goTo(name) { router.push({ name }) }
function gotoRecord(type) {
  router.push({ name: type === 'in' ? 'income' : 'expense' })
}
</script>

<template>
  <div class="dash-wrap">
    <!-- HERO ============================================== -->
    <!-- 3 列紧凑横向并排:左 brand 4 行 / 中 储蓄率+预计达成 垂直居中 / 右 进度环+底部 chip
         整体 padding/gap 全面压缩,避免 hero 占满整个首屏。 -->
    <!-- HERO:桌面用 074de8e 昨天的结构;手机用今天的 round-8 紧凑三列。
         两者共存于 DOM,用 class 在断点切换显隐。 -->
    <!-- 桌面 Hero(截图:左 进度环 / 中 FIRE2FREE 水印 / 右 指标列) -->
    <section class="hero hero--desktop">
      <div class="hero-ring-col">
        <FireProgressRing
          :progress="fs.progress"
          :size="200"
          class="hero-ring-svg"
        />
      </div>

      <div class="hero-stats">
        <div class="hero-stats-top">
          <div class="hero-stat-item">
            <NText depth="3" class="hero-stat-label">{{ $t('dashboard.etaLabel') }}</NText>
            <div class="hero-stat-val">{{ etaText }}</div>
          </div>
          <div class="hero-stat-div"></div>
          <div class="hero-stat-item">
            <NText depth="3" class="hero-stat-label">{{ $t('dashboard.savingsRate') }}</NText>
            <div class="hero-stat-val hero-stat-val--sr">{{ fmtPct(fs.savingsRate || 0) }}</div>
          </div>
        </div>
        <div class="hero-ff-divider"></div>
        <div class="hero-ff">
          <div class="hero-ff-head">
            <span class="hero-ff-label">{{ $t('dashboard.finFreedom') }}</span>
            <span class="hero-ff-val" :style="{ color: ffBar.color }">{{ ffBar.display }}</span>
          </div>
          <div class="ff-bar">
            <div class="ff-bar-fill" :style="{ width: ffBar.fillW + '%' }"></div>
            <div v-if="ffBar.overW > 0" class="ff-bar-over" :style="{ left: '100%', width: ffBar.overW + '%' }"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- 手机 Hero(今天 round-8:brand | 储蓄率+预计达成 | ring+达成chip) -->
    <section class="hero hero--mobile">
      <!-- 左列:brand 4 行紧凑堆叠 + 净现金流 chip -->
      <div class="hero-left">
        <FireLogo :size="36" :show-wordmark="true" />
        <h1 class="hero-title">
          {{ langGreeting }}<span v-if="userName">, {{ userName }}</span>
        </h1>
        <p class="hero-sub">{{ $t('dashboard.greeting') }}</p>
        <div class="hero-cashflow">
          <span class="hero-cashflow-label">{{ $t('dashboard.thisMonthCashflow') }}</span>
          <span class="hero-cashflow-val" :class="monthNet >= 0 ? 'is-pos' : 'is-neg'">
            {{ monthNet >= 0 ? '+' : '' }}{{ fmtL(monthNet, base) }}
          </span>
        </div>
      </div>

      <!-- 中列:储蓄率 + 预计达成,垂直居中 -->
      <div class="hero-mid">
        <div class="hero-mid-item">
          <div class="hero-mid-label">{{ $t('dashboard.savingsRate') }}</div>
          <div class="hero-mid-val hero-mid-val--sr">{{ fmtPct(fs.savingsRate || 0) }}</div>
        </div>
        <div class="hero-mid-divider"></div>
        <div class="hero-mid-item">
          <div class="hero-mid-label">{{ $t('dashboard.etaLabel') }}</div>
          <div class="hero-mid-val">{{ etaText }}</div>
        </div>
      </div>

      <!-- 右列:进度环 + 底部蓝色 chip -->
      <div class="hero-ring">
        <FireProgressRing
          :progress="fs.progress"
          :size="200"
          class="hero-ring-svg"
        />
        <div class="hero-ring-chip">
          <span class="hero-ring-chip-label">{{ $t('dashboard.achieved') }}</span>
          <span class="hero-ring-chip-val">{{ fmtPct(fs.progress || 0) }}</span>
        </div>
      </div>
    </section>

    <!-- STAT CARDS:
         桌面(≥769px):4 张横排(净资产/年被动/月入/月出,无财务自由度)
         手机(≤768px):5 张 1+2+2(净资产全宽 + 财务自由度/年被动/月入/月出)
         财务自由度只在手机 2×2 出现;桌面放 Hero 里即可避免重复。
    -->
    <!-- 桌面 4 卡 -->
    <NGrid class="stat-row stat-row--desk" :cols="4" :x-gap="12" :y-gap="12">
      <NGi :span="1">
        <NCard size="small" class="stat-card stat-blue" :bordered="false">
          <div class="stat-icon"><IconMoney /></div>
          <NStatistic :label="`${$t('dashboard.netAssets')} (${base})`" :value="fmtL(fs.netAssets, base)" />
          <div class="stat-foot">{{ $t('dashboard.investAccountValue') }}: {{ fmtL(totalInvestValue, base) }}</div>
          <div class="stat-foot">{{ $t('dashboard.investGrowth') }}: {{ investPLTotal >= 0 ? '+' : '' }}{{ fmtL(investPLTotal, base) }}</div>
        </NCard>
      </NGi>
      <NGi :span="1">
        <NCard size="small" class="stat-card stat-violet" :bordered="false">
          <div class="stat-icon"><IconMoney /></div>
          <NStatistic
            :label="$t('dashboard.annualPassive')"
            :value="`${fs.annualReturn >= 0 ? '+' : ''}${fmtL(fs.annualReturn, base)}`"
          />
          <div class="stat-foot" :style="{ color: fs.annualReturn >= 0 ? '#E9533B' : '#18a058' }">
            {{ $t('dashboard.returnRate', { r: fmtPct(fs.returnRate) }) }}
          </div>
          <div class="stat-foot">
            {{ $t('dashboard.coverage') }} {{ fs.coverage === Infinity ? '∞' : fmtPct(fs.coverage) }}
          </div>
        </NCard>
      </NGi>
      <NGi :span="1">
        <NCard size="small" class="stat-card stat-green" :bordered="false">
          <div class="stat-icon">
            <IconTrendUp v-if="incomeTrendIsActive" />
            <IconTrendDown v-else />
          </div>
          <NStatistic :label="`${$t('common.thisMonth')} ${$t('dashboard.totalIncome')}`" :value="fmtL(displayMonth.totalIncome, base)" />
          <div class="stat-foot">{{ $t('dashboard.activeIncome') }}: {{ fmtL(displayMonth.activeIncome, base) }} · {{ $t('dashboard.passiveIncome') }}: {{ fmtL(displayMonth.passiveIncome, base) }}</div>
          <div class="stat-foot">{{ $t('dashboard.mom') }}: {{ incomeMoM >= 0 ? '+' : '' }}{{ fmtL(incomeMoM, base) }}</div>
        </NCard>
      </NGi>
      <NGi :span="1">
        <NCard size="small" class="stat-card stat-rose" :bordered="false">
          <div class="stat-icon"><IconExpense /></div>
          <NStatistic :label="`${$t('common.thisMonth')} ${$t('dashboard.totalExpense')}`" :value="fmtL(displayMonth.totalExpense, base)" />
          <div class="stat-foot">{{ $t('dashboard.expenseRatio') }}: {{ displayMonth.totalIncome > 0 ? fmtPct(displayMonth.totalExpense / displayMonth.totalIncome) : '—' }}</div>
          <div class="stat-foot">{{ $t('dashboard.mom') }}: {{ expenseMoM >= 0 ? '+' : '' }}{{ fmtL(expenseMoM, base) }}</div>
        </NCard>
      </NGi>
    </NGrid>

    <!-- 手机 5 卡(含财务自由度):CSS 在 ≤768px 强制 2 列 + :first-child 跨整行 -->
    <NGrid class="stat-row stat-row--mob" :cols="5" :x-gap="12" :y-gap="12" responsive="screen" item-responsive>
      <NGi :span="1">
        <NCard size="small" class="stat-card stat-blue" :bordered="false">
          <div class="stat-icon"><IconMoney /></div>
          <NStatistic :label="`${$t('dashboard.netAssets')} (${base})`" :value="fmtL(fs.netAssets, base)" />
          <div class="stat-foot">{{ $t('dashboard.investAccountValue') }}: {{ fmtL(totalInvestValue, base) }}</div>
          <div class="stat-foot">{{ $t('dashboard.investGrowth') }}: {{ investPLTotal >= 0 ? '+' : '' }}{{ fmtL(investPLTotal, base) }}</div>
        </NCard>
      </NGi>
      <!-- 财务自由度(手机 2×2 左上):青蓝渐变(避免与橘色进度条同色看不清) -->
      <NGi :span="1">
        <NCard size="small" class="stat-card stat-cyan" :bordered="false">
          <div class="stat-icon">⚖️</div>
          <NStatistic :label="$t('dashboard.finFreedom')" :value="ffBar.display" />
          <div class="ff-bar ff-bar--card">
            <div class="ff-bar-fill" :style="{ width: ffBar.fillW + '%' }"></div>
            <div v-if="ffBar.overW > 0" class="ff-bar-over" :style="{ left: '100%', width: ffBar.overW + '%' }"></div>
          </div>
        </NCard>
      </NGi>
      <NGi :span="1">
        <NCard size="small" class="stat-card stat-violet" :bordered="false">
          <div class="stat-icon">⚖️</div>
          <NStatistic
            :label="$t('dashboard.annualPassive')"
            :value="`${fs.annualReturn >= 0 ? '+' : ''}${fmtL(fs.annualReturn, base)}`"
          />
          <div class="stat-foot" :style="{ color: fs.annualReturn >= 0 ? '#E9533B' : '#18a058' }">
            {{ $t('dashboard.returnRate', { r: fmtPct(fs.returnRate) }) }}
          </div>
          <div class="stat-foot">
            {{ $t('dashboard.coverage') }} {{ fs.coverage === Infinity ? '∞' : fmtPct(fs.coverage) }}
          </div>
        </NCard>
      </NGi>
      <NGi :span="1">
        <NCard size="small" class="stat-card stat-green" :bordered="false">
          <div class="stat-icon">
            <IconTrendUp v-if="incomeTrendIsActive" />
            <IconTrendDown v-else />
          </div>
          <NStatistic :label="`${$t('common.thisMonth')} ${$t('dashboard.totalIncome')}`" :value="fmtL(displayMonth.totalIncome, base)" />
          <div class="stat-foot">{{ $t('dashboard.activeIncome') }}: {{ fmtL(displayMonth.activeIncome, base) }} · {{ $t('dashboard.passiveIncome') }}: {{ fmtL(displayMonth.passiveIncome, base) }}</div>
          <div class="stat-foot">{{ $t('dashboard.mom') }}: {{ incomeMoM >= 0 ? '+' : '' }}{{ fmtL(incomeMoM, base) }}</div>
        </NCard>
      </NGi>
      <NGi :span="1">
        <NCard size="small" class="stat-card stat-rose" :bordered="false">
          <div class="stat-icon"><IconExpense /></div>
          <NStatistic :label="`${$t('common.thisMonth')} ${$t('dashboard.totalExpense')}`" :value="fmtL(displayMonth.totalExpense, base)" />
          <div class="stat-foot">{{ $t('dashboard.expenseRatio') }}: {{ displayMonth.totalIncome > 0 ? fmtPct(displayMonth.totalExpense / displayMonth.totalIncome) : '—' }}</div>
          <div class="stat-foot">{{ $t('dashboard.mom') }}: {{ expenseMoM >= 0 ? '+' : '' }}{{ fmtL(expenseMoM, base) }}</div>
        </NCard>
      </NGi>
    </NGrid>

    <!-- QUICK ACTIONS:桌面 4 按钮(074de8e)/ 手机 2 按钮(今天 round-8) 双布局 -->
    <!-- 桌面:4 个入口(记一笔收入/支出/FIRE计算器/提醒中心) -->
    <section class="section section-quick quick--desktop">
      <div class="section-head">
        <div class="section-title">
          <span>⚡ {{ $t('dashboard.quickActions') }}</span>
        </div>
      </div>
      <div class="quick-row">
        <NButton class="qa-dbtn qa-income" size="large" round tertiary @click="gotoRecord('in')">
          <template #icon><IconIncome :size="18" /></template>
          {{ $t('dashboard.addIncome') }}
        </NButton>
        <NButton class="qa-dbtn qa-expense" size="large" round tertiary @click="gotoRecord('out')">
          <template #icon><IconExpense :size="18" /></template>
          {{ $t('dashboard.addExpense') }}
        </NButton>
        <NButton class="qa-dbtn qa-calc" size="large" round tertiary @click="goTo('calculator')">
          <template #icon><IconRocket :size="18" /></template>
          {{ $t('nav.calculator') }}
        </NButton>
        <NButton class="qa-dbtn qa-remind" size="large" round tertiary @click="goTo('reminders')">
          <template #icon><IconReminders :size="18" /></template>
          {{ $t('nav.reminders') }}
        </NButton>
      </div>
    </section>

    <!-- 手机:标题"快捷入口" + FIRE计算器 + 提醒中心 同一行横排,紧凑 chip -->
    <section class="section section-quick quick--mobile">
      <div class="quick-bar">
        <div class="quick-title"><span class="quick-emoji">⚡</span>{{ $t('dashboard.quickActions') }}</div>
        <button class="qa-btn qa-calc" type="button" @click="goTo('calculator')">
          <IconRocket :size="18" />
          <span class="qa-label">{{ $t('nav.calculator') }}</span>
        </button>
        <button class="qa-btn qa-remind" type="button" @click="goTo('reminders')">
          <IconReminders :size="18" />
          <span class="qa-label">{{ $t('nav.reminders') }}</span>
        </button>
      </div>
    </section>

    <!-- GAMIFICATION / MONTH PROGRESS =================== -->
    <section class="section">
      <div class="section-head">
        <div class="section-title">
          <span>🎯 {{ isMonthly ? $t('dashboard.monthlyProgress.title') : ($t('streak.title') + ' & ' + $t('badges.title')) }}</span>
        </div>
        <NButton size="small" tertiary @click="goTo('report')">{{ $t('report.title') }} →</NButton>
      </div>

      <template v-if="isMonthly">
        <div class="mp-grid">
          <div class="mp-cell" :class="incomeDone ? 'mp-done' : 'mp-pending'" @click="goTo('income')">
            <div class="mp-label">{{ $t('dashboard.monthlyProgress.income') }}</div>
            <div class="mp-state">{{ incomeDone ? ('✓ ' + $t('dashboard.monthlyProgress.done')) : $t('dashboard.monthlyProgress.pending') }}</div>
          </div>
          <div class="mp-cell" :class="expenseDone ? 'mp-done' : 'mp-pending'" @click="goTo('expense')">
            <div class="mp-label">{{ $t('dashboard.monthlyProgress.expense') }}</div>
            <div class="mp-state">{{ expenseDone ? ('✓ ' + $t('dashboard.monthlyProgress.done')) : $t('dashboard.monthlyProgress.pending') }}</div>
          </div>
          <div class="mp-cell" :class="snapDone ? 'mp-done' : 'mp-pending'" @click="goTo('invest')">
            <div class="mp-label">{{ $t('dashboard.monthlyProgress.snapshot') }}</div>
            <div class="mp-state">{{ snapDone ? ('✓ ' + $t('dashboard.monthlyProgress.done')) : $t('dashboard.monthlyProgress.pending') }}</div>
          </div>
        </div>
        <p v-if="allDone" class="mp-alldone">{{ $t('dashboard.monthlyProgress.allDone') }}</p>
        <BadgesStrip :badges="monthlyBadges" />
      </template>
      <template v-else>
        <StreakGrid :streak="streak" style="margin-bottom: 14px" />
        <BadgesStrip :badges="badges" />
      </template>
    </section>

    <!-- COMMITMENT CONTRACTS ============================== -->
    <section v-if="betViews.length" class="section">
      <div class="section-head">
        <div class="section-title">
          <IconBet :size="20" class="section-icon" />
          <span>{{ $t('bets.title') }}</span>
        </div>
        <NButton size="small" tertiary @click="goTo('bets')">{{ $t('bets.title') }} →</NButton>
      </div>
      <div class="bet-mini-list">
        <div v-for="bv in betViews" :key="bv.c.id" class="bet-mini">
          <div class="bet-mini-top">
            <span class="bet-mini-goal">{{ betGoalLabel(bv.c) }}</span>
            <NTag size="small" :type="betStatusType(bv.ev.status)">{{ $t(betStatusKey(bv.ev.status)) }}</NTag>
          </div>
          <NProgress
            type="line"
            :percentage="Math.round(bv.ev.progress * 100)"
            :show-indicator="false"
            :height="6"
            :color="betStatusColor(bv.ev.status)"
            style="margin: 6px 0 4px"
          />
          <div class="bet-mini-foot">
            <strong>{{ betCurrent(bv.c, bv.ev) }}</strong>
            <span class="bet-sep"> / </span>
            <span>{{ betTarget(bv.c) }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- CORE CHARTS ======================================== -->
    <section class="section">
      <div class="section-head">
        <div class="section-title">
          <span>📊 {{ $t('dashboard.coreTrend') }}</span>
        </div>
      </div>
      <div class="charts-grid">
        <ChartBox
          :title="$t('dashboard.netWorthTrend')"
          :data="netWorthData"
          :types="['line', 'bar']"
          :default-type="'line'"
          :format-value="(v) => fmtL(v, base)"
        />
        <ChartBox
          :title="$t('dashboard.incomeExpense')"
          :data="incomeExpenseData"
          :types="['bar', 'line']"
          :default-type="'bar'"
          :format-value="(v) => fmtL(v, base)"
        />
        <ChartBox
          :title="$t('dashboard.expenseStructure')"
          :data="expenseStructureData"
          :types="['pie', 'bar']"
          :default-type="'pie'"
          :format-value="(v) => fmtL(v, base)"
        />
      </div>
    </section>

    <!-- TREND CHARTS ======================================= -->
    <section class="section">
      <div class="charts-grid two-cols">
        <ChartBox
          :title="$t('dashboard.monthlyCashFlow')"
          :data="cashFlowData"
          :types="['bar', 'line']"
          :default-type="'bar'"
          :format-value="(v) => fmtL(v, base)"
        />
        <ChartBox
          :title="$t('dashboard.investPLTrend')"
          :data="investPLData"
          :types="['bar', 'line']"
          :default-type="'bar'"
          :format-value="(v) => fmtL(v, base)"
        />
      </div>
    </section>
  </div>
</template>

<style scoped>
.dash-wrap { display: flex; flex-direction: column; gap: 12px; }

/* === HERO ============================================== */
/* 3 列横向并排:[左 brand 4 行][中 储蓄率+预计达成][右 进度环+底部 chip]
   整体紧凑上移,无大留白。 */
/* base = 桌面(>768px) 布局:今早改前的 3 列(brand | 中 | ring) + space-between。
   新的紧凑三列 + 净现金流chip + 达成chip 只在 @media(max-width:768px) 生效,
   避免改动漏到桌面。 */
/* === HERO 双布局:桌面=074de8e 昨天样子 / 手机=今天 round-8 ===
   .hero--desktop 仅 >768px 显示;.hero--mobile 仅 ≤768px 显示。
   储蓄率桌面用品牌橙(非绿,满足"不用绿色"规则)。 */

/* ---- 桌面 Hero(截图:左 进度环 / 中 FIRE2FREE 水印 / 右 指标列) ---- */
.hero--desktop {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 26px 32px;
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(255,200,87,0.10), rgba(233,83,59,0.05) 60%, rgba(91,141,239,0.08));
  border: 1px solid rgba(125,125,140,0.18);
  overflow: hidden;
  min-height: 220px;
}
.hero--desktop::before {
  content: 'FIRE2FREE';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 150px;
  font-weight: 900;
  letter-spacing: 8px;
  background: linear-gradient(135deg, rgba(255,138,61,0.12), rgba(123,97,255,0.10));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  pointer-events: none;
  user-select: none;
  z-index: 0;
  white-space: nowrap;
}
.hero--desktop .hero-ring-col { z-index: 1; display: flex; flex-direction: column; align-items: center; gap: 10px; flex-shrink: 0; }
.hero--desktop .hero-ring-svg { display: block; }
.hero--desktop .hero-stats { z-index: 1; display: flex; flex-direction: column; gap: 14px; align-items: stretch; flex-shrink: 0; width: 260px; }
.hero--desktop .hero-stats-top { display: flex; align-items: center; justify-content: space-between; gap: 18px; width: 100%; }
.hero--desktop .hero-stat-item { text-align: center; }
.hero--desktop .hero-stat-label { font-size: 11px; opacity: 0.7; }
.hero--desktop .hero-stat-val { font-size: 18px; font-weight: 700; margin-top: 2px; }
.hero--desktop .hero-stat-val--sr { color: #FF8A3D; }
.hero--desktop .hero-stat-div { width: 1px; height: 34px; background: rgba(125,125,140,0.3); }
.hero--desktop .hero-ff-divider { width: 100%; height: 1px; background: rgba(125,125,140,0.25); }
.hero--desktop .hero-ff { display: flex; flex-direction: column; gap: 6px; width: 100%; }
.hero--desktop .hero-ff-head { display: flex; align-items: baseline; justify-content: space-between; }
.hero--desktop .hero-ff-label { font-size: 12px; opacity: 0.75; }
.hero--desktop .hero-ff-val { font-size: 18px; font-weight: 800; font-variant-numeric: tabular-nums; }

/* 财务自由度进度条(橘 0–100% / 红溢出 + 100% 刻度) */
.ff-bar {
  position: relative;
  height: 6px;
  border-radius: 999px;
  background: rgba(125,125,140,0.18);
  margin-top: 6px;
  overflow: visible;
}
.ff-bar-fill { position: absolute; left: 0; top: 0; height: 100%; border-radius: 999px; background: #FF8A3D; }
.ff-bar-over { position: absolute; top: 0; height: 100%; border-radius: 999px; background: #E9533B; }
.ff-tick { position: absolute; top: -3px; left: 100%; width: 1px; height: 12px; background: rgba(125,125,140,0.55); }
.ff-tick-label { position: absolute; top: 11px; left: 100%; transform: translateX(-50%); font-size: 9px; opacity: 0.6; font-variant-numeric: tabular-nums; }
.ff-bar--card { margin-top: 10px; }

/* 平板:桌面 hero 改为纵向居中 */
@media (max-width: 1024px) and (min-width: 769px) {
  .hero--desktop { flex-direction: column; gap: 18px; }
  .hero--desktop .hero-stats { width: 100%; max-width: 320px; }
}

/* ---- 手机 Hero(今天 round-8 紧凑三列) ---- */
.hero--mobile {
  display: none;
  position: relative;
  grid-template-columns: minmax(0, 1fr) auto auto;
  align-items: center;
  gap: 8px 12px;
  padding: 4px 10px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(255,200,87,0.10), rgba(233,83,59,0.05) 60%, rgba(91,141,239,0.08));
  border: 1px solid rgba(125,125,140,0.18);
  overflow: hidden;
}
.hero--mobile .hero-left {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.hero--mobile .hero-left .fire-logo { flex-shrink: 0; min-width: max-content; margin-bottom: 2px; }
.hero--mobile .hero-title {
  font-size: 1rem;
  font-weight: 800;
  margin: 2px 0 0;
  background: linear-gradient(90deg, #FF8A3D 0%, #E9533B 60%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  line-height: 1.15;
}
.hero--mobile .hero-sub { font-size: 11px; margin: 0; opacity: 0.7; line-height: 1.4; }
.hero--mobile .hero-cashflow {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  padding: 3px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  width: fit-content;
  background: rgba(24,160,88,0.14);
  color: #18a058;
}
.hero--mobile .hero-cashflow.is-neg { background: rgba(233,83,59,0.14); color: #E9533B; }
.theme-dark .hero--mobile .hero-cashflow { background: rgba(24,160,88,0.22); color: #4fcf8e; }
.theme-dark .hero--mobile .hero-cashflow.is-neg { background: rgba(233,83,59,0.22); color: #ff7a5c; }
.hero--mobile .hero-cashflow-label { opacity: 0.85; }
.hero--mobile .hero-cashflow-val { font-variant-numeric: tabular-nums; }
.hero--mobile .hero-mid {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-width: 64px;
}
.hero--mobile .hero-mid-item { text-align: center; display: flex; flex-direction: column; align-items: center; gap: 0; }
.hero--mobile .hero-mid-label { font-size: 10px; opacity: 0.65; letter-spacing: 0.3px; }
.hero--mobile .hero-mid-val { font-size: 15px; font-weight: 800; font-variant-numeric: tabular-nums; color: var(--text-color, #1a1a1a); line-height: 1.2; }
.hero--mobile .hero-mid-val--sr { color: var(--ring-text-sr, #FF8A3D); }
.hero--mobile .hero-mid-divider { width: 36px; height: 1px; background: rgba(125,125,140,0.3); }
.hero--mobile .hero-ring { display: flex; flex-direction: column; align-items: center; gap: 2px; justify-self: end; }
.hero--mobile .hero-ring-svg { display: block; transform: scale(0.55); transform-origin: center center; }
.hero--mobile .hero-ring-chip {
  margin-top: -8px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 600;
  background: linear-gradient(135deg, #5B8DEF, #7B61FF);
  color: #fff;
  white-space: nowrap;
}
.hero--mobile .hero-ring-chip-label { opacity: 0.92; }
.hero--mobile .hero-ring-chip-val { font-variant-numeric: tabular-nums; }

/* 断点切换:≤768 显手机 hero,隐藏桌面 hero */
@media (max-width: 768px) {
  .hero--desktop { display: none !important; }
  .hero--mobile { display: grid !important; }
  /* 手机版:中列(储蓄率/预计达成)右移 93px 贴环(距环视觉左沿 5px);进度环右移 41px 保持右贴边 */
  .hero--mobile .hero-mid { transform: translate(93px, 3px); }
  .hero--mobile .hero-ring { transform: translateX(41px); }
}
@media (max-width: 480px) {
  .hero--mobile .hero-title { font-size: 0.95rem !important; }
  .hero--mobile .hero-mid-val { font-size: 14px; }
  .hero--mobile .hero-cashflow-label { display: none; }
  .hero--mobile .hero-cashflow { padding: 3px 8px; font-size: 11px; }
  .hero--mobile .hero-left { min-width: 0; }
  .hero--mobile .hero-ring-svg { transform: scale(0.45); transform-origin: center center; }
}

.stat-row { margin-top: 4px; }
/* 默认(桌面):只显桌面 4 卡,手机 5 卡隐藏(NGrid 自带 display:grid,
   优先级高于普通选择器,需 !important 覆盖) */
.stat-row--mob { display: none !important; }
.stat-card {
  position: relative; color: #fff; overflow: hidden;
  border-radius: 14px; padding: 4px; height: 100%;
}
.stat-card :deep(.n-card__content) { padding: 18px 18px 14px; }
.stat-card :deep(.n-statistic .n-statistic__label) { color: rgba(255,255,255,0.82); font-size: 12px; letter-spacing: 0.4px; }
.stat-card :deep(.n-statistic .n-statistic-value__content) { color: #fff; font-size: 26px; font-weight: 800; }
.stat-card .stat-icon {
  position: absolute; top: 12px; right: 12px;
  width: 32px; height: 32px; border-radius: 10px;
  background: rgba(255,255,255,0.18);
  display: flex; align-items: center; justify-content: center; color: #fff;
}
.stat-card .stat-foot { font-size: 11px; margin-top: 6px; opacity: 0.85; display: flex; align-items: center; gap: 4px; }
.stat-blue { background: var(--fire-grad-blue); }
.stat-gold { background: var(--fire-grad-primary); }
.stat-green { background: var(--fire-grad-green); }
.stat-rose { background: var(--fire-grad-rose); }
.stat-violet { background: var(--fire-grad-violet); }
.stat-cyan { background: linear-gradient(135deg, #06b6d4 0%, #0e7490 100%); }

.section {
  display: flex; flex-direction: column; gap: 10px; padding: 16px;
  background: rgba(125,125,140,0.04);
  border: 1px solid rgba(125,125,140,0.12);
  border-radius: 14px;
}
.section-head { display: flex; align-items: center; justify-content: space-between; }
.section-title { display: inline-flex; align-items: center; gap: 8px; font-size: 15px; font-weight: 700; }
.section-icon { color: #FF8A3D; }
.section-empty { padding: 24px; text-align: center; }

.charts-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
.charts-grid.two-cols { grid-template-columns: 1fr 1fr; }
@media (max-width: 900px) {
  .charts-grid, .charts-grid.two-cols { grid-template-columns: 1fr; }
}

/* 移动端适配(≤768px):sider 已自动收起(App.vue 监听 resize),
   这里进一步压缩 hero / stat-card / section 的内边距与字号,
   并把 bet-mini-list 改为单列避免横向溢出。 */
@media (max-width: 768px) {
  /* hero 排版在前面 @media(max-width:768px) 已设置(3 列→手机 2 行 brand|ring + mid 跨行),
     这里不重复覆盖,避免冲突。 */

  /* FIRE 目标卡片脚注(月支出 × 倍数)手机版 nowrap */
  .stat-card .stat-foot {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  /* 移动端适配(≤768px):
     强行把 NGrid 的 grid-template-columns 改成 2 列(覆盖默认 5 列),
     第一张(NGi:first-child)跨 1/-1 占整行 = 1+2+2 主+副卡布局:
       ┌───────────────────────┐
       │   净资产  ¥257.8万   │  (主卡)
       ├───────────┬───────────┤
       │ FIRE目标  │ 本月收入  │
       ├───────────┼───────────┤
       │ 本月支出  │ 年被动收益 │  (4 张副卡 2×2)
       └───────────┴───────────┘
     数字都可以完整显示(主卡 ~316px 宽,副卡 ~152px 宽)。
     5 横排硬塞在 326px 里数字物理截字严重,这个布局是极限下的最优解。 */
  /* hero 排版在前面 @media(max-width:768px) 已设置(3 列→手机 2 行 brand|ring + mid 跨行),
     这里不重复覆盖,避免冲突。 */

  /* 桌面 4 卡隐藏,手机 5 卡显示(1+2+2 布局) */
  .stat-row--desk { display: none !important; }
  .stat-row--mob {
    display: grid !important;
    grid-template-columns: 1fr 1fr !important;
  }
  .stat-row--mob > :first-child {
    grid-column: 1 / -1 !important;
  }
  /* 关键:覆盖 NGrid item-responsive 给各 NGi 算出的不等宽 inline span,
     强制 4 张副卡各占 1 列 = 严格等宽 */
  .stat-row--mob > :not(:first-child) {
    grid-column: span 1 !important;
    min-width: 0;
  }

  /* 主卡(首张 = 净资产):xs 满宽,接近桌面样式 */
  .stat-row--mob > :first-child .stat-card :deep(.n-card__content) { padding: 14px !important; }
  .stat-row--mob > :first-child .stat-card :deep(.n-statistic-value__content) {
    font-size: 22px !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .stat-row--mob > :first-child .stat-card :deep(.n-statistic .n-statistic__label) {
    font-size: 11px !important;
  }
  .stat-row--mob > :first-child .stat-card .stat-icon { width: 28px; height: 28px; top: 10px; right: 10px; }
  .stat-row--mob > :first-child .stat-card .stat-foot { font-size: 10.5px; margin-top: 4px; }

  /* 副卡(其余 4 张):xs 半宽,紧凑样式;放开 nowrap 让脚注(主动/被动收入)自然换行 */
  .stat-row--mob > :not(:first-child) .stat-card :deep(.n-card__content) { padding: 12px 10px 10px !important; }
  .stat-row--mob > :not(:first-child) .stat-card :deep(.n-statistic-value__content) {
    font-size: 15px !important;
    white-space: normal;
    word-break: break-word;
    line-height: 1.2;
  }
  .stat-row--mob > :not(:first-child) .stat-card :deep(.n-statistic .n-statistic__label) {
    font-size: 10.5px !important;
    white-space: normal;
    margin-bottom: 2px !important;
    line-height: 1.2;
  }
  .stat-row--mob > :not(:first-child) .stat-card .stat-icon { width: 22px; height: 22px; top: 6px; right: 6px; }
  .stat-row--mob > :not(:first-child) .stat-card .stat-foot {
    display: block !important;
    font-size: 10px !important;
    white-space: normal;
    word-break: break-word;
    margin-top: 4px !important;
    line-height: 1.4;
  }

  .section { padding: 12px !important; }
  .section-title { font-size: 14px; }
  .bet-mini-list { grid-template-columns: 1fr; }

  /* 快捷入口:切换桌面/手机 + 手机栏缩小字号防挤压 */
  .quick--desktop { display: none !important; }
  .quick--mobile { display: flex !important; }
  .quick--mobile.section-quick { padding: 12px 16px !important; }
  .quick--mobile .quick-bar { gap: 8px !important; }
  .quick--mobile .quick-title { font-size: 13px !important; }
  .quick--mobile .qa-btn { padding: 7px 8px !important; gap: 4px !important; font-size: 11px !important; }
  .quick--mobile .qa-label { font-size: 11px !important; }
}

/* iPhone SE 等 ≤480px 极窄屏:副卡数字再缩一档 */
@media (max-width: 480px) {
  .stat-row--mob > :not(:first-child) .stat-card :deep(.n-card__content) { padding: 10px 8px 8px !important; }
  .stat-row--mob > :not(:first-child) .stat-card :deep(.n-statistic-value__content) { font-size: 14px !important; }
  .stat-row--mob > :not(:first-child) .stat-card .stat-foot { font-size: 9.5px !important; }
}

/* 快捷入口:桌面 4 按钮(074de8e)/ 手机 2 按钮(今天 round-8) 双布局 */
.section-quick { padding: 16px !important; }
/* 桌面快捷:默认显示;手机隐藏 */
.quick--desktop { display: flex; }
/* 手机快捷:桌面隐藏;手机显示 */
.quick--mobile { display: none; }
.quick-row { display: flex; flex-wrap: wrap; gap: 10px; }
.qa-dbtn { padding: 6px 18px; font-weight: 600; }

/* 手机快捷栏:标题 + 2 按钮 同行横排 */
.quick-bar {
  display: flex;
  align-items: center;
  gap: 10px;
}
.quick-title {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  font-weight: 700;
}
.quick-emoji { font-size: 14px; }
/* 手机按钮:横排 icon+文字 的紧凑 chip */
.quick--mobile .qa-btn {
  flex: 1 1 0;
  display: inline-flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-width: 0;
  padding: 8px 10px;
  border: 1px solid rgba(125,125,140,0.18);
  background: rgba(125,125,140,0.04);
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.12s ease, box-shadow 0.15s ease, border-color 0.15s ease, background 0.15s ease;
  color: inherit;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.quick--mobile .qa-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 16px -8px rgba(125,125,140,0.3); background: rgba(125,125,140,0.08); }
.quick--mobile .qa-btn:active { transform: scale(0.97); }
.quick--mobile .qa-btn :deep(svg) { flex-shrink: 0; }
.quick--mobile .qa-label { font-size: 12px; line-height: 1.2; overflow: hidden; text-overflow: ellipsis; }
.qa-calc { color: #FF8A3D; }
.qa-remind { color: #18a058; }
.qa-bet { color: #7B61FF; }
.qa-report { color: #5B8DEF; }

.bet-mini-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
}
.bet-mini {
  padding: 12px 14px;
  border-radius: 10px;
  background: rgba(125,125,140,0.05);
  border: 1px solid rgba(125,125,140,0.12);
}
.bet-mini-top { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.bet-mini-goal { font-weight: 700; font-size: 13px; }
.bet-mini-foot { font-size: 11px; opacity: 0.78; }
.bet-sep { opacity: 0.5; }
.qa-income { color: #5B8DEF; }
.qa-expense { color: #E9533B; }
.qa-calc { color: #FF8A3D; }
.qa-remind { color: #18a058; }

.mp-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.mp-cell {
  cursor: pointer;
  border-radius: 12px;
  padding: 16px 14px;
  background: rgba(125, 125, 140, 0.06);
  border: 1.5px solid rgba(125, 125, 140, 0.18);
  transition: transform 0.15s ease, border-color 0.15s ease;
}
.mp-cell:hover { transform: translateY(-3px); }
.mp-label { font-size: 13px; font-weight: 700; margin-bottom: 8px; }
.mp-state { font-size: 12.5px; }
.mp-done { border-color: rgba(24, 160, 88, 0.55); }
.mp-done .mp-state { color: #18a058; font-weight: 700; }
.mp-pending { border-color: rgba(255, 138, 61, 0.5); }
.mp-pending .mp-state { color: #FF8A3D; }
.mp-alldone { margin: 12px 0 0; font-size: 13px; font-weight: 700; color: #18a058; }
@media (max-width: 640px) { .mp-grid { grid-template-columns: 1fr; } }
</style>
