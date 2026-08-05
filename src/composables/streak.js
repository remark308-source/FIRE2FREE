import { computed } from 'vue'
import dayjs from 'dayjs'
import { useAppStore } from '@/stores/app'

/**
 * 月度打卡 Streak:
 * 某月 ym 满足「收入 + 支出 + 投资净值快照」三项齐全 ⇒ 该月视为已打卡。
 * - currentStreak: 从当前月往前,连续已打卡的月数(当前月未打卡则从最后已打卡月往前数)。
 * - gridMonths:   以当前月为中心往前数 12 个月(含当前),用于年度格子渲染。
 */
export function useStreak() {
  const app = useAppStore()

  const monthsData = computed(() => {
    const map = new Map()
    const keyOf = (ym) => {
      if (!map.has(ym)) {
        map.set(ym, { ym, hasIncome: false, hasExpense: false, hasSnap: false, checked: false })
      }
      return map.get(ym)
    }
    app.db.incomes.forEach((r) => keyOf(dayjs(r.date).format('YYYY-MM')).hasIncome = true)
    app.db.expenses.forEach((r) => keyOf(dayjs(r.date).format('YYYY-MM')).hasExpense = true)
    app.db.snapshots.forEach((s) => keyOf(s.yearMonth).hasSnap = true)
    keyOf(dayjs().format('YYYY-MM')) // 当前月占位(即便没数据也要出现在序列)
    const arr = [...map.values()].map((m) => ({
      ...m,
      checked: m.hasIncome && m.hasExpense && m.hasSnap
    }))
    arr.sort((a, b) => a.ym.localeCompare(b.ym))
    return arr
  })

  const gridMonths = computed(() => {
    const list = []
    const cur = dayjs()
    for (let i = 11; i >= 0; i--) {
      const ym = cur.subtract(i, 'month').format('YYYY-MM')
      const found = monthsData.value.find((m) => m.ym === ym)
      list.push({
        ym,
        checked: found ? found.checked : false,
        isFuture: false,
        isCurrent: i === 0
      })
    }
    return list
  })

  const currentStreak = computed(() => {
    // 仅在「有真实数据」的月份上计算(排除当前月占位,否则未打卡月份会让 streak=0,体验过激)
    const list = monthsData.value.filter((m) => m.hasIncome || m.hasExpense || m.hasSnap)
    if (!list.length) return 0
    let count = 0
    for (let i = list.length - 1; i >= 0; i--) {
      if (list[i].checked) count++
      else break
    }
    return count
  })

  const longestStreak = computed(() => {
    let best = 0
    let run = 0
    monthsData.value.forEach((m) => {
      if (m.checked) { run++; best = Math.max(best, run) } else { run = 0 }
    })
    return best
  })

  const totalChecked = computed(() => monthsData.value.filter((m) => m.checked).length)

  const currentMonthChecked = computed(() => {
    const ym = dayjs().format('YYYY-MM')
    const m = monthsData.value.find((x) => x.ym === ym)
    return m ? m.checked : false
  })

  return { monthsData, gridMonths, currentStreak, longestStreak, totalChecked, currentMonthChecked }
}