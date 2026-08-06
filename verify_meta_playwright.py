"""验证 round 7:hero 改底部横排 + Calculator 改成 3 列 + 第 5 格跨两行大字"""
import json, asyncio, os
from playwright.async_api import async_playwright

BASE = 'http://127.0.0.1:8820/verify_meta/'

SEED = {
    'profile': {
        'name':'Alan','entryMode':'daily','theme':'light','locale':'zh-CN','baseCurrency':'CNY','fireMultiple':25,
        'fireStatement':'从独立到自由',
        'returnRates':{'conservative':0.04,'neutral':0.07,'optimistic':0.10},
        'defaultReturnScenario':'neutral','reminderDaysBefore':3
    },
    'incomes':[{'id':'i1','date':'2026-07-25','amount':30000,'currency':'CNY','category':'工资'}],
    'expenses':[{'id':'e1','date':'2026-07-20','amount':6000,'currency':'CNY','category':'餐饮'}],
    'loans':[],'accounts':[],'snapshots':[],'reminders':[],'contracts':[],'badges':{}
}

async def screenshot_hero(ctx, theme, w, h, out_path):
    page = await ctx.new_page()
    seed = json.dumps({**SEED, 'profile':{**SEED['profile'], 'theme':theme}})
    await page.add_init_script(f'localStorage.setItem("fire_companion_db_v1", JSON.stringify({seed}));')
    await page.goto(BASE)
    await page.wait_for_load_state('networkidle')
    await page.wait_for_timeout(800)
    # hero 完整元素
    info = await page.evaluate('''() => {
        const hero = document.querySelector('.hero');
        if (!hero) return {missing: true};
        const r = hero.getBoundingClientRect();
        const top = hero.querySelector('.hero-top');
        const divider = hero.querySelector('.hero-divider');
        const meta = hero.querySelector('.hero-meta');
        const ring = hero.querySelector('.fire-ring');
        const tl = hero.querySelector('.hero-meta-label:nth-of-type(1)');
        const labels = Array.from(hero.querySelectorAll('.hero-meta-label')).map(n=>n.textContent);
        const values = Array.from(hero.querySelectorAll('.hero-meta-val')).map(n=>n.textContent);
        const rTop = top? top.getBoundingClientRect(): null;
        const rDivider = divider? divider.getBoundingClientRect(): null;
        const rMeta = meta? meta.getBoundingClientRect(): null;
        return {
            heroRect: {x: Math.round(r.left), y: Math.round(r.top), w: Math.round(r.width), h: Math.round(r.height)},
            top: rTop? {y: Math.round(rTop.top), h: Math.round(rTop.height)}: null,
            divider: rDivider? {y: Math.round(rDivider.top), h: Math.round(rDivider.height)}: null,
            meta: rMeta? {y: Math.round(rMeta.top), h: Math.round(rMeta.height)}: null,
            labels, values,
            ringW: ring? Math.round(ring.getBoundingClientRect().width): 0,
        };
    }''')
    print(f"[hero {theme} {w}x{h}]", json.dumps(info, ensure_ascii=False))
    # 截 hero 区域
    clip_top = max(0, info['heroRect']['y'] - 4)
    clip_h = info['heroRect']['h'] + 8
    await page.screenshot(path=out_path, clip={'x':0, 'y':clip_top, 'width':w, 'height':clip_h})
    await page.close()

async def screenshot_calc(ctx, theme, w, h, out_path):
    page = await ctx.new_page()
    seed = json.dumps({**SEED, 'profile':{**SEED['profile'], 'theme':theme}})
    await page.add_init_script(f'localStorage.setItem("fire_companion_db_v1", JSON.stringify({seed}));')
    await page.goto(BASE + '#/calculator')
    await page.wait_for_load_state('networkidle')
    await page.wait_for_timeout(800)
    info = await page.evaluate('''() => {
        const cells = Array.from(document.querySelectorAll('.calc-cell'));
        return cells.map(c => {
            const r = c.getBoundingClientRect();
            const lbl = c.querySelector('.calc-label')?.textContent || '';
            const val = c.querySelector('.calc-value')?.textContent || '';
            return {
                label: lbl,
                value: val,
                cls: c.className,
                x: Math.round(r.left),
                y: Math.round(r.top),
                w: Math.round(r.width),
                h: Math.round(r.height),
            };
        });
    }''')
    print(f"[calc {theme} {w}x{h}]")
    for c in info:
        print(' ', json.dumps(c, ensure_ascii=False))
    # 全屏截图,Calc 在 viewport 顶部
    await page.screenshot(path=out_path, full_page=False)
    await page.close()

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        # === Dashboard hero ===
        for (theme, tag) in [('light', 'l'), ('dark', 'd')]:
            ctx = await browser.new_context(viewport={'width':1280,'height':820})
            await screenshot_hero(ctx, theme, 1280, 820, f'shot_meta_hero_{tag}_1280.png')
            await ctx.close()
            ctx = await browser.new_context(viewport={'width':390,'height':820})
            await screenshot_hero(ctx, theme, 390, 820, f'shot_meta_hero_{tag}_390.png')
            await ctx.close()
        # === Calculator ===
        for (theme, tag) in [('light', 'l'), ('dark', 'd')]:
            ctx = await browser.new_context(viewport={'width':1280,'height':820})
            await screenshot_calc(ctx, theme, 1280, 820, f'shot_meta_calc_{tag}_1280.png')
            await ctx.close()
            ctx = await browser.new_context(viewport={'width':390,'height':820})
            await screenshot_calc(ctx, theme, 390, 820, f'shot_meta_calc_{tag}_390.png')
            await ctx.close()
        await browser.close()

asyncio.run(main())
