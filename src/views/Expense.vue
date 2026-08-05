<script setup>
import { computed, ref, h, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  NCard, NForm, NFormItem, NInputNumber, NDatePicker, NSelect, NInput, NButton, NDataTable, useMessage, NPopconfirm, NTabs, NTabPane, NSpace, NEmpty
} from 'naive-ui'
import { useAppStore } from '@/stores/app'
import { CURRENCIES } from '@/constants'
import { fmtMoney } from '@/composables/format'
import { fireSave } from '@/composables/saveFx'
import dayjs from 'dayjs'

const { t } = useI18n()
const app = useAppStore()
const message = useMessage()

const tab = ref('daily')
const form = ref({ date: Date.now(), category: 'food', amount: null, currency: 'CNY', note: '' })
const justAddedId = ref(null)

// 月版模式:隐藏逐笔表,改为填「本月支出总额」一笔 isMonthlyTotal 记录(含月供)
const entryMode = computed(() => app.profile.entryMode)
const curYm = computed(() => dayjs().format('YYYY-MM'))
const monthExpenseInput = ref(null)
watch(
  [curYm, entryMode],
  () => {
    const rec = app.db.expenses.find((r) => r.isMonthlyTotal && dayjs(r.date).format('YYYY-MM') === curYm.value)
    monthExpenseInput.value = rec ? Number(rec.amount) : null
  },
  { immediate: true }
)
function submitMonth() {
  if (!monthExpenseInput.value || Number(monthExpenseInput.value) <= 0) return message.warning(t('expense.amountHint'))
  const ym = curYm.value
  const lastDay = dayjs().endOf('month').format('YYYY-MM-DD')
  const existing = app.db.expenses.find((r) => r.isMonthlyTotal && dayjs(r.date).format('YYYY-MM') === ym)
  const payload = {
    type: 'daily',
    date: lastDay,
    category: form.value.category,
    amount: Number(monthExpenseInput.value),
    currency: app.baseCurrency,
    note: ''
  }
  if (existing) app.update('expenses', existing.id, payload)
  else app.add('expenses', { ...payload, isMonthlyTotal: true })
  fireSave(t('expense.saved'))
}

function labelOf(c) {
  if (c.key === 'other') return t('common.other')
  return app.profile.locale === 'zh-CN' ? c.zh : c.en
}
const catOptions = computed(() => app.categories.expenseDaily.map((c) => ({ label: labelOf(c), value: c.key })))
const currencyOptions = computed(() => CURRENCIES.map((c) => ({
  label: `${c.code} ${app.profile.locale === 'zh-CN' ? c.zh : c.en}`,
  value: c.code
})))

// 千分位实时格式化:display 用 toLocaleString('en-US') 每 3 位加 ',';
// parser 反向剥逗号恢复数值,保证键盘录入与显示同步。
const numFmt = (v) => {
  if (v === null || v === undefined || v === '') return ''
  const n = Number(v)
  return Number.isFinite(n) ? n.toLocaleString('en-US') : ''
}
const numParse = (v) => {
  if (v === '' || v == null) return null
  const n = Number(String(v).replace(/,/g, ''))
  return Number.isFinite(n) ? n : null
}

function copyLast() {
  const last = [...app.db.expenses].sort((a, b) => b.date.localeCompare(a.date))[0]
  if (!last) return message.info(t('expense.noLast'))
  form.value = {
    date: Date.now(),
    category: last.category,
    amount: Number(last.amount),
    currency: last.currency,
    note: last.note || ''
  }
}

function submit() {
  if (!form.value.amount || Number(form.value.amount) <= 0) return message.warning(t('expense.amountHint'))
  const row = app.add('expenses', {
    type: 'daily',
    date: dayjs(form.value.date).format('YYYY-MM-DD'),
    category: form.value.category,
    amount: Number(form.value.amount),
    currency: form.value.currency,
    note: form.value.note
  })
  fireSave(t('expense.saved'))
  justAddedId.value = row.id
  setTimeout(() => (justAddedId.value = null), 1600)
  form.value = { date: Date.now(), category: 'food', amount: null, currency: app.baseCurrency, note: '' }
}

