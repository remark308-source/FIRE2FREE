<script setup>
defineProps({ size: { type: [Number, String], default: 18 } })
</script>
<template>
  <svg :width="size" :height="size" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <!-- 出账:上箭头出圆 -->
    <circle cx="12" cy="12" r="9" />
    <path d="M12 7 L12 17" />
    <path d="M8 12 L12 8 L16 12" />
  </svg>
</template>
