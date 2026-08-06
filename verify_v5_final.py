"""verify_v5 实测：9 项菜单 + 汉堡位置 + meta 字号"""
import asyncio, json
from playwright.async_api import async_playwright

SEED = {'profile':{'name':'Alan','locale':'zh-CN','theme':'light','entryMode':'monthly','baseCurrency':'CNY','defaultReturnScenario':'neutral','returnRates':{'conservative':0.04,'neutral':0.07,'optimistic':0.10}},'incomes':[],'expenses':[],'loans':[],'accounts':[],'snapshots':[],'reminders':[],'contracts':[]}
URL = 'http://localhost:8854/index.html'

JS_FALLBACK = "() => { const sider = document.querySelector('.n-layout-sider'); const drawer = document.querySelector('.ss-panel'); const root = drawer || sider; if (!root) return {error: 'no sider nor drawer'}; const items = root.querySelectorAll('li, .n-menu-item, .n-menu-item-content'); const seen = new Set(); items.forEach(el => { const t = (el.innerText || '').trim(); if (t && t.length < 30) seen.add(t); }); return {items: [...seen], drawer_open: !!drawer}; }"
JS_BURGER = "() => { const b=document.querySelector('.menu-fab').getBoundingClientRect(); return {x:Math.round(b.x), y:Math.round(b.y), w:Math.round(b.width), h:Math.round(b.height)}; }"
JS_META = "() => { const v=document.querySelector('.hero--desktop .hero-meta-val'); return v ? getComputedStyle(v).fontSize : null; }"

async def run(p, vp, theme, label, open_drawer=True):
    ctx = await p.new_context(viewport=vp, device_scale_factor=2 if vp['width'] < 500 else 1)
    pg = await ctx.new_page()
    await pg.add_init_script("localStorage.setItem('fire_companion_db_v1', '%s');" % json.dumps(SEED))
    await pg.add_init_script("(d=>{const x=JSON.parse(localStorage.getItem('fire_companion_db_v1'));x.profile.theme='%s';localStorage.setItem('fire_companion_db_v1',JSON.stringify(x));})();" % theme)
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto(URL + '#/dashboard', wait_until='networkidle')
    await pg.wait_for_timeout(1100)
    if open_drawer and vp['width'] <= 768:
        await pg.click('.menu-fab')
        await pg.wait_for_timeout(700)
    items = await pg.evaluate(JS_FALLBACK)
    box = await pg.evaluate(JS_BURGER) if vp['width'] <= 768 else {}
    meta_size = await pg.evaluate(JS_META) if vp['width'] >= 1024 else None
    await pg.screenshot(path='verify_v5_shots/final_%s.png' % label, full_page=False)
    await ctx.close()
    return {'label': label, 'items': items, 'errors': errs[:3], 'burger_box': box, 'meta_val_fontsize': meta_size}


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        rs = []
        rs.append(await run(b, {'width': 1280, 'height': 800}, 'light', 'd1280_light_sider', open_drawer=False))
        rs.append(await run(b, {'width': 390, 'height': 844}, 'light', 'm390_light_drawer', open_drawer=True))
        rs.append(await run(b, {'width': 390, 'height': 844}, 'dark', 'm390_dark_drawer', open_drawer=True))
        rs.append(await run(b, {'width': 1280, 'height': 800}, 'dark', 'd1280_dark_hero', open_drawer=False))
        # mobile drawer closed (to see burger + hero position)
        rs.append(await run(b, {'width': 390, 'height': 844}, 'light', 'm390_light_closed', open_drawer=False))
        await b.close()
    for r in rs:
        print('---', r['label'], '---')
        print('  menu items:', r['items'].get('items', r['items']))
        print('  menu count:', len(r['items'].get('items', [])))
        print('  page errors:', r['errors'])
        print('  burger box:', r['burger_box'])
        print('  meta-val font-size:', r['meta_val_fontsize'])


asyncio.run(main())
