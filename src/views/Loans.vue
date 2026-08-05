<script setup>
import { computed, ref, h } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  NCard, NForm, NFormItem, NInputNumber, NDatePicker, NSelect, NInput, NButton, NDataTable, useMessage, NPopconfirm,
  NTag, NSpace, NText, NEmpty
} from 'naive-ui'
import AppModal from '@/components/AppModal.vue'
import { useAppStore } from '@/stores/app'
import { repaySchedule, loanMonthlyPayment } from '@/finance'
import { fmtMoney } from '@/composables/format'
import { fireSave } from '@/composables/saveFx'
import dayjs from 'dayjs'

const { t } = useI18n()
const app = useAppStore()
const message = useMessage()
// 月版:月供已含在支出总额,无需逐月登记,仅展示锁定原因条
const isMonthly = computed(() => app.profile.entryMode === 'monthly')

const showAdd = ref(false)
const editingId = ref(null)
const justAddedId = ref(null)
const form = ref({
  name: '', type: 'mortgage', principal: null, annualRate: 4.9, termMonths: 360, startDate: Date.now(),
  repayMethod: 'equal_payment', status: 'active'
})
const loanTypeOptions = app.categories.loanType.map((c) => ({ label: c.zh, value: c.key }))
const repayOptions = [
  { label: t('loans.equalPayment'), value: 'equal_payment' },
  { label: t('loans.equalPrincipal'), value: 'equal_principal' }
]

function openAdd() {
  editingId.value = null
  form.value = { name: '', type: 'mortgage', principal: null, annualRate: 4.9, termMonths: 360, startDate: Date.now(), repayMethod: 'equal_payment', status: 'active' }
  showAdd.value = true
}
function submit() {
  if (!form.value.name || !form.value.principal || Number(form.value.principal) <= 0)
    return message.warning(t('loans.formHint'))
  const payload = {
    name: form.value.name, type: form.value.type,
    principal: Number(form.value.principal), annualRate: Number(form.value.annualRate) / 100,
    termMonths: Number(form.value.termMonths), startDate: dayjs(form.value.startDate).format('YYYY-MM-DD'),
    repayMethod: form.value.repayMethod, status: form.value.status
  }
  let row
  if (editingId.value) {
    app.update('loans', editingId.value, payload)
    row = { id: editingId.value }
  } else {
    row = app.add('loans', payload)
  }
  fireSave(t('loans.saved'))
  justAddedId.value = row.id
  setTimeout(() => (justAddedId.value = null), 1600)
  showAdd.value = false
}

const rows = computed(() => app.db.loans)
const rowProps = (r) => ({ class: r.id === justAddedId.value ? 'row-just-added' : '' })
const columns = computed(() => [
  { title: t('loans.name'), key: 'name' },
  { title: t('loans.type'), key: 'type', render: (r) => loanTypeName(r.type) },
  { title: t('loans.principal'), key: 'principal', render: (r) => fmtMoney(r.principal, 'CNY') },
  { title: t('loans.monthlyPayment'), key: 'mp', render: (r) => fmtMoney(loanMonthlyPayment(r), 'CNY') },
  {
    title: t('loans.status'),
    key: 'status',
    render: (r) => h(NTag, { type: r.status === 'cleared' ? 'success' : 'warning' }, () => (r.status === 'cleared' ? t('loans.cleared') : t('loans.active')))
  },
  {
    title: '',
    key: 'op',
    render: (r) =>
      h(NSpace, {}, () => [
        h(NButton, { size: 'small', quaternary: true, onClick: () => openSchedule(r) }, () => t('loans.schedule')),
        h(NButton, { size: 'small', quaternary: true, onClick: () => toggleClear(r) }, () => (r.status === 'cleared' ? t('loans.active') : t('loans.cleared'))),
        h(
          NPopconfirm,
          { onPositiveClick: () => app.remove('loans', r.id) },
          { trigger: () => h(NButton, { size: 'small', type: 'error', quaternary: true }, () => t('common.delete')), default: () => t('common.deleteConfirm') }
        )
      ])
  }
])
function loanTypeName(key) {
  const c = app.categories.loanType.find((x) => x.key === key)
  return c ? c.zh : key
}
function toggleClear(r) {
  app.update('loans', r.id, { status: r.status === 'cleared' ? 'active' : 'cleared' })
}

