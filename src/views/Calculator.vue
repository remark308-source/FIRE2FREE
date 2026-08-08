<script setup>
/**
 * FIRE 计算器 - 5 格紧凑信息表(用户图片方案)
 * 布局:左 2x2 + 第 3 列跨 2 行的「达成进度」大字
 * 风格:简洁单元格 + 边框,匹配图片样式
 */
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { NCard, NSpace, NText, NForm, NFormItem, NSlider, NTag, NRadioGroup, NRadioButton } from 'naive-ui'
import { useAggregate } from '@/composables/aggregate'
import { useAppStore } from '@/stores/app'
import { yearsToFire } from '@/finance'
import { fmtCompact, fmtPct, fmtMoney } from '@/composables/format'

const { t, locale } = useI18n()
const app = useAppStore()
const { fireState, monthly } = useAggregate()
const fs = fireState
const base = computed(() => app.baseCurrency)
const isZh = computed(() => locale.value.startsWith('zh'))

const fmtL = (v, c) => fmtCompact(v, c, app.profile.locale)

// what-if: 储蓄率提升对达成年份的影响
const extraSaving = ref(0)
const whatIf = computed(() => {
  const net = fs.value.netCashFlow + extraSaving.value
  const r = app.profile.returnRates[app.profile.defaultReturnScenario]
  return yearsToFire(fs.value.netAssets, fs.value.gap, net, r)
})

const scenarios = computed(() => {
  const r = app.profile.returnRates
  return [
    { label: t('settings.conservative'), eta: yearsToFire(fs.value.netAssets, fs.value.gap, fs.value.netCashFlow, r.conservative) },
    { label: t('settings.neutral'), eta: yearsToFire(fs.value.netAssets, fs.value.gap, fs.value.netCashFlow, r.neutral) },
    { label: t('settings.optimistic'), eta: yearsToFire(fs.value.netAssets, fs.value.gap, fs.value.netCashFlow, r.optimistic) }
  ]
})

// 财富自由推演:M1 支出覆盖(资产×收益率≥年支出) + M2 收入替代(被动≥主动)
// 逐年迭代:资产 = 资产 + 年净流入 + 资产×收益率;主动收入按工资增速复利。
// 失业情景:开始时资产扣除「失业月数×月支出」一次性冲击。
const salaryGrowth = ref(0) // 工资年增率,默认 0%
const unemployment = ref(0) // 失业月数:0/6/12/18
const wealthPlan = computed(() => {
  const r = app.profile.returnRates[app.profile.defaultReturnScenario] || 0.08
  const monthlyExpense = fs.value.lastExpense
  const netMonthly = fs.value.netCashFlow
  const target = fs.value.target
  const ms = monthly.value
  const last12 = ms.slice(-12)
  const activeAnnual = last12.reduce((s, m) => s + (m.activeIncome || 0), 0)
    || (ms.length ? ms[ms.length - 1].activeIncome * 12 : 0)
  const passive0 = fs.value.netAssets * r
  let assets = Math.max(0, fs.value.netAssets - unemployment.value * monthlyExpense)
  let active = activeAnnual
  let m1 = null
  let m2 = null
  const maxT = 80
  for (let y = 0; y <= maxT; y++) {
    if (m1 === null && assets >= target) m1 = y
    if (m2 === null && active > 0 && assets * r >= active) m2 = y
    assets = assets + netMonthly * 12 + assets * r
    active = active * (1 + salaryGrowth.value)
  }
  return { m1, m2, activeAnnual, passive0 }
})
</script>