function catLabel(key) {
  const c = app.categories.expenseDaily.find((x) => x.key === key)
  return c ? labelOf(c) : key
}
const rows = computed(() =>
  app.db.expenses.filter((r) => r.type === 'daily').slice().sort((a, b) => b.date.localeCompare(a.date))
)
const columns = computed(() => [
  { title: t('common.date'), key: 'date' },
  { title: t('common.category'), key: 'category', render: (r) => catLabel(r.category) },
  { title: t('common.amount'), key: 'amount', render: (r) => fmtMoney(r.amount, r.currency) },
  { title: t('common.note'), key: 'note' },
  {
    title: '',
    key: 'op',
    render: (r) =>
      h(
        NPopconfirm,
        { onPositiveClick: () => app.remove('expenses', r.id) },
        { trigger: () => h(NButton, { size: 'small', type: 'error', quaternary: true }, () => t('common.delete')), default: () => t('common.deleteConfirm') }
      )
  }
])
const rowProps = (r) => ({ class: r.id === justAddedId.value ? 'row-just-added' : '' })
</script>

<template>
  <div>
    <template v-if="entryMode !== 'monthly'">
    <NTabs v-model:value="tab" type="segment">
      <NTabPane name="daily" :tab="t('expense.daily')" />
    </NTabs>
    <NCard :title="t('expense.title')" style="margin-top: 12px">
      <NForm :model="form" :show-feedback="false" class="entry-form">
        <NFormItem :label="t('common.date')">
          <NDatePicker v-model:value="form.date" type="date" style="width: 100%" />
        </NFormItem>
        <NFormItem :label="t('common.category')">
          <NSelect v-model:value="form.category" :options="catOptions" style="width: 100%" />
        </NFormItem>
        <NFormItem :label="t('common.amount')">
          <NInputNumber v-model:value="form.amount" :min="0" :precision="2" :placeholder="t('common.inputAmount')" :format="numFmt" :parse="numParse" style="width: 100%" />
        </NFormItem>
        <NFormItem :label="t('common.currency')">
          <NSelect v-model:value="form.currency" :options="currencyOptions" style="width: 100%" />
        </NFormItem>
        <NFormItem :label="t('common.note')">
          <NInput v-model:value="form.note" :placeholder="t('common.note')" style="width: 100%" />
        </NFormItem>
        <NSpace class="entry-form-buttons">
          <NButton type="primary" @click="submit">{{ t('common.save') }}</NButton>
          <NButton secondary @click="copyLast">{{ t('common.copyLast') }}</NButton>
        </NSpace>
      </NForm>
    </NCard>
    <NCard style="margin-top: 12px">
      <NDataTable :columns="columns" :data="rows" :row-key="(r) => r.id" :row-props="rowProps" size="small">
        <template #empty>
          <div class="tbl-empty"><NEmpty :description="t('expense.empty')" /></div>
        </template>
      </NDataTable>
    </NCard>
    </template>
    <div v-else class="month-mode">
      <NCard :title="t('expense.title')">
        <NForm :model="form" :show-feedback="false" class="entry-form">
          <NFormItem :label="t('dashboard.monthlyProgress.expense')">
            <NInputNumber v-model:value="monthExpenseInput" :min="0" :precision="2" :placeholder="t('common.inputAmount')" :format="numFmt" :parse="numParse" style="width: 100%" />
          </NFormItem>
          <NSpace class="entry-form-buttons">
            <NButton type="primary" @click="submitMonth">{{ t('common.save') }}</NButton>
          </NSpace>
        </NForm>
      </NCard>
    </div>
  </div>
</template>

<style scoped>
.tbl-empty { padding: 36px 0; }
/* 表单栅格:自适应列宽,最窄 160px,窄屏自动换行 */
.entry-form { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 14px; align-items: end; }
.entry-form-buttons { grid-column: 1 / -1; justify-content: flex-end; }
</style>
