<script setup>
import { computed, ref, onMounted, h } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  NCard, NButton, NForm, NFormItem, NSelect, NInputNumber, NInput,
  NProgress, NTag, NSpace, NText, NEmpty, useMessage, NPopconfirm
} from 'naive-ui'
import AppModal from '@/components/AppModal.vue'
import { useAppStore } from '@/stores/app'
import { useContracts, CONTRACT_GOAL_TYPES, CONTRACT_PERIODS } from '@/composables/contracts'
import { fireSave } from '@/composables/saveFx'
import { fmtMoney } from '@/composables/format'
import dayjs from 'dayjs'

const { t } = useI18n()
const app = useAppStore()
const message = useMessage()
const { contracts, evaluate, takeSessionWins, addContract, updateContract, removeContract } = useContracts()
const base = computed(() => app.baseCurrency)

const showAdd = ref(false)
const editingId = ref(null)
const form = ref({ goalType: 'streak', periodType: 'quarter', target: 6, promise: '' })

// 选项
const cap = (k) => k.charAt(0).toUpperCase() + k.slice(1)
const goalTypeOptions = CONTRACT_GOAL_TYPES.map((k) => ({ label: t('bets.goalType' + cap(k)), value: k }))
const periodOptions = CONTRACT_PERIODS.map((k) => ({ label: t('bets.period' + cap(k)), value: k }))
const targetProps = computed(() => {
  const g = form.value.goalType
  if (g === 'streak') return { min: 1, step: 1, precision: 0 }
  if (g === 'savingsRate') return { min: 1, max: 100, step: 0.5, precision: 1 }
  return { min: 0, step: 100, precision: 0 }
})

// 每条契约附带实时评估
const views = computed(() =>
  contracts.value.map((c) => {
    const ev = evaluate(c)
    const isNew = c.status === 'won' && c.resolvedAt === dayjs().format('YYYY-MM-DD')
    return { c, ev, isNew }
  })
)

function goalTypeLabel(c) {
  const map = { streak: t('bets.goalTypeStreak'), savingsRate: t('bets.goalTypeSavingsRate'), expenseCap: t('bets.goalTypeExpenseCap') }
  return map[c.goalType] || c.goalType
}
function statusKey(s) {
  return { onTrack: 'bets.statusOnTrack', atRisk: 'bets.statusAtRisk', won: 'bets.statusWon', lost: 'bets.statusLost' }[s] || s
}
function statusTagType(s) {
  return { onTrack: 'info', atRisk: 'warning', won: 'success', lost: 'error' }[s] || 'default'
}
function statusColor(s) {
  return { onTrack: '#5B8DEF', atRisk: '#FF8A3D', won: '#18a058', lost: '#E9533B' }[s] || '#5B8DEF'
}
function fmtCurrent(c, ev) {
  if (c.goalType === 'streak') return `${ev.current} ${t('bets.unitMonths')}`
  if (c.goalType === 'savingsRate') return `${ev.current.toFixed(1)}%`
  return fmtMoney(ev.current, base.value)
}
function fmtTarget(c) {
  if (c.goalType === 'streak') return `${Number(c.target)} ${t('bets.unitMonths')}`
  if (c.goalType === 'savingsRate') return `${Number(c.target).toFixed(1)}%`
  return fmtMoney(Number(c.target), base.value)
}

function openAdd() {
  editingId.value = null
  form.value = { goalType: 'streak', periodType: 'quarter', target: 6, promise: '' }
  showAdd.value = true
}
function openEdit(c) {
  editingId.value = c.id
  form.value = { goalType: c.goalType, periodType: c.periodType, target: Number(c.target), promise: c.promise || '' }
  showAdd.value = true
}
function submit() {
  const payload = {
    goalType: form.value.goalType,
    periodType: form.value.periodType,
    target: Number(form.value.target) || 0,
    promise: form.value.promise || ''
  }
  if (!payload.target || payload.target <= 0) return message.warning(t('bets.target') + ' > 0')
  if (editingId.value) updateContract(editingId.value, payload)
  else addContract(payload)
  fireSave(t('bets.saved'))
  showAdd.value = false
}
function forfeit(c) {
  updateContract(c.id, { status: 'lost', resolvedAt: dayjs().format('YYYY-MM-DD') })
  fireSave(t('bets.statusLost'))
}

