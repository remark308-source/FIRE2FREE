<script setup>
defineProps({ size: { type: [Number, String], default: 18 } })
</script>
<template>
  <svg :width="size" :height="size" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <!-- 投资:K线 / 上行趋势 + 圆点 -->
    <path d="M3 18 L9 12 L13 15 L21 6" />
    <path d="M15 6 L21 6 L21 12" />
    <circle cx="3" cy="18" r="1.2" fill="currentColor" />
    <circle cx="9" cy="12" r="1.2" fill="currentColor" />
    <circle cx="13" cy="15" r="1.2" fill="currentColor" />
  </svg>
</template>
