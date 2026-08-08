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

async def run(browser, viewport, theme):
    ctx = await browser.new_context(viewport=viewport)
    page = await ctx.new_page()
    errs=[]
    page.on("pageerror", lambda e: errs.append(str(e)))
    await page.goto("http://127.0.0.1:8848/", wait_until="networkidle")
    await page.evaluate("(s)=>localStorage.setItem('fire_companion_db_v1', JSON.stringify(s))", SEED)
    await page.reload(wait_until="networkidle")
    await page.wait_for_timeout(600)
    data = await page.evaluate("""() => {
      const cards=[...document.querySelectorAll('.stat-row--mob > :not(:first-child) .stat-card')];
      const rows=[...document.querySelectorAll('.stat-row--mob > :not(:first-child)')];
      const res=rows.map((r,i)=>{
        const c=r.querySelector('.stat-card');
        const det=r.querySelector('.stat-foot--income-detail');
        const visDet = det ? getComputedStyle(det).display !== 'none' : null;
        return {w:Math.round(r.getBoundingClientRect().width), h:Math.round(c.getBoundingClientRect().height), incomeDetailVisible: visDet};
      });
      return res;
    }""")
    await ctx.close()
    return data, errs

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for theme in ["light","dark"]:
            for vp in [{"width":390,"height":780},{"width":768,"height":1024}]:
                d, errs = await run(b, vp, theme)
                ws=[x["w"] for x in d]; hs=[x["h"] for x in d]
                wEq=len(set(ws))==1; hEq=len(set(hs))==1
                vis = [x["incomeDetailVisible"] for x in d]
                print(f"[{theme} {vp['width']}x{vp['height']}] widths={ws} wEq={wEq} | heights={hs} hEq={hEq} | incomeDetailVisible(4副卡)={vis} | errs={errs}")
        await b.close()

asyncio.run(main())
