import json, asyncio
from playwright.async_api import async_playwright

BASE = 'http://127.0.0.1:8810/'
SEED = {
  'profile': {'name':'Alan','entryMode':'daily','theme':'light','locale':'zh-CN','baseCurrency':'CNY','fireMultiple':25,'fireStatement':'从独立到自由','returnRates':{'conservative':0.04,'neutral':0.07,'optimistic':0.10},'defaultReturnScenario':'neutral','reminderDaysBefore':3},
  'incomes':[],'expenses':[],'loans':[],'accounts':[],'snapshots':[],'reminders':[],'contracts':[],'badges':{}
}

async def run(theme, w, h, tag):
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        ctx = await b.new_context(viewport={'width':w,'height':h})
        p = await ctx.new_page()
        s = json.dumps(SEED | {'profile': {**SEED['profile'], 'theme': theme}})
        await p.add_init_script(f'localStorage.setItem("fire_companion_db_v1", JSON.stringify({s}));')
        await p.goto(BASE)
        await p.wait_for_load_state('networkidle')
        await p.wait_for_timeout(800)
        # 滚到 quick-bar 在视口顶部可见(用 mouse.wheel 模拟用户拖动)
        await p.evaluate('() => { const bar = document.querySelector(".quick-bar"); bar.scrollIntoView({block: \"center\"}); }')
        await p.wait_for_timeout(400)
        info = await p.evaluate('() => { const bar = document.querySelector(".quick-bar"); const r = bar.getBoundingClientRect(); return {top: Math.round(r.top), bottom: Math.round(r.bottom), barH: Math.round(r.height), barW: Math.round(r.width)}; }')
        print(theme, w, json.dumps(info))
        clip_top = max(0, info['top'] - 6)
        clip_h = min(h - clip_top, info['barH'] + 12)
        await p.screenshot(path='shot_q_' + tag + '.png', clip={'x': 0, 'y': clip_top, 'width': w, 'height': clip_h})
        await b.close()

asyncio.run(run('light', 390, 820, 'light_390'))
asyncio.run(run('dark', 390, 820, 'dark_390'))
asyncio.run(run('light', 1280, 820, 'light_1280'))
asyncio.run(run('dark', 1280, 820, 'dark_1280'))
print('DONE')