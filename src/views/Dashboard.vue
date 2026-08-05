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

const incomeTrendIsActive = computed(() => displayMonth.value.activeIncome >= displayMonth.value.passiveIncome)

function goTo(name) { router.push({ name }) }
function gotoRecord(type) {
  router.push({ name: type === 'in' ? 'income' : 'expense' })
}
</script>

<template>
  <div class="dash-wrap">
    <!-- HERO ============================================== -->
    <section class="hero">
      <div class="hero-greeting">
        <NText depth="2" style="font-size: 12px; letter-spacing: 1.2px; text-transform: uppercase; opacity: 0.7">
          {{ $t('app.title') }}
        </NText>
        <h1 class="hero-title">
          {{ langGreeting }}<span v-if="userName">, {{ userName }}</span>
        </h1>
        <p class="hero-sub">{{ $t('dashboard.greeting') }}</p>
        <p v-if="statement" class="hero-statement">“{{ statement }}”</p>
        <NSpace size="small" style="margin-top: 14px" :wrap="true">
          <NTag v-for="(tag, i) in heroTags" :key="i" :type="tag.type" round size="small">{{ tag.text }}</NTag>
        </NSpace>
      </div>

      <div class="hero-ring">
        <FireProgressRing
          :progress="fs.progress"
          :target="fs.target"
          :net-assets="fs.netAssets"
          :eta="fs.eta"
          :base-currency="base"
          :size="220"
        />
      </div>

      <div class="hero-meta">
        <div class="hero-meta-item">
          <NText depth="3" style="font-size: 11px">{{ $t('dashboard.etaLabel') }}</NText>
          <div style="font-size: 22px; font-weight: 700; margin-top: 2px">{{ etaText }}</div>
        </div>
        <div class="hero-meta-divider"></div>
        <div class="hero-meta-item">
          <NText depth="3" style="font-size: 11px">{{ $t('dashboard.savingsRate') }}</NText>
          <div style="font-size: 22px; font-weight: 700; margin-top: 2px; color: #18a058">{{ fmtPct(fs.savingsRate || 0) }}</div>
        </div>
      </div>
    </section>

    <!-- STAT CARDS (含动态平衡) ==========================
         桌面(≥640):5 张等宽横排。
         移动端(<640):用 CSS 把 NGrid 强制成 grid-template-columns: 1fr 1fr,
         第一张跨 1/-1 全宽 = 1+2+2 三行布局。
         (NGrid 的 cols responsive object 在 2.38 不稳定,改用 CSS !important 覆盖更稳)
    -->
    <NGrid class="stat-row" :cols="5" :x-gap="12" :y-gap="12" responsive="screen" item-responsive>
      <NGi :span="1">
        <NCard size="small" class="stat-card stat-blue" :bordered="false">
          <div class="stat-icon"><IconMoney /></div>
          <NStatistic :label="`${$t('dashboard.netAssets')} (${base})`" :value="fmtL(fs.netAssets, base)" />
          <div class="stat-foot">{{ $t('dashboard.investAccountValue') }}: {{ fmtL(totalInvestValue, base) }}</div>
          <div class="stat-foot">{{ $t('dashboard.investGrowth') }}: {{ investPLTotal >= 0 ? '+' : '' }}{{ fmtL(investPLTotal, base) }}</div>
        </NCard>
      </NGi>
      <NGi :span="1">
        <NCard size="small" class="stat-card stat-gold" :bordered="false">
          <div class="stat-icon"><IconRocket /></div>
          <NStatistic :label="`${$t('dashboard.fireTarget')} (${base})`" :value="fmtL(fs.target, base)" />
          <div class="stat-foot">{{ $t('dashboard.progress') }} {{ fmtPct(fs.progress) }}</div>
        </NCard>
      </NGi>
      <NGi :span="1">
        <NCard size="small" class="stat-card stat-green" :bordered="false">
          <div class="stat-icon">
            <IconTrendUp v-if="incomeTrendIsActive" />
            <IconTrendDown v-else />
          </div>
          <NStatistic :label="`${$t('common.thisMonth')} ${$t('dashboard.totalIncome')}`" :value="fmtL(displayMonth.totalIncome, base)" />
          <div class="stat-foot">{{ $t('dashboard.activeIncome') }}: {{ fmtL(displayMonth.activeIncome, base) }}</div>
        </NCard>
      </NGi>
      <NGi :span="1">
        <NCard size="small" class="stat-card stat-rose" :bordered="false">
          <div class="stat-icon"><IconExpense /></div>
          <NStatistic :label="`${$t('common.thisMonth')} ${$t('dashboard.totalExpense')}`" :value="fmtL(displayMonth.totalExpense, base)" />
          <div class="stat-foot">{{ $t('dashboard.expenseRatio') }}: {{ displayMonth.totalIncome > 0 ? fmtPct(displayMonth.totalExpense / displayMonth.totalIncome) : '—' }}</div>
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
    </NGrid>

    <!-- QUICK ACTIONS ====================================== -->
    <!-- 快捷入口上移到 5 张卡之后(原 db-section 位置);
         动态平衡已并入上方 stat-row 不再重复展示。 -->
    <section class="section">
      <div class="section-head">
        <div class="section-title">
          <span>⚡ {{ $t('dashboard.quickActions') }}</span>
        </div>
      </div>
      <div class="quick-row">
        <NButton class="qa-btn qa-income" size="large" round tertiary @click="gotoRecord('in')">
          <template #icon><IconIncome :size="18" /></template>
          {{ $t('dashboard.addIncome') }}
        </NButton>
        <NButton class="qa-btn qa-expense" size="large" round tertiary @click="gotoRecord('out')">
          <template #icon><IconExpense :size="18" /></template>
          {{ $t('dashboard.addExpense') }}
        </NButton>
        <NButton class="qa-btn qa-calc" size="large" round tertiary @click="goTo('calculator')">
          <template #icon><IconRocket :size="18" /></template>
          {{ $t('nav.calculator') }}
        </NButton>
        <NButton class="qa-btn qa-remind" size="large" round tertiary @click="goTo('reminders')">
          <template #icon><IconReminders :size="18" /></template>
          {{ $t('nav.reminders') }}
        </NButton>
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
.dash-wrap { display: flex; flex-direction: column; gap: 18px; }

