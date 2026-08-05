<script setup>
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import FireLogo from '@/components/icons/FireLogo.vue'

const { t } = useI18n()
const router = useRouter()
const app = useAppStore()

// 已选过模式又误入此页 → 直接回仪表盘
onMounted(() => {
  if (app.profile.entryMode) router.replace('/dashboard')
})

function choose(mode) {
  app.updateProfile({ entryMode: mode })
  router.replace('/dashboard')
}
</script>

<template>
  <div class="ob-wrap">
    <div class="ob-logo"><FireLogo :size="84" :show-wordmark="true" /></div>
    <h1 class="ob-title">{{ t('onboarding.title') }}</h1>
    <p class="ob-note">{{ t('onboarding.note') }}</p>

    <div class="ob-cards">
      <div class="ob-card ob-daily" @click="choose('daily')">
        <div class="ob-card-name">{{ t('onboarding.daily') }}</div>
        <p class="ob-desc">{{ t('onboarding.dailyDesc') }}</p>
        <div class="ob-pros">✓ {{ t('onboarding.dailyPros') }}</div>
        <div class="ob-cons">• {{ t('onboarding.dailyCons') }}</div>
        <button class="ob-btn" type="button">{{ t('onboarding.choose') }}</button>
      </div>

      <div class="ob-card ob-monthly" @click="choose('monthly')">
        <div class="ob-card-name">{{ t('onboarding.monthly') }}</div>
        <p class="ob-desc">{{ t('onboarding.monthlyDesc') }}</p>
        <div class="ob-pros">✓ {{ t('onboarding.monthlyPros') }}</div>
        <div class="ob-cons">• {{ t('onboarding.monthlyCons') }}</div>
        <button class="ob-btn" type="button">{{ t('onboarding.choose') }}</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ob-wrap {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  padding: 32px 20px;
  background:
    radial-gradient(1200px 500px at 50% -10%, rgba(255, 138, 61, 0.16), transparent 60%),
    radial-gradient(900px 500px at 80% 110%, rgba(123, 97, 255, 0.14), transparent 60%),
    #0f1430;
}
.ob-logo { margin-bottom: 4px; }
.ob-title {
  font-size: 26px;
  font-weight: 800;
  margin: 0;
  background: linear-gradient(90deg, #ffc857 0%, #ff8a3d 50%, #e9533b 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.ob-note { font-size: 13px; color: rgba(255, 255, 255, 0.65); margin: 0 0 10px; max-width: 520px; text-align: center; }
.ob-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
  width: 100%;
  max-width: 760px;
}
.ob-card {
  cursor: pointer;
  border-radius: 16px;
  padding: 22px 20px;
  background: rgba(255, 255, 255, 0.04);
  border: 1.5px solid rgba(125, 125, 140, 0.22);
  transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.ob-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.35);
}
.ob-daily:hover { border-color: #5b8def; }
.ob-monthly:hover { border-color: #18a058; }
.ob-card-name { font-size: 19px; font-weight: 800; }
.ob-daily .ob-card-name { color: #7ea2f2; }
.ob-monthly .ob-card-name { color: #4fcf8e; }
.ob-desc { font-size: 13px; color: rgba(255, 255, 255, 0.78); margin: 0; line-height: 1.6; min-height: 42px; }
.ob-pros { font-size: 12.5px; color: #4fcf8e; font-weight: 600; }
.ob-cons { font-size: 12.5px; color: rgba(255, 255, 255, 0.55); }
.ob-btn {
  margin-top: 6px;
  align-self: flex-start;
  border: none;
  border-radius: 10px;
  padding: 9px 22px;
  font-weight: 700;
  font-size: 14px;
  color: #fff;
  cursor: pointer;
  background: linear-gradient(135deg, #ff8a3d 0%, #e9533b 100%);
}
.ob-monthly .ob-btn { background: linear-gradient(135deg, #18a058 0%, #36ad6a 100%); }
@media (max-width: 640px) {
  .ob-cards { grid-template-columns: 1fr; }
}
</style>