const scheduleLoan = ref(null)
const scheduleRows = computed(() => (scheduleLoan.value ? repaySchedule(scheduleLoan.value) : []))
function openSchedule(r) {
  scheduleLoan.value = r
}
</script>

<template>
  <div>
    <div v-if="isMonthly" class="monthly-lock">
      <span class="ml-icon">🔒</span>
      <span>{{ t('loans.monthlyLock') }}</span>
    </div>
    <NCard :title="t('loans.title')">
      <template #header-extra>
        <NButton type="primary" size="small" @click="openAdd">{{ t('loans.addLoan') }}</NButton>
      </template>
      <NDataTable :columns="columns" :data="rows" :row-key="(r) => r.id" :row-props="rowProps" size="small">
        <template #empty>
          <div class="tbl-empty"><NEmpty :description="t('loans.empty')" /></div>
        </template>
      </NDataTable>
    </NCard>

    <AppModal v-model:show="showAdd" :title="t('loans.addLoan')" :card-style="{ width: '560px', maxWidth: '92vw' }">
      <NForm :model="form" class="entry-form">
        <NFormItem :label="t('loans.name')" style="grid-column: 1 / -1"><NInput v-model:value="form.name" style="width: 100%" /></NFormItem>
        <NFormItem :label="t('loans.type')" style="grid-column: 1 / -1"><NSelect v-model:value="form.type" :options="loanTypeOptions" style="width: 100%" /></NFormItem>
        <NFormItem :label="t('loans.principal')">
          <NInputNumber v-model:value="form.principal" :min="0" :placeholder="t('common.inputPrincipal')" style="width: 100%" :show-button="false" />
        </NFormItem>
        <NFormItem :label="t('loans.annualRate')">
          <NInputNumber v-model:value="form.annualRate" :min="0" :step="0.1" placeholder="%" style="width: 100%" :show-button="false" />
        </NFormItem>
        <NFormItem :label="t('loans.termMonths')">
          <NInputNumber v-model:value="form.termMonths" :min="1" style="width: 100%" :show-button="false" />
        </NFormItem>
        <NFormItem :label="t('loans.startDate')">
          <NDatePicker v-model:value="form.startDate" type="date" style="width: 100%" />
        </NFormItem>
        <NFormItem :label="t('loans.repayMethod')" style="grid-column: 1 / -1">
          <NSelect v-model:value="form.repayMethod" :options="repayOptions" style="width: 100%" />
        </NFormItem>
        <NSpace class="entry-form-buttons">
          <NButton type="primary" block @click="submit">{{ t('common.save') }}</NButton>
        </NSpace>
      </NForm>
    </AppModal>

    <AppModal :show="!!scheduleLoan" :title="t('loans.schedule') + ' · ' + (scheduleLoan?.name || '')" :card-style="{ width: '600px', maxWidth: '92vw' }" @update:show="(v) => { if (!v) scheduleLoan = null }">
      <NDataTable
        v-if="scheduleLoan"
        :columns="[
          { title: '#', key: 'index' },
          { title: t('loans.monthlyPayment'), key: 'payment', render: (r) => fmtMoney(r.payment, 'CNY') },
          { title: t('loans.principal'), key: 'principalPart', render: (r) => fmtMoney(r.principalPart, 'CNY') },
          { title: t('loans.remaining'), key: 'remaining', render: (r) => fmtMoney(r.remaining, 'CNY') }
        ]"
        :data="scheduleRows"
        size="small"
        :max-height="360"
      />
    </AppModal>
  </div>
</template>

<style scoped>
.monthly-lock {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 14px;
  margin-bottom: 14px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 1.5;
  color: #ffd9a8;
  background: rgba(255, 138, 61, 0.12);
  border: 1px solid rgba(255, 138, 61, 0.32);
}
.ml-icon { font-size: 15px; }
.tbl-empty { padding: 36px 0; }
/* 表单栅格:与 Income/Expense 保持一致的自适应布局 */
.entry-form { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 14px; align-items: end; }
.entry-form-buttons { grid-column: 1 / -1; justify-content: flex-end; }
</style>
