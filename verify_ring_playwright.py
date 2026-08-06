"""验证 Hero 改版 + Calculator 2x2x1 + 深色模式 ring 内文字清晰度"""
import asyncio
import json
from playwright.async_api import async_playwright

BASE = 'http://127.0.0.1:8800/'
VIEWPORTS = [
    ('desktop', 1280, 820),
    ('mobile_390', 390, 844),
    ('mobile_360', 360, 780),
]

# 同步把 profile entryMode/dimTheme 设好,跳过 Onboarding
SEED = {
    'profile': {
        'name': 'Alan',
        'entryMode': 'daily',
        'theme': 'light',
        'locale': 'zh-CN',
        'baseCurrency': 'CNY',
        'fireMultiple': 25,
        'fireStatement': '从独立到自由',
        'returnRates': {'conservative': 0.04, 'neutral': 0.07, 'optimistic': 0.10},
        'defaultReturnScenario': 'neutral',
        'reminderDaysBefore': 3,
    },
    'incomes': [],
    'expenses': [],
    'loans': [],
    'accounts': [],
    'snapshots': [],
    'reminders': [],
    'contracts': [],
    'badges': {},
}

async def run():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        results = []
        for theme in ['light', 'dark']:
            seed = json.dumps({**SEED, 'profile': {**SEED['profile'], 'theme': theme}})
            for label, w, h in VIEWPORTS:
                ctx = await browser.new_context(viewport={'width': w, 'height': h})
                page = await ctx.new_page()
                # 注入 localStorage,跳过 Onboarding
                await page.add_init_script(f"""
                    try {{
                        localStorage.setItem('fire_companion_db_v1', JSON.stringify({seed}));
                    }} catch (e) {{}}
                """)
                console_errs = []
                page.on('pageerror', lambda exc: console_errs.append(f'pageerror: {exc}'))
                page.on('console', lambda m: console_errs.append(f'console.{m.type}: {m.text}') if m.type in ('error', 'warning') else None)

                # Dashboard 验证
                await page.goto(BASE)
                await page.wait_for_load_state('networkidle', timeout=15000)
                await page.wait_for_timeout(800)
                await page.screenshot(path=f'shot_dash_{theme}_{label}.png', full_page=False)

                # 探测 SVG 文本
                info = await page.evaluate("""
                () => {
                  const ring = document.querySelector('.fire-ring svg');
                  const ringInfo = ring ? {
                    width: ring.getBoundingClientRect().width,
                    texts: Array.from(ring.querySelectorAll('text')).map(t => ({
                      content: t.textContent,
                      fill: getComputedStyle(t).fill,
                      x: t.getAttribute('x'),
                      y: t.getAttribute('y'),
                      fontsize: getComputedStyle(t).fontSize,
                    })),
                  } : null;
                  const hero = document.querySelector('.hero');
                  const heroMid = document.querySelector('.hero-mid');
                  const heroRing = document.querySelector('.hero-ring');
                  return {
                    ringInfo,
                    hasHeroMid: !!heroMid,
                    heroExists: !!hero,
                    heroRingRect: heroRing ? heroRing.getBoundingClientRect().toJSON() : null,
                    heroRingRightGap: heroRing ? (window.innerWidth - heroRing.getBoundingClientRect().right) : null,
                    bodyOverflowX: document.body.scrollWidth > window.innerWidth,
                    documentOverflowX: document.documentElement.scrollWidth > window.innerWidth,
                  };
                }
                """)
                results.append({'phase': f'dash-{theme}-{label}', 'info': info, 'errs': console_errs[:5]})

                # Calculator 验证
                await page.goto(BASE + '#/calculator')
                await page.wait_for_load_state('networkidle', timeout=15000)
                await page.wait_for_timeout(800)
                await page.screenshot(path=f'shot_calc_{theme}_{label}.png', full_page=True)
                calc_info = await page.evaluate("""
                () => {
                  const grid = document.querySelector('.calc-grid');
                  const cells = document.querySelectorAll('.calc-grid .calc-cell');
                  const wide = document.querySelectorAll('.calc-grid .calc-cell-wide');
                  return {
                    gridCols: grid ? getComputedStyle(grid).gridTemplateColumns : null,
                    cellCount: cells.length,
                    wideCount: wide.length,
                    wideRect: wide[0] ? wide[0].getBoundingClientRect().toJSON() : null,
                    calcWrapRect: document.querySelector('.calc-wrap') ? document.querySelector('.calc-wrap').getBoundingClientRect().toJSON() : null,
                    bodyOverflowX: document.body.scrollWidth > window.innerWidth,
                  };
                }
                """)
                results.append({'phase': f'calc-{theme}-{label}', 'info': calc_info, 'errs': console_errs[:5]})
                await ctx.close()
        await browser.close()
        # 报告
        print(json.dumps(results, ensure_ascii=False, indent=2, default=str))

asyncio.run(run())