<template>
  <div class="calc-wrap">
    <h3 class="calc-title">{{ t('calculator.title') }}</h3>

    <!-- 5 格紧凑信息表:4 个小格 2x2 + 第 5 格 (达成进度) 第 3 列跨 2 行大字 -->
    <div class="calc-grid">
      <div class="calc-cell">
        <div class="calc-label">{{ t('calculator.currentAssets') }}</div>
        <div class="calc-value">{{ fmtL(fs.netAssets, base) }}</div>
      </div>
      <div class="calc-cell">
        <div class="calc-label">{{ t('calculator.target') }}</div>
        <div class="calc-value">{{ fmtL(fs.target, base) }}</div>
      </div>
      <div class="calc-cell">
        <div class="calc-label">{{ t('calculator.annualExpense') }}</div>
        <div class="calc-value">{{ fmtL(fs.lastExpense * 12, base) }}</div>
      </div>
      <div class="calc-cell">
        <div class="calc-label">{{ t('calculator.gap') }}</div>
        <div class="calc-value">{{ fmtL(fs.gap, base) }}</div>
      </div>
      <!-- 第 5 格 跨 2 行在第 3 列,大字 -->
      <div class="calc-cell calc-cell-wide">
        <div class="calc-label">{{ t('calculator.progress') }}</div>
        <div class="calc-value calc-value--big">{{ fmtPct(fs.progress) }}</div>
      </div>
    </div>

    <!-- 情景模拟(全宽放在下方) -->
    <NCard :title="t('calculator.scenario')" style="margin-top: 16px" size="small">
      <NSpace vertical>
        <div v-for="s in scenarios" :key="s.label">
          <NText>{{ s.label }}: </NText>
          <NTag :type="s.eta == null ? 'error' : 'success'">{{ s.eta == null ? '∞' : s.eta + ' ' + t('calculator.eta') }}</NTag>
        </div>
        <NForm style="margin-top: 12px">
          <NFormItem :label="t('calculator.whatIf')">
            <NSlider v-model:value="extraSaving" :min="0" :max="50000" :step="1000" />
          </NFormItem>
          <NText>{{ isZh ? '每月多攒' : 'Each month save extra' }} {{ fmtMoney(extraSaving, base) }} → ETA: {{ whatIf == null ? '∞' : whatIf + ' ' + t('calculator.eta') }}</NText>
        </NForm>
      </NSpace>
    </NCard>
  </div>

  <!-- 财富自由推演(全宽,放在计算器下方,不受 350×500 约束,交互更舒适) -->
  <NCard class="wp-card" :title="t('calculator.wealthPlan')" style="margin-top: 16px" size="small">
    <div class="wp-grid">
      <div class="wp-cell">
        <div class="wp-label">{{ t('calculator.m1') }}</div>
        <div class="wp-sub">{{ t('calculator.m1desc') }}</div>
        <div class="wp-val">{{ wealthPlan.m1 == null ? '∞' : wealthPlan.m1 + ' ' + t('calculator.eta') }}</div>
      </div>
      <div class="wp-cell">
        <div class="wp-label">{{ t('calculator.m2') }}</div>
        <div class="wp-sub">{{ t('calculator.m2desc') }}</div>
        <div class="wp-val wp-val--red">{{ wealthPlan.m2 == null ? '∞' : wealthPlan.m2 + ' ' + t('calculator.eta') }}</div>
      </div>
    </div>
    <div class="wp-controls">
      <div class="wp-ctrl">
        <span class="wp-ctrl-label">{{ t('calculator.salaryGrowth') }}</span>
        <NSlider v-model:value="salaryGrowth" :min="0" :max="0.15" :step="0.01" style="flex: 1" />
        <span class="wp-ctrl-val">{{ (salaryGrowth * 100).toFixed(0) }}%</span>
      </div>
      <div class="wp-ctrl">
        <span class="wp-ctrl-label">{{ t('calculator.unemployment') }}</span>
        <NRadioGroup v-model:value="unemployment" size="small">
          <NRadioButton :value="0">{{ t('calculator.unempOff') }}</NRadioButton>
          <NRadioButton :value="6">{{ t('calculator.unempMonths', { n: 6 }) }}</NRadioButton>
          <NRadioButton :value="12">{{ t('calculator.unempMonths', { n: 12 }) }}</NRadioButton>
          <NRadioButton :value="18">{{ t('calculator.unempMonths', { n: 18 }) }}</NRadioButton>
        </NRadioGroup>
      </div>
    </div>
    <div class="wp-note">
      {{ t('dashboard.activeIncome') }}: {{ fmtL(wealthPlan.activeAnnual, base) }} · {{ t('dashboard.annualPassive') }}: {{ fmtL(wealthPlan.passive0, base) }}
    </div>
  </NCard>
</template>

<style scoped>
/* 手机/平板:全宽响应式(回 350×500 前的上一版);桌面(≥769px)才用 350×500 固定框 */
.calc-wrap { display: flex; flex-direction: column; }
@media (min-width: 769px) {
  .calc-wrap { width: 350px; height: 500px; overflow: auto; }
}
.calc-title { margin: 0 0 12px; font-size: 17px; font-weight: 700; }

