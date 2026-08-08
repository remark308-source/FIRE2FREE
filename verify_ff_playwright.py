#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证 财务自由度 + 财富自由推演
- Dashboard 桌面/手机 × 浅/深:截图 + 测量 财务自由度 文本/进度条 + 无 pageerror
- Calculator:截图验证 推演区块渲染
"""
import json, asyncio
from datetime import date, timedelta
from playwright.async_api import async_playwright

BASE = 'http://127.0.0.1:8844/'

# 生成 12 个月数据:主动 20000/月, 被动 12800/月(=64%), 支出 15000/月
def build_seed():
    inc, exp = [], []
    d = date(2025, 8, 5)
    for i in range(12):
        ym = (d + timedelta(days=32 * i)).strftime('%Y-%m-05')
        inc.append({'id': f'i{i}', 'date': ym, 'amount': 20000, 'type': 'active', 'category': '工资', 'note': ''})
        inc.append({'id': f'p{i}', 'date': ym, 'amount': 12800, 'type': 'passive', 'category': '分红', 'note': ''})
        exp.append({'id': f'e{i}', 'date': ym, 'amount': 15000, 'type': 'daily', 'category': '生活', 'note': ''})
    return inc, exp

SEED = {
    'profile': {
        'name': 'Alan', 'entryMode': 'daily', 'theme': 'light', 'locale': 'zh-CN',
        'baseCurrency': 'CNY', 'fireMultiple': 25, 'fireStatement': '从独立到自由',
        'returnRates': {'conservative': 0.04, 'neutral': 0.07, 'optimistic': 0.10},
        'defaultReturnScenario': 'neutral', 'reminderDaysBefore': 3,
    },
    'incomes': [], 'expenses': [], 'loans': [], 'accounts': [], 'snapshots': [], 'reminders': [], 'contracts': [], 'badges': {}
}
inc, exp = build_seed()
SEED['incomes'] = inc
SEED['expenses'] = exp
SEED['accounts'] = [{'id': 'a1', 'name': '投资账户', 'currency': 'CNY', 'openingValue': 1000000}]
SEED['snapshots'] = [{'id': 's1', 'accountId': 'a1', 'yearMonth': '2026-07', 'value': 1120000, 'currency': 'CNY', 'netInflow': 0}]

errors = []

async def shoot(pw, path, theme, w, h, name):
    b = await pw.chromium.launch()
    ctx = await b.new_context(viewport={'width': w, 'height': h})
    p = await ctx.new_page()
    p.on('pageerror', lambda e: errors.append(f'{name}:PAGEERROR:{e}'))
    p.on('console', lambda m: errors.append(f'{name}:CONSOLE_ERR:{m.text}') if m.type == 'error' else None)
    seed = dict(SEED); seed['profile'] = dict(SEED['profile']); seed['profile']['theme'] = theme
    s = json.dumps(seed, ensure_ascii=False)
    await p.add_init_script('localStorage.setItem("fire_companion_db_v1", JSON.stringify(' + s + '));')
    await p.goto(BASE + path)
    await p.wait_for_load_state('networkidle')
    await p.wait_for_timeout(1400)
    await p.screenshot(path=f'shot_ff_{name}.png')
    info = await p.evaluate('''() => {
      const ff = document.querySelector('.hero-ff, .ff-bar--card');
      const fill = document.querySelector('.ff-bar-fill');
      const txt = document.querySelector('.hero-ff-val, .n-statistic-value__content');
      // 统计卡张数
      const ngis = document.querySelectorAll('.stat-row > *').length;
      const deskHero = !!document.querySelector('.hero--desktop .hero-ring-col');
      const deskStats = !!document.querySelector('.hero--desktop .hero-stats');
      const deskFF = !!document.querySelector('.hero--desktop .hero-ff');
      const calcWP = !!document.querySelector('.wp-grid');
      return {
        ffText: txt ? txt.textContent.trim() : 'N/A',
        fillW: fill ? Math.round(parseFloat(getComputedStyle(fill).width)) : 'N/A',
        statCards: ngis,
        deskHero, deskStats, deskFF, calcWP
      };
    }''')
    print(name, json.dumps(info, ensure_ascii=False))
    await b.close()

async def main():
    async with async_playwright() as pw:
        for theme in ('light', 'dark'):
            await shoot(pw, '', theme, 1280, 760, f'dash_{theme}_desk')
            await shoot(pw, '', theme, 390, 780, f'dash_{theme}_mob')
            await shoot(pw, '#/calculator', theme, 1280, 900, f'calc_{theme}_desk')
            await shoot(pw, '#/calculator', theme, 390, 900, f'calc_{theme}_mob')
    print('ERRORS:', errors if errors else 'none')

asyncio.run(main())
print('done')
