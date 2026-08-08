#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证 dashboard 4 卡 / 手机 5 卡 + 副卡等宽 + hero 等宽 + 编辑功能 + 工资增速输入 + wp-grid 自适应(无失业)
- Dashboard 桌面/手机 × 浅/深:截图 + 测量 stat 卡数 + 副卡等宽 + 财务自由度条 + hero 等宽
- Calculator:截图验证 推演区块(flex 自适应, 无失业 radio) + 工资增速输入框
- Income/Expense:截图验证 编辑按钮存在
"""
import json, asyncio
from datetime import date, timedelta
from playwright.async_api import async_playwright

BASE = 'http://127.0.0.1:8845/'

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

async def shoot(pw, path, theme, w, h, name, hash_route='#/'):
    b = await pw.chromium.launch()
    ctx = await b.new_context(viewport={'width': w, 'height': h})
    p = await ctx.new_page()
    p.on('pageerror', lambda e: errors.append(f'{name}:PAGEERROR:{e}'))
    p.on('console', lambda m: errors.append(f'{name}:CONSOLE_ERR:{m.text}') if m.type == 'error' else None)
    seed = dict(SEED); seed['profile'] = dict(SEED['profile']); seed['profile']['theme'] = theme
    s = json.dumps(seed, ensure_ascii=False)
    await p.add_init_script('localStorage.setItem("fire_companion_db_v1", JSON.stringify(' + s + '));')
    await p.goto(BASE + hash_route + path)
    await p.wait_for_load_state('networkidle')
    await p.wait_for_timeout(1400)
    await p.screenshot(path=f'shot_ff2_{name}.png')
    info = await p.evaluate('''() => {
      const ff = document.querySelector('.hero-ff, .ff-bar--card');
      const fill = document.querySelector('.ff-bar-fill');
      const txt = document.querySelector('.hero-ff-val, .n-statistic-value__content');
      const deskCards = document.querySelectorAll('.stat-row--desk > *').length;
      const mobCards = document.querySelectorAll('.stat-row--mob > *').length;
      const deskVisible = document.querySelector('.stat-row--desk') ? getComputedStyle(document.querySelector('.stat-row--desk')).display : 'none';
      const mobVisible = document.querySelector('.stat-row--mob') ? getComputedStyle(document.querySelector('.stat-row--mob')).display : 'none';
      const deskHero = !!document.querySelector('.hero--desktop .hero-ring-col');
      const deskStats = !!document.querySelector('.hero--desktop .hero-stats');
      const deskFF = !!document.querySelector('.hero--desktop .hero-ff');
      const calcWP = !!document.querySelector('.wp-grid');
      const wpGrid = document.querySelector('.wp-grid');
      const wpGridDisplay = wpGrid ? getComputedStyle(wpGrid).display : 'none';
      const hasUnemp = !!document.querySelector('.wp-ctrl .n-radio-group') || !!document.body.innerText.includes('失业');
      let mobSubWidths = [];
      const mobGrid = document.querySelector('.stat-row--mob');
      if (mobGrid) {
        const subs = [...mobGrid.querySelectorAll(':scope > *')].slice(1);
        mobSubWidths = subs.map(c => { const card = c.querySelector('.stat-card') || c; return Math.round(card.getBoundingClientRect().width); });
      }
      const mobSubEqual = mobSubWidths.length >= 4 ? (Math.abs(mobSubWidths[0]-mobSubWidths[1])<2 && Math.abs(mobSubWidths[2]-mobSubWidths[3])<2) : null;
      const top = document.querySelector('.hero--desktop .hero-stats-top');
      const ffRow = document.querySelector('.hero--desktop .hero-ff');
      const heroEqualWidth = top && ffRow ? Math.abs(top.getBoundingClientRect().width - ffRow.getBoundingClientRect().width) < 2 : null;
      const salaryInput = !!document.querySelector('.wp-ctrl .n-input-number input');
      const has100 = !!document.body.innerText.match(/(^|\\s)100(\\s|$)/) && !!document.querySelector('.ff-tick-label');
      return {
        ffText: txt ? txt.textContent.trim() : 'N/A',
        fillW: fill ? Math.round(parseFloat(getComputedStyle(fill).width)) : 'N/A',
        statCardsDesk: deskCards, statCardsMob: mobCards, deskVisible, mobVisible,
        deskHero, deskStats, deskFF, calcWP, wpGridDisplay, hasUnemp, mobSubWidths, mobSubEqual,
        heroEqualWidth, salaryInput, has100
      };
    }''')
    print(name, json.dumps(info, ensure_ascii=False))
    await b.close()

async def shoot_income(pw, theme, w, h, name):
    b = await pw.chromium.launch()
    ctx = await b.new_context(viewport={'width': w, 'height': h})
    p = await ctx.new_page()
    p.on('pageerror', lambda e: errors.append(f'{name}:PAGEERROR:{e}'))
    p.on('console', lambda m: errors.append(f'{name}:CONSOLE_ERR:{m.text}') if m.type == 'error' else None)
    seed = dict(SEED); seed['profile'] = dict(SEED['profile']); seed['profile']['theme'] = theme
    s = json.dumps(seed, ensure_ascii=False)
    await p.add_init_script('localStorage.setItem("fire_companion_db_v1", JSON.stringify(' + s + '));')
    await p.goto(BASE + '#/income')
    await p.wait_for_load_state('networkidle')
    await p.wait_for_timeout(1000)
    await p.screenshot(path=f'shot_ff2_{name}.png')
    info = await p.evaluate('''() => {
      const allBtns = [...document.querySelectorAll('.n-data-table button')];
      const edits = allBtns.filter(b => b.textContent.trim() === '编辑').length;
      const rows = document.querySelectorAll('.n-data-table-tr').length;
      return { editBtns: edits, rows };
    }''')
    print(name, json.dumps(info, ensure_ascii=False))
    await b.close()

async def main():
    async with async_playwright() as pw:
        for theme in ('light', 'dark'):
            await shoot(pw, '', theme, 1280, 760, f'dash_{theme}_desk')
            await shoot(pw, '', theme, 390, 780, f'dash_{theme}_mob')
            await shoot(pw, 'calculator', theme, 1280, 900, f'calc_{theme}_desk')
            await shoot(pw, 'calculator', theme, 390, 900, f'calc_{theme}_mob')
            await shoot_income(pw, theme, 1280, 760, f'inc_{theme}_desk')
    print('ERRORS:', errors if errors else 'none')

asyncio.run(main())
print('done')
