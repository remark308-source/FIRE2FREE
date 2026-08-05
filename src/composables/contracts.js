import { computed } from 'vue'
import { useAppStore } from '@/stores/app'
import { useStreak } from '@/composables/streak'
import { useAggregate } from '@/composables/aggregate'
import dayjs from 'dayjs'

let uid = () => Math.random().toString(36).slice(2, 10) + Date.now().toString(36)

// 模块级:跨 useContracts() 实例共享。App 挂载时 autoResolve 把新赢契约 id 推入这里,
// Bets 页挂载时 takeSessionWins() 取走弹庆祝;若放在函数内则每个实例各一份,庆祝永不弹出。
let sessionWins = []

const PERIOD_MONTHS = { quarter: 3, halfyear: 6, year: 12 }

// 确保旧库(无 contracts 字段)也能用
function ensureList(app) {
  if (!Array.isArray(app.db.contracts)) app.db.contracts = []
  return app.db.contracts
}

/**
 * 自我对赌(Commitment Contract)系统
 * 契约 = 一个可量化的 FIRE 习惯目标 + 一句"赌注"承诺。不涉及真实资金,是心理承诺装置。
 *
 * 目标类型:
 *  - streak:       连续打卡月数 ≥ target
 *  - savingsRate:  周期内月均储蓄率(%) ≥ target
 *  - expenseCap:   周期内月均支出 ≤ target(基准币种)
 *
 * 评估为"实时":进度条 + 状态(onTrack / atRisk / won / lost)。
 * 达标时由 Bets 页面 onMounted 自动把 status 落为 won(庆祝);
 * 认输由用户手动点。
 */
export function useContracts() {
  const app = useAppStore()
  const { currentStreak } = useStreak()
  const { monthly } = useAggregate()

  const contracts = computed(() => {
    ensureList(app)
    return [...app.db.contracts].sort((a, b) => (b.createdAt || '').localeCompare(a.createdAt || ''))
  })

  const activeContracts = computed(() => contracts.value.filter((c) => c.status === 'active'))

  // 评估单条契约
  function evaluate(c) {
    const months = PERIOD_MONTHS[c.periodType] || 6
    let current = 0
    let progress = 0
    let met = false

    if (c.goalType === 'streak') {
      current = currentStreak.value
      const target = Number(c.target) || 1
      progress = Math.min(1, target > 0 ? current / target : 0)
      met = current >= target
    } else if (c.goalType === 'savingsRate') {
      const recent = monthly.value.slice(-months).filter((m) => m.totalIncome > 0)
      const avg =
        recent.length > 0
          ? recent.reduce((s, m) => s + Math.min(1, Math.max(0, (m.totalIncome - m.totalExpense) / m.totalIncome)), 0) / recent.length
          : 0
      current = Math.round(avg * 1000) / 10 // %
      const target = Number(c.target) || 1
      progress = Math.min(1, target > 0 ? current / target : 0)
      met = current >= target
    } else if (c.goalType === 'expenseCap') {
      const recent = monthly.value.slice(-months)
      const avg = recent.length > 0 ? recent.reduce((s, m) => s + m.totalExpense, 0) / recent.length : 0
      current = Math.round(avg)
      const target = Number(c.target) || 1
      // 花得越少越好:进度 = 目标/实际(封顶 1),达标=实际≤目标
      progress = target > 0 ? Math.min(1, target / (avg || target)) : 0
      met = avg > 0 && avg <= target
    }

    let status
    if (c.status === 'won') status = 'won'
    else if (c.status === 'lost') status = 'lost'
    else status = met ? 'won' : progress < 0.5 ? 'atRisk' : 'onTrack'

    return { progress, current, target: Number(c.target), met, status }
  }

  // 会话内待庆祝的获胜契约见模块级 sessionWins(跨实例共享)。
  // autoResolve 在 App 挂载时全局跑一次,把新赢的 id 暂存那里;
  // Bets 页挂载时 takeSessionWins() 取走并弹庆祝,保证只庆祝一次、不漏。

  // 自动判定:活跃且已达标 → 落为 won(庆祝)
  function autoResolve() {
    ensureList(app)
    const won = []
    app.db.contracts.forEach((c) => {
      if (c.status === 'active' && evaluate(c).met) {
        c.status = 'won'
        c.resolvedAt = dayjs().format('YYYY-MM-DD')
        won.push(c.id)
      }
    })
    if (won.length) {
      app.persist()
      sessionWins.push(...won)
    }
    return won
  }

  // 取走并清空本次会话的获胜契约(供 Bets 页弹庆祝)
  function takeSessionWins() {
    const w = sessionWins
    sessionWins = []
    return w
  }

  function addContract(payload) {
    ensureList(app)
    const row = {
      id: uid(),
      createdAt: dayjs().format('YYYY-MM-DD'),
      status: 'active',
      ...payload
    }
    app.db.contracts.push(row)
    app.persist()
    return row
  }
  function updateContract(id, patch) {
    ensureList(app)
    const i = app.db.contracts.findIndex((c) => c.id === id)
    if (i >= 0) {
      app.db.contracts[i] = { ...app.db.contracts[i], ...patch }
      app.persist()
    }
  }
  function removeContract(id) {
    ensureList(app)
    app.db.contracts = app.db.contracts.filter((c) => c.id !== id)
    app.persist()
  }

  return { contracts, activeContracts, evaluate, autoResolve, takeSessionWins, addContract, updateContract, removeContract }
}

export const CONTRACT_GOAL_TYPES = ['streak', 'savingsRate', 'expenseCap']
export const CONTRACT_PERIODS = ['quarter', 'halfyear', 'year']
