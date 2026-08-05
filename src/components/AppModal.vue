<template>
  <Teleport to="body">
    <div v-if="show" class="app-modal-mask" @click.self="onMaskClick">
      <NCard
        class="app-modal-card"
        :bordered="false"
        :title="title"
        :style="cardStyle"
        role="dialog"
        aria-modal="true"
      >
        <template #header-extra>
          <button type="button" class="app-modal-close" aria-label="close" @click="close">×</button>
        </template>
        <slot />
        <template v-if="$slots.footer" #footer>
          <slot name="footer" />
        </template>
      </NCard>
    </div>
  </Teleport>
</template>

<script setup>
import { NCard } from 'naive-ui'

const props = defineProps({
  show: { type: Boolean, default: false },
  title: { type: String, default: '' },
  cardStyle: { type: [String, Object], default: '' },
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
