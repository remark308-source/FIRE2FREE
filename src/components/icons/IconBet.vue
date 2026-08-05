<script setup>
/**
 * 自我对赌图标:靶心(目标 + 赌一把)。
 * currentColor 继承文字色。
 */
defineProps({ size: { type: [Number, String], default: 20 } })
</script>

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    xmlns="http://www.w3.org/2000/svg"
    role="img"
    aria-label="Bet"
    fill="none"
  >
    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.6" opacity="0.4" />
    <circle cx="12" cy="12" r="6.4" stroke="currentColor" stroke-width="1.6" opacity="0.7" />
    <circle cx="12" cy="12" r="2.6" fill="currentColor" />
  </svg>
</template>
