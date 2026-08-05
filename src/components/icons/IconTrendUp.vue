<script setup>
defineProps({ size: { type: [Number, String], default: 18 } })
</script>
<template>
  <svg :width="size" :height="size" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <!-- 加速箭头 -->
    <path d="M4 18 L10 12 L14 16 L20 8" />
    <path d="M14 8 L20 8 L20 14" />
  </svg>
</template>
