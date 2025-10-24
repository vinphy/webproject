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
    path: '/logs/:id',
    name: 'LogDetail',
    component: () => import('../views/LogDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/test',
    name: 'Test',
    component: () => import('../views/QueryBuilderDemo.vue'),
    meta: { requiresAuth: true }
  },
  // {
  //   path: '/bitTest',
  //   name: 'BitTest',
  //   component: () => import('../views/BitTest.vue'),
  //   meta: { requiresAuth: true }
  // },
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
    meta: { requiresAuth: true, permissions: ['auth:manage'] }
  },
  {
    path: '/permission',
    name: 'Permission',
    component: () => import('../views/Permission.vue'),
    meta: { requiresAuth: true, permissions: ['auth:manage'] }
  },
  {
    path: '/projects',
    name: 'Projects',
    component: () => import('../views/Projects.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/project-add',
    name: 'ProjectAdd',
    component: () => import('../views/ProjectAdd.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/project-detail/:id',
    name: 'ProjectDetail',
    component: () => import('../views/ProjectDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/test-cases',
    name: 'TestCases',
    component: () => import('../views/TestCases.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/test-case-detail/:id',
    name: 'TestCaseDetail',
    component: () => import('../views/TestCaseDetail.vue'),
    meta: { requiresAuth: true }
  }
]

import { getCurrentUser } from '../utils/auth'
import { initPermissions, hasPermission, permissionsRef } from '../utils/permission'


const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const user = getCurrentUser()
  if (to.meta && to.meta.requiresAuth && !user) {
    return next({ path: '/login', query: { redirect: to.fullPath } })
  }

  // If route defines permissions, check them. We allow admin role as fallback.
  if (to.meta && to.meta.permissions && to.meta.permissions.length > 0) {
    // ensure permissions loaded
    try {
      if (user && permissionsRef && Array.isArray(permissionsRef.value) && permissionsRef.value.length === 0) {
        await initPermissions()
      }
    } catch (e) {
      // ignore
    }
    const isAdmin = user && user.role === 'admin'
    if (!isAdmin) {
      // require at least one of the permissions
      const ok = to.meta.permissions.some(p => hasPermission(p))
      if (!ok) return next('/home')
    }
  }

  // legacy role-based guard (kept for backward compatibility)
  if (to.meta && to.meta.roles && user && to.meta.roles.length > 0) {
    const role = user.role || 'user'
    if (!to.meta.roles.includes(role)) {
      return next('/home')
    }
  }
  next()
})

export default router 