.hero {
  position: relative;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 24px;
  padding: 26px 28px;
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(255,200,87,0.10), rgba(233,83,59,0.05) 60%, rgba(91,141,239,0.08));
  border: 1px solid rgba(125,125,140,0.18);
  overflow: hidden;
  min-height: 220px;
}
.hero::before {
  content: 'FIRE2FREE';
  position: absolute;
  top: -40px;
  right: -30px;
  font-size: 200px;
  font-weight: 900;
  letter-spacing: 10px;
  background: linear-gradient(135deg, rgba(255,138,61,0.12), rgba(123,97,255,0.10));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  pointer-events: none;
  user-select: none;
  z-index: 0;
}
.hero-greeting { z-index: 1; }
.hero-title {
  font-size: 30px;
  font-weight: 800;
  margin: 6px 0 4px;
  background: linear-gradient(90deg,#FF8A3D 0%, #E9533B 60%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.hero-sub { font-size: 13px; margin: 0; opacity: 0.7; }
.hero-statement {
  font-size: 13px;
  margin: 10px 0 0;
  padding: 8px 14px;
  border-left: 3px solid var(--fire-grad-primary, #FF8A3D);
  background: rgba(255,200,87,0.10);
  border-radius: 0 8px 8px 0;
  font-style: italic;
  opacity: 0.92;
  max-width: 560px;
}
.hero-ring { z-index: 1; padding-bottom: 22px; }
.hero-meta { display: flex; align-items: center; gap: 18px; justify-content: flex-end; z-index: 1; padding-right: 6px; }
.hero-meta-item { text-align: right; }
.hero-meta-divider { width: 1px; height: 36px; background: rgba(125,125,140,0.3); }

@media (max-width: 1024px) {
  .hero { grid-template-columns: 1fr; text-align: center; }
  .hero-meta { justify-content: center; }
  .hero-meta-divider { display: none; }
  .hero-meta-item { text-align: center; }
}

.stat-row { margin-top: 4px; }
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
  .hero { padding: 14px !important; gap: 14px; border-radius: 12px; }
  .hero-title { font-size: 1.3rem !important; }
  .hero-sub { font-size: 13px; }
  .hero-statement { font-size: 12px; }
  .hero-meta { gap: 12px; padding-right: 0; }
  .hero-meta-item { font-size: 12px; }
  .hero-meta-divider { height: 28px; }
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
  .hero { padding: 14px !important; gap: 14px; border-radius: 12px; }
  .hero-title { font-size: 1.3rem !important; }
  .hero-sub { font-size: 13px; }
  .hero-statement { font-size: 12px; }
  .hero-meta { gap: 12px; padding-right: 0; }
  .hero-meta-item { font-size: 12px; }
  .hero-meta-divider { height: 28px; }

  /* stat-row 1+2+2 布局 */
  .stat-row {
    grid-template-columns: 1fr 1fr !important;
  }
  .stat-row > :first-child {
    grid-column: 1 / -1 !important;
  }

  /* 主卡(首张 = 净资产):xs 满宽,接近桌面样式 */
  .stat-row > :first-child .stat-card :deep(.n-card__content) { padding: 14px !important; }
  .stat-row > :first-child .stat-card :deep(.n-statistic-value__content) {
    font-size: 22px !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .stat-row > :first-child .stat-card :deep(.n-statistic .n-statistic__label) {
    font-size: 11px !important;
  }
  .stat-row > :first-child .stat-card .stat-icon { width: 28px; height: 28px; top: 10px; right: 10px; }
  .stat-row > :first-child .stat-card .stat-foot { font-size: 10.5px; margin-top: 4px; }

  /* 副卡(其余 4 张):xs 半宽,紧凑样式,数字/label/foot 全部 nowrap + ellipsis */
  .stat-row > :not(:first-child) .stat-card :deep(.n-card__content) { padding: 12px 10px 10px !important; }
  .stat-row > :not(:first-child) .stat-card :deep(.n-statistic-value__content) {
    font-size: 15px !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    line-height: 1.2;
  }
  .stat-row > :not(:first-child) .stat-card :deep(.n-statistic .n-statistic__label) {
    font-size: 10.5px !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 2px !important;
    line-height: 1.2;
  }
  .stat-row > :not(:first-child) .stat-card .stat-icon { width: 22px; height: 22px; top: 6px; right: 6px; }
  .stat-row > :not(:first-child) .stat-card .stat-foot {
    display: block !important;
    font-size: 10px !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-top: 4px !important;
    line-height: 1.2;
  }

  .section { padding: 12px !important; }
  .section-title { font-size: 14px; }
  .bet-mini-list { grid-template-columns: 1fr; }
}

/* iPhone SE 等 ≤480px 极窄屏:副卡数字再缩一档 */
@media (max-width: 480px) {
  .stat-row > :not(:first-child) .stat-card :deep(.n-card__content) { padding: 10px 8px 8px !important; }
  .stat-row > :not(:first-child) .stat-card :deep(.n-statistic-value__content) { font-size: 14px !important; }
  .stat-row > :not(:first-child) .stat-card .stat-foot { font-size: 9.5px !important; }
}

.quick-row { display: flex; flex-wrap: wrap; gap: 10px; }
.qa-btn { padding: 6px 18px; font-weight: 600; }

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
