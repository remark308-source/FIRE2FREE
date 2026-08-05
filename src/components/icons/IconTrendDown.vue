<script setup>
defineProps({ size: { type: [Number, String], default: 18 } })
</script>
<template>
  <svg :width="size" :height="size" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <!-- 趋势下 -->
    <path d="M4 8 L10 12 L14 10 L20 16" />
    <path d="M14 16 L20 16 L20 10" />
  </svg>
</template>
