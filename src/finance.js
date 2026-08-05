// 金融计算工具

// 等额本息月供
export function equalPaymentMonthly(principal, annualRate, termMonths) {
  if (termMonths <= 0) return 0
  const r = annualRate / 12
  if (r === 0) return principal / termMonths
  const f = Math.pow(1 + r, termMonths)
  return (principal * r * f) / (f - 1)
}

// 等额本金首月还款(递减),返回每月还款数组
export function equalPrincipalSchedule(principal, annualRate, termMonths) {
  if (termMonths <= 0) return []
  const r = annualRate / 12
  const principalPart = principal / termMonths
  const arr = []
  let remaining = principal
  for (let i = 0; i < termMonths; i++) {
    const interest = remaining * r
    arr.push(principalPart + interest)
    remaining -= principalPart
  }
  return arr
}

// 生成还款计划表 {index, payment, principalPart, interest, remaining}
export function repaySchedule(loan) {
  const { principal, annualRate, termMonths, repayMethod } = loan
  const r = annualRate / 12
  const schedule = []
  let remaining = principal
  if (repayMethod === 'equal_principal') {
    const pp = principal / termMonths
    for (let i = 0; i < termMonths; i++) {
      const interest = remaining * r
      const payment = pp + interest
      remaining = i === termMonths - 1 ? 0 : remaining - pp
      schedule.push({ index: i + 1, payment, principalPart: pp, interest, remaining })
    }
  } else {
    const pay = equalPaymentMonthly(principal, annualRate, termMonths)
    for (let i = 0; i < termMonths; i++) {
      const interest = remaining * r
      let pp = pay - interest
      remaining -= pp
      if (i === termMonths - 1) {
        pp += remaining // 修正尾差
        remaining = 0
      }
      schedule.push({ index: i + 1, payment: pay, principalPart: pp, interest, remaining })
    }
  }
  return schedule
}

// 某笔贷款在某自然月是否应还款、月供多少(active 状态才计)
export function loanMonthlyPayment(loan) {
  if (loan.status === 'cleared') return 0
  if (loan.repayMethod === 'equal_principal') {
    // 取首月(简化:等额本金月供近似首月,UI 提供完整计划表)
    const s = equalPrincipalSchedule(loan.principal, loan.annualRate, loan.termMonths)
    return s.length ? s[0] : 0
  }
  return equalPaymentMonthly(loan.principal, loan.annualRate, loan.termMonths)
}

// 货币换算:amount(原币种) -> 基准币种
// fxRates: { USD: 7.2, HKD: 0.92, ... } 表示 1 单位外币 = X 基准(CNY)
export function toBase(amount, currency, baseCurrency, fxRates) {
  const a = Number(amount) || 0
  if (!currency || !baseCurrency) return a
  if (currency === baseCurrency) return a
  const rates = fxRates || {}
  const rate = rates[currency]
  if (rate == null) return a
  return a * rate
}

// 4% 法则 FIRE 目标:年支出 × 倍数(默认 25)
export function fireTarget(annualExpense, multiple = 25) {
  return annualExpense * multiple
}

// 预计达成年数(简化复利求解)
// P = 当前净资产, G = 缺口, m = 月净储蓄, r = 年化收益率
// 迭代至资产 >= FIRE 目标
export function yearsToFire(currentAssets, gap, monthlyNet, annualRate) {
  if (gap <= 0) return 0
  if (monthlyNet <= 0 && annualRate <= 0) return null // 永远到不了
  let assets = currentAssets
  const monthsPerYear = 12
  let months = 0
  const maxMonths = 1200 // 100 年上限
  const monthlyRate = annualRate / 12
  while (assets < currentAssets + gap && months < maxMonths) {
    assets = assets * (1 + monthlyRate) + monthlyNet
    months++
  }
  if (months >= maxMonths) return null
  return +(months / monthsPerYear).toFixed(1)
}
