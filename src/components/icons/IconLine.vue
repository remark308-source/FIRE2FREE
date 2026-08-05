<script setup>
defineProps({ size: { type: [Number, String], default: 18 } })
</script>
<template>
  <svg :width="size" :height="size" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <!-- 折线图 -->
    <path d="M3 18 L8 13 L12 17 L16 9 L21 14" />
    <path d="M3 21 L21 21" />
  </svg>
</template>