// 进入页面:取走 App 挂载时已全局结算的获胜契约,弹庆祝(只庆祝一次)
const celebrate = ref([])
const showCelebrate = computed(() => celebrate.value.length > 0)
function closeCelebrate() { celebrate.value = [] }
onMounted(() => {
  const won = takeSessionWins()
  if (won.length) {
    fireSave(t('bets.wonHint'), 'success')
    celebrate.value = contracts.value.filter((c) => won.includes(c.id))
  }
})
</script>

<template>
  <div>
    <NCard :title="t('bets.title')">
      <template #header-extra>
        <NButton type="primary" size="small" @click="openAdd">{{ t('bets.addBet') }}</NButton>
      </template>
      <NText depth="3" style="display: block; margin-bottom: 14px; font-size: 12px">{{ t('bets.subtitle') }}</NText>

      <NEmpty v-if="views.length === 0" :description="t('bets.empty')" style="padding: 30px 0">
        <template #extra>
          <NButton size="small" type="primary" @click="openAdd">{{ t('bets.addBet') }}</NButton>
        </template>
      </NEmpty>

      <div v-else class="bet-list">
        <NCard
          v-for="(v, i) in views"
          :key="v.c.id"
          size="small"
          class="bet-card"
          :bordered="false"
          :style="{ borderLeft: `4px solid ${statusColor(v.ev.status)}` }"
        >
          <div class="bet-head">
            <NSpace align="center" :wrap="false">
              <span class="bet-goal">{{ goalTypeLabel(v.c) }}</span>
              <NTag v-if="v.isNew" size="small" type="success" :bordered="false" style="background: rgba(24,160,88,0.14)">🏆 {{ t('bets.newBadge') }}</NTag>
              <NTag v-else size="small" :type="statusTagType(v.ev.status)">{{ t(statusKey(v.ev.status)) }}</NTag>
            </NSpace>
            <NText depth="3" style="font-size: 11px">{{ t('bets.period' + cap(v.c.periodType)) }}</NText>
          </div>

          <p v-if="v.c.promise" class="bet-promise">“{{ v.c.promise }}”</p>

          <NProgress
            type="line"
            :percentage="Math.round(v.ev.progress * 100)"
            :show-indicator="false"
            :height="8"
            :color="statusColor(v.ev.status)"
            style="margin: 10px 0 6px"
          />
          <div class="bet-foot">
            <span>
              <span class="bet-foot-label">{{ t('bets.current') }}:</span>
              <strong>{{ fmtCurrent(v.c, v.ev) }}</strong>
              <span class="bet-sep"> / </span>
              <span class="bet-foot-label">{{ t('bets.target') }}:</span>
              {{ fmtTarget(v.c) }}
            </span>
          </div>

          <NSpace class="bet-actions" :wrap="false">
            <NButton size="small" quaternary @click="openEdit(v.c)">{{ t('common.edit') }}</NButton>
            <NButton
              v-if="v.c.status === 'active'"
              size="small"
              quaternary
              type="warning"
              @click="forfeit(v.c)"
            >{{ t('bets.loseBtn') }}</NButton>
            <NPopconfirm
              :on-positive-click="() => removeContract(v.c.id)"
            >
              <template #trigger>
                <NButton size="small" quaternary type="error">{{ t('common.delete') }}</NButton>
              </template>
              {{ t('common.deleteConfirm') }}
            </NPopconfirm>
          </NSpace>
        </NCard>
      </div>
    </NCard>

    <AppModal v-model:show="showAdd" :title="editingId ? t('common.edit') : t('bets.addBet')" :card-style="{ width: '520px', maxWidth: '92vw' }">
      <NForm :model="form">
        <NFormItem :label="t('bets.goalType')">
          <NSelect v-model:value="form.goalType" :options="goalTypeOptions" />
        </NFormItem>
        <NSpace>
          <NFormItem :label="t('bets.periodType')">
            <NSelect v-model:value="form.periodType" :options="periodOptions" style="width: 180px" />
          </NFormItem>
          <NFormItem :label="t('bets.target')">
            <NInputNumber v-model:value="form.target" v-bind="targetProps" style="width: 180px" />
          </NFormItem>
        </NSpace>
        <NFormItem :label="t('bets.promise')">
          <NInput
            v-model:value="form.promise"
            type="textarea"
            :autosize="{ minRows: 2, maxRows: 4 }"
            :placeholder="t('bets.promiseHint')"
          />
        </NFormItem>
        <NButton type="primary" block @click="submit">{{ t('common.save') }}</NButton>
      </NForm>
    </AppModal>

    <!-- 庆祝弹窗:用自定义 overlay 而非 NModal,规避 naive-ui FocusTrap 在 vue3 下
         withDirectives(null) 崩溃(所有 NModal 弹窗的通病,表单/设置等亦受影响) -->
    <Teleport to="body">
      <div v-if="showCelebrate" class="celebrate-mask" @click.self="closeCelebrate">
        <div class="celebrate-card" role="dialog" aria-modal="true">
          <div class="celebrate-emoji">🎉</div>
          <h3 class="celebrate-title">{{ t('bets.celebrateTitle') }}</h3>
          <p class="celebrate-body">{{ t('bets.celebrateBody', { n: celebrate.length }) }}</p>
          <ul class="celebrate-list">
            <li v-for="c in celebrate" :key="c.id">
              <strong>{{ goalTypeLabel(c) }}</strong>
              <span class="celebrate-sub"> · {{ t('bets.period' + cap(c.periodType)) }}</span>
            </li>
          </ul>
          <NButton type="primary" block @click="closeCelebrate">{{ t('common.ok') }}</NButton>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.bet-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; }
