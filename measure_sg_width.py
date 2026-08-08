import asyncio
from playwright.async_api import async_playwright

SEED = {"profile":{"name":"Alan","entryMode":"monthly","locale":"zh-CN","baseCurrency":"CNY","returnRates":{"equity":0.07,"bond":0.03,"reit":0.05,"cash":0.01},"targetMode":"coverage","coverageTarget":25,"withdrawalRate":0.04,"birthYear":1990,"retireAge":45,"currentAge":36,"ffTarget":100,"ffMethod":"income-swap"},"incomes":[{"id":"i1","date":"2026-07-31","amount":50000,"category":"salary","note":"工资"},{"id":"i2","date":"2026-07-15","amount":8000,"category":"passive","note":"分红"}],"expenses":[{"id":"e1","date":"2026-07-20","amount":20000,"category":"living","note":"生活"}],"loans":[],"accounts":[],"snapshots":[],"reminders":[],"contracts":[]}

async def measure(b, w, h, theme):
    ctx = await b.new_context(viewport={"width":w,"height":h})
    pg = await ctx.new_page()
    await pg.goto("http://127.0.0.1:8850/#/calculator", wait_until="networkidle")
    await pg.evaluate("(s)=>localStorage.setItem('fire_companion_db_v1', JSON.stringify(s))", SEED)
    await pg.reload(wait_until="networkidle"); await pg.wait_for_timeout(400)
    d = await pg.evaluate("""() => {
      const ctrl = [...document.querySelectorAll('.wp-ctrl-label')].find(e => /工资年增率|Salary/.test(e.textContent));
      if (!ctrl) return null;
      const row = ctrl.closest('.wp-ctrl');
      const label = ctrl.getBoundingClientRect();
      const input = row.querySelector('.n-input');
      const ir = input.getBoundingClientRect();
      const val = row.querySelector('input');
      return { vp: window.innerWidth, labelW: Math.round(label.width), inputW: Math.round(ir.width), inputTextW: val ? Math.round(val.getBoundingClientRect().width) : -1, rowW: Math.round(row.getBoundingClientRect().width), inputFlex: getComputedStyle(input).flex };
    }""")
    await ctx.close()
    return d

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        r1 = await measure(b, 1280, 800, "desk")
        r2 = await measure(b, 390, 780, "mob")
        print("DESK", r1)
        print("MOB ", r2)

asyncio.run(main())
