<script setup>
import { computed } from 'vue'
import { useSaveFx } from '@/composables/saveFx'

const fx = useSaveFx()
const visible = computed(() => fx.id > 0)

// 8 个方向 × 品牌色,纸屑爆开
const confetti = [
  { dx: -70, dy: -40, c: '#FFC857' },
  { dx: -40, dy: -70, c: '#FF8A3D' },
  { dx: 0, dy: -90, c: '#E9533B' },
  { dx: 45, dy: -68, c: '#5B8DEF' },
  { dx: 72, dy: -38, c: '#7B61FF' },
  { dx: 80, dy: 10, c: '#18a058' },
  { dx: 50, dy: 55, c: '#FF6B9D' },
  { dx: -55, dy: 50, c: '#C147E9' }
]
</script>

<template>
  <Teleport to="body">
    <Transition name="fx-fade">
      <div v-if="visible" :key="fx.id" class="savefx" :class="fx.tone">
        <!-- 纸屑 -->
        <span class="confetti-wrap">
          <i v-for="(p, i) in confetti" :key="i" class="confetti" :style="{ '--dx': p.dx + 'px', '--dy': p.dy + 'px', background: p.c }"></i>
        </span>
        <!-- 勾选圆环 -->
        <span class="ring"></span>
        <svg class="check" viewBox="0 0 52 52" aria-hidden="true">
          <path fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"
                d="M14 27 l8 8 l16 -18" />
        </svg>
        <span class="label">{{ fx.label }}</span>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.savefx {
  position: fixed;
  left: 50%;
  bottom: 40px;
  transform: translateX(-50%);
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 22px 12px 16px;
  border-radius: 999px;
  background: rgba(20, 22, 40, 0.92);
  color: #fff;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(8px);
  pointer-events: none;
}
.savefx.success { color: #4ade80; }
.savefx.info { color: #7B61FF; }

/* 圆环绕中心脉冲 */
.ring {
  position: absolute;
  left: 28px;
  top: 50%;
  width: 34px;
  height: 34px;
  margin: -17px 0 0 -17px;
  border-radius: 50%;
  border: 2px solid currentColor;
  animation: ring-pulse 0.9s ease-out;
}
@keyframes ring-pulse {
  0% { transform: scale(0.4); opacity: 0.9; }
  100% { transform: scale(1.8); opacity: 0; }
}

/* 勾选描边动画 */
.check {
  width: 34px;
  height: 34px;
  color: currentColor;
  flex: 0 0 auto;
  animation: check-pop 0.4s cubic-bezier(0.2, 0.8, 0.2, 1.2);
}
.check path {
  stroke-dasharray: 48;
  stroke-dashoffset: 48;
  animation: check-draw 0.45s ease forwards 0.1s;
}
@keyframes check-pop { 0% { transform: scale(0.3); } 60% { transform: scale(1.15); } 100% { transform: scale(1); } }
@keyframes check-draw { to { stroke-dashoffset: 0; } }

.label { font-size: 14px; font-weight: 600; color: #fff; letter-spacing: 0.3px; }

/* 纸屑 */
.confetti-wrap { position: absolute; left: 28px; top: 50%; width: 0; height: 0; }
.confetti {
  position: absolute;
  left: 0; top: 0;
  width: 7px; height: 7px;
  border-radius: 2px;
  opacity: 0;
  animation: confetti-burst 0.9s ease-out forwards;
}
@keyframes confetti-burst {
  0% { transform: translate(0, 0) scale(0.6) rotate(0deg); opacity: 1; }
  100% { transform: translate(var(--dx), var(--dy)) scale(0.8) rotate(180deg); opacity: 0; }
}

.fx-fade-enter-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.fx-fade-leave-active { transition: opacity 0.35s ease, transform 0.35s ease; }
.fx-fade-enter-from { opacity: 0; transform: translateX(-50%) translateY(12px) scale(0.92); }
.fx-fade-leave-to { opacity: 0; transform: translateX(-50%) translateY(8px) scale(0.96); }
</style>
