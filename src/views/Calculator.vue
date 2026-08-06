<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { NCard, NStatistic, NText, NSpace, NInputNumber, NForm, NFormItem, NSlider, NTag } from 'naive-ui'
import { useAggregate } from '@/composables/aggregate'
import { useAppStore } from '@/stores/app'
import { fireTarget, yearsToFire } from '@/finance'
import { fmtCompact, fmtPct, fmtMoney } from '@/composables/format'

const { t } = useI18n()
const app = useAppStore()
const { fireState } = useAggregate()
const fs = fireState
const base = computed(() => app.baseCurrency)

const fmtL = (v, c) => fmtCompact(v, c, app.profile.locale)

// what-if: 储蓄率提升对达成年份的影响
const extraSaving = ref(0) // 每月额外储蓄(基准币种)
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
    <!-- FIRE 计算器 2x2x1:第 5 项(达成进度)横向跨整行 -->
    <h3 class="calc-title">{{ t('calculator.title') }}</h3>
    <div class="calc-grid">
      <NCard size="small" class="calc-cell" :bordered="true">
        <NStatistic :label="t('calculator.currentAssets')" :value="fmtL(fs.netAssets, base)" />
      </NCard>
      <NCard size="small" class="calc-cell" :bordered="true">
        <NStatistic :label="t('calculator.target')" :value="fmtL(fs.target, base)" />
      </NCard>
      <NCard size="small" class="calc-cell" :bordered="true">
        <NStatistic :label="t('calculator.annualExpense')" :value="fmtL(fs.lastExpense * 12, base)" />
      </NCard>
      <NCard size="small" class="calc-cell" :bordered="true">
        <NStatistic :label="t('calculator.gap')" :value="fmtL(fs.gap, base)" />
      </NCard>
      <!-- 达成进度:横向跨整行 -->
      <NCard size="small" class="calc-cell calc-cell-wide" :bordered="true">
        <NStatistic :label="t('calculator.progress')" :value="fmtPct(fs.progress)" />
      </NCard>
    </div>

    <!-- 情景模拟卡(原 scenario 卡,放下面全宽) -->
    <NCard :title="t('calculator.scenario')" style="margin-top: 16px">
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
/* 2x2 网格;第 5 项 (calc-cell-wide) 横向跨整行;
   ≤640px 退化为单列避免拥挤。 */
.calc-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.calc-cell-wide { grid-column: 1 / -1; }
.calc-cell :deep(.n-card__content) { padding: 14px 16px; }
@media (max-width: 640px) {
  .calc-grid { grid-template-columns: 1fr; }
  .calc-cell-wide { grid-column: auto; }
}
</style>
