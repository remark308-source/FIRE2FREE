import { computed } from 'vue'

/**
 * 6 个本地计算的里程碑徽章,全部走已有 aggregate / streak 数据,零后端。
 * 每个徽章:{ id, emoji, titleKey, descKey, unlocked, progress? }
 */
export function useBadges(agg, streak) {
  const last = computed(() => {
    const m = agg.monthly.value
    return m[m.length - 1] || null
  })

  const savingsRate = computed(() => {
    const m = last.value
    if (!m || m.totalIncome <= 0) return 0
    return Math.max(0, (m.totalIncome - m.totalExpense) / m.totalIncome)
  })

  const passiveCoversExpense = computed(() => {
    const m = last.value
    return !!(m && m.passiveIncome > 0 && m.passiveIncome >= m.totalExpense)
  })

  const fs = computed(() => agg.fireState.value)

  return computed(() => [
    {
      id: 'savings_30',
      emoji: '🌱',
      titleKey: 'badges.savings30',
      descKey: 'badges.savings30Desc',
      unlocked: savingsRate.value >= 0.3,
      progress: Math.min(1, savingsRate.value / 0.3)
    },
    {
      id: 'passive_covers_expense',
      emoji: '💤',
      titleKey: 'badges.passive',
      descKey: 'badges.passiveDesc',
      unlocked: passiveCoversExpense.value,
      progress: Math.min(1, savingsRate.value)
    },
    {
      id: 'fire_25',
      emoji: '🛤️',
      titleKey: 'badges.fire25',
      descKey: 'badges.fire25Desc',
      unlocked: fs.value.progress >= 0.25,
      progress: Math.min(1, fs.value.progress / 0.25)
    },
    {
      id: 'fire_50',
      emoji: '🎯',
      titleKey: 'badges.fire50',
      descKey: 'badges.fire50Desc',
      unlocked: fs.value.progress >= 0.5,
      progress: Math.min(1, fs.value.progress / 0.5)
    },
    {
      id: 'fire_75',
      emoji: '🚀',
      titleKey: 'badges.fire75',
      descKey: 'badges.fire75Desc',
      unlocked: fs.value.progress >= 0.75,
      progress: Math.min(1, fs.value.progress / 0.75)
    },
    {
      id: 'streak_6',
      emoji: '🔥',
      titleKey: 'badges.streak6',
      descKey: 'badges.streak6Desc',
      unlocked: streak.currentStreak.value >= 6,
      progress: Math.min(1, streak.currentStreak.value / 6)
    }
  ])
}