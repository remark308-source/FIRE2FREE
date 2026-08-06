<script setup>
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  NDrawer, NDrawerContent, NInput, NDatePicker, NInputNumber, useMessage
} from 'naive-ui'
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
const amountInput = ref('')
const selectedCat = ref(null)
const note = ref('')
const date = ref(Date.now())
const monthTotal = ref(null)

const proxyShow = computed({
  get: () => props.show,
  set: (v) => emit('update:show', v)
})

const catList = computed(() =>
  type.value === 'income' ? app.categories.incomeActive : app.categories.expenseDaily
)
const labelOf = (c) => (c.key === 'other' ? t('common.other') : app.profile.locale === 'zh-CN' ? c.zh : c.en)

// 分类色板(按 index 取色,保证渐变一致)
const palette = ['#FF8A3D', '#5B8DEF', '#18a058', '#FF6B9D', '#7B61FF', '#FFA94D', '#36ad6a', '#C147E9']
const catColor = (i) => palette[i % palette.length]

function reset() {
  type.value = 'expense'
  amountInput.value = ''
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

// 自定义数字键盘(MoneyFlow 风格:3 列,带 tap 反馈)
function inputNum(n) {
  if (n === '.' && amountInput.value.includes('.')) return
  if (amountInput.value.replace('.', '').length >= 9) return
  if (amountInput.value === '0') amountInput.value = '' // 避免前导 0
  amountInput.value += n
}
function delNum() {
  amountInput.value = amountInput.value.slice(0, -1)
}
const amountNum = computed(() => {
  const v = parseFloat(amountInput.value)
  return Number.isFinite(v) ? v : 0
})
const amountDisplay = computed(() => {
  if (!amountInput.value) return '0.00'
  if (amountInput.value.endsWith('.')) return amountInput.value
  return amountNum.value.toFixed(2)
})

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
  if (!amountNum.value || amountNum.value <= 0) return message.warning(t('common.inputAmount'))
  if (!selectedCat.value) return message.warning(t('quick.pickCategory'))
  const coll = type.value === 'income' ? 'incomes' : 'expenses'
  app.add(coll, {
    type: type.value === 'income' ? 'active' : 'daily',
    date: dayjs(date.value).format('YYYY-MM-DD'),
    category: selectedCat.value,
    amount: amountNum.value,
    currency: base.value,
    note: note.value
  })
  fireSave(t('common.saved'))
  proxyShow.value = false
}

// 抽屉高度:占屏 90%,封顶 620px,内部滚动
const sheetH = computed(() => {
  const h = typeof window !== 'undefined' ? window.innerHeight : 800
  return Math.min(Math.round(h * 0.9), 620)
})
</script>

<template>
  <NDrawer v-model:show="proxyShow" placement="bottom" :height="sheetH" :auto-focus="false">
    <NDrawerContent :native-scrollbar="true" :closable="false" class="quick-sheet">
      <div class="qs-head">
        <h3 class="qs-title">{{ t('quick.title') }}</h3>
        <button class="qs-close" type="button" :aria-label="t('common.cancel')" @click="proxyShow = false">✕</button>
      </div>

      <!-- 类型切换 -->
      <div class="qs-type">
        <button :class="['qs-type-btn', type === 'expense' && 'expense active']" type="button" @click="setType('expense')">
          {{ t('quick.expense') }}
        </button>
        <button :class="['qs-type-btn', type === 'income' && 'income active']" type="button" @click="setType('income')">
          {{ t('quick.income') }}
        </button>
      </div>

      <!-- 逐笔模式:金额 + 分类 + 数字键盘 -->
      <template v-if="entryMode !== 'monthly'">
        <div class="qs-amount">
          <span class="qs-cur">{{ base }}</span>
          <span class="qs-amt">{{ amountDisplay }}</span>
        </div>

        <div class="qs-cats">
          <p class="qs-cats-label">{{ t('quick.pickCategory') }}</p>
          <div class="qs-cat-grid">
            <button
              v-for="(c, i) in catList"
              :key="c.key"
              :class="['qs-cat', selectedCat === c.key && 'sel']"
              type="button"
              @click="selectedCat = c.key"
            >
              <span class="qs-cat-ic" :style="{ background: catColor(i) }">{{ labelOf(c).charAt(0) }}</span>
              <span class="qs-cat-name">{{ labelOf(c) }}</span>
            </button>
          </div>
        </div>

        <div class="qs-pad">
          <button v-for="n in ['1', '2', '3', '4', '5', '6', '7', '8', '9']" :key="n" class="qs-num" type="button" @click="inputNum(n)">{{ n }}</button>
          <button class="qs-num" type="button" @click="inputNum('.')">.</button>
          <button class="qs-num" type="button" @click="inputNum('0')">0</button>
          <button class="qs-num qs-del" type="button" aria-label="delete" @click="delNum()">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 4H8l-4 4 4 4h13" /><line x1="18" y1="9" x2="12" y2="15" /><line x1="12" y1="9" x2="18" y2="15" />
            </svg>
          </button>
        </div>

        <NInput v-model:value="note" :placeholder="t('common.note')" class="qs-note" />
        <NDatePicker v-model:value="date" type="date" class="qs-date" />
      </template>

      <!-- 月总额模式:单笔总额 -->
      <template v-else>
        <div class="qs-month">
          <p class="qs-month-label">{{ t('quick.monthTotal') }}</p>
          <NInputNumber v-model:value="monthTotal" :min="0" :precision="2" :placeholder="t('common.inputAmount')" class="qs-month-input" />
        </div>
      </template>

      <button class="qs-save" type="button" @click="save">{{ t('common.save') }}</button>
    </NDrawerContent>
  </NDrawer>
