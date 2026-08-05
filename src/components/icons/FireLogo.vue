<script setup>
/**
 * FIRE2FREE 专属 LOGO:海平面上一轮冉冉升起的太阳(财务自由的黎明) + 帆船
 * — 替代 emoji 火苗,主题色随 currentColor 继承,可放在侧边栏头部
 * 设计:暖色日出(品牌渐变) + V3 船(深石板船身 #2B3050 + 暖橙帆 + 白描边)
 *  —— 白描边确保夜间深色背景下船身仍清晰(accessibility)
 *  —— 8 根尖三角光芒,太阳略偏右下、底缘微压船帆
 */
defineProps({
  size: { type: [Number, String], default: 40 },
  showWordmark: { type: Boolean, default: true }
})
</script>

<template>
  <div class="fire-logo" :style="{ display: 'inline-flex', alignItems: 'center', gap: '10px' }">
    <svg
      :width="size"
      :height="size"
      viewBox="0 0 64 64"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-label="FIRE2FREE Logo"
    >
      <defs>
        <linearGradient id="fireSunGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#FFC857" />
          <stop offset="60%" stop-color="#FF8A3D" />
          <stop offset="100%" stop-color="#E9533B" />
        </linearGradient>
        <linearGradient id="fireSeaGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#5B8DEF" stop-opacity="0.85" />
          <stop offset="100%" stop-color="#7B61FF" stop-opacity="0.85" />
        </linearGradient>
        <linearGradient id="fireSailGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#FFB36B" />
          <stop offset="100%" stop-color="#FF7A45" />
        </linearGradient>
      </defs>

      <!-- 太阳:8 根尖三角光芒(中心 40,22,右移 4px,略偏右下) -->
      <g transform="translate(4,0)">
        <g fill="url(#fireSunGrad)">
          <polygon points="49,22 43.9,20.8 43.9,23.3" />
          <polygon points="45.2,31.2 42.5,26.7 40.7,28.5" />
          <polygon points="36,35 37.3,29.9 34.8,29.9" />
          <polygon points="26.8,31.2 31.3,28.5 29.5,26.7" />
          <polygon points="23,22 28.1,23.3 28.1,20.8" />
          <polygon points="26.8,12.8 29.5,17.3 31.3,15.6" />
          <polygon points="36,9 34.8,14.1 37.3,14.1" />
          <polygon points="45.2,12.8 40.7,15.6 42.5,17.3" />
        </g>
        <!-- 太阳中心实心圆 -->
        <circle cx="36" cy="22" r="7" fill="url(#fireSunGrad)" />
      </g>

      <!-- 海平面 -->
      <path d="M4 46 Q18 43 32 46 T60 46" stroke="url(#fireSeaGrad)" stroke-width="2.6" fill="none" stroke-linecap="round" />
      <!-- 水面涟漪 -->
      <path d="M10 51 Q22 49 32 51 T54 51" stroke="url(#fireSeaGrad)" stroke-width="1.6" fill="none" stroke-opacity="0.55" stroke-linecap="round" />
      <path d="M16 56 Q26 54.5 34 56 T52 56" stroke="url(#fireSeaGrad)" stroke-width="1.4" fill="none" stroke-opacity="0.35" stroke-linecap="round" />
      <!-- 帆船 V3:深石板船身 + 暖橙帆 + 白描边(夜间可读) -->
      <g>
        <!-- 桅杆 -->
        <line x1="32" y1="46" x2="32" y2="30" stroke="#2B3050" stroke-width="2" stroke-linecap="round" />
        <!-- 主帆(右) -->
        <polygon points="32,30 32,46 44,46" fill="url(#fireSailGrad)" stroke="#E8ECF5" stroke-width="1" stroke-linejoin="round" />
        <!-- 前帆(左) -->
        <polygon points="32,35 32,46 21,46" fill="url(#fireSailGrad)" stroke="#E8ECF5" stroke-width="1" stroke-linejoin="round" fill-opacity="0.9" />
        <!-- 船身 -->
        <path d="M22 46 L42 46 L39 51 L25 51 Z" fill="#2B3050" stroke="#E8ECF5" stroke-width="1" stroke-linejoin="round" />
      </g>
    </svg>

    <div v-if="showWordmark" class="wordmark" style="display: flex; flex-direction: column; align-items: center; line-height: 1.1">
      <div style="font-weight: 800; font-size: 16px; letter-spacing: 1px; background: linear-gradient(90deg,#FFC857 0%, #FF8A3D 50%, #E9533B 100%); -webkit-background-clip: text; background-clip: text; color: transparent;">FIRE2FREE</div>
      <!-- 副标题居中于字标下方,与字标留约 4px 呼吸空间 -->
      <div style="font-size: 10.5px; opacity: 0.65; font-weight: 500; letter-spacing: 0.3px; margin-top: 4px; text-align: center">{{ $t('app.subtitle') }}</div>
    </div>
  </div>
</template>

<style scoped>
.fire-logo svg { display: block; }
</style>
