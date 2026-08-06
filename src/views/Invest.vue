<script setup>
import { computed, h, ref, reactive, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import dayjs from 'dayjs'
import {
  NCard, NSpace, NButton, NForm, NFormItem, NInput, NSelect,
  NInputNumber, NDatePicker, NTag, NEmpty, NDataTable, NText, NIcon,
  NDropdown, useMessage
} from 'naive-ui'
import AppModal from '@/components/AppModal.vue'
import ChartBox from '@/components/ChartBox.vue'
import { useAppStore } from '@/stores/app'
import { useAggregate } from '@/composables/aggregate'
import { CATEGORIES, CURRENCIES } from '@/constants'
import { toBase } from '@/finance'
import { fmtMoney, fmtCompact } from '@/composables/format'
import IconInvest from '@/components/icons/IconInvest.vue'
import IconMoney from '@/components/icons/IconMoney.vue'

const { t } = useI18n()
const app = useAppStore()
const agg = useAggregate()
const { investValueSeries } = agg
const message = useMessage()
const base = computed(() => app.baseCurrency)

// 当前语系下的紧凑货币(避免每个 fmtCompact 调用都重复传 locale)
const fmtL = (v, c) => fmtCompact(v, c, app.profile.locale)
const fx = computed(() => app.fxRates)
const isZh = computed(() => app.profile.locale === 'zh-CN')

const catLabel = (c) => (isZh.value ? c.zh : c.en)
const typeOptions = CATEGORIES.accountType.map((c) => ({ label: catLabel(c), value: c.key }))
const typeMap = Object.fromEntries(CATEGORIES.accountType.map((c) => [c.key, c]))
const currencyOptions = CURRENCIES.map((c) => ({ label: `${c.code} ${isZh.value ? c.zh : c.en}`, value: c.code }))

const accounts = computed(() => app.db.accounts)

// 顶部汇总(复用 aggregate,全部折算基准币种)
const summary = computed(() => ({
  value: agg.totalInvestValue.value,
  cost: agg.totalCostBasis.value,
  pl: agg.investPLTotal.value,
  count: accounts.value.length
}))

// 市值走势图(从 Dashboard 投资区块迁入)
const investValueData = computed(() => ({
  x: investValueSeries.value.map((d) => d.ym),
  series: [{
    key: 'value',
    label: t('dashboard.investValueTrend'),
    color: '#7B61FF',
    data: investValueSeries.value.map((d) => Math.round(d.value))
  }]
}))

// 每个账户的视图:最新市值(基准)、快照排序、月度盈亏
const accountViews = computed(() =>
  accounts.value.map((acc) => {
    const snaps = app.db.snapshots
      .filter((s) => s.accountId === acc.id)
      .sort((a, b) => a.yearMonth.localeCompare(b.yearMonth))
    let latest = null
    let latestBase = 0
    const rows = snaps.map((s, i) => {
      const prev = snaps[i - 1]
      let pl
      if (!prev) {
        // 首条快照:用账户基线 openingValue(老账户回退首条 value),首月即显示累计收益
        const opening = Number((acc.openingValue ?? s.value) || 0)
        pl = Number(s.value || 0) - opening
      } else {
        pl = Number(s.value || 0) - Number(prev.value || 0) - Number(s.netInflow || 0)
      }
      if (!latest || s.yearMonth > latest.yearMonth) {
        latest = s
        latestBase = toBase(Number(s.value || 0), s.currency || acc.currency, base.value, fx.value)
      }
      return { ...s, pl }
    })
    return { acc, latestBase, latestMonth: latest ? latest.yearMonth : null, rows }
  })
)

// 千分位实时格式化:display 用 toLocaleString(3 位逗号),
// parser 反向剥除逗号恢复数值,保证键盘录入与显示同步。
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

// ---------- 账户弹窗 ----------
const accountShow = ref(false)
const accountForm = ref({ id: null, name: '', type: 'a_share', currency: 'CNY', note: '', marketValue: null, holdingPL: null })
function openAccount(acc) {
  if (acc) {
    const snaps = app.db.snapshots
      .filter((s) => s.accountId === acc.id)
      .sort((a, b) => a.yearMonth.localeCompare(b.yearMonth))
    const latest = snaps[snaps.length - 1]
    const mv = latest ? latest.value : (acc.openingValue != null ? acc.openingValue : null)
    const pl = latest && acc.openingValue != null ? latest.value - acc.openingValue : (acc.openingValue != null && !latest ? 0 : null)
    accountForm.value = {
      id: acc.id, name: acc.name, type: acc.type, currency: acc.currency, note: acc.note || '',
      marketValue: mv, holdingPL: pl
    }
  } else {
    accountForm.value = { id: null, name: '', type: 'a_share', currency: base.value, note: '', marketValue: null, holdingPL: null }
  }
  accountShow.value = true
}
function saveAccount() {
  const f = accountForm.value
  if (!f.name.trim()) {
    message.warning(isZh.value ? '请填写账户名' : 'Name required')
    return
  }
  // 目前市值 + 持仓盈亏 → 推导成本基线 openingValue(持仓盈亏仅用于推导,不单独存)
  let openingValue = null
  if (f.marketValue != null && f.marketValue !== '') {
    const mv = Number(f.marketValue)
    const pl = Number(f.holdingPL || 0)
    if (pl > mv) {
      message.warning(isZh.value ? '持仓盈亏不能超过目前市值,请复核' : 'Holding P/L cannot exceed current value')
      return
    }
    openingValue = mv - pl
  }
  const patch = { name: f.name.trim(), type: f.type, currency: f.currency, note: f.note }
  if (openingValue != null) patch.openingValue = openingValue
  if (f.id) {
    app.update('accounts', f.id, patch)
    // 编辑:若账户尚无快照,补一条首月净值(seed 基线),避免账户一直空白
    const hasSnap = app.db.snapshots.some((s) => s.accountId === f.id)
    if (!hasSnap && openingValue != null) {
      app.upsertSnapshot({ accountId: f.id, yearMonth: dayjs().format('YYYY-MM'), value: Number(f.marketValue), currency: f.currency, netInflow: 0 })
    }
  } else {
    const row = app.add('accounts', patch)
    // 新建:自动写入首月净值快照,使账户立即显示市值与持仓盈亏(首月 pl = 持仓盈亏)
    if (openingValue != null) {
      app.upsertSnapshot({ accountId: row.id, yearMonth: dayjs().format('YYYY-MM'), value: Number(f.marketValue), currency: f.currency, netInflow: 0 })
    }
  }
  accountShow.value = false
  message.success(isZh.value ? '已保存' : 'Saved')
}
function delAccount(acc) {
  const count = app.db.snapshots.filter((s) => s.accountId === acc.id).length
  const content = (isZh.value ? '将同时删除该账户的 ' : 'This also deletes ') +
    count + (isZh.value ? ' 条净值记录,不可撤销。' : ' snapshots. Cannot be undone.')
  askConfirm(
    isZh.value ? '删除账户' : 'Delete Account',
    content,
    () => {
      app.removeAccount(acc.id)
      message.success(isZh.value ? '已删除' : 'Deleted')
    }
  )
}

// ---------- 快照弹窗 ----------
const snapShow = ref(false)
const snapTarget = ref(null) // 账户
const snapForm = ref({ yearMonth: '', monthTs: null, value: null, netInflow: 0, editingId: null })
function openSnap(acc, snap) {
  snapTarget.value = acc
  if (snap) {
    snapForm.value = {
      yearMonth: snap.yearMonth,
      monthTs: dayjs(snap.yearMonth + '-01').valueOf(),
      value: snap.value,
      netInflow: snap.netInflow || 0,
      editingId: snap.id
    }
  } else {
    snapForm.value = {
      yearMonth: '',
      monthTs: dayjs().startOf('month').valueOf(),
      value: null,
      netInflow: 0,
      editingId: null
    }
  }
  snapShow.value = true
}
function saveSnap() {
  const f = snapForm.value
  const acc = snapTarget.value
  if (f.value == null || f.value === '') {
    message.warning(isZh.value ? '请填写期末市值' : 'End value required')
    return
  }
  const ym = dayjs(f.monthTs).format('YYYY-MM')
  app.upsertSnapshot({
    accountId: acc.id,
    yearMonth: ym,
    value: Number(f.value),
    currency: acc.currency,
    netInflow: Number(f.netInflow || 0)
  })
  snapShow.value = false
  message.success(isZh.value ? '已记录' : 'Logged')
}
function delSnap(snap) {
  askConfirm(
    isZh.value ? '删除快照' : 'Delete Snapshot',
    t('common.deleteConfirm'),
    () => {
      app.remove('snapshots', snap.id)
      message.success(isZh.value ? '已删除' : 'Deleted')
    }
  )
}

// 自定义确认弹窗(替代 naive-ui NDialog,规避 vue3.5 FocusTrap 崩溃)
const showConfirm = ref(false)
const confirmState = ref({ title: '', content: '', onOk: () => {} })
function askConfirm(title, content, onOk) {
  confirmState.value = { title, content, onOk }
  showConfirm.value = true
}
function onConfirmOk() {
  confirmState.value.onOk?.()
  showConfirm.value = false
}

// ---------- 展开状态 ----------
// 用 reactive Set 支持多账户同时展开(取消手风琴联动)。
// 默认全部展开,新账户自动跟随加入;用户点"收起"才从 Set 里移除。
const expanded = reactive(new Set())
watch(
  accountViews,
  (views) => { views.forEach((v) => expanded.add(v.acc.id)) },
  { immediate: true, flush: 'post' }
)
function toggle(accId) {
  if (expanded.has(accId)) expanded.delete(accId)
  else expanded.add(accId)
}

// 「编辑/删除/收起」下拉选单的处理
function onMenuSelect(acc, key) {
  if (key === 'edit') openAccount(acc)
  else if (key === 'delete') delAccount(acc)
  else if (key === 'toggle') toggle(acc.id)
}
function buildMenuOptions(acc) {
  const isOpen = expanded.has(acc.id)
  return [
    { label: t('common.edit'), key: 'edit' },
    { label: t('common.delete'), key: 'delete' },
    { type: 'divider', key: 'd1' },
    { label: isOpen ? (isZh.value ? '收起' : 'Collapse') : (isZh.value ? '展开' : 'Expand'), key: 'toggle' }
  ]
}

function buildColumns(acc) {
  const cur = acc.currency
  return [
    { title: t('common.month'), key: 'yearMonth', width: 86 },
    {
      title: t('accounts.value'),
      key: 'value',
      render: (row) => h(NText, { strong: true }, { default: () => fmtMoney(row.value, cur) })
    },
    {
      title: t('accounts.netInflow'),
      key: 'netInflow',
      render: (row) => fmtMoney(row.netInflow || 0, cur)
    },
    {
      title: isZh.value ? '当月盈亏' : 'P/L',
      key: 'pl',
      render: (row) =>
        h(
          'span',
          { style: { color: row.pl >= 0 ? '#E9533B' : '#18a058', fontWeight: 700 } },
          { default: () => (row.pl >= 0 ? '+' : '') + fmtMoney(row.pl, cur) }
        )
    },
    {
      title: '',
      key: 'actions',
      width: 88,
      render: (row) =>
        h(NSpace, { size: 4 }, () => [
          h(
            NButton,
            { size: 'tiny', tertiary: true, onClick: () => openSnap(acc, row) },
            { default: () => '✎' }
          ),
          h(
            NButton,
            { size: 'tiny', tertiary: true, type: 'error', onClick: () => delSnap(row) },
            { default: () => '×' }
          )
        ])
    }
  ]
}
</script>

<template>
  <div class="invest-page">
    <!-- 顶部汇总 -->
    <NSpace :wrap="true" :size="16" class="stat-row">
      <NCard size="small" class="stat-card grad-blue" :bordered="false">
        <div class="stat-top">{{ t('dashboard.investedValue') }}</div>
        <div class="stat-num">{{ fmtL(summary.value, base) }}</div>
      </NCard>
      <NCard size="small" class="stat-card grad-green" :bordered="false">
        <div class="stat-top">{{ isZh ? '累计净投入' : 'Net Invested' }}</div>
        <div class="stat-num">{{ fmtL(summary.cost, base) }}</div>
      </NCard>
      <NCard size="small" class="stat-card grad-violet" :bordered="false">
        <div class="stat-top">{{ isZh ? '累计浮盈亏' : 'Total P/L' }}</div>
        <div class="stat-num" :style="{ color: summary.pl >= 0 ? '#E9533B' : '#18a058' }">
          {{ summary.pl >= 0 ? '+' : '' }}{{ fmtL(summary.pl, base) }}
        </div>
      </NCard>
      <NCard size="small" class="stat-card grad-orange" :bordered="false">
        <div class="stat-top">{{ t('accounts.title') }}</div>
        <div class="stat-num">{{ summary.count }}</div>
      </NCard>
    </NSpace>

    <!-- 市值走势(从 Dashboard 投资区块迁入) -->
    <NCard size="small" class="value-chart-card" :bordered="false" style="margin-bottom: 18px">
      <ChartBox
        :title="$t('dashboard.investValueTrend')"
        :data="investValueData"
        :types="['line', 'bar']"
        :default-type="'line'"
        height="200"
        :format-value="(v) => fmtL(v, base)"
      />
    </NCard>

    <!-- 账户区 -->
    <div class="section-head">
      <div class="section-title">
        <NIcon size="20" color="#7B61FF"><IconInvest /></NIcon>
        <span>{{ t('accounts.title') }}</span>
        <NText depth="3" style="font-size: 12px">{{ accounts.length }}</NText>
      </div>
      <NButton type="primary" @click="openAccount()">
        <template #icon><NIcon><IconMoney /></NIcon></template>
        {{ t('accounts.addAccount') }}
      </NButton>
    </div>

    <NEmpty v-if="!accounts.length" :description="t('common.invStart')" style="margin: 48px 0" />

    <div class="account-grid">
      <NCard
        v-for="v in accountViews"
        :key="v.acc.id"
        class="account-card"
        :bordered="false"
      >
        <div class="acc-head">
          <div class="acc-title">
            <span class="acc-name">{{ v.acc.name }}</span>
            <NTag size="small" :bordered="false" type="info">{{ catLabel(typeMap[v.acc.type] || { zh: v.acc.type, en: v.acc.type }) }}</NTag>
            <NTag size="small" :bordered="false">{{ v.acc.currency }}</NTag>
          </div>
          <NSpace :size="6" align="center">
            <NButton size="small" type="primary" ghost @click="openSnap(v.acc)">
              {{ t('common.addSnapshot') }}
            </NButton>
            <NDropdown
              trigger="click"
              :options="buildMenuOptions(v.acc)"
              @select="(k) => onMenuSelect(v.acc, k)"
            >
              <NButton size="small" quaternary circle aria-label="more">
                <template #icon>
                  <span style="font-size: 18px; line-height: 1">⋯</span>
                </template>
              </NButton>
            </NDropdown>
          </NSpace>
        </div>

        <div class="acc-value">{{ v.latestMonth ? fmtMoney(v.latestBase, base) : '—' }}</div>
        <div class="acc-sub">
          {{ v.latestMonth ? (isZh ? '最新 ' + v.latestMonth : 'Latest ' + v.latestMonth) : (isZh ? '尚无记录' : 'No record') }}
          · {{ v.rows.length }} {{ isZh ? '条快照' : 'snapshots' }}
        </div>

        <div v-if="expanded.has(v.acc.id)" class="acc-table">
          <NDataTable
            size="small"
            :columns="buildColumns(v.acc)"
            :data="v.rows"
            :row-key="(r) => r.id"
            :max-height="220"
            :scroll-x="360"
          />
        </div>
      </NCard>
    </div>

    <!-- 账户弹窗 -->
    <AppModal
      v-model:show="accountShow"
      :title="accountForm.id ? t('common.edit') + ' · ' + t('accounts.title') : t('accounts.addAccount')"
      :card-style="{ width: '460px', maxWidth: '92vw' }"
    >
      <NForm label-placement="top">
        <NFormItem :label="t('accounts.name')">
          <NInput v-model:value="accountForm.name" :placeholder="isZh ? '如:华泰证券 / Interactive Brokers' : 'e.g. Huatai / IBKR'" />
        </NFormItem>
        <NFormItem :label="t('accounts.type')">
          <NSelect v-model:value="accountForm.type" :options="typeOptions" />
        </NFormItem>
        <NFormItem :label="t('accounts.currency')">
          <NSelect v-model:value="accountForm.currency" :options="currencyOptions" />
        </NFormItem>
        <NFormItem :label="t('accounts.marketValue') + ' (' + accountForm.currency + ')'">
          <NInputNumber
            v-model:value="accountForm.marketValue"
            :min="0"
            style="width: 100%"
            :show-button="false"
            :placeholder="isZh ? '开户/当前总市值' : 'Current total value'"
            :format="numFmt"
            :parse="numParse"
          />
        </NFormItem>
        <NFormItem :label="t('accounts.holdingPL') + ' (' + accountForm.currency + ')'">
          <NInputNumber
            v-model:value="accountForm.holdingPL"
            style="width: 100%"
            :show-button="false"
            :placeholder="isZh ? '如:+20000 或 -5000' : 'e.g. +20000 or -5000'"
            :format="numFmt"
            :parse="numParse"
          />
        </NFormItem>
        <NFormItem>
          <NText depth="3" style="font-size: 12px; line-height: 1.5">{{ t('accounts.openingHint') }}</NText>
        </NFormItem>
        <NFormItem :label="t('accounts.note')">
          <NInput v-model:value="accountForm.note" type="textarea" :rows="2" />
        </NFormItem>
      </NForm>
      <template #footer>
        <NSpace justify="end">
          <NButton @click="accountShow = false">{{ t('common.cancel') }}</NButton>
          <NButton type="primary" @click="saveAccount">{{ t('common.save') }}</NButton>
        </NSpace>
      </template>
    </AppModal>

    <!-- 快照弹窗 -->
    <AppModal
      v-model:show="snapShow"
      :title="(snapForm.editingId ? t('common.edit') : t('common.addSnapshot')) + (snapTarget ? ' · ' + snapTarget.name : '')"
      :card-style="{ width: '460px', maxWidth: '92vw' }"
    >
      <NForm label-placement="top">
        <NFormItem :label="t('common.month')">
          <NDatePicker v-model:value="snapForm.monthTs" type="month" style="width: 100%" />
        </NFormItem>
        <NFormItem :label="t('accounts.value') + ' (' + (snapTarget ? snapTarget.currency : '') + ')'">
          <NInputNumber
            v-model:value="snapForm.value"
            :min="0"
            style="width: 100%"
            :show-button="false"
            :placeholder="isZh ? '请输入期末市值' : 'End value'"
            :format="numFmt"
            :parse="numParse"
          />
        </NFormItem>
        <NFormItem :label="t('accounts.netInflow') + ' (' + (snapTarget ? snapTarget.currency : '') + ')'">
          <NInputNumber
            v-model:value="snapForm.netInflow"
            style="width: 100%"
            :show-button="false"
            :placeholder="isZh ? '如:3000' : 'e.g. 3000'"
            :format="numFmt"
            :parse="numParse"
          />
        </NFormItem>
      </NForm>
      <template #footer>
        <NSpace justify="end">
          <NButton @click="snapShow = false">{{ t('common.cancel') }}</NButton>
          <NButton type="primary" @click="saveSnap">{{ t('common.save') }}</NButton>
        </NSpace>
      </template>
    </AppModal>

    <!-- 删除确认:自定义 overlay 替代 NDialog,规避 naive-ui FocusTrap 崩溃 -->
    <AppModal
      v-model:show="showConfirm"
      :title="confirmState.title"
      :card-style="{ width: '420px', maxWidth: '92vw' }"
    >
      <p class="app-modal-text">{{ confirmState.content }}</p>
      <template #footer>
        <NSpace justify="end">
          <NButton @click="showConfirm = false">{{ t('common.cancel') }}</NButton>
          <NButton type="error" @click="onConfirmOk">{{ t('common.confirm') }}</NButton>
        </NSpace>
      </template>
    </AppModal>
  </div>
</template>

<style scoped>
.invest-page { max-width: 1180px; margin: 0 auto; }
.stat-row { margin-bottom: 22px; }
.stat-card { flex: 1 1 200px; min-width: 180px; border-radius: 16px !important; color: #fff; }
.stat-top { font-size: 12px; opacity: 0.85; }
.stat-num { font-size: 26px; font-weight: 700; margin-top: 6px; letter-spacing: 0.5px; }
.grad-blue { background: var(--fire-grad-blue); }
.grad-green { background: var(--fire-grad-green); }
/* 累计浮盈亏:深紫底色,红字 #E9533B 与绿字 #18a058 都能保持 4.5:1 对比度 */
.grad-violet { background: var(--fire-grad-violet); }
.grad-orange { background: var(--fire-grad-orange); }

/* 移动端:4 张 stat 卡强制 2x2 网格(覆盖 NSpace 默认 200px min-width) */
@media (max-width: 640px) {
  .invest-page .stat-row {
    display: grid !important;
    grid-template-columns: 1fr 1fr !important;
    gap: 10px !important;
  }
  .invest-page .stat-card {
    flex: none !important;
    min-width: 0 !important;
  }
  .invest-page .stat-card :deep(.n-card__content) {
    padding: 14px 12px 12px !important;
  }
  .invest-page .stat-num { font-size: 19px !important; }
  .invest-page .stat-top { font-size: 11px !important; }
}

@media (max-width: 380px) {
  .invest-page .stat-num { font-size: 17px !important; }
}

.section-head { display: flex; align-items: center; justify-content: space-between; margin: 8px 0 16px; }
.section-title { display: inline-flex; align-items: center; gap: 8px; font-weight: 600; font-size: 16px; }
.account-grid { display: grid; grid-template-columns: minmax(0, 1fr); gap: 16px; }
.account-card { border-radius: 16px !important; }
.acc-head { display: flex; align-items: flex-start; justify-content: space-between; }
.acc-title { display: inline-flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.acc-name { font-weight: 700; font-size: 15px; }
.acc-value { font-size: 24px; font-weight: 700; margin-top: 10px; }
.acc-sub { font-size: 12px; opacity: 0.6; margin-top: 2px; }
.acc-table { margin-top: 12px; border-top: 1px solid rgba(128,128,128,0.18); padding-top: 10px; }
</style>
