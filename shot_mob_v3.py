import asyncio
from playwright.async_api import async_playwright
SEED = {"profile":{"name":"Alan","entryMode":"monthly","locale":"zh-CN","baseCurrency":"CNY","returnRates":{"equity":0.07,"bond":0.03,"reit":0.05,"cash":0.01},"targetMode":"coverage","coverageTarget":25,"withdrawalRate":0.04,"birthYear":1990,"retireAge":45,"currentAge":36,"ffTarget":100,"ffMethod":"income-swap"},"incomes":[{"id":"i1","date":"2026-07-31","amount":50000,"category":"salary","note":"工资"},{"id":"i2","date":"2026-07-15","amount":8000,"category":"passive","note":"分红"}],"expenses":[{"id":"e1","date":"2026-07-20","amount":20000,"category":"living","note":"生活"}],"loans":[],"accounts":[],"snapshots":[],"reminders":[],"contracts":[]}
async def shot(b, theme, path):
    ctx = await b.new_context(viewport={"width":390,"height":820}, device_scale_factor=2)
    pg = await ctx.new_page()
    await pg.goto("http://127.0.0.1:8848/#/", wait_until="networkidle")
    await pg.evaluate("(s)=>localStorage.setItem('fire_companion_db_v1', JSON.stringify(s))", SEED)
    if theme == "dark":
        await pg.evaluate("localStorage.setItem('fire_theme','dark')")
    await pg.reload(wait_until="networkidle"); await pg.wait_for_timeout(600)
    el = await pg.query_selector(".stat-row--mob")
    await el.screenshot(path=path)
    await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await shot(b, "light", "shot_mobv3_light.png")
        await shot(b, "dark", "shot_mobv3_dark.png")
        await b.close()
asyncio.run(main())
