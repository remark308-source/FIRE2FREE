<script setup>
defineProps({ size: { type: [Number, String], default: 18 } })
</script>
<template>
  <svg :width="size" :height="size" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <!-- 计算器:算盘变体 -->
    <rect x="5" y="3" width="14" height="18" rx="2" />
    <rect x="8" y="6" width="8" height="3" rx="0.8" />
    <circle cx="9" cy="13" r="0.9" fill="currentColor" />
    <circle cx="15" cy="13" r="0.9" fill="currentColor" />
    <circle cx="12" cy="13" r="0.9" fill="currentColor" />
    <circle cx="9" cy="17" r="0.9" fill="currentColor" />
    <circle cx="15" cy="17" r="0.9" fill="currentColor" />
    <circle cx="12" cy="17" r="0.9" fill="currentColor" />
  </svg>
</template>
