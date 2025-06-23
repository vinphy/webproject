import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue')
  },
  {
    path: '/components',
    name: 'Components',
    component: () => import('../views/Components.vue')
  },
  {
    path: '/logs',
    name: 'Logs',
    component: () => import('../views/Logs.vue')
  },
  {
    path: '/test',
    name: 'Test',
    component: () => import('../views/TestD.vue')
  },
  {
    path: '/bitTest',
    name: 'BitTest',
    component: () => import('../views/BitTest.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 


