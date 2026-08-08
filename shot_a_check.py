import asyncio
from playwright.async_api import async_playwright

SEED = {"profile":{"name":"Alan","entryMode":"monthly","locale":"zh-CN","baseCurrency":"CNY","returnRates":{"equity":0.07,"bond":0.03,"reit":0.05,"cash":0.01},"targetMode":"coverage","coverageTarget":25,"withdrawalRate":0.04,"birthYear":1990,"retireAge":45,"currentAge":36,"ffTarget":100,"ffMethod":"income-swap"},"incomes":[{"id":"i1","date":"2026-07-31","amount":50000,"category":"salary","note":"工资"},{"id":"i2","date":"2026-07-15","amount":8000,"category":"passive","note":"分红"}],"expenses":[{"id":"e1","date":"2026-07-20","amount":20000,"category":"living","note":"生活"}],"loans":[],"accounts":[],"snapshots":[],"reminders":[],"contracts":[]}

async def shot(page, sel, path):
    el = await page.query_selector(sel)
    await el.screenshot(path=path)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        # mobile
        ctx = await b.new_context(viewport={"width":390,"height":780})
        pg = await ctx.new_page()
        await pg.goto("http://127.0.0.1:8849/#/", wait_until="networkidle")
        await pg.evaluate("(s)=>localStorage.setItem('fire_companion_db_v1', JSON.stringify(s))", SEED)
        await pg.reload(wait_until="networkidle"); await pg.wait_for_timeout(500)
        await shot(pg, ".stat-row--mob .stat-green", "shot_a_mob_green.png")
        info = await pg.evaluate("""() => {
          const d = document.querySelector('.stat-row--mob .stat-green .stat-foot--income-detail');
          const cs = getComputedStyle(d);
          const rect = d.getBoundingClientRect();
          return { text: d.innerText.replace(/\\n/g,'|'), ws: cs.whiteSpace, h: Math.round(rect.height) };
        }""")
        print("MOBILE income-detail:", info)
        await ctx.close()
        # desktop
        ctx2 = await b.new_context(viewport={"width":1280,"height":800})
        pg2 = await ctx2.new_page()
        await pg2.goto("http://127.0.0.1:8849/#/", wait_until="networkidle")
        await pg2.evaluate("(s)=>localStorage.setItem('fire_companion_db_v1', JSON.stringify(s))", SEED)
        await pg2.reload(wait_until="networkidle"); await pg2.wait_for_timeout(500)
        await shot(pg2, ".stat-row--desk .stat-green", "shot_a_desk_green.png")
        dinfo = await pg2.evaluate("""() => {
          const d = document.querySelector('.stat-row--desk .stat-green .stat-foot--income-detail');
          return { text: d.innerText.replace(/\\n/g,'|') };
        }""")
        print("DESKTOP income-detail:", dinfo)
        await ctx2.close()
        await b.close()

asyncio.run(main())
