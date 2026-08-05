import { defineStore } from 'pinia'
import { loadDb, saveDb } from '@/storage'
import { emptyDb } from '@/constants'
import { CATEGORIES } from '@/constants'

let uid = () => Math.random().toString(36).slice(2, 10) + Date.now().toString(36)

export const useAppStore = defineStore('app', {
  state: () => ({
    db: loadDb()
  }),
  getters: {
    profile: (s) => s.db.profile,
    baseCurrency: (s) => s.db.profile.baseCurrency,
    fxRates: (s) => s.db.profile.fxRates,
    // 合并内置 + 自定义类别
    categories: (s) => ({
      incomeActive: [...CATEGORIES.incomeActive, ...(s.db.profile.customCategories.incomeActive || [])],
      incomePassive: [...CATEGORIES.incomePassive, ...(s.db.profile.customCategories.incomePassive || [])],
      expenseDaily: [...CATEGORIES.expenseDaily, ...(s.db.profile.customCategories.expenseDaily || [])],
      accountType: CATEGORIES.accountType,
      loanType: CATEGORIES.loanType
    })
  },
  actions: {
    persist() {
      saveDb(this.db)
    },
    resetAll() {
      this.db = emptyDb()
      this.persist()
    },
    importJson(obj) {
      if (obj && obj.profile) {
        this.db = loadDb.__normalize ? loadDb.__normalize(obj) : obj
        this.persist()
      }
    },
    // profile
    updateProfile(patch) {
      this.db.profile = { ...this.db.profile, ...patch }
      this.persist()
    },
    ensureCustomCategory(group, key, label) {
      const list = this.db.profile.customCategories[group] || (this.db.profile.customCategories[group] = [])
      if (!list.find((c) => c.key === key)) list.push({ key, zh: label, en: label })
    },
    // 通用增删改
    add(collection, item) {
      const row = { id: uid(), ...item }
      this.db[collection].push(row)
      this.persist()
      return row
    },
    remove(collection, id) {
      this.db[collection] = this.db[collection].filter((x) => x.id !== id)
      this.persist()
    },
    update(collection, id, patch) {
      const i = this.db[collection].findIndex((x) => x.id === id)
      if (i >= 0) {
        this.db[collection][i] = { ...this.db[collection][i], ...patch }
        this.persist()
      }
    },
    // 投资净值快照:同账户同月份 upsert
    upsertSnapshot(payload) {
      const i = this.db.snapshots.findIndex(
        (s) => s.accountId === payload.accountId && s.yearMonth === payload.yearMonth
      )
      if (i >= 0) {
        this.db.snapshots[i] = { ...this.db.snapshots[i], ...payload }
      } else {
        this.db.snapshots.push({ id: uid(), ...payload })
      }
      this.persist()
    },
    // 删除账户时连带删除其快照
    removeAccount(id) {
      this.db.accounts = this.db.accounts.filter((a) => a.id !== id)
      this.db.snapshots = this.db.snapshots.filter((s) => s.accountId !== id)
      this.persist()
    }
  }
})
