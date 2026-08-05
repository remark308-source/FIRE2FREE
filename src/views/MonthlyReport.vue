<script setup>
import { computed, ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import dayjs from 'dayjs'
import {
  NCard, NSpace, NButton, NText, NDatePicker, NEmpty, NStatistic,
  useMessage
} from 'naive-ui'
import { useAppStore } from '@/stores/app'
import { useAggregate } from '@/composables/aggregate'
import { CATEGORIES, CURRENCIES } from '@/constants'
import { toBase } from '@/finance'
import { fmtMoney, fmtCompact } from '@/composables/format'
import ChartBox from '@/components/ChartBox.vue'

const { t } = useI18n()
const app = useAppStore()
const agg = useAggregate()
const message = useMessage()
const base = computed(() => app.baseCurrency)

// 当前语系下的紧凑货币(避免每个 fmtCompact 调用都重复传 locale)
const fmtL = (v, c) => fmtCompact(v, c, app.profile.locale)
const fx = computed(() => app.fxRates)
const isZh = computed(() => app.profile.locale === 'zh-CN')

const monthTs = ref(dayjs().startOf('month').valueOf())
const selectedYm = computed(() => dayjs(monthTs.value).format('YYYY-MM'))

// 进入时自动跳到最近一个有数据的月份(更好的 UX)
onMounted(() => {
  const m = agg.monthly.value
  if (m.length) monthTs.value = dayjs(m[m.length - 1].ym + '-01').valueOf()
})

function shiftMonth(delta) {
  monthTs.value = dayjs(monthTs.value).add(delta, 'month').valueOf()
}

// 该月汇总
const summary = computed(() => {
  const m = agg.monthly.value.find((x) => x.ym === selectedYm.value)
  if (!m) return null
  return {
    income: m.totalIncome,
    expense: m.totalExpense,
    savings: m.netCashFlow,
    activeIncome: m.activeIncome,
    passiveIncome: m.passiveIncome,
    investPL: m.investPL,
    dailyExpense: m.dailyExpense,
    rate: m.totalIncome > 0 ? Math.max(0, (m.totalIncome - m.totalExpense) / m.totalIncome) : 0
  }
})

// 该月支出按类别分组(基准币种)
const expensesByCategory = computed(() => {
  if (!summary.value) return []
  const ym = selectedYm.value
  const map = new Map()
  app.db.expenses.forEach((r) => {
    if (dayjs(r.date).format('YYYY-MM') !== ym) return
    if (r.type !== 'daily') return
    const v = toBase(Number(r.amount), r.currency, base.value, fx.value)
    map.set(r.category, (map.get(r.category) || 0) + v)
  })
  const total = [...map.values()].reduce((a, b) => a + b, 0)
  return [...map.entries()]
    .map(([key, value]) => {
      const cat = CATEGORIES.expenseDaily.find((c) => c.key === key)
      return {
        key,
        label: cat ? (isZh.value ? cat.zh : cat.en) : key,
        value,
        share: total > 0 ? value / total : 0
      }
    })
    .sort((a, b) => b.value - a.value)
})

const pieData = computed(() => ({
  x: expensesByCategory.value.map((d) => d.label),
  series: [{
    key: 'expense',
    label: isZh.value ? '支出' : 'Expense',
    data: expensesByCategory.value.map((d) => Math.round(d.value))
  }]
}))

const statement = computed(() => app.profile.fireStatement || '')

// ----- canvas 导出 PNG -----
const PALETTE = ['#FFC857', '#FF8A3D', '#E9533B', '#7B61FF', '#5B8DEF', '#18a058', '#36ad6a', '#FF6B9D', '#C147E9']

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath()
  ctx.moveTo(x + r, y)
  ctx.lineTo(x + w - r, y)
  ctx.arcTo(x + w, y, x + w, y + r, r)
  ctx.lineTo(x + w, y + h - r)
  ctx.arcTo(x + w, y + h, x + w - r, y + h, r)
  ctx.lineTo(x + r, y + h)
  ctx.arcTo(x, y + h, x, y + h - r, r)
  ctx.lineTo(x, y + r)
  ctx.arcTo(x, y, x + r, y, r)
  ctx.closePath()
}

function wrapText(ctx, text, x, y, maxWidth, lineHeight) {
  const chars = text.split('')
  let line = ''
  for (let i = 0; i < chars.length; i++) {
    const test = line + chars[i]
    if (ctx.measureText(test).width > maxWidth && line) {
      ctx.fillText(line, x, y)
      line = chars[i]
      y += lineHeight
    } else {
      line = test
    }
  }
  ctx.fillText(line, x, y)
}

