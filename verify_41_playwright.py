#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证 41px nudge:中列(储蓄率/预计达成)与进度环同时右移 41px(仅 ≤768px)
- 量:左列↔中列间距(colGap, 期望≈53=12+41)、环视觉右沿是否被裁(ringSlack)
- 浅色/深色 × 桌面 1280 / 移动 390
- 监听 pageerror / console.error
"""
import json, asyncio
from playwright.async_api import async_playwright

BASE = 'http://127.0.0.1:8842/'

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
    await p.screenshot(path=f'shot_41_{name}_vp.png')
    info = await p.evaluate('''() => {
      const mc = document.querySelector('.mobile-content');
      const hero = document.querySelector('.hero--mobile');
      const mid = document.querySelector('.hero-mid');
      const left = document.querySelector('.hero-left');
      const ringSvg = document.querySelector('.hero-ring .hero-ring-svg');
      const rHero = hero ? hero.getBoundingClientRect() : null;
      const rMid = mid ? mid.getBoundingClientRect() : null;
      const rLeft = left ? left.getBoundingClientRect() : null;
      const rRing = ringSvg ? ringSvg.getBoundingClientRect() : null;
      // 卡片内容区右沿 = 卡片 border-box 右 - 右边框(1) - 右 padding(10)
      const contentRight = rHero ? (rHero.right - 1 - 10) : null;
      const ringSlack = (contentRight != null && rRing) ? Math.round(contentRight - rRing.right) : 'N/A';
      return {
        mobContentPadTop: mc ? getComputedStyle(mc).paddingTop : 'N/A',
        leftRight: rLeft ? Math.round(rLeft.right) : 'N/A',
        midLeft: rMid ? Math.round(rMid.left) : 'N/A',
        colGap: (rLeft && rMid) ? Math.round(rMid.left - rLeft.right) : 'N/A',
        ringSvgRight: rRing ? Math.round(rRing.right) : 'N/A',
        cardContentRight: contentRight != null ? Math.round(contentRight) : 'N/A',
        ringSlack: ringSlack,
      };
    }''')
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
