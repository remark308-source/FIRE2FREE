<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { NCard, NGrid, NGi, NStatistic, NText, NSpace, NInputNumber, NForm, NFormItem, NSlider, NTag } from 'naive-ui'
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
  <div>
    <NGrid :cols="2" :x-gap="12" :y-gap="12" responsive="screen" item-responsive>
      <NGi span="2 m:1">
        <NCard :title="t('calculator.title')">
          <NSpace vertical>
            <NStatistic :label="t('calculator.currentAssets')" :value="fmtL(fs.netAssets, base)" />
            <NStatistic :label="t('calculator.annualExpense')" :value="fmtL(fs.lastExpense * 12, base)" />
            <NStatistic :label="t('calculator.target')" :value="fmtL(fs.target, base)" />
            <NStatistic :label="t('calculator.gap')" :value="fmtL(fs.gap, base)" />
            <NStatistic :label="t('calculator.progress')" :value="fmtPct(fs.progress)" />
          </NSpace>
        </NCard>
      </NGi>
      <NGi span="2 m:1">
        <NCard :title="t('calculator.scenario')">
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
      </NGi>
    </NGrid>
  </div>
</template>
