import { emptyDb } from '@/constants'

const KEY = 'fire_companion_db_v1'

// 一次性迁移/补全:旧数据缺字段时合入默认结构,避免读取报错
function normalize(db) {
  const base = emptyDb()
  if (!db || typeof db !== 'object') return base
  return {
    profile: { ...base.profile, ...(db.profile || {}) },
    incomes: db.incomes || [],
    expenses: db.expenses || [],
    loans: db.loans || [],
    accounts: db.accounts || [],
    snapshots: db.snapshots || [],
    reminders: db.reminders || [],
    contracts: Array.isArray(db.contracts) ? db.contracts : []
  }
}

export function loadDb() {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return emptyDb()
    return normalize(JSON.parse(raw))
  } catch (e) {
    console.error('loadDb failed', e)
    return emptyDb()
  }
}

export function saveDb(db) {
  try {
    localStorage.setItem(KEY, JSON.stringify(db))
    return true
  } catch (e) {
    console.error('saveDb failed', e)
    return false
  }
}

export function exportJson(db) {
  return JSON.stringify(db, null, 2)
}

// 将数组导出为 CSV(UTF-8 BOM 防止 Excel 中文乱码)
export function toCsv(rows, columns) {
  const header = columns.map((c) => c.label).join(',')
  const body = rows.map((r) =>
    columns.map((c) => {
      let v = r[c.key]
      if (v == null) v = ''
      v = String(v)
      if (v.includes(',') || v.includes('"') || v.includes('\n')) {
        v = '"' + v.replace(/"/g, '""') + '"'
      }
      return v
    }).join(',')
  )
  return '\uFEFF' + [header, ...body].join('\r\n')
}

export function downloadFile(filename, content, mime = 'application/json') {
  const blob = new Blob([content], { type: mime + ';charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
