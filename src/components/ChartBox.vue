<script setup>
/**
 * ChartBox v2 — 真正联动
 *
 * 用法:
 *   <ChartBox
 *     title="xx"
 *     :data="{
 *       x: ['Jan','Feb',...],
 *       series: [
 *         { key: 'income', label: t('income'), color: '#5B8DEF', data: [..] },
 *         { key: 'expense', label: t('expense'), color: '#E9533B', data: [-..] }
 *       ]
 *     }"
 *     :types="['line','bar','pie']"
 *     :default-type="'line'"
 *     :format-value="(v) => fmtMoney(v, base)"
 *   />
 *
 * 现在切换 type 会真实重新生成 ECharts option 并 setOption('series.type', ...) 切图。
 */
import { ref, watch, onMounted, onBeforeUnmount, computed, nextTick } from 'vue'
import * as echarts from 'echarts'
import { NCard, NSelect, NSpace, NText } from 'naive-ui'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const props = defineProps({
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  data: { type: Object, required: true },
  types: { type: Array, default: () => ['line', 'bar', 'pie'] },
  defaultType: { type: String, default: 'line' },
  formatValue: { type: Function, default: (v) => v },
  height: { type: [Number, String], default: 280 }
})

const chartEl = ref(null)
let chart = null
const chartType = ref(props.defaultType && props.types.includes(props.defaultType) ? props.defaultType : props.types[0])

const typeOptions = computed(() =>
  props.types.map((tp) => ({
    label: tp === 'line' ? t('dashboard.line') : tp === 'bar' ? t('dashboard.bar') : t('dashboard.pie'),
    value: tp
  }))
)

// 不同 type 用不同 series 配置,但数据源统一来自 data
function buildOption(type) {
  const x = props.data?.x || []
  const series = props.data?.series || []
  const colors = ['#5B8DEF', '#E9533B', '#18a058', '#FF8A3D', '#7B61FF', '#FFC857', '#C147E9', '#36ad6a']

  const legendData = series.map((s, i) => ({ name: s.label, icon: 'circle' }))
  // 单序列时不必显示图例(只有一种颜色,无需说明)
  const singleSeries = series.length === 1

  if (type === 'pie') {
    // 饼图:把所有 series 合并为「按 series 归类」;仅当 series 数量=1 时按 x 分桶
    let pieData = []
    if (series.length === 1) {
      const s = series[0]
      pieData = x.map((lab, i) => ({ name: String(lab), value: Math.abs(Number(s.data[i] || 0)) }))
    } else {
      const totals = series.map((s) => s.data.reduce((a, v) => a + Math.abs(Number(v || 0)), 0))
      pieData = series.map((s, i) => ({ name: s.label, value: totals[i] }))
    }
    pieData = pieData.filter((d) => d.value > 0)
    return {
      tooltip: {
        trigger: 'item',
        formatter: (p) => `${p.name}<br/>${props.formatValue(p.value)} (${p.percent}%)`
      },
      legend: { bottom: 0, icon: 'circle', textStyle: { fontSize: 12 } },
      series: [
        {
          type: 'pie',
          radius: ['46%', '72%'],
          center: ['50%', '46%'],
          avoidLabelOverlap: true,
          itemStyle: { borderRadius: 6, borderColor: 'transparent', borderWidth: 2 },
          label: {
            formatter: '{b}\n{d}%',
            fontSize: 11
          },
          labelLine: { length: 8, length2: 6 },
          data: pieData,
          color: colors
        }
      ]
    }
  }

  // line / bar 共用结构
  const seriesOpt = series.map((s, i) => {
    const color = s.color || colors[i % colors.length]
    if (type === 'bar') {
      return {
        name: s.label,
        type: 'bar',
        barMaxWidth: 26,
        barCategoryGap: '40%',
        data: s.data,
        itemStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color },
              { offset: 1, color: color + '99' }
            ]
          },
          borderRadius: [6, 6, 0, 0]
        }
      }
    }
    return {
      name: s.label,
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { width: 2.6, color },
      itemStyle: { color, borderColor: '#fff', borderWidth: 2 },
      emphasis: { focus: 'series', scale: true },
      data: s.data,
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: color + '55' },
            { offset: 1, color: color + '05' }
          ]
        }
      }
    }
  })

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      valueFormatter: (v) => props.formatValue(v),
      backgroundColor: 'rgba(20,20,30,0.85)',
      borderWidth: 0,
      textStyle: { color: '#fff', fontSize: 12 }
    },
    legend: { data: legendData, top: 4, icon: 'circle', textStyle: { fontSize: 12 }, show: !singleSeries },
    grid: { left: 56, right: 18, top: 36, bottom: 28, containLabel: true },
    xAxis: {
      type: 'category',
      data: x,
      axisLine: { lineStyle: { color: 'rgba(125,125,140,0.3)' } },
      axisLabel: { color: 'rgba(125,125,140,0.85)', fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: 'rgba(125,125,140,0.18)', type: 'dashed' } },
      axisLabel: {
        color: 'rgba(125,125,140,0.85)',
        fontSize: 11,
        formatter: (v) => props.formatValue(v)
      }
    },
    series: seriesOpt
  }
}

const option = computed(() => buildOption(chartType.value))

function init() {
  if (!chartEl.value) return
  chart = echarts.init(chartEl.value)
  chart.setOption(option.value)
  // 暴露 series 数 + legend 状态到 data-attr,方便自动化测试 + dev 调试
  // (2 个自定义属性不影响渲染/SEO/性能,作为 e2e 测试钩子保留)
  writeAttrs()
}

function writeAttrs() {
  if (!chartEl.value || !chart) return
  const opt = chart.getOption()
  const sLen = (opt.series || []).length
  const legendShow = opt.legend && opt.legend[0] ? opt.legend[0].show !== false : true
  chartEl.value.setAttribute('data-series-len', String(sLen))
  chartEl.value.setAttribute('data-legend-show', String(legendShow))
}

function resize() { chart && chart.resize() }

onMounted(async () => {
  await nextTick()
  init()
  window.addEventListener('resize', resize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  chart && chart.dispose()
})

// 1) type 变了 → 整个 option 变了 → 全量重设
watch(
  () => option.value,
  (opt) => {
    if (!chart) return
    chart.clear()
    chart.setOption(opt, true)
    writeAttrs()
  }
)

// 2) 数据源变了 → type 未变 → 只 setOption(merge)
watch(
  () => props.data,
  (d) => {
    if (!chart) return
    chart.setOption(buildOption(chartType.value), true)
    writeAttrs()
  },
  { deep: true }
)
</script>

<template>
  <NCard :title="title" size="small" :segmented="{ content: true }" class="fire-card">
    <template #header-extra v-if="types.length > 1">
      <NSpace size="small" :wrap="false">
        <NText v-if="subtitle" depth="3" style="font-size: 11px">{{ subtitle }}</NText>
        <NSelect
          size="small"
          :value="chartType"
          :options="typeOptions"
          style="width: 110px"
          @update:value="(v) => (chartType = v)"
        />
      </NSpace>
    </template>

    <div ref="chartEl" :style="{ height: (typeof height === 'number' ? height + 'px' : (typeof height === 'string' && /^\d+$/.test(height) ? height + 'px' : height)), width: '100%' }"></div>

    <div v-if="!data || !data.series || !data.series.length" class="chart-empty">
      <NText depth="3">{{ $t('common.noData') }}</NText>
    </div>
  </NCard>
</template>

<style scoped>
.chart-empty {
  text-align: center;
  padding: 30px 0;
}
.fire-card :deep(.n-card__content) { padding: 12px 14px 8px; }
</style>