async function exportPng() {
  if (!summary.value) {
    message.warning(isZh.value ? '该月暂无数据' : 'No data for this month')
    return
  }
  const W = 1080
  const H = 1350
  const canvas = document.createElement('canvas')
  canvas.width = W
  canvas.height = H
  const ctx = canvas.getContext('2d')

  // 背景渐变
  const bg = ctx.createLinearGradient(0, 0, W, H)
  bg.addColorStop(0, '#FFF8E8')
  bg.addColorStop(0.5, '#FFE7D6')
  bg.addColorStop(1, '#FCD3C0')
  ctx.fillStyle = bg
  ctx.fillRect(0, 0, W, H)

  // 顶部色条
  const top = ctx.createLinearGradient(0, 0, W, 0)
  top.addColorStop(0, '#FFC857')
  top.addColorStop(0.5, '#FF8A3D')
  top.addColorStop(1, '#E9533B')
  ctx.fillStyle = top
  ctx.fillRect(0, 0, W, 12)

  // LOGO + 标题
  ctx.fillStyle = '#1a1a1a'
  ctx.font = 'bold 56px "PingFang SC", "Microsoft YaHei", system-ui, sans-serif'
  ctx.textAlign = 'left'
  ctx.fillText(isZh.value ? 'FIRE2FREE 月度报告' : 'FIRE2FREE Monthly Report', 60, 110)

  ctx.font = 'bold 36px "PingFang SC", sans-serif'
  ctx.fillStyle = '#E9533B'
  ctx.fillText(selectedYm.value, 60, 170)

  if (statement.value) {
    ctx.font = 'italic 22px "PingFang SC", sans-serif'
    ctx.fillStyle = '#888'
    wrapText(ctx, `“${statement.value}”`, 60, 220, W - 120, 32)
  }

  // 4 个数据卡 2x2
  const stats = [
    { label: isZh.value ? '总收入' : 'Total Income', value: fmtL(summary.value.income, base.value), color: '#18a058' },
    { label: isZh.value ? '总支出' : 'Total Expense', value: fmtL(summary.value.expense, base.value), color: '#E9533B' },
    { label: isZh.value ? '净储蓄' : 'Net Saved', value: fmtL(summary.value.savings, base.value), color: '#7B61FF' },
    { label: isZh.value ? '储蓄率' : 'Savings Rate', value: (summary.value.rate * 100).toFixed(1) + '%', color: '#FF8A3D' }
  ]
  const cardY = statement.value ? 290 : 240
  const cardW = (W - 60 * 2 - 30) / 2
  const cardH = 150
  stats.forEach((s, i) => {
    const col = i % 2
    const row = Math.floor(i / 2)
    const x = 60 + col * (cardW + 30)
    const y = cardY + row * (cardH + 20)
    ctx.fillStyle = '#ffffff'
    roundRect(ctx, x, y, cardW, cardH, 16)
    ctx.fill()
    ctx.strokeStyle = 'rgba(0,0,0,0.06)'
    ctx.stroke()
    ctx.fillStyle = '#666'
    ctx.font = '24px "PingFang SC", sans-serif'
    ctx.fillText(s.label, x + 24, y + 42)
    ctx.fillStyle = s.color
    ctx.font = 'bold 50px "PingFang SC", sans-serif'
    ctx.fillText(s.value, x + 24, y + 105)
  })

  // 支出结构标题
  const structY = cardY + 2 * cardH + 60
  ctx.fillStyle = '#1a1a1a'
  ctx.font = 'bold 32px "PingFang SC", sans-serif'
  ctx.fillText(isZh.value ? '支出结构' : 'Expense Breakdown', 60, structY)

  // 甜甜圈 + 图例
  const donutX = 60 + 130
  const donutY = structY + 60 + 130
  const R = 130
  const r = 70
  const totalExp = summary.value.expense
  if (expensesByCategory.value.length && totalExp > 0) {
    let start = -Math.PI / 2
    expensesByCategory.value.slice(0, 8).forEach((d, i) => {
      const ang = (d.value / totalExp) * Math.PI * 2
      ctx.beginPath()
      ctx.arc(donutX, donutY, R, start, start + ang)
      ctx.arc(donutX, donutY, r, start + ang, start, true)
      ctx.closePath()
      ctx.fillStyle = PALETTE[i % PALETTE.length]
      ctx.fill()
      start += ang
    })
    // 中心文字
    ctx.fillStyle = '#1a1a1a'
    ctx.textAlign = 'center'
    ctx.font = 'bold 30px "PingFang SC", sans-serif'
    ctx.fillText((summary.value.rate * 100).toFixed(0) + '%', donutX, donutY - 6)
    ctx.font = '18px "PingFang SC", sans-serif'
    ctx.fillStyle = '#888'
    ctx.fillText(isZh.value ? '储蓄率' : 'Savings', donutX, donutY + 22)
    ctx.textAlign = 'left'

    // 图例(右侧)
    const legendX = donutX + R + 60
    let ly = donutY - 100
    expensesByCategory.value.slice(0, 8).forEach((d, i) => {
      ctx.fillStyle = PALETTE[i % PALETTE.length]
      roundRect(ctx, legendX, ly + 6, 16, 16, 4)
      ctx.fill()
      ctx.fillStyle = '#1a1a1a'
      ctx.font = '22px "PingFang SC", sans-serif'
      ctx.fillText(d.label, legendX + 28, ly + 22)
      ctx.fillStyle = '#888'
      ctx.font = '20px "PingFang SC", sans-serif'
      const pct = (d.share * 100).toFixed(0) + '%'
      ctx.fillText(pct, legendX + 240, ly + 22)
      ly += 36
    })
  } else {
    ctx.fillStyle = '#aaa'
    ctx.font = '24px "PingFang SC", sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText(isZh.value ? '当月无支出记录' : 'No expenses', W / 2, donutY)
    ctx.textAlign = 'left'
  }

  // 底部签名
  ctx.fillStyle = '#999'
  ctx.font = '20px "PingFang SC", sans-serif'
  ctx.textAlign = 'center'
  ctx.fillText(isZh.value ? 'FIRE2FREE · 财务独立 · 提前退休' : 'FIRE2FREE · Financial Independence · Early Retirement', W / 2, H - 50)
  ctx.fillStyle = '#bbb'
  ctx.font = '16px "PingFang SC", sans-serif'
  ctx.fillText(`Generated ${dayjs().format('YYYY-MM-DD HH:mm')} · 数据仅存于本地浏览器`, W / 2, H - 24)
  ctx.textAlign = 'left'

  // 下载
  const url = canvas.toDataURL('image/png')
  const a = document.createElement('a')
  a.href = url
  a.download = `FIRE2FREE-Monthly-${selectedYm.value}.png`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  message.success(isZh.value ? '已导出 PNG' : 'PNG exported')
}
</script>

