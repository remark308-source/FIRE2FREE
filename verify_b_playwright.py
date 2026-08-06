#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证 B 方案:手机版 .mobile-content padding-top 58→32 + hero 卡内 padding 8→4 + grid 列距 8→12
- 浅色/深色 × 桌面 1280 / 移动 390
- 监听 pageerror / console.error
- 测量 mobile-content padding-top、hero top、menu-fab top、列距
"""
import json, asyncio
from playwright.async_api import async_playwright

BASE = 'http://127.0.0.1:8840/'

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
    await p.screenshot(path=f'shot_b_{name}_vp.png')
    info = await p.evaluate('''() => {
      const mc = document.querySelector('.mobile-content');
      const hero = document.querySelector('.hero--mobile');
      const fab = document.querySelector('.menu-fab');
      const mid = document.querySelector('.hero-mid');
      const left = document.querySelector('.hero-left');
      const mcStyle = mc ? getComputedStyle(mc) : null;
      const rHero = hero ? hero.getBoundingClientRect() : null;
      const rFab = fab ? fab.getBoundingClientRect() : null;
      const rMid = mid ? mid.getBoundingClientRect() : null;
      const rLeft = left ? left.getBoundingClientRect() : null;
      return {
        mobContentPadTop: mcStyle ? mcStyle.paddingTop : 'N/A',
        heroTop: rHero ? Math.round(rHero.top) : 'N/A',
        fabTop: rFab ? Math.round(rFab.top) : 'N/A',
        heroMinusFab: (rHero && rFab) ? Math.round(rHero.top - rFab.top) : 'N/A',
        leftRight: rLeft ? Math.round(rLeft.right) : 'N/A',
        midLeft: rMid ? Math.round(rMid.left) : 'N/A',
        colGap: (rLeft && rMid) ? Math.round(rMid.left - rLeft.right) : 'N/A',
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
