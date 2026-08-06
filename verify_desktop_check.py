import json, sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:8850/index.html"

SEED = {
    "profile": {
        "name": "Alan", "locale": "zh-CN", "entryMode": "daily",
        "baseCurrency": "CNY",
        "fireStatement": "财务自由不是终点,而是选择的自由。",
        "fireMultiple": 25, "theme": "light",
    },
    "incomes": [
        {"id": "i1", "date": "2026-08-01", "type": "active", "category": "工资", "amount": 30000, "accountId": "a1", "currency": "CNY"}
    ],
    "expenses": [
        {"id": "e1", "date": "2026-08-02", "category": "餐饮", "amount": 8000, "accountId": "a1", "currency": "CNY"}
    ],
    "loans": [],
    "accounts": [
        {"id": "a1", "name": "总账户", "type": "cash", "balance": 1000000, "currency": "CNY"}
    ],
    "snapshots": [
        {"id": "s1", "accountId": "a1", "yearMonth": "2026-08", "value": 1000000, "currency": "CNY", "netInflow": 0}
    ],
    "reminders": [],
    "contracts": [],
}

def check(page, vw, theme):
    # seed + reload
    page.goto(URL)
    page.evaluate("(d)=>localStorage.setItem('fire_companion_db_v1', d)", json.dumps(SEED))
    page.reload()
    page.wait_for_selector(".hero", timeout=15000)
    page.wait_for_timeout(800)

    def disp(sel):
        el = page.query_selector(sel)
        if el is None:
            return "MISSING"
        return page.evaluate("(e)=>getComputedStyle(e).display", el)

    def color(sel):
        el = page.query_selector(sel)
        if el is None:
            return "MISSING"
        return page.evaluate("(e)=>getComputedStyle(e).color", el)

    grid = page.evaluate("(e)=>getComputedStyle(e).gridTemplateColumns", page.query_selector(".hero"))

    res = {
        "viewport": vw,
        "theme": theme,
        "hero_grid": grid,
        "statement": disp(".hero-statement"),
        "tags": disp(".hero-tags"),
        "divider": disp(".hero-mid-divider"),
        "cashflow": disp(".hero-cashflow"),
        "ringchip": disp(".hero-ring-chip"),
        "sr_color": color(".hero-mid-val--sr"),
    }
    # screenshot viewport top
    page.screenshot(path=f"verify_desktop_shots/vw{vw}_{theme}.png")
    return res

def main():
    out = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for theme in ["light", "dark"]:
            SEED["profile"]["theme"] = theme
            for vw in [1280, 390]:
                ctx = browser.new_context(viewport={"width": vw, "height": 1000})
                page = ctx.new_page()
                out.append(check(page, vw, theme))
                ctx.close()
        browser.close()
    for r in out:
        print(json.dumps(r, ensure_ascii=False))

if __name__ == "__main__":
    main()
