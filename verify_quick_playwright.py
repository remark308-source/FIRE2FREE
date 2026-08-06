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
        # 找 quick-bar
        info = await p.evaluate('''() => {
          const bar = document.querySelector('.quick-bar');
          if (!bar) return {found:false};
          const r = bar.getBoundingClientRect();
          const btns = Array.from(bar.querySelectorAll('.qa-btn')).map(b => {
            const t = b.querySelector('.qa-label');
            return {text: t? t.textContent : '', w: Math.round(b.getBoundingClientRect().width), h: Math.round(b.getBoundingClientRect().height)};
          });
          const title = bar.querySelector('.quick-title');
          return {found:true, barW: Math.round(r.width), barH: Math.round(r.height), title: title? title.textContent.trim():'', btns};
        }''')
        print(theme, w, json.dumps(info, ensure_ascii=False))
        bar = await p.query_selector('.quick-bar')
        if bar:
            await bar.screenshot(path=f'shot_q_{tag}.png')
        await b.close()

asyncio.run(run('light', 1280, 820, 'light_1280'))
asyncio.run(run('dark', 1280, 820, 'dark_1280'))
asyncio.run(run('light', 390, 820, 'light_390'))
asyncio.run(run('dark', 390, 820, 'dark_390'))
print('DONE')
