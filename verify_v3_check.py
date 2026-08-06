import asyncio, json
from playwright.async_api import async_playwright

SEED = {
    "profile": {
        "name": "Alan", "locale": "zh-CN", "theme": "light", "entryMode": "monthly",
        "baseCurrency": "CNY", "defaultReturnScenario": "neutral",
        "returnRates": {"conservative": 0.04, "neutral": 0.07, "optimistic": 0.10},
    },
    "incomes": [], "expenses": [], "loans": [], "accounts": [],
    "snapshots": [], "reminders": [], "contracts": [],
}

URL = "http://localhost:8852/index.html"

def seed_script(theme):
    # 关键:JSON 必须包在单引号里,否则 setItem 会把对象 toString 成 [object Object]
    base = "localStorage.setItem('fire_companion_db_v1', '%s');" % json.dumps(SEED)
    ov = "(()=>{const d=JSON.parse(localStorage.getItem('fire_companion_db_v1'));d.profile.theme='%s';localStorage.setItem('fire_companion_db_v1',JSON.stringify(d));})();" % theme
    return base + ov

async def check_page(page, route):
    await page.goto(URL + "#/" + route, wait_until="networkidle")
    await page.wait_for_timeout(700)
    bn = await page.query_selector(".bottom-nav")
    mf = await page.query_selector(".menu-fab")
    fab = await page.query_selector(".fab")
    return bn is not None, mf is not None, fab is not None

async def main():
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        for theme in ("light", "dark"):
            # MOBILE
            ctx = await browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2)
            page = await ctx.new_page()
            await page.add_init_script(seed_script(theme))
            bn, mf, fab = await check_page(page, "dashboard")
            # calculator
            await page.goto(URL + "#/calculator", wait_until="networkidle")
            await page.wait_for_timeout(700)
            cw = await page.query_selector(".calc-wrap")
            box = await cw.bounding_box() if cw else None
            mf_el = await page.query_selector(".menu-fab")
            drawer_opened = False
            if mf_el:
                await mf_el.click()
                await page.wait_for_timeout(500)
                ds = await page.query_selector(".side-sheet")
                drawer_opened = bool(ds and await ds.is_visible())
            results.append({
                "viewport": "MOBILE 390", "theme": theme,
                "bottom_nav": bn, "menu_fab": mf, "fab": fab,
                "calc_w": round(box["width"], 1) if box else None,
                "calc_h": round(box["height"], 1) if box else None,
                "drawer_opens": drawer_opened,
            })
            await page.screenshot(path=f"verify_v3_shots/m390_{theme}_calc.png")
            await page.screenshot(path=f"verify_v3_shots/m390_{theme}_dash.png")
            await ctx.close()

            # DESKTOP
            ctx = await browser.new_context(viewport={"width": 1280, "height": 800}, device_scale_factor=1)
            page = await ctx.new_page()
            await page.add_init_script(seed_script(theme))
            bn, mf, fab = await check_page(page, "dashboard")
            await page.goto(URL + "#/calculator", wait_until="networkidle")
            await page.wait_for_timeout(700)
            cw = await page.query_selector(".calc-wrap")
            box = await cw.bounding_box() if cw else None
            results.append({
                "viewport": "DESKTOP 1280", "theme": theme,
                "bottom_nav": bn, "menu_fab": mf, "fab": fab,
                "calc_w": round(box["width"], 1) if box else None,
                "calc_h": round(box["height"], 1) if box else None,
                "drawer_opens": None,
            })
            await page.screenshot(path=f"verify_v3_shots/d1280_{theme}_calc.png")
            await ctx.close()

        await browser.close()

    for r in results:
        print(r)

asyncio.run(main())
