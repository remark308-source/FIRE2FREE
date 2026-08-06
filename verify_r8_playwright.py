#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Round 8: Hero 改成 3 列横向并排(图示样式),Playwright 截图验证
- 浅色 / 深色 × 桌面 1280 / 移动 390
- 验证:左列 4 行 brand(logo+wordmark/标题/副标/净现金流chip) + 中列 储蓄率+预计达成 + 右列 进度环+底部蓝色 chip
"""
import json, asyncio
from playwright.async_api import async_playwright

BASE = 'http://127.0.0.1:8830/'

SEED = {
    'profile': {
        'name': 'Alan',
        'entryMode': 'daily',
        'theme': 'light',
        'locale': 'zh-CN',
        'baseCurrency': 'CNY',
        'fireMultiple': 25,
        'fireStatement': '从独立到自由',
        'returnRates': {'conservative': 0.04, 'neutral': 0.07, 'optimistic': 0.10},
        'defaultReturnScenario': 'neutral',
        'reminderDaysBefore': 3,
    },
    'incomes': [{'id': 'i1', 'date': '2026-08-05', 'amount': 30000, 'category': '工资', 'note': ''}],
    'expenses': [{'id': 'e1', 'date': '2026-08-05', 'amount': 5000, 'category': '餐饮', 'note': ''}],
    'loans': [], 'accounts': [], 'snapshots': [], 'reminders': [], 'contracts': [], 'badges': {}
}

async def shoot(pw, theme, w, h, name):
    b = await pw.chromium.launch()
    ctx = await b.new_context(viewport={'width': w, 'height': h})
    p = await ctx.new_page()
    seed = dict(SEED)
    seed['profile'] = dict(SEED['profile'])
    seed['profile']['theme'] = theme
    s = json.dumps(seed, ensure_ascii=False)
    await p.add_init_script('localStorage.setItem("fire_companion_db_v1", JSON.stringify(' + s + '));')
    await p.goto(BASE)
    await p.wait_for_load_state('networkidle')
    await p.wait_for_timeout(1200)
    # 截首屏(viewport,适合看 hero 上移效果)
    await p.screenshot(path=f'shot_r8_{name}_vp.png')
    # 整页
    await p.screenshot(path=f'shot_r8_{name}_full.png', full_page=True)
    # hero 单独
    info = await p.evaluate('''() => {
      const hero = document.querySelector('.hero');
      const left = document.querySelector('.hero-left');
      const mid = document.querySelector('.hero-mid');
      const ring = document.querySelector('.hero-ring');
      const cf = document.querySelector('.hero-cashflow');
      const chip = document.querySelector('.hero-ring-chip');
      const lr = hero.getBoundingClientRect();
      const r1 = left.getBoundingClientRect();
      const r2 = mid.getBoundingClientRect();
      const r3 = ring.getBoundingClientRect();
      return {
        heroH: Math.round(lr.height), heroW: Math.round(lr.width), heroTop: Math.round(lr.top),
        leftText: left.innerText.replace(/\\n/g, ' | '),
        midText: mid.innerText.replace(/\\n/g, ' | '),
        ringText: ring.innerText.replace(/\\n/g, ' | '),
        cfText: cf? cf.innerText: '',
        chipText: chip? chip.innerText: '',
        cfColor: cf? getComputedStyle(cf).color: '',
        cfBg: cf? getComputedStyle(cf).backgroundColor: '',
        chipBg: chip? getComputedStyle(chip).backgroundImage: '',
        leftW: Math.round(r1.width),
        midW: Math.round(r2.width),
        ringW: Math.round(r3.width),
        leftTop: Math.round(r1.top),
        midCenterY: Math.round(r2.top + r2.height/2),
        ringCenterY: Math.round(r3.top + r3.height/2),
      };
    }''')
    print(theme, w, json.dumps(info, ensure_ascii=False))
    await b.close()

async def main():
    async with async_playwright() as pw:
        for theme in ('light', 'dark'):
            await shoot(pw, theme, 1280, 720, f'{theme}_desk')
            await shoot(pw, theme, 390, 760, f'{theme}_mob')

asyncio.run(main())
print('done')
