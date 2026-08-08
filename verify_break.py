import json, asyncio
from datetime import date, timedelta
from playwright.async_api import async_playwright

BASE = 'http://127.0.0.1:8845/'

def build_seed():
    inc, exp = [], []
    d = date(2025, 8, 5)
    for i in range(12):
        ym = (d + timedelta(days=32 * i)).strftime('%Y-%m-05')
        inc.append({'id': f'i{i}', 'date': ym, 'amount': 20000, 'type': 'active', 'category': '工资', 'note': ''})
        inc.append({'id': f'p{i}', 'date': ym, 'amount': 12800, 'type': 'passive', 'category': '分红', 'note': ''})
        exp.append({'id': f'e{i}', 'date': ym, 'amount': 15000, 'type': 'daily', 'category': '生活', 'note': ''})
    return inc, exp

SEED = {
    'profile': {
        'name': 'Alan', 'entryMode': 'daily', 'theme': 'light', 'locale': 'zh-CN',
        'baseCurrency': 'CNY', 'fireMultiple': 25, 'fireStatement': '从独立到自由',
        'returnRates': {'conservative': 0.04, 'neutral': 0.07, 'optimistic': 0.10},
        'defaultReturnScenario': 'neutral', 'reminderDaysBefore': 3,
    },
    'incomes': [], 'expenses': [], 'loans': [], 'accounts': [], 'snapshots': [], 'reminders': [], 'contracts': [], 'badges': {}
}
inc, exp = build_seed()
SEED['incomes'] = inc
SEED['expenses'] = exp
SEED['accounts'] = [{'id': 'a1', 'name': '投资账户', 'currency': 'CNY', 'openingValue': 1000000}]
SEED['snapshots'] = [{'id': 's1', 'accountId': 'a1', 'yearMonth': '2026-07', 'value': 1120000, 'currency': 'CNY', 'netInflow': 0}]

async def check(viewport_w, theme, label):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width': viewport_w, 'height': 844})
        pg = await ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: errs.append('CONSOLE:'+m.text) if m.type == 'error' else None)
        seed = dict(SEED); seed['profile'] = dict(SEED['profile']); seed['profile']['theme'] = theme
        s = json.dumps(seed, ensure_ascii=False)
        await pg.add_init_script('localStorage.setItem("fire_companion_db_v1", JSON.stringify(' + s + '));')
        await pg.goto(BASE + '#/', wait_until='networkidle')
        await pg.wait_for_timeout(1400)
        info = await pg.evaluate('''() => {
          const g = document.querySelector('.stat-row--mob');
          if(!g) return {foundMob:false};
          const cards = [...g.querySelectorAll('.stat-card')];
          let target = null;
          for (const c of cards) {
            const lbl = (c.querySelector('.n-statistic__label')||{}).textContent||'';
            if (lbl.includes('总收入')) { target = c; break; }
          }
          if(!target) return {foundMob:true, foundCard:false};
          const foot = target.querySelector('.stat-foot');
          const span = foot ? foot.querySelector('.mob-ff-break') : null;
          const fr = foot ? foot.getBoundingClientRect() : null;
          const sr = span ? span.getBoundingClientRect() : null;
          return {
            foundMob:true, foundCard:true,
            spanDisplay: span ? getComputedStyle(span).display : null,
            spanTop: sr ? Math.round(sr.top) : null,
            footTop: fr ? Math.round(fr.top) : null,
            footText: foot ? foot.textContent.trim() : null
          };
        }''')
        info['errs'] = errs[:5]
        await b.close()
        return info

async def main():
    mob = await check(390, 'light', 'MOBILE')
    dsk = await check(1280, 'light', 'DESKTOP')
    print(json.dumps({'MOBILE':mob,'DESKTOP':dsk}, ensure_ascii=False, indent=2))

asyncio.run(main())
