<script setup>
/**
 * 自定义侧滑抽屉(从左/右滑入)
 * 替代 naive-ui NDrawer —— NDrawer 在本项目(naive-ui 2.38.2 / vue 3.5)下
 *   移动端运行时 NDrawerContent 内的 NMenu/NSelect 等子组件偶发不渲染(显示成空白面板)。
 * 用 Teleport + 自定义 overlay + 内层 panel 包成 NCard 来规避该问题,
 *   渲染稳定可控,主题/深浅色由外层 .theme-light/.theme-dark 接管。
 *
 * 用法:
 *   <SideSheet v-model:show="open" placement="left" :width="280" :title="...">
 *     <template #header>...</template>
 *     <div>...主体内容...</div>
 *   </SideSheet>
 */
import { Teleport } from 'vue'
import { NCard } from 'naive-ui'

const props = defineProps({
  show: { type: Boolean, default: false },
  placement: { type: String, default: 'left' }, // 'left' | 'right'
  width: { type: [Number, String], default: 280 },
  title: { type: String, default: '' },
  closeOnMask: { type: Boolean, default: true }
})
const emit = defineEmits(['update:show', 'close'])

function close() {
  emit('update:show', false)
  emit('close')
}
function onMaskClick() {
  if (props.closeOnMask) close()
}
</script>

<template>
  <Teleport to="body">
    <div v-if="show" class="ss-root" :class="['ss-' + placement]">
      <div class="ss-mask" @click.self="onMaskClick" />
      <NCard
        class="ss-panel"
        :bordered="false"
        :title="title || undefined"
        role="dialog"
        aria-modal="true"
      >
        <template v-if="$slots.header" #header>
          <slot name="header" />
        </template>
        <template #header-extra>
          <button type="button" class="ss-close" :aria-label="$t ? $t('common.cancel') : 'close'" @click="close">×</button>
        </template>
        <slot />
      </NCard>
    </div>
  </Teleport>
</template>

<style>
.ss-root {
  position: fixed;
  inset: 0;
  z-index: 1200; /* 高于 bottom-nav (800) 与 fab (850),与 NDrawer 一致 */
  display: flex;
  pointer-events: none;
}
.ss-root.ss-left { justify-content: flex-start; }
.ss-root.ss-right { justify-content: flex-end; }
.ss-mask {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  -webkit-backdrop-filter: blur(2px);
  backdrop-filter: blur(2px);
  pointer-events: auto;
  animation: ssMaskIn 0.18s ease;
}
@keyframes ssMaskIn { from { opacity: 0; } to { opacity: 1; } }

.ss-panel {
  position: relative;
  pointer-events: auto;
  width: 280px;
  max-width: 86vw;
  height: 100vh;
  max-height: 100vh;
  border-radius: 0 !important;
  display: flex;
  flex-direction: column;
  animation: ssPanelInLeft 0.22s cubic-bezier(0.2, 0.8, 0.2, 1);
}
.ss-left .ss-panel { animation-name: ssPanelInLeft; }
.ss-right .ss-panel { animation-name: ssPanelInRight; }
@keyframes ssPanelInLeft {
  from { transform: translateX(-100%); }
  to { transform: translateX(0); }
}
@keyframes ssPanelInRight {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

/* 关闭按钮 */
.ss-close {
  width: 28px; height: 28px;
  border: none; background: transparent;
  font-size: 20px; line-height: 1; cursor: pointer;
  color: inherit; opacity: 0.65;
  transition: opacity 0.15s ease, transform 0.1s ease;
}
.ss-close:hover { opacity: 1; }
.ss-close:active { transform: scale(0.9); }

/* 主体滚动 */
.ss-panel :deep(.n-card__content) {
  flex: 1;
  overflow-y: auto;
  padding: 12px 12px 20px 12px;
  -webkit-overflow-scrolling: touch;
}
</style>
