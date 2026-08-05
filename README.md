# FIRE2FREE · 你的 FIRE 早起退休陪跑系统 / Your FIRE Early-Retirement Companion

> 一个**纯前端、本地优先、隐私安全**的个人财务陪跑 Web 应用。 — A **pure-frontend, local-first, privacy-safe** personal-finance companion web app.
> 帮你记清每一笔收支、看清投资盈亏、算准「还要多久能退休」,并用**对赌 + 徽章 + 连胜**把枯燥的攒钱变成可持续的游戏。 — It helps you track every income and expense, see your investment gains and losses clearly, calculate *"how long until I can retire"*, and turns the grind of saving into a sustainable game with **self-betting, badges, and streaks**.

FIRE（Financial Independence, Retire Early）不是一夜暴富,而是用数据看清「我现在离自由还有多远」。FIRE2FREE 把记账、投资、目标计算与自律激励整合到一个轻量应用里——**不联网、不上传、不卖数据**,所有信息只存在你自己的浏览器中。
FIRE (Financial Independence, Retire Early) is not about getting rich overnight — it's about using data to see *"how far am I from freedom, right now."* FIRE2FREE brings bookkeeping, investing, goal calculation, and self-discipline motivation into one lightweight app — **no network, no uploads, no data selling**. Everything lives only in your own browser.

---

## ✨ 八大核心亮点（Why FIRE2FREE）/ Eight Core Highlights

| # | 亮点 / Highlight | 一句话价值 / Value |
|---|------|-----------|
| 1 | 🎯 **自我对赌系统 / Self-Betting System** | 和自己签「赌约」:连续打卡 / 月储蓄率 / 月支出上限,达标自动弹庆祝。纯心理承诺,把自律变成有仪式感的事。 — Make a "bet" with yourself — check-in streaks / monthly savings rate / monthly spending cap. Hit the goal and a celebration fires automatically. |
| 2 | 🔀 **双录入模式 / Dual Entry Mode** | 首次启动选「每日逐笔」或「每月总额」,两种记账习惯都尊重,随时切换(下月生效)。 — Choose "daily itemized" or "monthly total" on first launch; both habits respected, switch anytime (takes effect next month). |
| 3 | 🧮 **FIRE ETA 计算器 / FIRE ETA Calculator** | 基于 4% 法则算目标/缺口/进度,保守/中性/乐观三情景,拖「每月多攒」滑杆实时重算退休时间表。 — Targets / gaps / progress from the 4% rule, with conservative / neutral / optimistic scenarios; drag the "save more" slider to recompute your timeline live. |
| 4 | ⚖️ **动态平衡 / 躺平检测 / Dynamic Balance · Coast-FI Check** | 用「净资产 × 年化收益 − 年支出」判断是否「已可躺平」,给出覆盖率与明确结论。 — Uses "net worth × annual return − annual spending" to tell you whether you can already *coast*, with a coverage ratio and a clear verdict. |
| 5 | 📈 **投资成本基线 / Investment Cost Basis** | 由「当前市值 − 持仓盈亏」反推建仓成本,首月即显示累计盈亏,不从头算起。 — Reverse-engineers entry cost from "current market value − unrealized P/L", so cumulative gains since purchase show from month one. |
| 6 | 🏅 **游戏化激励 / Gamified Motivation** | 6 枚里程碑徽章 + 12 个月连胜打卡网格,把长期坚持可视化。 — 6 milestone badges + a 12-month streak check-in grid that makes long-term consistency visible. |
| 7 | 🖼️ **一键分享月度报告 / One-Click Monthly Report** | Canvas 现绘 1080×1350 分享图(含 LOGO 与甜甜圈图),一键导出 PNG 发朋友圈。 — A Canvas-drawn 1080×1350 share image (with logo and donut chart) exports to PNG in one tap, ready for social sharing. |
| 8 | 🌐 **双语 · PWA · 隐私优先 / Bilingual · PWA · Privacy-First** | 中文/英文实时切换、可安装为离线 App、数据仅存本地浏览器。 — Instant Chinese/English switching, installable as an offline app, data stored only in your local browser. |

---

## 📋 功能清单 / Feature List

### 核心记账 / Core Tracking
- **收入记录 / Income logging**:主动 / 被动收入双 Tab,多币种,千分位格式化,「复制上一笔」快捷填充。 — Active / passive income dual tabs, multi-currency, thousands formatting, "copy previous entry" quick-fill.
- **支出记录 / Expense logging**:15 个内置分类 + 自定义,多币种逐笔录入。 — 15 built-in categories + custom, multi-currency itemized entry.
- **双录入模式 / Dual Entry Mode** ⭐:每日逐笔 / 每月总额,贯穿全局展示逻辑。 — Daily itemized / monthly total, threaded through the entire display logic.
- **多币种与汇率 / Multi-currency & FX**:CNY / HKD / TWD / USD,可编辑 FX 汇率,全量按基准币种折算。 — CNY / HKD / TWD / USD with editable FX rates; everything converted to a base currency.
- **净资产 / 现金流聚合 / Net-worth / Cash-flow Aggregation**:按月汇总,投资市值变动不混入现金流(避免重复计)。 — Monthly rollups where investment market-value changes are NOT mixed into cash flow (no double counting).
- **本地存储与备份 / Local Storage & Backup**:localStorage 持久化,支持 JSON / CSV 导入导出与一键重置。 — localStorage persistence, JSON / CSV import-export and one-tap reset.

