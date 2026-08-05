<script setup>
defineProps({ size: { type: [Number, String], default: 18 } })
</script>
<template>
  <svg :width="size" :height="size" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <!-- 信贷:合同文档 + $ -->
    <path d="M6 3 L15 3 L18 6 L18 21 L6 21 Z" />
    <path d="M15 3 L15 6 L18 6" />
    <path d="M9 12 H15" />
    <path d="M9 15 L13 15" />
    <path d="M12 17 L13.5 17" />
  </svg>
</template>
