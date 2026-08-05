import { createRouter, createWebHashHistory } from 'vue-router'
import Dashboard from '@/views/Dashboard.vue'
import Income from '@/views/Income.vue'
import Expense from '@/views/Expense.vue'
import Calculator from '@/views/Calculator.vue'
import Reminders from '@/views/Reminders.vue'
import Bets from '@/views/Bets.vue'
import Settings from '@/views/Settings.vue'
import Invest from '@/views/Invest.vue'
import MonthlyReport from '@/views/MonthlyReport.vue'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', name: 'dashboard', component: Dashboard },
  { path: '/income', name: 'income', component: Income },
  { path: '/expense', name: 'expense', component: Expense },
  { path: '/invest', name: 'invest', component: Invest },
  { path: '/calculator', name: 'calculator', component: Calculator },
  { path: '/reminders', name: 'reminders', component: Reminders },
  { path: '/bets', name: 'bets', component: Bets },
  { path: '/report', name: 'report', component: MonthlyReport },
  { path: '/settings', name: 'settings', component: Settings }
]

export default createRouter({
  history: createWebHashHistory(),
  routes
})