### 投资管理 / Investment
- **投资账户 / Investment Accounts**:9 种账户类型,账户级月度净值快照(同账户同月覆盖更新)。 — 9 account types, per-account monthly net-worth snapshots (same account + same month = overwrite update).
- **成本基线 / Cost Basis** ⭐:自动反推,首月即显建仓以来累计盈亏。 — Auto-reverse-engineered; cumulative P/L since purchase shows from month one.
- **月度盈亏与汇总 / Monthly P/L & Rollup**:逐月盈亏 = 市值变动 − 净流入,配市值走势图。 — Monthly P/L = market-value change − net inflow, paired with a value-trend chart.

### 自律与激励 / Motivation & Gamification
- **自我对赌 / Self-Betting** ⭐:三类目标 + 一句承诺,实时进度条与状态机,达标自动庆祝。 — Three goal types + a personal pledge, live progress bar and state machine, auto-celebration on success.
- **徽章系统 / Badge System** ⭐:6 个本地计算的里程碑徽章(储蓄率、被动收入覆盖、FIRE 进度、连胜等)。 — 6 locally-computed milestone badges (savings rate, passive-income coverage, FIRE progress, streak, etc.).
- **连胜打卡 / Streak Check-in** ⭐:收入 + 支出 + 投资快照三项齐全即打卡,12 个月网格可视化。 — Check in when income + expense + investment snapshot are all done; 12-month grid visualization.
- **保存微动效 / Save Micro-feedback**:全局「已保存」反馈,操作有回应。 — Global "saved" feedback so every action feels responded to.

### 规划与计算 / Planning & Calculator
- **FIRE ETA 计算器 / FIRE ETA Calculator** ⭐:4% 法则 + 三情景复利迭代,「每月多攒」what-if 滑杆。 — 4% rule + three-scenario compound iteration, "save more each month" what-if slider.
- **动态平衡 / 安全边际 / Dynamic Balance · Safety Margin** ⭐:Dashboard 实时展示「已可躺平 / 还差多少」。 — Dashboard shows "already coasting / how much more to go" in real time.
- **提醒 / Reminders**:系统提醒(月末净资产回顾 / 每月 1 日)+ 自定义「每月几号」提醒。 — System reminders (month-end net-worth review / 1st of month) + custom "day of month" reminders.

### 报告 / Reports
- **月度报告 / Monthly Report** ⭐:任选月份收支 / 储蓄率 + 支出结构饼图 + Canvas 分享图导出。 — Pick any month — income/expense / savings rate + spending-structure donut + Canvas share-image export.

### 系统 / 体验 / System / UX
- **双语 i18n / Bilingual i18n** ⭐:vue-i18n 中 / 英,侧栏实时切换,naive-ui 内置文案同步本地化。 — vue-i18n Chinese / English, instant switch in the sidebar, naive-ui built-in copy localized in sync.
- **PWA 离线 / PWA Offline** ⭐:生产构建注册 Service Worker,可安装、可离线使用。 — Service Worker registered in production builds; installable and usable offline.
- **主题 / Theme**:跟随系统 / 亮色 / 暗色三态。 — Follow system / light / dark — three states.
- **设置中心 / Settings Center**:个人资料、基准币种、FIRE 倍数、三档年化收益率、FX 汇率、数据管理。 — Profile, base currency, FIRE multiple, three-tier annual return, FX rates, data management.

---

## 🛠 技术栈 / Tech Stack

Vue 3 · Vite 5 · Pinia · naive-ui · ECharts 5 · vue-i18n · dayjs · PWA（Service Worker）
Pure frontend with no backend dependency. The build output can be hosted on any static server (includes a GitHub Pages auto-deploy workflow).

纯前端、无后端依赖,构建产物可直接托管任意静态服务(已含 GitHub Pages 自动部署工作流)。

## 🚀 本地运行 / Run Locally

```bash
npm install
npm run dev        # 开发预览 / dev preview
npm run build      # 生产构建 → dist/ / production build → dist/
```

## 🔒 隐私声明 / Privacy Statement

FIRE2FREE 不依赖任何服务器,所有财务数据仅存储于你当前浏览器的 `localStorage` 中,不会上传、不会同步、不会被第三方读取。换设备需手动导出 / 导入备份文件。
FIRE2FREE depends on no server. All financial data is stored only in your current browser's `localStorage` — never uploaded, never synced, never read by any third party. Switching devices requires manually exporting / importing a backup file.

---

© FIRE2FREE — 陪你算清每一笔,早一天自由。 / Count every cent with you, and help you reach freedom one day sooner.