<template>
  <div class="report-page">
    <NCard class="hero-card" :bordered="false">
      <div class="hero-row">
        <div>
          <div class="eyebrow">{{ t('report.title') }}</div>
          <div class="title">{{ t('report.subtitle') }}</div>
        </div>
        <NSpace align="center">
          <NButton @click="shiftMonth(-1)">‹</NButton>
          <NDatePicker v-model:value="monthTs" type="month" />
          <NButton @click="shiftMonth(1)">›</NButton>
          <NButton type="primary" @click="exportPng">
            {{ t('report.exportPng') }}
          </NButton>
        </NSpace>
      </div>
    </NCard>

    <NEmpty v-if="!summary" :description="t('common.noData')" style="margin: 40px 0" />

    <template v-else>
      <NSpace :wrap="true" :size="16" style="margin-top: 16px">
        <NCard size="small" class="stat grad-green" :bordered="false">
          <div class="stat-top">{{ t('dashboard.totalIncome') }}</div>
          <div class="stat-num">{{ fmtL(summary.income, base) }}</div>
          <div class="stat-sub">{{ t('dashboard.activeIncome') }} {{ fmtL(summary.activeIncome, base) }} · {{ t('dashboard.passiveIncome') }} {{ fmtL(summary.passiveIncome, base) }}</div>
        </NCard>
        <NCard size="small" class="stat grad-pink" :bordered="false">
          <div class="stat-top">{{ t('dashboard.totalExpense') }}</div>
          <div class="stat-num">{{ fmtL(summary.expense, base) }}</div>
          <div class="stat-sub">{{ t('dashboard.dailyExpense') }} {{ fmtL(summary.dailyExpense, base) }}</div>
        </NCard>
        <NCard size="small" class="stat grad-blue" :bordered="false">
          <div class="stat-top">{{ t('report.netSaved') }}</div>
          <div class="stat-num">{{ fmtL(summary.savings, base) }}</div>
          <div class="stat-sub">{{ t('dashboard.investPL') }} {{ fmtL(summary.investPL, base) }}</div>
        </NCard>
        <NCard size="small" class="stat grad-orange" :bordered="false">
          <div class="stat-top">{{ t('dashboard.savingsRate') }}</div>
          <div class="stat-num">{{ (summary.rate * 100).toFixed(1) }}%</div>
          <div class="stat-sub">{{ t('report.rateHint') }}</div>
        </NCard>
      </NSpace>

      <NCard class="chart-card" :bordered="false" size="small" style="margin-top: 16px">
        <ChartBox
          :title="t('dashboard.expenseStructure')"
          :data="pieData"
          :types="['pie']"
          :default-type="'pie'"
          height="320px"
          :format-value="(v) => fmtL(v, base)"
        />
      </NCard>
    </template>
  </div>
</template>

<style scoped>
.report-page { max-width: 1180px; margin: 0 auto; }
.hero-card { border-radius: 16px !important; }
.hero-row { display: flex; align-items: flex-end; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
.eyebrow { font-size: 12px; opacity: 0.6; }
.title { font-size: 22px; font-weight: 700; margin-top: 4px; }
.stat { flex: 1 1 220px; min-width: 200px; border-radius: 14px !important; color: #fff; }
.stat-top { font-size: 12px; opacity: 0.85; }
.stat-num { font-size: 26px; font-weight: 700; margin-top: 6px; }
.stat-sub { font-size: 11px; opacity: 0.85; margin-top: 4px; }
.grad-green { background: var(--fire-grad-green); }
.grad-pink { background: var(--fire-grad-pink); }
.grad-blue { background: var(--fire-grad-blue); }
.grad-orange { background: var(--fire-grad-orange); }
.chart-card { border-radius: 16px !important; }
</style>