<script setup>
defineProps({ size: { type: [Number, String], default: 18 } })
</script>
<template>
  <svg :width="size" :height="size" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <!-- 钱币 -->
    <circle cx="12" cy="12" r="9" />
    <path d="M9 9 a3 2 0 0 1 6 0 c0 1.5 -3 1.5 -3 3" />
    <circle cx="12" cy="16" r="0.6" fill="currentColor" />
  </svg>
</template>
