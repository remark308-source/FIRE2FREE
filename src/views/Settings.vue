<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  NCard, NForm, NFormItem, NInput, NInputNumber, NDatePicker, NSelect, NButton, NSpace, NGrid, NGi,
  NDivider, NText, useMessage, NPopconfirm, NUpload, NRadioGroup, NRadioButton
} from 'naive-ui'
import AppModal from '@/components/AppModal.vue'
import { useAppStore } from '@/stores/app'
import { CURRENCIES } from '@/constants'
import { exportJson, toCsv, downloadFile } from '@/storage'
import { fmtMoney } from '@/composables/format'
import dayjs from 'dayjs'

const { t } = useI18n()
const app = useAppStore()
const message = useMessage()
const base = computed(() => app.baseCurrency)

const profile = computed(() => app.profile)
const currencyOptions = computed(() => CURRENCIES.map((c) => ({
  label: `${c.code} ${app.profile.locale === 'zh-CN' ? c.zh : c.en}`,
  value: c.code
})))

// 录入模式切换(切换前弹确认,历史保留、当月用原模式、下月生效)
const modeDraft = ref(app.profile.entryMode || 'daily')
const showModeModal = ref(false)
const pendingMode = ref(null)
function onModeChange(v) {
  pendingMode.value = v
  showModeModal.value = true
}
function confirmMode() {
  app.updateProfile({ entryMode: pendingMode.value })
  modeDraft.value = pendingMode.value
  showModeModal.value = false
  message.success(t('common.save'))
}
function cancelMode() {
  modeDraft.value = app.profile.entryMode || 'daily'
  showModeModal.value = false
}

// NDatePicker 需要时间戳;profile.startDate 存 'YYYY-MM-DD'
const startDateTs = computed({
  get: () => (profile.value.startDate ? dayjs(profile.value.startDate).valueOf() : Date.now()),
  set: (v) => { profile.value.startDate = dayjs(v).format('YYYY-MM-DD') }
})

function save() {
  app.updateProfile({ ...profile.value, initialAssets: Number(profile.value.initialAssets || 0) })
  message.success('已保存')
}

function setFx(code, val) {
  const fx = { ...app.profile.fxRates, [code]: Number(val) || 1 }
  app.updateProfile({ fxRates: fx })
}

function doExportJson() {
  downloadFile('fire-backup.json', exportJson(app.db))
  message.success('已导出 JSON')
}
function doExportCsv() {
  const cols = [
    { key: 'date', label: 'Date' }, { key: 'type', label: 'Type' }, { key: 'category', label: 'Category' },
    { key: 'amount', label: 'Amount' }, { key: 'currency', label: 'Currency' }, { key: 'note', label: 'Note' }
  ]
  const rows = [...app.db.incomes, ...app.db.expenses].map((r) => ({ ...r }))
  downloadFile('fire-records.csv', toCsv(rows, cols), 'text/csv')
  message.success('已导出 CSV')
}
function handleImport({ file }) {
  const reader = new FileReader()
  reader.onload = () => {
    try {
      const obj = JSON.parse(reader.result)
      app.importJson(obj)
      message.success('导入成功')
    } catch (e) {
      message.error('JSON 解析失败')
    }
  }
  reader.readAsText(file.file)
  return false
}
function doReset() {
  app.resetAll()
  message.success('已重置')
}
</script>

<template>
  <div>
    <NGrid :cols="2" :x-gap="12" :y-gap="12" responsive="screen" item-responsive>
      <NGi span="2 m:1">
        <NCard :title="t('settings.profile')">
          <NForm :model="profile">
            <NFormItem :label="t('settings.name')"><NInput v-model:value="profile.name" :placeholder="t('settings.nameHint')" /></NFormItem>
            <NFormItem :label="t('settings.startDate')"><NDatePicker v-model:value="startDateTs" type="date" style="width: 100%" /></NFormItem>
            <NFormItem :label="t('settings.initialAssets')"><NInputNumber v-model:value="profile.initialAssets" :min="0" style="width: 100%" /></NFormItem>
            <NFormItem :label="t('settings.fireStatement')">
              <NInput v-model:value="profile.fireStatement" type="textarea" :rows="2" :placeholder="t('settings.fireStatementHint')" />
            </NFormItem>
            <NFormItem :label="t('settings.entryMode')">
              <NRadioGroup :value="modeDraft" @update:value="onModeChange">
                <NRadioButton value="daily">{{ t('settings.entryDaily') }}</NRadioButton>
                <NRadioButton value="monthly">{{ t('settings.entryMonthly') }}</NRadioButton>
              </NRadioGroup>
            </NFormItem>
            <NFormItem :label="t('settings.baseCurrency')"><NSelect v-model:value="profile.baseCurrency" :options="currencyOptions" /></NFormItem>
            <NFormItem :label="t('settings.fireMultiple')"><NInputNumber v-model:value="profile.fireMultiple" :min="1" :step="1" style="width: 100%" /></NFormItem>
            <NFormItem :label="t('settings.conservative')"><NInputNumber v-model:value="profile.returnRates.conservative" :min="0" :max="0.3" :step="0.01" style="width: 100%" /></NFormItem>
            <NFormItem :label="t('settings.neutral')"><NInputNumber v-model:value="profile.returnRates.neutral" :min="0" :max="0.3" :step="0.01" style="width: 100%" /></NFormItem>
            <NFormItem :label="t('settings.optimistic')"><NInputNumber v-model:value="profile.returnRates.optimistic" :min="0" :max="0.3" :step="0.01" style="width: 100%" /></NFormItem>
            <NButton type="primary" @click="save">{{ t('common.save') }}</NButton>
          </NForm>
        </NCard>
      </NGi>

      <NGi span="2 m:1">
        <NCard :title="t('settings.fxRates')">
          <NText depth="3" style="font-size: 12px">{{ t('settings.fxHint') }}</NText>
          <NGrid :cols="2" :x-gap="8" style="margin-top: 8px">
            <NGi v-for="c in CURRENCIES.filter((x) => x.code !== 'CNY')" :key="c.code">
              <NFormItem :label="c.code + ' → CNY'">
                <NInputNumber :value="profile.fxRates[c.code]" :min="0" :step="0.01" @update:value="(v) => setFx(c.code, v)" />
              </NFormItem>
            </NGi>
          </NGrid>

          <NDivider />
          <NCard :title="t('settings.data')" size="small">
            <NSpace vertical>
              <NButton @click="doExportJson">{{ t('settings.exportJson') }}</NButton>
              <NButton @click="doExportCsv">{{ t('settings.exportCsv') }}</NButton>
              <NUpload :show-file-list="false" accept=".json" :before-upload="handleImport">
                <NButton>{{ t('settings.importJson') }}</NButton>
              </NUpload>
              <NPopconfirm @positive-click="doReset">
                <template #trigger><NButton type="error">{{ t('settings.reset') }}</NButton></template>
                {{ t('common.deleteConfirm') }}
              </NPopconfirm>
            </NSpace>
          </NCard>
        </NCard>
      </NGi>
    </NGrid>

    <AppModal
      v-model:show="showModeModal"
      :title="t('settings.modeSwitchTitle')"
      :card-style="{ width: '420px', maxWidth: '92vw' }"
    >
      <p class="app-modal-text">{{ t('settings.modeSwitchHint') }}</p>
      <template #footer>
        <NSpace justify="end">
          <NButton @click="cancelMode">{{ t('common.cancel') }}</NButton>
          <NButton type="primary" @click="confirmMode">{{ t('common.confirm') }}</NButton>
        </NSpace>
      </template>
    </AppModal>
  </div>
</template>
