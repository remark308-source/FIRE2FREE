"""
验证 Hero 改 C(中列储蓄率+预计达成)+ Calculator 紧凑表格(2x2+1,纯边框)
"""
import asyncio, json, os
from playwright.async_api import async_playwright

BASE = 'http://127.0.0.1:8810/'

SEED = {
  'profile': {
    'name':'Alan','entryMode':'daily','theme':'light','locale':'zh-CN',
    'baseCurrency':'CNY','fireMultiple':25,'fireStatement':'从独立到自由',
    'returnRates':{'conservative':0.04,'neutral':0.07,'optimistic':0.10},
    'defaultReturnScenario':'neutral','reminderDaysBefore':3
  },
  'incomes':[],'expenses':[],'loans':[],'accounts':[],
  'snapshots':[
    {'id':'s1','accountId':'a1','yearMonth':'2026-07','value':800000,'currency':'CNY','netInflow':0},
    {'id':'s2','accountId':'a1','yearMonth':'2026-08','value':850000,'currency':'CNY','netInflow':5000},
  ],
  'reminders':[],'contracts':[],'badges':{},
  'accounts':[{'id':'a1','name':'主仓','type':'fund','currency':'CNY','note':''}]
}

async def shot(page, name):
    await page.wait_for_timeout(500)
    await page.screenshot(path=name, full_page=False)
    print(f'[ok] {name}')

async def verify(theme, viewport):
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        ctx = await b.new_context(viewport=viewport)
        p = await ctx.new_page()
        seed = json.dumps(SEED)
        await p.add_init_script(f"localStorage.setItem('fire_companion_db_v1', JSON.stringify({seed}));")
        await p.goto(BASE)
        await p.wait_for_load_state('networkidle')
        await p.wait_for_timeout(800)

        # === Dashboard Hero: 验证 3 列结构 & 中列内容 ===
        hero_left = await p.locator('.hero-left').is_visible()
        hero_mid = await p.locator('.hero-mid').is_visible()
        hero_ring = await p.locator('.hero-ring').is_visible()
        mid_text = await p.locator('.hero-mid').inner_text()
        ring_svg = await p.locator('.fire-ring svg').is_visible()

        # 检查中列上下两块
        mid_items = await p.locator('.hero-mid-item').count()
        sr_text = await p.locator('.hero-mid-val--sr').inner_text()
        eta_text = await p.locator('.hero-mid-item').nth(1).locator('.hero-mid-val').inner_text()

        print(f'[DASH][{theme} {viewport["width"]}x{viewport["height"]}]')
        print(f'  hero-left={hero_left} hero-mid={hero_mid} hero-ring={hero_ring} ring-svg={ring_svg}')
        print(f'  mid-items={mid_items} savingsRate="{sr_text}" eta="{eta_text}"')
        print(f'  mid-text: {mid_text!r}')

        prefix = f'shot_v_dash_{theme}_{viewport["width"]}'
        await shot(p, f'{prefix}.png')

        # === Calculator: 紧凑表格验证 ===
        await p.goto(BASE + '#/calculator')
        await p.wait_for_load_state('networkidle')
        await p.wait_for_timeout(800)

        cells = await p.locator('.calc-cell').count()
        wide = await p.locator('.calc-cell-wide').count()
        labels = await p.locator('.calc-label').all_inner_texts()
        values = await p.locator('.calc-value').all_inner_texts()
        print(f'[CALC][{theme} {viewport["width"]}x{viewport["height"]}]')
        print(f'  cells={cells} wide={wide}')
        print(f'  labels={labels}')
        print(f'  values={values}')

        prefix = f'shot_v_calc_{theme}_{viewport["width"]}'
        await shot(p, f'{prefix}.png')

        await b.close()

async def main():
    await verify('light', {'width':1280,'height':820})
    await verify('dark', {'width':1280,'height':820})
    await verify('light', {'width':390,'height':780})
    await verify('dark', {'width':390,'height':780})

asyncio.run(main())