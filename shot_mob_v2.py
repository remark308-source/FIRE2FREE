import asyncio
from playwright.async_api import async_playwright

SEED = {
  "profile": {"name":"测试","entryMode":"monthly","locale":"zh-CN","baseCurrency":"CNY",
    "returnRates":{"stocks":0.07,"bonds":0.03,"cash":0.01,"realEstate":0.02,"other":0.02},
    "fireTarget":25,"monthlyExpense":20000,"currentAge":30,"retireAge":45,"passiveIncome":0},
  "incomes":[{"id":"i1","date":"2026-07-31","amount":30000,"category":"工资","account":"a1","isMonthlyTotal":True}],
  "expenses":[{"id":"e1","date":"2026-07-31","amount":12000,"category":"生活","account":"a1","isMonthlyTotal":True}],
  "loans":[],"accounts":[{"id":"a1","name":"现金","type":"cash","balance":500000,"currency":"CNY"}],
  "snapshots":[],"reminders":[],"contracts":[]
}

async def shot(browser, theme, path):
    ctx = await browser.new_context(viewport={"width":390,"height":780})
    page = await ctx.new_page()
    await page.goto("http://127.0.0.1:8848/", wait_until="networkidle")
    await page.evaluate("(s)=>localStorage.setItem('fire_companion_db_v1', JSON.stringify(s))", SEED)
    await page.reload(wait_until="networkidle")
    await page.wait_for_timeout(700)
    el = await page.query_selector(".stat-row--mob")
    await el.screenshot(path=path)
    await ctx.close()
    print("saved", path)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await shot(b, "light", "shot_mobv2_light.png")
        await shot(b, "dark", "shot_mobv2_dark.png")
        await b.close()

asyncio.run(main())
