#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测量手机版 4 张副卡(财务自由度/年被动/月入/月出)的宽高是否一致。"""
import json, asyncio
from datetime import date, timedelta
from playwright.async_api import async_playwright

BASE = 'http://127.0.0.1:8846/'

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

async def measure(pw, theme, w, h, name):
    b = await pw.chromium.launch()
    ctx = await b.new_context(viewport={'width': w, 'height': h})
    p = await ctx.new_page()
    seed = dict(SEED); seed['profile'] = dict(SEED['profile']); seed['profile']['theme'] = theme
    s = json.dumps(seed, ensure_ascii=False)
    await p.add_init_script('localStorage.setItem("fire_companion_db_v1", JSON.stringify(' + s + '));')
    await p.goto(BASE + '#/')
    await p.wait_for_load_state('networkidle')
    await p.wait_for_timeout(1400)
    info = await p.evaluate('''() => {
      const grid = document.querySelector('.stat-row--mob');
      const subs = [...grid.querySelectorAll(':scope > *')].slice(1);
      const rects = subs.map(c => {
        const card = c.querySelector('.stat-card') || c;
        const r = card.getBoundingClientRect();
        return { w: Math.round(r.width), h: Math.round(r.height) };
      });
      const widths = rects.map(r => r.w);
      const heights = rects.map(r => r.h);
      const wEqual = Math.max(...widths) - Math.min(...widths) <= 2;
      const hEqual = Math.max(...heights) - Math.min(...heights) <= 2;
      return { widths, heights, wEqual, hEqual };
    }''')
    print(name, json.dumps(info, ensure_ascii=False))
    await p.screenshot(path=f'shot_mobeq_{name}.png')
    await b.close()

async def main():
    async with async_playwright() as pw:
        for theme in ('light', 'dark'):
            await measure(pw, theme, 390, 780, f'{theme}_mob')

asyncio.run(main())
print('done')
