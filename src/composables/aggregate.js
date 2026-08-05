import { computed } from 'vue'
import { useAppStore } from '@/stores/app'
import { toBase, fireTarget, yearsToFire, loanMonthlyPayment } from '@/finance'
import dayjs from 'dayjs'

/**
 * 把所有业务数据聚合成「月度序列 + FIRE 状态 + 投资趋势」
 * Dashboard / Calculator / Reminders 共用
 */
export function useAggregate() {
  const app = useAppStore()

  // 按月聚合
  const monthly = computed(() => {
    const db = app.db
    const base = app.baseCurrency
    const fx = app.fxRates

    const map = new Map()
    const ensure = (ym) => {
      if (!map.has(ym)) {
        map.set(ym, {
          ym,
          activeIncome: 0,
          passiveIncome: 0,
          investPL: 0,
          dailyExpense: 0,
          loanExpense: 0
        })
      }
      return map.get(ym)
    }
    const ymOf = (dateStr) => dayjs(dateStr).format('YYYY-MM')

    db.incomes.forEach((r) => {
      const m = ensure(ymOf(r.date))
      const v = toBase(Number(r.amount), r.currency, base, fx)
      if (r.type === 'active') m.activeIncome += v
      else m.passiveIncome += v
    })
    db.expenses.forEach((r) => {
      const m = ensure(ymOf(r.date))
      const v = toBase(Number(r.amount), r.currency, base, fx)
      if (r.type === 'daily') m.dailyExpense += v
      else m.loanExpense += v
    })

    // 投资盈亏:从每月净值差额 - 净流入 倒推(按账户)
    // 账户成本基线 openingValue:新建账户时用「目前市值 − 持仓盈亏」推导;
    // 老账户(无该字段)回退到首条快照 value,首月 pl=0,行为不变。
    const accountMap = new Map(db.accounts.map((a) => [a.id, a]))
    const snapMap = new Map()
    db.snapshots.forEach((s) => {
      if (!snapMap.has(s.accountId)) snapMap.set(s.accountId, [])
      snapMap.get(s.accountId).push(s)
    })
    snapMap.forEach((list, accountId) => {
      const acc = accountMap.get(accountId)
      const sorted = [...list].sort((a, b) => a.yearMonth.localeCompare(b.yearMonth))
      for (let i = 0; i < sorted.length; i++) {
        const cur = sorted[i]
        const prev = sorted[i - 1]
        let pl = 0
        if (!prev) {
          // 首条快照:用账户基线 openingValue,首月即显示累计收益(=建仓以来盈亏),而非 0
          const oBase = toBase(Number((acc?.openingValue ?? cur.value) || 0), acc?.currency || cur.currency, base, fx)
          const cBase = toBase(Number(cur.value), cur.currency, base, fx)
          pl = cBase - oBase
        } else {
          pl = toBase(Number(cur.value), cur.currency, base, fx)
          pl -= toBase(Number(prev.value), prev.currency, base, fx)
          pl -= toBase(Number(cur.netInflow || 0), cur.currency, base, fx)
        }
        const m = ensure(cur.yearMonth)
        m.investPL += pl
      }
    })

    const arr = [...map.values()].sort((a, b) => a.ym.localeCompare(b.ym))
    arr.forEach((m) => {
      // 投资盈亏(市值变动)不计入月度现金流:它非可花现金,且已体现在净资产市值里,
      // 计入会重复计算净资产 + 误导储蓄率/ETA。仅真实收入(主动+被动,含基金分红)入流。
      m.totalIncome = m.activeIncome + m.passiveIncome
      m.totalExpense = m.dailyExpense + m.loanExpense
      m.netCashFlow = m.totalIncome - m.totalExpense
    })
    return arr
  })

  // 净资产序列(累计净现金流 + 起点净资产 + 当前投资市值)
  const netWorthSeries = computed(() => {
    const base = app.baseCurrency
    const fx = app.fxRates
    const init = toBase(Number(app.profile.initialAssets || 0), app.profile.baseCurrency || base, fx)

    const latestSnap = new Map()
    app.db.snapshots.forEach((s) => {
      const prev = latestSnap.get(s.accountId)
      if (!prev || s.yearMonth > prev.yearMonth) latestSnap.set(s.accountId, s)
    })
    let investValue = 0
    latestSnap.forEach((s) => {
      investValue += toBase(Number(s.value || 0), s.currency, base, fx)
    })

    const ms = monthly.value
    let cum = init
    return ms.map((m) => ({
      ym: m.ym,
      value: (cum += m.netCashFlow) + investValue
    }))
  })

  // 投资账户市值序列(各账户最新净值加总,按月回放)
  const investValueSeries = computed(() => {
    const base = app.baseCurrency
    const fx = app.fxRates
    const grouped = new Map() // ym -> value
    const latestPerAccount = new Map()
    app.db.snapshots.forEach((s) => {
      const prev = latestPerAccount.get(s.accountId)
      if (!prev || s.yearMonth > prev.yearMonth) latestPerAccount.set(s.accountId, s)
    })
    app.db.snapshots.forEach((s) => {
      const v = toBase(Number(s.value || 0), s.currency, base, fx)
      grouped.set(s.yearMonth, (grouped.get(s.yearMonth) || 0) + v)
    })
    // 没快照的月份补 0
    const months = [...new Set(app.db.snapshots.map((s) => s.yearMonth))].sort()
    const result = months.map((ym) => ({ ym, value: grouped.get(ym) || 0 }))
    const total = [...latestPerAccount.values()].reduce(
      (acc, s) => acc + toBase(Number(s.value || 0), s.currency, base, fx),
      0
    )
    if (result.length === 0 && total > 0) result.push({ ym: dayjs().format('YYYY-MM'), value: total })
    return result
  })

  // 当月投资盈亏累计
  const totalInvestValue = computed(() => {
    const base = app.profile.baseCurrency
    const fx = app.fxRates
    const latest = new Map()
    app.db.snapshots.forEach((s) => {
      const prev = latest.get(s.accountId)
      if (!prev || s.yearMonth > prev.yearMonth) latest.set(s.accountId, s)
    })
    let sum = 0
    latest.forEach((s) => {
      sum += toBase(Number(s.value || 0), s.currency, base, fx)
    })
    return sum
  })

  // 累计净投入 = 各账户(成本基线 openingValue + 全部快照净流入之和)
  // 老账户无 openingValue 时回退首条快照 value,等价于旧逻辑(首条净流入通常为 0)。
  const totalCostBasis = computed(() => {
    const base = app.profile.baseCurrency
    const fx = app.fxRates
    const accountMap = new Map(app.db.accounts.map((a) => [a.id, a]))
    const byAcc = new Map()
    app.db.snapshots.forEach((s) => {
      if (!byAcc.has(s.accountId)) byAcc.set(s.accountId, [])
      byAcc.get(s.accountId).push(s)
    })
    let sum = 0
    byAcc.forEach((list, accId) => {
      const acc = accountMap.get(accId)
      const sorted = [...list].sort((a, b) => a.yearMonth.localeCompare(b.yearMonth))
      const oBase = toBase(
        Number((acc?.openingValue ?? sorted[0].value) || 0),
        acc?.currency || sorted[0].currency,
        base,
        fx
      )
      let cost = oBase
      sorted.forEach((s) => {
        cost += toBase(Number(s.netInflow || 0), s.currency, base, fx)
      })
      sum += cost
    })
    return sum
  })

  const investPLTotal = computed(() => totalInvestValue.value - totalCostBasis.value)

  const fireState = computed(() => {
    const ms = monthly.value
    const last = ms[ms.length - 1]
    const netCashFlow = last ? last.netCashFlow : 0
    const lastExpense = last ? last.totalExpense : 0
    const target = fireTarget(lastExpense * 12, app.profile.fireMultiple)
    const netAssets = netWorthSeries.value.length
      ? netWorthSeries.value[netWorthSeries.value.length - 1].value
      : 0
    const gap = Math.max(0, target - netAssets)
    const progress = target > 0 ? Math.min(1, netAssets / target) : 0
    const r = app.profile.returnRates[app.profile.defaultReturnScenario] || 0.08
    const eta = yearsToFire(netAssets, gap, netCashFlow, r)
    const savingsRate =
      last && last.totalIncome > 0
        ? Math.min(1, Math.max(0, (last.totalIncome - last.totalExpense) / last.totalIncome))
        : 0
    // 动态平衡(安全边际): 净资产产生的年化被动收益 是否覆盖 年支出
    // 公式: (净资产 × 年化收益率) − 年支出 > 0 即视为「已可躺平」
    const annualReturn = netAssets * r
    const annualExpense = lastExpense * 12
    const dynamicSurplus = annualReturn - annualExpense
    const dynamicCovered = dynamicSurplus >= 0
    const coverage = annualExpense > 0 ? annualReturn / annualExpense : (netAssets > 0 ? Infinity : 0)
    return {
      target, netAssets, gap, progress, eta, lastExpense, netCashFlow, savingsRate,
      returnRate: r,
      scenario: app.profile.defaultReturnScenario,
      annualReturn, annualExpense, dynamicSurplus, dynamicCovered, coverage
    }
  })

  // 计算月度现金流的环比变化(用于 Dashboard 红绿)
  const cashFlowDelta = computed(() => {
    const ms = monthly.value
    if (ms.length < 2) return 0
    return ms[ms.length - 1].netCashFlow - ms[ms.length - 2].netCashFlow
  })

  return {
    monthly,
    netWorthSeries,
    fireState,
    investValueSeries,
    totalInvestValue,
    totalCostBasis,
    investPLTotal,
    cashFlowDelta
  }
}
