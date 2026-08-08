import asyncio
from playwright.async_api import async_playwright

SEED = {
  "profile": {
    "name": "Alan", "entryMode": "monthly", "locale": "zh-CN", "baseCurrency": "CNY",
    "returnRates": { "equity": 0.07, "bond": 0.03, "reit": 0.05, "cash": 0.01 },
    "targetMode": "coverage", "coverageTarget": 25, "withdrawalRate": 0.04,
    "birthYear": 1990, "retireAge": 45, "currentAge": 36,
    "ffTarget": 100, "ffMethod": "income-swap"
  },
  "incomes": [
    { "id": "i1", "date": "2026-07-31", "amount": 50000, "category": "salary", "note": "工资" },
    { "id": "i2", "date": "2026-07-15", "amount": 8000, "category": "passive", "note": "分红" }
  ],
  "expenses": [
    { "id": "e1", "date": "2026-07-20", "amount": 20000, "category": "living", "note": "生活" }
  ],
  "loans": [], "accounts": [], "snapshots": [], "reminders": [], "contracts": []
}

async def run(browser, viewport, theme):
    ctx = await browser.new_context(viewport=viewport)
    page = await ctx.new_page()
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    await page.goto("http://127.0.0.1:8848/#/", wait_until="networkidle")
    await page.evaluate("(s)=>localStorage.setItem('fire_companion_db_v1', JSON.stringify(s))", SEED)
    if theme == "dark":
        await page.evaluate("localStorage.setItem('fire_theme','dark')")
    await page.reload(wait_until="networkidle")
    await page.wait_for_timeout(500)
    data = await page.evaluate("""
    () => {
      const out = { cards: [], mobVisible: null, deskVisible: null, incomeDetailVisible: null, errs: [] };
      const mob = document.querySelector('.stat-row--mob');
      const desk = document.querySelector('.stat-row--desk');
      out.mobVisible = mob ? getComputedStyle(mob).display !== 'none' : false;
      out.deskVisible = desk ? getComputedStyle(desk).display !== 'none' : false;
      if (!mob) return out;
      const subs = [...mob.children].filter(c => !c.classList.contains(mob.firstElementChild?.classList?.[0] ?? '__x__'));
      // sub-cards = all children except first (净资产 full-width)
      const subCards = [...mob.children].slice(1);
      for (const ngi of subCards) {
        const card = ngi.querySelector('.stat-card');
        if (!card) continue;
        const r = card.getBoundingClientRect();
        const cls = [...card.classList].join(' ');
        out.cards.push({ cls, w: Math.round(r.width), h: Math.round(r.height) });
      }
      // 本月总收入 = stat-green
      const green = mob.querySelector('.stat-green');
      if (green) {
        const cr = green.getBoundingClientRect();
        const feet = green.querySelectorAll('.stat-foot');
        // last footer = mom
        const last = feet[feet.length - 1];
        const lr = last.getBoundingClientRect();
        const detail = green.querySelector('.stat-foot--income-detail');
        out.incomeDetailVisible = detail ? getComputedStyle(detail).display !== 'none' : false;
        out.greenMomGap = Math.round(cr.bottom - lr.bottom);
        out.greenH = Math.round(cr.height);
      }
      return out;
    }
    """)
    data["errs"] = errs
    data["theme"] = theme
    data["vp"] = viewport
    await ctx.close()
    return data

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for vp, label in [({"width":390,"height":780},"mobile"),({"width":768,"height":1024},"tablet")]:
            for theme in ["light","dark"]:
                d = await run(b, vp, theme)
                hs = [c["h"] for c in d["cards"]]
                ws = [c["w"] for c in d["cards"]]
                print(f"[{label} {theme}] w={ws} h={hs} equal_w={len(set(ws))==1} equal_h={len(set(hs))==1} momGap={d.get('greenMomGap')} greenH={d.get('greenH')} incDetail={d.get('incomeDetailVisible')} mobVis={d['mobVisible']} deskVis={d['deskVisible']} errs={len(d['errs'])}")
        await b.close()

asyncio.run(main())
