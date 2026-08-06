"""实际验证：菜单里到底有没有 dashboard。
- 桌面 1280 light：扫侧栏 NMenu 全部 key
- 手机 390 light：点汉堡开 drawer + 扫 drawer NMenu 全部 key
- 同时打一张截图
"""
import asyncio, json
from playwright.async_api import async_playwright

SEED = {
    'profile': {
        'name': 'Alan',
        'locale': 'zh-CN',
        'theme': 'light',
        'entryMode': 'monthly',
        'baseCurrency': 'CNY',
        'defaultReturnScenario': 'neutral',
        'returnRates': {'conservative': 0.04, 'neutral': 0.07, 'optimistic': 0.10}
    },
    'incomes': [], 'expenses': [], 'loans': [], 'accounts': [],
    'snapshots': [], 'reminders': [], 'contracts': []
}
URL = 'http://localhost:8854/index.html'

# 抓所有菜单项可见文本 + key, 不依赖具体 selector
LIST_JS = '''() => {
    const out = [];
    document.querySelectorAll('.n-menu-item, .n-menu-item-content, [class*="n-menu-option"], li[role="menuitem"]').forEach(el => {
        const t = el.innerText || el.textContent || '';
        const k = el.getAttribute('data-key') || el.getAttribute('data-cate') || '';
        if (t.trim()) out.push({key: k, text: t.trim()});
    });
    return out;
}'''

# 备选:把所有 visible 的菜单文本列出来
FALLBACK_JS = '''() => {
    const sider = document.querySelector('.n-layout-sider');
    const drawer = document.querySelector('.ss-panel');
    const root = drawer || sider;
    if (!root) return {error: 'no sider nor drawer', html: document.body.innerHTML.slice(0,500)};
    const items = [];
    root.querySelectorAll('li, a, div').forEach(el => {
        const text = (el.innerText || '').trim();
        if (text && text.length < 30 && text.length > 0) {
            const role = el.getAttribute('role');
            if (role === 'menuitem' || el.parentElement?.getAttribute('role') === 'menuitem' || el.classList.contains('n-menu-item-content')) {
                items.push(text);
            }
        }
    });
    return {items: [...new Set(items)], drawer_open: !!drawer};
}'''


async def run_viewport(p, viewport, theme, label):
    ctx = await p.new_context(viewport=viewport, device_scale_factor=2 if viewport['width'] < 500 else 1)
    page = await ctx.new_page()
    await page.add_init_script(
        "localStorage.setItem('fire_companion_db_v1', '%s');" % json.dumps(SEED))
    await page.add_init_script(
        "(d=>{const x=JSON.parse(localStorage.getItem('fire_companion_db_v1'));x.profile.theme='%s';localStorage.setItem('fire_companion_db_v1',JSON.stringify(x));})();" % theme)
    await page.goto(URL + '#/dashboard', wait_until='networkidle')
    await page.wait_for_timeout(1100)
    out = {'viewport': viewport, 'theme': theme}

    if viewport['width'] <= 768:
        # mobile: 点汉堡开 drawer
        fab = await page.query_selector('.menu-fab')
        out['menu-fab present'] = fab is not None
        if fab:
            await fab.click()
            await page.wait_for_timeout(700)
        ss = await page.query_selector('.ss-root')
        out['ss-root visible after click'] = ss is not None
        await page.screenshot(path=f'verify_v5/menu_{label}.png')
        # 抓 drawer NMenu 内容
        items = await page.evaluate(FALLBACK_JS)
        out['items'] = items
        # 抓 dashboard 关键词
        body_text = await page.evaluate('() => document.body.innerText')
        out['has_dashboard_text'] = ('仪表盘' in body_text)
        out['has_menu_keyword'] = ('菜单' in body_text)
    else:
        # desktop: 截图侧栏
        await page.screenshot(path=f'verify_v5/menu_{label}.png', full_page=False)
        items = await page.evaluate(FALLBACK_JS)
        out['items'] = items
        body_text = await page.evaluate('() => document.body.innerText')
        out['has_dashboard_text'] = ('仪表盘' in body_text)
    await ctx.close()
    return out


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        results = []
        results.append(await run_viewport(b, {'width': 1280, 'height': 800}, 'light', 'd1280_light'))
        results.append(await run_viewport(b, {'width': 390, 'height': 844}, 'light', 'm390_light'))
        results.append(await run_viewport(b, {'width': 390, 'height': 844}, 'dark', 'm390_dark'))
        await b.close()
    for r in results:
        print('---', r.get('viewport'), r.get('theme'), '---')
        for k, v in r.items():
            if k in ('viewport', 'theme'):
                continue
            print(f'  {k}: {v}')


asyncio.run(main())
