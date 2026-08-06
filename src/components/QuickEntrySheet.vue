<script setup>
/**
 * 记一笔 全屏 Modal(参考 MoneyFlow 风格)
 *
 * 与 NDrawer bottom-sheet 方案的区别:
 *   - 全屏(fixed inset:0),覆盖底栏,内部不再滚动 — 单屏可见
 *   - 类型切换 + 金额(点 NInputNumber 弹系统键盘) + 8 类精简网格
 *     + 备注 + 日期 + 底部固定保存按钮
 *   - 分类精简到 8 个(MoneyFlow 风格:餐饮/交通/购物/娱乐/居住/医疗/教育/其他),
 *     录入数据写入对应原 key 以保持向后兼容;旧数据非 8 个之内的原 key 保留
 *
 * 数据约束:
 *   - 支出 category 用 8 个精简 key(其他 7 个原 key 折入"其他")
 *   - 收入 category 保留原 4 个(工资/奖金/副业/其他)
 *   - monthly 模式走单笔 isMonthlyTotal 记录(同 Income/Expense 月版)
 */
import { computed, ref, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { NInput, NDatePicker, NInputNumber, useMessage } from 'naive-ui'
import { useAppStore } from '@/stores/app'
import { fireSave } from '@/composables/saveFx'
import dayjs from 'dayjs'

const props = defineProps({ show: { type: Boolean, default: false } })
const emit = defineEmits(['update:show'])
const { t } = useI18n()
const app = useAppStore()
const message = useMessage()

const entryMode = computed(() => app.profile.entryMode)
const base = computed(() => app.baseCurrency)

const type = ref('expense') // 'expense' | 'income'
const amount = ref(null) // NInputNumber 双向绑定
const selectedCat = ref(null)
const note = ref('')
const date = ref(Date.now())
const monthTotal = ref(null)
const amountInputRef = ref(null) // 用于点金额聚焦

const proxyShow = computed({
  get: () => props.show,
  set: (v) => emit('update:show', v)
})

// === 分类(从 store 取,自动合并 constants + 用户自定义) ===
// 支出完整列表(constants.expenseDaily 15 项),其他旧 key 也保留;
// 收入保持原 4 项(salary/bonus/side_hustle/other)
const labelOf = (c) => (app.profile.locale === 'zh-CN' ? c.zh : c.en)
const catList = computed(() =>
  type.value === 'income'
    ? [
        { key: 'salary',      zh: '工资', en: 'Salary' },
        { key: 'bonus',       zh: '奖金', en: 'Bonus' },
        { key: 'side_hustle', zh: '副业', en: 'Side Hustle' },
        { key: 'other',       zh: t('common.other'), en: t('common.other') }
      ]
    : (app.categories?.expenseDaily || [])
)

// 分类色板(8 类,4 列)
const palette = ['#FF8A3D', '#5B8DEF', '#FF6B9D', '#7B61FF', '#18a058', '#E9533B', '#36ad6a', '#C147E9']
const catColor = (i) => palette[i % palette.length]
// 缩写:用第一字(zh) 或 第一字母(en)
const catAbbr = (c) => app.profile.locale === 'zh-CN' ? c.zh.charAt(0) : c.en.charAt(0)

function reset() {
  type.value = 'expense'
  amount.value = null
  selectedCat.value = null
  note.value = ''
  date.value = Date.now()
  monthTotal.value = null
}
watch(() => props.show, (v) => { if (v) reset() })

function setType(tp) {
  type.value = tp
  selectedCat.value = null
}

// 点金额区域:聚焦到 NInputNumber 的隐藏 input,弹系统键盘
function focusAmount() {
  // NInputNumber 把 input 元素放在 .n-input__input-el;聚焦到容器内首个 input
  const el = document.querySelector('.qe-amount-input input')
  if (el) el.focus()
}

function save() {
  if (entryMode.value === 'monthly') {
    if (!monthTotal.value || Number(monthTotal.value) <= 0) return message.warning(t('common.inputAmount'))
    const ym = dayjs().format('YYYY-MM')
    const lastDay = dayjs().endOf('month').format('YYYY-MM-DD')
    const coll = type.value === 'income' ? 'incomes' : 'expenses'
    const existing = app.db[coll].find((r) => r.isMonthlyTotal && dayjs(r.date).format('YYYY-MM') === ym)
    const payload = {
      type: type.value === 'income' ? 'active' : 'daily',
      date: lastDay,
      category: type.value === 'income' ? 'salary' : 'food',
      amount: Number(monthTotal.value),
      currency: base.value,
      note: ''
    }
    if (existing) app.update(coll, existing.id, payload)
    else app.add(coll, { ...payload, isMonthlyTotal: true })
    fireSave(t('common.saved'))
    proxyShow.value = false
    return
  }
  if (!amount.value || Number(amount.value) <= 0) return message.warning(t('common.inputAmount'))
  if (!selectedCat.value) return message.warning(t('quick.pickCategory'))
  const coll = type.value === 'income' ? 'incomes' : 'expenses'
  app.add(coll, {
    type: type.value === 'income' ? 'active' : 'daily',
    date: dayjs(date.value).format('YYYY-MM-DD'),
    category: selectedCat.value,
    amount: Number(amount.value),
    currency: base.value,
    note: note.value
  })
  fireSave(t('common.saved'))
  proxyShow.value = false
}
</script>

<template>
  <Teleport to="body">
    <div v-if="proxyShow" class="qe-root" role="dialog" aria-modal="true">
      <div class="qe-mask" @click.self="proxyShow = false" />

      <div class="qe-card">
        <!-- 顶部条:标题 + 关闭 -->
        <div class="qe-head">
          <h3 class="qe-title">{{ t('quick.title') }}</h3>
          <button class="qe-close" type="button" :aria-label="t('common.cancel')" @click="proxyShow = false">✕</button>
        </div>

        <!-- 类型切换 -->
        <div class="qe-type">
          <button :class="['qe-type-btn', type === 'expense' && 'expense active']" type="button" @click="setType('expense')">
            {{ t('quick.expense') }}
          </button>
          <button :class="['qe-type-btn', type === 'income' && 'income active']" type="button" @click="setType('income')">
            {{ t('quick.income') }}
          </button>
        </div>

        <!-- 中部可滚动区 -->
        <div class="qe-body">
          <template v-if="entryMode !== 'monthly'">
            <!-- 金额(点击聚焦,弹系统键盘) -->
            <div class="qe-amount" :class="{ filled: amount }" @click="focusAmount">
              <span class="qe-cur">{{ base }}</span>
              <NInputNumber
                ref="amountInputRef"
                v-model:value="amount"
                :min="0"
                :precision="2"
                :show-button="false"
                :placeholder="'0.00'"
                :bordered="false"
                class="qe-amount-input"
              />
            </div>
            <p class="qe-amount-hint">{{ t('quick.addHint') }}</p>

            <!-- 分类网格 4 列 8 项 -->
            <p class="qe-cats-label">{{ t('quick.pickCategory') }}</p>
            <div class="qe-cat-grid">
              <button
                v-for="(c, i) in catList"
                :key="c.key"
                :class="['qe-cat', selectedCat === c.key && 'sel']"
                type="button"
                @click="selectedCat = c.key"
              >
                <span class="qe-cat-ic" :style="{ background: catColor(i) }">{{ catAbbr(c) }}</span>
                <span class="qe-cat-name">{{ labelOf(c) }}</span>
              </button>
            </div>

            <!-- 备注 + 日期(2 列紧凑) -->
            <div class="qe-row">
              <NInput v-model:value="note" :placeholder="t('common.note')" class="qe-note" />
              <NDatePicker v-model:value="date" type="date" class="qe-date" />
            </div>
          </template>

          <!-- 月总额模式 -->
          <template v-else>
            <div class="qe-month">
              <p class="qe-month-label">{{ t('quick.monthTotal') }}</p>
              <NInputNumber
                v-model:value="monthTotal"
                :min="0"
                :precision="2"
                :placeholder="t('common.inputAmount')"
                class="qe-month-input"
              />
            </div>
          </template>
        </div>

        <!-- 底部固定:保存按钮 -->
        <div class="qe-foot">
          <button class="qe-save" type="button" @click="save">{{ t('common.save') }}</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style>
/* ===== 记一笔 全屏 Modal(参考 MoneyFlow 风格) ===== */
.qe-root {
  position: fixed;
  inset: 0;
  z-index: 1300; /* 高于 SideSheet (1200) */
  display: flex;
  align-items: stretch;
  justify-content: stretch;
  animation: qeFadeIn 0.18s ease;
}
@keyframes qeFadeIn { from { opacity: 0; } to { opacity: 1; } }

.qe-mask {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  -webkit-backdrop-filter: blur(2px);
  backdrop-filter: blur(2px);
}

.qe-card {
  position: relative;
  width: 100vw;
  height: 100vh;
  max-width: 480px; /* 平板/桌面端不撑全宽,居中卡片 */
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  background: var(--qe-bg, #1b1f33);
  color: var(--qs-text, #e6e8f0);
  animation: qeSlideUp 0.22s cubic-bezier(0.2, 0.8, 0.2, 1);
}
@keyframes qeSlideUp {
  from { transform: translateY(20px); opacity: 0.6; }
  to { transform: translateY(0); opacity: 1; }
}
.theme-light .qe-card { background: #f6f7fb; }

/* 顶部 */
.qe-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: calc(12px + env(safe-area-inset-top)) 18px 10px;
  flex-shrink: 0;
}
.qe-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
}
.qe-close {
  width: 32px; height: 32px;
  border-radius: 50%;
  border: none;
  background: rgba(125, 125, 140, 0.16);
  color: inherit;
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
  transition: transform 0.1s ease, background 0.15s ease;
}
.qe-close:active { transform: scale(0.9); }

/* 类型切换 */
.qe-type {
  display: flex;
  gap: 6px;
  margin: 4px 16px 12px;
  background: rgba(125, 125, 140, 0.12);
  border-radius: 12px;
  padding: 4px;
  flex-shrink: 0;
}
.qe-type-btn {
  flex: 1;
  padding: 11px;
  border: none;
  border-radius: 9px;
  font-size: 15px;
  font-weight: 600;
  background: transparent;
  color: #9aa0b4;
  cursor: pointer;
  transition: all 0.2s ease;
}
.qe-type-btn.expense.active {
  background: linear-gradient(135deg, #FF6B35 0%, #E9533B 100%);
  color: #fff;
}
.qe-type-btn.income.active {
  background: linear-gradient(135deg, #18a058 0%, #36ad6a 100%);
  color: #fff;
}

/* 中部可滚动 */
.qe-body {
  flex: 1;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  padding: 0 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 金额区(点聚焦) */
.qe-amount {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 8px;
  padding: 10px 0 0;
  cursor: text;
  min-height: 70px;
}
.qe-cur {
  font-size: 16px;
  font-weight: 600;
  opacity: 0.6;
}
.qe-amount-input {
  font-variant-numeric: tabular-nums;
}
.qe-amount-input :deep(.n-input) {
  font-size: 38px;
  font-weight: 800;
  letter-spacing: -0.5px;
  text-align: center;
  background: transparent !important;
}
.qe-amount-input :deep(.n-input__input-el),
.qe-amount-input :deep(input) {
  font-size: 38px !important;
  font-weight: 800 !important;
  text-align: center;
  padding: 0 !important;
  background: transparent !important;
  color: inherit;
}
.qe-amount.filled .qe-amount-input :deep(.n-input__input-el) {
  color: #5B8DEF;
}
.theme-light .qe-amount.filled .qe-amount-input :deep(.n-input__input-el) {
  color: #3b6fe0;
}
.qe-amount-hint {
  font-size: 11px;
  text-align: center;
  margin: 0 0 4px;
  opacity: 0.5;
}

/* 分类标题 */
.qe-cats-label {
  font-size: 12px;
  margin: 4px 0 6px;
  opacity: 0.6;
  padding: 0 2px;
}

/* 分类网格 4 列 8 项 = 2 行 */
.qe-cat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-bottom: 6px;
}
.qe-cat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  padding: 9px 4px;
  border-radius: 12px;
  background: rgba(125, 125, 140, 0.08);
  border: 1.5px solid transparent;
  cursor: pointer;
  transition: all 0.18s ease;
}
.qe-cat:active { transform: scale(0.95); }
.qe-cat.sel {
  background: rgba(91, 141, 239, 0.16);
  border-color: #5B8DEF;
}
.qe-cat-ic {
  width: 36px;
  height: 36px;
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  color: #fff;
}
.qe-cat-name {
  font-size: 11.5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  color: #e6e8f0;
  font-weight: 500;
}
.theme-light .qe-cat-name { color: #1a1a1a; }

/* 备注 + 日期(2 列) */
.qe-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin: 4px 0 8px;
}
.qe-note, .qe-date { margin: 0; }

/* 月总额 */
.qe-month { padding: 20px 2px; }
.qe-month-label { font-size: 13px; opacity: 0.6; margin: 0 0 10px; }
.qe-month-input { width: 100%; }

/* 底部固定保存 */
.qe-foot {
  flex-shrink: 0;
  padding: 12px 16px calc(14px + env(safe-area-inset-bottom));
  background: var(--qe-bg, #1b1f33);
  border-top: 1px solid rgba(125, 125, 140, 0.12);
}
.theme-light .qe-foot { background: #f6f7fb; }
.qe-save {
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: 14px;
  background: linear-gradient(135deg, #5B8DEF 0%, #7B61FF 100%);
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 8px 20px -6px rgba(91, 141, 239, 0.55);
  transition: transform 0.12s ease, opacity 0.15s ease;
}
.qe-save:active { transform: scale(0.98); opacity: 0.92; }
.qe-save:disabled { opacity: 0.5; cursor: not-allowed; }

/* 极小屏(iPhone SE 5.4" = 320×568)收紧 */
@media (max-height: 600px) {
  .qe-amount { min-height: 56px; padding-top: 4px; }
  .qe-amount-input :deep(.n-input__input-el),
  .qe-amount-input :deep(input) { font-size: 32px !important; }
  .qe-cat { padding: 7px 4px; }
  .qe-cat-ic { width: 32px; height: 32px; }
  .qe-type-btn { padding: 9px; font-size: 14px; }
}
</style>
