// 内置类别与币种常量(方案 v0.2 已确认)
// 每条带 zh / en 文案,走 i18n;用户自定义项累积进 UserProfile.customCategories

export const CATEGORIES = {
  // A 主动收入
  incomeActive: [
    { key: 'salary', zh: '工资', en: 'Salary' },
    { key: 'bonus', zh: '奖金', en: 'Bonus' },
    { key: 'side_hustle', zh: '副业', en: 'Side Hustle' },
    { key: 'other', zh: '其他', en: 'Other' }
  ],
  // B 被动收入
  incomePassive: [
    { key: 'rent', zh: '房租', en: 'Rent' },
    { key: 'interest', zh: '利息', en: 'Interest' },
    { key: 'fund_dividend', zh: '基金分红', en: 'Fund Dividend' },
    { key: 'stock_dividend', zh: '股票分红', en: 'Stock Dividend' },
    { key: 'other', zh: '其他', en: 'Other' }
  ],
  // C 日常支出
  expenseDaily: [
    { key: 'food', zh: '餐饮', en: 'Food' },
    { key: 'transport', zh: '交通', en: 'Transport' },
    { key: 'shopping', zh: '购物', en: 'Shopping' },
    { key: 'housing', zh: '居住(物业/水电)', en: 'Housing' },
    { key: 'medical', zh: '医疗', en: 'Medical' },
    { key: 'education', zh: '教育', en: 'Education' },
    { key: 'entertainment', zh: '娱乐', en: 'Entertainment' },
    { key: 'communication', zh: '通讯', en: 'Communication' },
    { key: 'insurance', zh: '保险', en: 'Insurance' },
    { key: 'subscription', zh: '订阅', en: 'Subscription' },
    { key: 'travel', zh: '旅行', en: 'Travel' },
    { key: 'gift', zh: '人情礼品', en: 'Gift' },
    { key: 'tax', zh: '税费', en: 'Tax' },
    { key: 'pet', zh: '宠物', en: 'Pet' },
    { key: 'other', zh: '其他', en: 'Other' }
  ],
  // D 投资账户类型
  accountType: [
    { key: 'a_share', zh: 'A股', en: 'A-Share' },
    { key: 'hk_stock', zh: '港股', en: 'HK Stock' },
    { key: 'us_stock', zh: '美股', en: 'US Stock' },
    { key: 'fund', zh: '基金', en: 'Fund' },
    { key: 'crypto', zh: '加密货币', en: 'Crypto' },
    { key: 'gold', zh: '黄金', en: 'Gold' },
    { key: 'bond', zh: '债券', en: 'Bond' },
    { key: 'wealth_mgmt', zh: '银行理财', en: 'Wealth Mgmt' },
    { key: 'other', zh: '其他', en: 'Other' }
  ],
  // E 信贷类型
  loanType: [
    { key: 'mortgage', zh: '房贷', en: 'Mortgage' },
    { key: 'auto_loan', zh: '车贷', en: 'Auto Loan' },
    { key: 'online_loan', zh: '网贷', en: 'Online/P2P Loan' },
    { key: 'other', zh: '其他', en: 'Other' }
  ]
}

// F 币种预设
export const CURRENCIES = [
  { code: 'CNY', symbol: '¥', zh: '人民币', en: 'CNY' },
  { code: 'HKD', symbol: 'HK$', zh: '港币', en: 'HKD' },
  { code: 'TWD', symbol: 'NT$', zh: '新台币', en: 'TWD' },
  { code: 'USD', symbol: '$', zh: '美元', en: 'USD' }
]

export const RETURN_SCENARIOS = {
  conservative: 0.05,
  neutral: 0.08,
  optimistic: 0.10
}

export const DEFAULT_FX = {
  CNY: 1,
  HKD: 0.92,
  TWD: 0.22,
  USD: 7.2
}

export function defaultProfile() {
  const now = new Date()
  return {
    name: '',
    startDate: `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`,
    initialAssets: 0,
    locale: 'zh-CN',
    theme: 'system',
    baseCurrency: 'CNY',
    fxRates: { CNY: 1, HKD: 0.92, TWD: 0.22, USD: 7.2 }, // 以 CNY 为基准:1 外币 = X CNY
    fireMultiple: 25,
    returnRates: { conservative: 0.05, neutral: 0.08, optimistic: 0.10 },
    defaultReturnScenario: 'neutral',
    fireStatement: '',
    entryMode: null, // 'daily' | 'monthly' | null(首次进入强制选)
    customCategories: { incomeActive: [], incomePassive: [], expenseDaily: [] }
  }
}

export function emptyDb() {
  return {
    profile: defaultProfile(),
    incomes: [],
    expenses: [],
    loans: [],
    accounts: [],
    snapshots: [],
    reminders: [],
    contracts: []
  }
}
