<script setup>
/**
 * FIRE 进度环:中心储蓄率+预计达成 + 渐变圆环 + 底部状态徽章
 * 接受 progress(0-1)、target、netAssets 三件套,带 0.8s 动画
 * 中心文字四行(储蓄率 / 数值 / 预计达成 / 数值),跟随主题切换对比度
 *   - 浅色主题:label rgba(0,0,0,0.55),main #1a1a1a,savingsRate #FF8A3D
 *   - 深色主题:label rgba(255,255,255,0.65),main rgba(255,255,255,0.95),savingsRate #FFB36B
 */
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { fmtCompact, fmtPct } from '@/composables/format'

const props = defineProps({
  progress: { type: Number, default: 0 },
  target: { type: Number, default: 0 },
  netAssets: { type: Number, default: 0 },
  eta: { type: [Number, null], default: null },
  savingsRate: { type: Number, default: 0 },
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
  if (props.progress >= 1) return { key: 'aboveTarget', color: '#FF8A3D' }
  if (props.progress >= 0.5) return { key: 'onTrack', color: '#FFB36B' }
  return { key: 'needMore', color: '#FF8A3D' }
})

// 储蓄率:中国语境下绿色不代表正向,改用品牌主橙 #FF8A3D(浅色) / #FFB36B(深色)
const savingsRateText = computed(() => fmtPct(props.savingsRate || 0))
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
      <!-- 中心 4 行:储蓄率 label / 数值 / 预计达成 label / 数值,垂直居中(几何中心 110,110)
           用 CSS class 控 fill,主题穿透用 :deep 选择外层 .theme-dark/.theme-light -->
      <text class="ring-label" x="110" y="86" text-anchor="middle" dominant-baseline="middle">{{ $t('dashboard.savingsRate') }}</text>
      <text class="ring-num ring-sr" x="110" y="113" text-anchor="middle" dominant-baseline="middle">{{ savingsRateText }}</text>
      <text class="ring-label" x="110" y="143" text-anchor="middle" dominant-baseline="middle">{{ $t('dashboard.etaLabel') }}</text>
      <text class="ring-num ring-eta" x="110" y="168" text-anchor="middle" dominant-baseline="middle">{{ etaText }}</text>
    </svg>

    <div class="ring-meta" :style="{ position: 'absolute', left: 0, right: 0, bottom: '-22px', textAlign: 'center' }">
      <span class="ring-status" :style="{ background: status.color }">{{ $t(`dashboard.${status.key}`) }}</span>
    </div>
  </div>
</template>

<style scoped>
.fire-ring { position: relative; display: inline-block; }
/* 中心文字 fill 用 CSS 变量(定义在 App.vue :root / .theme-dark),
   CSS 变量在 SVG 子元素继承,不受 scoped 影响,
   浅色 / 深色主题各一套自然切换。 */
.ring-label {
  font-size: 11px;
  font-weight: 500;
  fill: var(--ring-text-label);
  letter-spacing: 0.5px;
}
.ring-num { font-variant-numeric: tabular-nums; }
/* 储蓄率:中国语境下绿色不表示正向,改品牌主橙(浅色 #FF8A3D,深色提亮 #FFB36B 保对比度) */
.ring-sr { font-size: 26px; font-weight: 800; fill: var(--ring-text-sr); }
.ring-eta { font-size: 20px; font-weight: 700; fill: var(--ring-text-main); }

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
