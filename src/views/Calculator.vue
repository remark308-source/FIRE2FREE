<script setup>
/**
 * FIRE 计算器:5 格紧凑信息表(2x2 + 1 跨整行)
 * 风格:简洁表格单元格 + 边框,匹配图片样式
 */
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { NCard, NSpace, NText, NForm, NFormItem, NSlider, NTag } from 'naive-ui'
import { useAggregate } from '@/composables/aggregate'
import { useAppStore } from '@/stores/app'
import { yearsToFire } from '@/finance'
import { fmtCompact, fmtPct, fmtMoney } from '@/composables/format'

const { t, locale } = useI18n()
const app = useAppStore()
const { fireState } = useAggregate()
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
</script>

<template>
  <div class="calc-wrap">
    <h3 class="calc-title">{{ t('calculator.title') }}</h3>

    <!-- 5 格紧凑信息表(2x2 + 第 5 格跨整行),纯 div + 边框,无大数字 -->
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
      <!-- 第 5 格 跨整行 -->
      <div class="calc-cell calc-cell-wide">
        <div class="calc-label">{{ t('calculator.progress') }}</div>
        <div class="calc-value">{{ fmtPct(fs.progress) }}</div>
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
</template>

<style scoped>
.calc-wrap { display: flex; flex-direction: column; }
.calc-title { margin: 0 0 12px; font-size: 17px; font-weight: 700; }

/* 2x2 网格;第 5 格 (calc-cell-wide) 横向跨整行;
   ≤640px 退化为单列。 */
.calc-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  border: 1px solid rgba(125, 125, 140, 0.22);
  border-radius: 8px;
  overflow: hidden;
  background: rgba(125, 125, 140, 0.04);
}
/* 用 border 制造单元格分割线(每格四周 1px) */
.calc-cell {
  padding: 12px 14px;
  border-right: 1px solid rgba(125, 125, 140, 0.15);
  border-bottom: 1px solid rgba(125, 125, 140, 0.15);
  background: transparent;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}
.calc-cell:nth-child(2n) { border-right: none; } /* 每行右侧无边框 */
/* 第 5 格 (跨整行):去掉右边框 */
.calc-cell-wide {
  grid-column: 1 / -1;
  border-right: none;
}
/* 前 4 格最后一行去掉下边框(避免与第 5 格边框重叠) */
.calc-cell:nth-child(n + 5) { border-bottom: none; }

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
}

@media (max-width: 640px) {
  .calc-grid { grid-template-columns: 1fr; }
  .calc-cell { border-right: none; }
  .calc-cell-wide { grid-column: auto; }
}
</style>