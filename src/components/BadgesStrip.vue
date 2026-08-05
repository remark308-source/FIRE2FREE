<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { NCard, NTooltip } from 'naive-ui'

const props = defineProps({
  badges: { type: Array, required: true }
})
const { t } = useI18n()
const earned = computed(() => props.badges.filter((b) => b.unlocked).length)
</script>

<template>
  <NCard class="badges-card" :bordered="false" size="small">
    <div class="badges-head">
      <div>
        <div class="badges-eyebrow">{{ t('badges.title') }}</div>
        <div class="badges-num">{{ earned }} <span class="unit">/ {{ badges.length }}</span></div>
      </div>
      <div class="badges-hint">{{ t('badges.hint') }}</div>
    </div>

    <div class="badges-grid">
      <NTooltip v-for="b in badges" :key="b.id" placement="top" trigger="hover">
        <template #trigger>
          <div class="badge" :class="{ on: b.unlocked }">
            <div class="badge-emoji">{{ b.unlocked ? b.emoji : '🔒' }}</div>
            <div class="badge-title">{{ t(b.titleKey) }}</div>
            <div class="badge-desc">{{ t(b.descKey) }}</div>
            <div v-if="!b.unlocked && b.progress != null" class="badge-progress">
              <div class="bar"><div class="fill" :style="{ width: Math.round(b.progress * 100) + '%' }"></div></div>
            </div>
          </div>
        </template>
        {{ t(b.descKey) }}
      </NTooltip>
    </div>
  </NCard>
</template>

<style scoped>
.badges-card { border-radius: 16px !important; }
.badges-head { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 12px; }
.badges-eyebrow { font-size: 12px; opacity: 0.7; }
.badges-num { font-size: 24px; font-weight: 700; }
.badges-num .unit { font-size: 14px; opacity: 0.6; }
.badges-hint { font-size: 11px; opacity: 0.55; max-width: 50%; text-align: right; line-height: 1.4; }
.badges-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; }
.badge {
  border-radius: 12px;
  padding: 10px 6px;
  text-align: center;
  background: rgba(128,128,128,0.08);
  filter: grayscale(1);
  opacity: 0.55;
  transition: all .2s ease;
  cursor: help;
}
.badge.on {
  background: var(--fire-grad-pink);
  filter: none;
  opacity: 1;
  color: #fff;
  box-shadow: 0 6px 16px rgba(193,71,233,0.22);
  transform: translateY(-1px);
}
.badge-emoji { font-size: 24px; line-height: 1.2; }
.badge-title { font-size: 12px; font-weight: 600; margin-top: 2px; }
.badge-desc { font-size: 10px; opacity: 0.7; margin-top: 2px; line-height: 1.3; }
.badge.on .badge-desc { opacity: 0.9; }
.badge-progress { margin-top: 6px; }
.bar { width: 100%; height: 3px; background: rgba(128,128,128,0.25); border-radius: 2px; overflow: hidden; }
.fill { height: 100%; background: var(--fire-grad-blue); }
</style>