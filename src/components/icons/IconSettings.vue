<script setup>
defineProps({ size: { type: [Number, String], default: 18 } })
</script>
<template>
  <svg :width="size" :height="size" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <!-- 设置:齿轮 -->
    <circle cx="12" cy="12" r="3" />
    <path d="M19.4 15 a7.97 7.97 0 0 0 0 -6" />
    <path d="M4.6 9 a7.97 7.97 0 0 0 0 6" />
    <path d="M15 4.6 a7.97 7.97 0 0 1 6 0" />
    <path d="M3 19.4 a7.97 7.97 0 0 1 0 -6" />
    <path d="M19.4 21 a7.97 7.97 0 0 0 0 -6" />
  </svg>
</template>
