<script setup>
/**
 * FIRE 进度环:大数字 + 渐变圆环 + 辅助信息
 * 接受 progress(0-1)、target、netAssets 三件套,带 0.8s 动画
 */
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { fmtCompact, fmtPct } from '@/composables/format'

const props = defineProps({
  progress: { type: Number, default: 0 },
  target: { type: Number, default: 0 },
  netAssets: { type: Number, default: 0 },
  eta: { type: [Number, null], default: null },
  baseCurrency: { type: String, default: 'CNY' },
  size: { type: Number, default: 220 }
})
const { t } = useI18n()

const animated = ref(0)
watch(
  () => props.progress,
  (p) => {
    const start = animated.value
    const end = Math.max(0, Math.min(1, p))
    const duration = 800
    const t0 = performance.now()
    function step(now) {
      const k = Math.min(1, (now - t0) / duration)
      animated.value = start + (end - start) * (1 - Math.pow(1 - k, 3))
      if (k < 1) requestAnimationFrame(step)
    }
    requestAnimationFrame(step)
  },
  { immediate: true }
)

const RADIUS = 86
const STROKE = 16
const CIRC = 2 * Math.PI * RADIUS
const dashOffset = computed(() => CIRC * (1 - animated.value))

const status = computed(() => {
  if (props.progress >= 1) return { key: 'aboveTarget', color: '#18a058' }
  if (props.progress >= 0.5) return { key: 'onTrack', color: '#FF8A3D' }
  return { key: 'needMore', color: '#5B8DEF' }
})

const etaText = computed(() => {
  if (props.eta == null) return '∞'
  if (props.eta < 1) return `~${Math.round(props.eta * 12)} mo`
  return `${props.eta.toFixed(1)} yr`
})
</script>

<template>
  <div class="fire-ring" :style="{ width: size + 'px', height: size + 'px' }">
    <svg :width="size" :height="size" viewBox="0 0 220 220" :aria-label="$t('dashboard.progress')">
      <defs>
        <linearGradient id="fireRingGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#FFC857" />
          <stop offset="50%" stop-color="#FF8A3D" />
          <stop offset="100%" stop-color="#E9533B" />
        </linearGradient>
        <filter id="ringShadow" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="3" />
          <feOffset dy="2" result="b" />
          <feFlood flood-color="#000" flood-opacity=".18" />
          <feComposite in2="b" operator="in" />
          <feMerge><feMergeNode /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>
      <!-- 背景环 -->
      <circle cx="110" cy="110" :r="RADIUS" fill="none" stroke="rgba(125,125,140,0.18)" :stroke-width="STROKE" />
      <!-- 进度环 -->
      <circle
        cx="110"
        cy="110"
        :r="RADIUS"
        fill="none"
        stroke="url(#fireRingGrad)"
        :stroke-width="STROKE"
        stroke-linecap="round"
        :stroke-dasharray="CIRC"
        :stroke-dashoffset="dashOffset"
        transform="rotate(-90 110 110)"
        filter="url(#ringShadow)"
      />
      <!-- 中心文字:0.0% 大字 + 已达成 小字,整体居中(相对几何中心 110,110) -->
      <text x="110" y="108" text-anchor="middle" font-size="36" font-weight="800" fill="currentColor" dominant-baseline="middle">{{ fmtPct(animated) }}</text>
      <text x="110" y="135" text-anchor="middle" font-size="12" fill="rgba(125,125,140,0.85)" dominant-baseline="middle">{{ $t('dashboard.progressLabel') }}</text>
    </svg>

    <div class="ring-meta" :style="{ position: 'absolute', left: 0, right: 0, bottom: '-22px', textAlign: 'center' }">
      <span class="ring-status" :style="{ background: status.color }">{{ $t(`dashboard.${status.key}`) }}</span>
    </div>
  </div>
</template>

<style scoped>
.fire-ring { position: relative; display: inline-block; color: var(--text-color, #1a1a1a); }
.ring-status {
  display: inline-block;
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 999px;
  letter-spacing: 0.5px;
}
</style>
