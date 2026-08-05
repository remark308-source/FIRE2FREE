import { CURRENCIES } from '@/constants'

export function currencySymbol(code) {
  const c = CURRENCIES.find((x) => x.code === code)
  return c ? c.symbol : code
}

export function fmtMoney(amount, code = 'CNY') {
  const sym = currencySymbol(code)
  const n = Number(amount || 0)
  return sym + n.toLocaleString('en-US', { maximumFractionDigits: 0 })
}

export function fmtNum(n, digits = 0) {
  return Number(n || 0).toLocaleString('en-US', { maximumFractionDigits: digits })
}

export function fmtPct(n) {
  return (Number(n || 0) * 100).toFixed(1) + '%'
}

// 千分位 + 紧凑显示 — zh 使用 万/亿,en 使用 K/M/B
export function fmtCompact(amount, code = 'CNY', locale = 'zh-CN') {
  const sym = currencySymbol(code)
  const n = Number(amount || 0)
  const abs = Math.abs(n)
  if (locale === 'zh-CN') {
    if (abs >= 1e8) return sym + (n / 1e8).toFixed(2) + '亿'
    if (abs >= 1e4) return sym + (n / 1e4).toFixed(1) + '万'
  } else {
    // English / non-zh: K / M / B suffix
    if (abs >= 1e9) return sym + (n / 1e9).toFixed(2) + 'B'
    if (abs >= 1e6) return sym + (n / 1e6).toFixed(1) + 'M'
    if (abs >= 1e3) return sym + (n / 1e3).toFixed(1) + 'K'
  }
  return sym + n.toLocaleString('en-US', { maximumFractionDigits: 0 })
}
