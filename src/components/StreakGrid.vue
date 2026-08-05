<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { NCard, NText, NTag } from 'naive-ui'
import dayjs from 'dayjs'

const props = defineProps({
  streak: { type: Object, required: true } // useStreak 返回值
})
const { t } = useI18n()
const grid = computed(() => props.streak.gridMonths.value)
const current = computed(() => props.streak.currentStreak.value)
const total = computed(() => props.streak.totalChecked.value)
const longest = computed(() => props.streak.longestStreak.value)
const thisMonthDone = computed(() => props.streak.currentMonthChecked.value)

function monthShort(ym) {
  return Number(ym.slice(5)) + (ym.slice(5, 6) === '0' ? '' : '')
}
</script>

<template>
  <NCard class="streak-card" :bordered="false" size="small">
    <div class="streak-head">
      <div>
        <div class="streak-eyebrow">{{ t('streak.title') }}</div>
        <div class="streak-num">
          <span class="big">{{ current }}</span>
          <span class="unit">{{ t('streak.months') }}</span>
        </div>
        <NText depth="3" style="font-size: 12px">
          {{ t('streak.longest') }} {{ longest }} · {{ t('streak.totalChecked') }} {{ total }}
        </NText>
      </div>
      <NTag :type="thisMonthDone ? 'success' : 'warning'" round size="small" :bordered="false">
        {{ thisMonthDone ? '✓ ' + t('streak.thisMonthDone') : '○ ' + t('streak.thisMonthTodo') }}
      </NTag>
    </div>

    <div class="streak-grid">
      <div
        v-for="m in grid"
        :key="m.ym"
        class="cell"
        :class="{ checked: m.checked, current: m.isCurrent }"
      >
        <div class="cell-mo">{{ dayjs(m.ym + '-01').format('M') }}<span class="cell-suf">{{ t('streak.monthShort') }}</span></div>
        <div class="cell-mark">{{ m.checked ? '✓' : (m.isCurrent ? '○' : '·') }}</div>
        <div class="cell-year" v-if="m.isCurrent">{{ dayjs(m.ym + '-01').format('YYYY') }}</div>
      </div>
    </div>
  </NCard>
</template>

<style scoped>
.streak-card { border-radius: 16px !important; }
.streak-head { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 12px; }
.streak-eyebrow { font-size: 12px; opacity: 0.7; }
.streak-num { display: inline-flex; align-items: baseline; gap: 6px; margin: 4px 0 2px; }
.streak-num .big { font-size: 30px; font-weight: 700; background: var(--fire-grad-primary); -webkit-background-clip: text; background-clip: text; color: transparent; }
.streak-num .unit { font-size: 13px; opacity: 0.7; }
.streak-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 8px; }
.cell {
  border-radius: 10px;
  padding: 8px 4px 6px;
  text-align: center;
  background: rgba(128,128,128,0.10);
  position: relative;
  transition: transform .15s ease;
}
.cell.checked { background: var(--fire-grad-primary); color: #fff; box-shadow: 0 4px 12px rgba(233,83,59,0.18); }
.cell.current { outline: 2px dashed rgba(255,200,87,0.7); outline-offset: 2px; }
.cell-mo { font-size: 12px; font-weight: 600; }
.cell-mark { font-size: 14px; font-weight: 700; line-height: 1.4; }
.cell-suf { font-size: 10px; opacity: 0.65; margin-left: 1px; }
.cell-year { font-size: 9px; opacity: 0.7; margin-top: 2px; }
</style>