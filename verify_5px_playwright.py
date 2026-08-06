#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证 中列↔进度环 视觉间距 = 5px (仅 ≤768px)
- .hero-ring div 受 translateX(41) 且为 200px box(scale 仅作用于内部 svg), rect 可靠
- 环视觉左沿 = .hero-ring.rect.left + 45 (scale0.55 居中内缩)
- 视觉间距 visualGap = ringVisualLeft - mid.rect.right  (期望 5)
- 浅色/深色 × 桌面 1280 / 移动 390;监听 pageerror
"""
import json, asyncio
from playwright.async_api import async_playwright

BASE = 'http://127.0.0.1:8843/'

SEED = {
    'profile': {
        'name': 'Alan', 'entryMode': 'daily', 'theme': 'light', 'locale': 'zh-CN',
        'baseCurrency': 'CNY', 'fireMultiple': 25, 'fireStatement': '从独立到自由',
        'returnRates': {'conservative': 0.04, 'neutral': 0.07, 'optimistic': 0.10},
        'defaultReturnScenario': 'neutral', 'reminderDaysBefore': 3,
    },
    'incomes': [{'id': 'i1', 'date': '2026-08-05', 'amount': 30000, 'category': '工资', 'note': ''}],
    'expenses': [{'id': 'e1', 'date': '2026-08-05', 'amount': 5000, 'category': '餐饮', 'note': ''}],
    'loans': [], 'accounts': [], 'snapshots': [], 'reminders': [], 'contracts': [], 'badges': {}
}

RING_INSET = 45  # scale(0.55) on 200px box -> 视觉内缩 45px
errors = []

async def shoot(pw, theme, w, h, name):
    b = await pw.chromium.launch()
    ctx = await b.new_context(viewport={'width': w, 'height': h})
    p = await ctx.new_page()
    p.on('pageerror', lambda e: errors.append(f'{name}:PAGEERROR:{e}'))
    p.on('console', lambda m: errors.append(f'{name}:CONSOLE_ERR:{m.text}') if m.type == 'error' else None)
    seed = dict(SEED); seed['profile'] = dict(SEED['profile']); seed['profile']['theme'] = theme
    s = json.dumps(seed, ensure_ascii=False)
    await p.add_init_script('localStorage.setItem("fire_companion_db_v1", JSON.stringify(' + s + '));')
    await p.goto(BASE)
    await p.wait_for_load_state('networkidle')
    await p.wait_for_timeout(1200)
    await p.screenshot(path=f'shot_5px_{name}_vp.png')
    info = await p.evaluate('''(inset) => {
      const mid = document.querySelector('.hero--mobile .hero-mid');
      const left = document.querySelector('.hero--mobile .hero-left');
      const ringDiv = document.querySelector('.hero--mobile .hero-ring');
      const rMid = mid ? mid.getBoundingClientRect() : null;
      const rLeft = left ? left.getBoundingClientRect() : null;
      const rRing = ringDiv ? ringDiv.getBoundingClientRect() : null;
      const ringVisualLeft = rRing ? (rRing.left + inset) : null;
      const visualGap = (rMid && ringVisualLeft != null) ? Math.round(ringVisualLeft - rMid.right) : 'N/A';
      const leftGap = (rLeft && rMid) ? Math.round(rMid.left - rLeft.right) : 'N/A';
      return { midRight: rMid ? Math.round(rMid.right) : 'N/A', ringDivLeft: rRing ? Math.round(rRing.left) : 'N/A', ringVisualLeft: ringVisualLeft != null ? Math.round(ringVisualLeft) : 'N/A', visualGap, leftGap };
    }''', RING_INSET)
    print(theme, w, json.dumps(info, ensure_ascii=False))
    await b.close()

async def main():
    async with async_playwright() as pw:
        for theme in ('light', 'dark'):
            await shoot(pw, theme, 1280, 720, f'{theme}_desk')
            await shoot(pw, theme, 390, 760, f'{theme}_mob')
    print('ERRORS:', errors if errors else 'none')

asyncio.run(main())
print('done')