.bet-card { background: rgba(125, 125, 140, 0.05); }
:deep(.n-card.bet-card > .n-card__content) { padding: 14px 16px; }
.bet-head { display: flex; align-items: center; justify-content: space-between; }
.bet-goal { font-weight: 700; font-size: 14px; }
.bet-promise {
  margin: 8px 0 0; padding: 8px 12px;
  background: rgba(91, 141, 239, 0.10);
  border-left: 3px solid #5B8DEF; border-radius: 0 8px 8px 0;
  font-style: italic; font-size: 12px; opacity: 0.92;
}
.bet-foot { font-size: 12px; }
.bet-foot-label { opacity: 0.6; margin-right: 2px; }
.bet-sep { opacity: 0.5; }
.bet-actions { margin-top: 10px; }

/* 庆祝弹窗(自定义 overlay,规避 naive-ui FocusTrap 崩溃) */
.celebrate-mask {
  position: fixed; inset: 0; z-index: 2000;
  display: flex; align-items: center; justify-content: center;
  background: rgba(10, 12, 24, 0.55); backdrop-filter: blur(4px);
}
.celebrate-card {
  width: 460px; max-width: 92vw; padding: 28px 26px 22px;
  border-radius: 18px; text-align: center;
  background: linear-gradient(160deg, rgba(36, 40, 66, 0.96), rgba(22, 24, 42, 0.96));
  border: 1px solid rgba(255, 255, 255, 0.10);
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.45);
  animation: celebratePop .35s cubic-bezier(0.2, 0.8, 0.2, 1.2);
}
@keyframes celebratePop {
  0% { transform: scale(0.85) translateY(10px); opacity: 0; }
  100% { transform: scale(1) translateY(0); opacity: 1; }
}
.celebrate-emoji { font-size: 44px; line-height: 1; margin-bottom: 8px; }
.celebrate-title { margin: 0 0 8px; font-size: 19px; color: #fff; }
.celebrate-body { margin: 0 0 14px; font-size: 14px; color: rgba(255, 255, 255, 0.75); }
.celebrate-list { margin: 0 0 18px; padding: 0; list-style: none; line-height: 1.9; color: rgba(255, 255, 255, 0.9); }
.celebrate-sub { opacity: 0.55; }
</style>