</template>

<style>
/* ===== 记一笔 底部抽屉(参考 MoneyFlow 记一笔交互) ===== */
.quick-sheet {
  --qs-radius: 14px;
}
.quick-sheet .n-drawer-body {
  padding: 0 !important;
}
.qs-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 18px 10px;
}
.qs-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
  color: var(--qs-text, #e6e8f0);
}
.qs-close {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: rgba(125, 125, 140, 0.16);
  color: #c2c6d6;
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
  transition: transform 0.1s ease, background 0.15s ease;
}
.qs-close:active { transform: scale(0.9); }

/* 类型切换 */
.qs-type {
  display: flex;
  gap: 6px;
  margin: 4px 18px 14px;
  background: rgba(125, 125, 140, 0.12);
  border-radius: 12px;
  padding: 4px;
}
.qs-type-btn {
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
.qs-type-btn.expense.active {
  background: linear-gradient(135deg, #FF6B35 0%, #E9533B 100%);
  color: #fff;
}
.qs-type-btn.income.active {
  background: linear-gradient(135deg, #18a058 0%, #36ad6a 100%);
  color: #fff;
}

/* 金额显示 */
.qs-amount {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 8px;
  padding: 10px 0 16px;
}
.qs-cur {
  font-size: 16px;
  font-weight: 600;
  color: #8a90a6;
}
.qs-amt {
  font-size: 40px;
  font-weight: 800;
  letter-spacing: -0.5px;
  color: var(--qs-text, #e6e8f0);
  font-variant-numeric: tabular-nums;
}

/* 分类网格 */
.qs-cats-label {
  font-size: 12px;
  color: #8a90a6;
  margin: 0 0 8px;
  padding: 0 2px;
}
.qs-cat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-bottom: 14px;
}
.qs-cat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 10px 4px;
  border-radius: 12px;
  background: rgba(125, 125, 140, 0.08);
  border: 1.5px solid transparent;
  cursor: pointer;
  transition: all 0.18s ease;
}
.qs-cat:active { transform: scale(0.95); }
.qs-cat.sel {
  background: rgba(91, 141, 239, 0.16);
  border-color: #5B8DEF;
}
.qs-cat-ic {
  width: 38px;
  height: 38px;
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 17px;
  font-weight: 700;
  color: #fff;
}
.qs-cat-name {
  font-size: 11px;
  color: #c2c6d6;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

/* 数字键盘 */
.qs-pad {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 14px;
}
.qs-num {
  height: 54px;
  border: none;
  border-radius: 12px;
  background: rgba(125, 125, 140, 0.1);
  color: var(--qs-text, #e6e8f0);
  font-size: 22px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.08s ease, background 0.15s ease;
}
.qs-num:active { transform: scale(0.94); background: rgba(91, 141, 239, 0.3); }
.qs-del { color: #f0886b; }

/* 备注 / 日期 */
.qs-note { margin-bottom: 10px; }
.qs-date { margin-bottom: 16px; }

/* 月总额 */
.qs-month { padding: 8px 2px 20px; }
.qs-month-label { font-size: 13px; color: #8a90a6; margin: 0 0 10px; }
.qs-month-input { width: 100%; }

/* 保存按钮 */
.qs-save {
  width: 100%;
  padding: 15px;
  border: none;
  border-radius: 14px;
  background: linear-gradient(135deg, #5B8DEF 0%, #7B61FF 100%);
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 8px 20px -6px rgba(91, 141, 239, 0.55);
  transition: transform 0.12s ease, opacity 0.15s ease;
  margin-bottom: calc(8px + env(safe-area-inset-bottom));
}
.qs-save:active { transform: scale(0.98); opacity: 0.92; }

/* 浅色主题适配 */
:root[data-theme='light'] .quick-sheet,
.quick-sheet[data-theme='light'] {
  --qs-text: #1b2350;
}
</style>
