<script setup>
defineProps({ size: { type: [Number, String], default: 18 } })
</script>
<template>
  <svg :width="size" :height="size" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <!-- 直立柱状图 -->
    <path d="M5 20 V12" />
    <path d="M10 20 V6" />
    <path d="M15 20 V14" />
    <path d="M20 20 V9" />
    <path d="M3 20 L22 20" />
  </svg>
</template>
