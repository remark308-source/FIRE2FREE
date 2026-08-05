import { reactive } from 'vue'

/**
 * 全局「保存成功」微动效状态机。
 * 任意页面调用 fireSave(label, tone) 即可触发一次性庆祝动画,
 * 由 <SaveFxLayer /> 统一渲染(避免每个页面各自 toast 污染)。
 */
const state = reactive({
  seq: 0,
  id: 0, // 每次 fireSave 自增,SaveFxLayer 用 key=id 重播动画
  label: '',
  tone: 'success' // success | info
})

let timer = null

export function fireSave(label = '已保存', tone = 'success') {
  state.seq += 1
  state.id = state.seq
  state.label = label
  state.tone = tone
  if (timer) clearTimeout(timer)
  timer = setTimeout(() => {
    // 仅隐藏,保留最后 id 以便组件决定是否收起
    state.id = 0
  }, 1500)
}

export function useSaveFx() {
  return state
}
