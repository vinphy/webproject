import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'

const routes = [
  {
    path: '/',
    redirect: '/home'
  },
  { path: '/login', name: 'Login', component: () => import('../views/AuthLogin.vue') },
  { path: '/register', name: 'Register', component: () => import('../views/AuthRegister.vue') },
  {
    path: '/home',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/components',
    name: 'Components',
    component: () => import('../views/Components.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/logs',
    name: 'Logs',
    component: () => import('../views/Logs.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/test',
    name: 'Test',
    component: () => import('../views/QueryBuilderDemo.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/bitTest',
    name: 'BitTest',
    component: () => import('../views/childernVue.vue/HomeProjectItem.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/sqlErDiagram',
    name: 'SqlErDiagram',
    component: () => import('../views/SqlErDiagram.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/users',
    name: 'UserManagement',
    component: () => import('../views/UserManagement.vue'),
    meta: { requiresAuth: true, roles: ['admin'] }
  }
]

import { getCurrentUser } from '../utils/auth'

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const user = getCurrentUser()
  if (to.meta && to.meta.requiresAuth && !user) {
    return next({ path: '/login', query: { redirect: to.fullPath } })
  }
  if (to.meta && to.meta.roles && user && to.meta.roles.length > 0) {
    const role = user.role || 'user'
    if (!to.meta.roles.includes(role)) {
      return next('/dashboard')
    }
  }
  next()
})

export default router 

