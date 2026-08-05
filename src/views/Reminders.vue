<script setup>
import { computed, ref, h } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  NCard, NForm, NFormItem, NInput, NInputNumber, NSelect, NButton, NDataTable, useMessage, NSpace, NTag, NPopconfirm, NEmpty
} from 'naive-ui'
import AppModal from '@/components/AppModal.vue'
import { useAppStore } from '@/stores/app'
import { fireSave } from '@/composables/saveFx'
import dayjs from 'dayjs'

const { t } = useI18n()
const app = useAppStore()
const message = useMessage()

const showAdd = ref(false)
const form = ref({ name: '', dayOfMonth: 1, type: 'bill', enabled: true })
const justAddedId = ref(null)

const systemReminders = computed(() => {
  const list = []
  // 英文版用 month-end;中文版保 末尾月(同理)
  const meSuffix = app.profile.locale === 'zh-CN' ? '月末' : 'month-end'
  list.push({ name: t('common.other') + ': ' + t('dashboard.netWorthTrend') + ' (' + meSuffix + ')', dayOfMonth: 28, type: 'review', enabled: true, system: true })
  list.push({ name: t('reminders.review'), dayOfMonth: 1, type: 'review', enabled: true, system: true })
  return list
})
const customReminders = computed(() => app.db.reminders)

const typeOptions = [
  { label: t('reminders.bill'), value: 'bill' },
  { label: t('reminders.review'), value: 'review' },
  { label: t('reminders.custom'), value: 'custom' }
]

function submit() {
  if (!form.value.name) return message.warning(t('reminders.nameHint'))
  const row = app.add('reminders', {
    name: form.value.name, dayOfMonth: Number(form.value.dayOfMonth), type: form.value.type, enabled: true
  })
  fireSave(t('reminders.saved'))
  justAddedId.value = row.id
  setTimeout(() => (justAddedId.value = null), 1600)
  showAdd.value = false
}

const columns = computed(() => [
  { title: t('reminders.name'), key: 'name' },
  { title: t('reminders.dayOfMonth'), key: 'dayOfMonth', render: (r) => r.dayOfMonth + (app.profile.locale === 'zh-CN' ? ' 日' : '') },
  { title: t('reminders.type'), key: 'type', render: (r) => typeTag(r.type) },
  {
    title: t('reminders.enabled'),
    key: 'enabled',
    render: (r) => (r.enabled ? h(NTag, { type: 'success' }, () => 'ON') : h(NTag, {}, () => 'OFF'))
  },
  {
    title: '',
    key: 'op',
    render: (r) =>
      r.id
        ? h(
            NPopconfirm,
            { onPositiveClick: () => app.remove('reminders', r.id) },
            { trigger: () => h(NButton, { size: 'small', type: 'error', quaternary: true }, () => t('common.delete')), default: () => t('common.deleteConfirm') }
          )
        : null
  }
])
const rowProps = (r) => ({ class: r.id === justAddedId.value ? 'row-just-added' : '' })
function typeTag(tp) {
  const map = { bill: ['warning', t('reminders.bill')], review: ['info', t('reminders.review')], custom: ['default', t('reminders.custom')] }
  const [type, label] = map[tp] || ['default', tp]
  return h(NTag, { type }, () => label)
}
</script>

<template>
  <div>
    <NCard :title="t('reminders.title')">
      <template #header-extra>
        <NButton type="primary" size="small" @click="showAdd = true">{{ t('reminders.addRem') }}</NButton>
      </template>
      <NSpace vertical :size="16">
        <div>
          <NText strong>{{ t('reminders.system') }}</NText>
          <NDataTable :columns="columns" :data="systemReminders" size="small" :row-key="(r) => r.name" />
        </div>
        <div>
          <NText strong>{{ t('reminders.customRem') }}</NText>
          <NDataTable :columns="columns" :data="customReminders" :row-props="rowProps" size="small" :row-key="(r) => r.id">
            <template #empty>
              <div class="tbl-empty"><NEmpty :description="t('reminders.emptyCustom')" /></div>
            </template>
          </NDataTable>
        </div>
      </NSpace>
    </NCard>

    <AppModal v-model:show="showAdd" :title="t('reminders.addRem')" :card-style="{ width: '460px', maxWidth: '92vw' }">
      <NForm :model="form">
        <NFormItem :label="t('reminders.name')"><NInput v-model:value="form.name" /></NFormItem>
        <NSpace>
          <NFormItem :label="t('reminders.dayOfMonth')"><NInputNumber v-model:value="form.dayOfMonth" :min="1" :max="31" /></NFormItem>
          <NFormItem :label="t('reminders.type')"><NSelect v-model:value="form.type" :options="typeOptions" style="width: 140px" /></NFormItem>
        </NSpace>
        <NButton type="primary" block @click="submit">{{ t('common.save') }}</NButton>
      </NForm>
    </AppModal>
  </div>
</template>

<style scoped>
.tbl-empty { padding: 28px 0; }
</style>