/* 3 列网格:col 1-2 各 2x1(共 4 个小格),col 3 跨 2 行(达成进度 大字) */
.calc-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1.15fr;
  grid-template-rows: auto auto;
  gap: 0;
  border: 1px solid rgba(125, 125, 140, 0.22);
  border-radius: 10px;
  overflow: hidden;
  background: rgba(125, 125, 140, 0.04);
}
/* 定位 5 个 cell:nth-child(1~4) 占前两列 2x2,nth-child(5) 占第 3 列跨 2 行 */
.calc-cell:nth-child(1) { grid-column: 1; grid-row: 1; }
.calc-cell:nth-child(2) { grid-column: 2; grid-row: 1; }
.calc-cell:nth-child(3) { grid-column: 1; grid-row: 2; border-bottom: none; }
.calc-cell:nth-child(4) { grid-column: 2; grid-row: 2; border-right: 1px solid rgba(125,125,140,0.15); border-bottom: none; }
.calc-cell-wide {
  grid-column: 3;
  grid-row: 1 / span 2;
  border-right: none;
  background: rgba(255, 138, 61, 0.06);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  gap: 6px;
}
/* 用 border 制造单元格分割线 */
.calc-cell {
  padding: 14px 16px;
  border-right: 1px solid rgba(125, 125, 140, 0.15);
  border-bottom: 1px solid rgba(125, 125, 140, 0.15);
  background: transparent;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.calc-label {
  font-size: 12px;
  opacity: 0.65;
  letter-spacing: 0.3px;
}
.calc-value {
  font-size: 18px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  color: inherit;
  line-height: 1.2;
}
/* 第 5 格 (达成进度):大字,品牌橙 */
.calc-value--big {
  font-size: 30px;
  font-weight: 800;
  color: #FF8A3D;
}

/* 财富自由推演:M1/M2 双格 + 控制区 */
.wp-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  border: 1px solid rgba(125,125,140,0.22);
  border-radius: 10px;
  overflow: hidden;
  background: rgba(125,125,140,0.04);
}
.wp-cell {
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}
.wp-cell:first-child { border-right: 1px solid rgba(125,125,140,0.15); }
.wp-label { font-size: 13px; font-weight: 700; }
.wp-sub { font-size: 11px; opacity: 0.6; }
.wp-val { font-size: 22px; font-weight: 800; color: #FF8A3D; font-variant-numeric: tabular-nums; }
.wp-val--red { color: #E9533B; }
.wp-controls {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 14px;
}
.wp-ctrl { display: flex; align-items: center; gap: 10px; }
.wp-ctrl-label { font-size: 12px; opacity: 0.75; white-space: nowrap; min-width: 76px; }
.wp-ctrl-val { font-size: 12px; font-weight: 700; font-variant-numeric: tabular-nums; min-width: 34px; text-align: right; }
.wp-note { margin-top: 12px; font-size: 11px; opacity: 0.7; }
@media (max-width: 640px) {
  .wp-grid { grid-template-columns: 1fr; }
  .wp-cell:first-child { border-right: none; border-bottom: 1px solid rgba(125,125,140,0.15); }
}

@media (max-width: 640px) {
  /* 移动端退化为 5 行单列;wide cell 不再跨行,跟其他 cell 同样式 */
  .calc-grid { grid-template-columns: 1fr; }
  .calc-cell, .calc-cell:nth-child(1), .calc-cell:nth-child(2), .calc-cell:nth-child(3), .calc-cell:nth-child(4) {
    grid-column: 1;
  }
  .calc-cell:nth-child(1) { grid-row: 1; }
  .calc-cell:nth-child(2) { grid-row: 2; }
  .calc-cell:nth-child(3) { grid-row: 3; border-bottom: 1px solid rgba(125,125,140,0.15); }
  .calc-cell:nth-child(4) { grid-row: 4; border-right: none; border-bottom: 1px solid rgba(125,125,140,0.15); }
  .calc-cell-wide {
    grid-column: 1;
    grid-row: 5;
    border-right: none;
    border-bottom: none;
  }
  .calc-value--big { font-size: 26px; }
}
</style>
