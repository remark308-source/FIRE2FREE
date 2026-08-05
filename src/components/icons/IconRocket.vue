<script setup>
defineProps({ size: { type: [Number, String], default: 18 } })
</script>
<template>
  <svg :width="size" :height="size" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <!-- 火箭 / FIRE -->
    <path d="M12 3 c3 3 5 7 5 11 v3 H7 v-3 c0 -4 2 -8 5 -11 z" />
    <circle cx="12" cy="10" r="1.6" />
    <path d="M9 17 L6 21" />
    <path d="M15 17 L18 21" />
  </svg>
</template>
