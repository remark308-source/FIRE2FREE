<script setup>
/**
 * FIRE 进度环:大数字 + 渐变圆环 + 底部状态徽章
 * 中心只显示达成百分比 + 「已达成」小字(储蓄率/预计达成移到 Hero 中间列)
 */
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { fmtPct } from '@/composables/format'

const props = defineProps({
  progress: { type: Number, default: 0 },
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
      </defs>
      <circle cx="110" cy="110" :r="RADIUS" fill="none" stroke="rgba(125,125,140,0.18)" :stroke-width="STROKE" />
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
      />
      <text class="ring-num" x="110" y="108" text-anchor="middle" font-size="38" font-weight="800" dominant-baseline="middle">{{ fmtPct(animated) }}</text>
      <text class="ring-label" x="110" y="138" text-anchor="middle" font-size="12" dominant-baseline="middle">{{ $t('dashboard.progressLabel') }}</text>
    </svg>

    <div class="ring-meta" :style="{ position: 'absolute', left: 0, right: 0, bottom: '-22px', textAlign: 'center' }">
      <span class="ring-status" :style="{ background: status.color }">{{ $t(`dashboard.${status.key}`) }}</span>
    </div>
  </div>
</template>

<style scoped>
.fire-ring { position: relative; display: inline-block; color: var(--ring-text-main, #1a1a1a); }
.ring-num { fill: var(--ring-text-main, #1a1a1a); font-variant-numeric: tabular-nums; }
.ring-label { fill: var(--ring-text-label, rgba(0,0,0,0.55)); letter-spacing: 0.5px; }
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