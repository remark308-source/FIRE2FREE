<script setup>
defineProps({ size: { type: [Number, String], default: 18 } })
</script>
<template>
  <svg :width="size" :height="size" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <!-- 仪表盘:仪表 + 指针 + 三段刻度 -->
    <circle cx="12" cy="13" r="7.5" />
    <path d="M5.5 13 A6.5 6.5 0 0 1 18.5 13" />
    <path d="M12 13 L15 9.5" />
    <path d="M3.5 21 L5.5 18.5" />
    <path d="M20.5 21 L18.5 18.5" />
  </svg>
</template>
