<script setup>
defineProps({ size: { type: [Number, String], default: 18 } })
</script>
<template>
  <svg :width="size" :height="size" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <!-- 环形图 -->
    <circle cx="12" cy="12" r="8" />
    <path d="M12 4 A8 8 0 0 1 20 12" />
  </svg>
</template>
