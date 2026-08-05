<script setup>
defineProps({ size: { type: [Number, String], default: 18 } })
</script>
<template>
  <svg :width="size" :height="size" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <!-- 提醒:铃铛 -->
    <path d="M6 16 V11 a6 6 0 0 1 12 0 V16 L20 18 H4 Z" />
    <path d="M10 21 a2 2 0 0 0 4 0" />
    <path d="M12 4 V2.5" />
  </svg>
</template>
