import asyncio, json
from playwright.async_api import async_playwright

SEED = {
    "profile": {
        "name": "Alan", "entryMode": "daily", "locale": "zh-CN",
        "baseCurrency": "CNY", "fireMultiple": 25, "theme": "light",
        "returnRates": {"conservative": 0.04, "neutral": 0.07, "optimistic": 0.10},
        "defaultReturnScenario": "neutral", "fireStatement": "财务自由不是终点，而是选择的自由。",
        "monthlyTarget": {}
    },
    "incomes": [{"id":"i1","date":"2026-07-31","amount":30000,"category":"工资","type":"active"}],
    "expenses": [{"id":"e1","date":"2026-07-31","amount":12000,"category":"生活","type":"need"}],
    "loans": [], "accounts": [], "snapshots": [],
    "reminders": [], "contracts": []
}

URL = "http://localhost:8851/index.html"

async def seed(page):
    await page.add_init_script(
        "localStorage.setItem('fire_companion_db_v1', " + json.dumps(json.dumps(SEED)) + ");"
        "localStorage.setItem('fire_companion_theme', 'light');"
    )

async def check_hero(page, w, label):
    rows = []
    def vis(sel):
        return page.eval_on_selector(sel, "el => { const s = getComputedStyle(el); const r = el.getBoundingClientRect(); return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0; }")
    deskV = await vis(".hero--desktop")
    mobV = await vis(".hero--mobile")
    rows.append(f"{label}: hero--desktop visible={deskV}, hero--mobile visible={mobV}")
    # quick buttons count
    dq = await page.locator(".quick--desktop .qa-dbtn").count()
    mq = await page.locator(".quick--mobile .qa-btn").count()
    rows.append(f"   desktop quick buttons={dq}, mobile quick buttons={mq}")
    # savings rate color on desktop
    if deskV:
        sr = await page.eval_on_selector(".hero--desktop .hero-meta-val--sr", "el => getComputedStyle(el).color")
        rows.append(f"   desktop savings-rate color={sr}")
    # watermark present
    wm = await page.eval_on_selector(".hero--desktop", "el => getComputedStyle(el, '::before').content")
    rows.append(f"   desktop watermark ::before content={wm!r}")
    # mobile chips
    if mobV:
        cf = await vis(".hero--mobile .hero-cashflow")
        rc = await vis(".hero--mobile .hero-ring-chip")
        rows.append(f"   mobile cashflow chip={cf}, ring chip={rc}")
    return "\n".join(rows)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        out = []
        for w, h, theme in [(1280, 900, "light"), (1280, 900, "dark"), (390, 844, "light"), (390, 844, "dark")]:
            page = await browser.new_page(viewport={"width": w, "height": h})
            await seed(page)
            if theme == "dark":
                await page.add_init_script("localStorage.setItem('fire_companion_theme', 'dark');")
                SEED["profile"]["theme"] = "dark"
                await page.add_init_script("localStorage.setItem('fire_companion_db_v1', " + json.dumps(json.dumps(SEED)) + ");")
            await page.goto(URL + "#/", wait_until="networkidle")
            await page.wait_for_timeout(1200)
            out.append(await check_hero(page, w, f"DASH {w}x{h} {theme}"))
            await page.screenshot(path=f"verify_v2_shots/dash_{w}_{theme}.png", full_page=False)
            # calculator
            await page.goto(URL + "#/calculator", wait_until="networkidle")
            await page.wait_for_timeout(1000)
            box = await page.eval_on_selector(".calc-wrap", "el => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el); return {w: Math.round(r.width), h: Math.round(r.height), overflow: s.overflow, overflowY: s.overflowY}; }")
            out.append(f"CALC {w}x{h} {theme}: .calc-wrap -> width={box['w']} height={box['h']} overflow={box['overflow']}/{box['overflowY']}")
            await page.screenshot(path=f"verify_v2_shots/calc_{w}_{theme}.png", full_page=False)
            await page.close()
        await browser.close()
        print("\n".join(out))

asyncio.run(main())
