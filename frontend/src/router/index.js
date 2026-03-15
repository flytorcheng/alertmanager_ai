import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue')
  },
  {
    path: '/receivers',
    name: 'Receivers',
    component: () => import('@/views/Receivers.vue')
  },
  {
    path: '/alert-groups',
    name: 'AlertGroups',
    component: () => import('@/views/AlertGroups.vue')
  },
  {
    path: '/alert-history',
    name: 'AlertHistory',
    component: () => import('@/views/AlertHistory.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router