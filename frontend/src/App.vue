<template>
  <div class="app">
    <router-view v-if="$route.path.startsWith('/login') || $route.path.startsWith('/register')"></router-view>
    <el-container v-else class="layout-container">
      <!-- 侧边栏 -->
      <el-aside :width="isCollapse ? '64px' : '220px'" class="aside">
        <div class="logo" :class="{ 'is-collapse': isCollapse }">
          <img src="./assets/logo.svg" alt="Logo" class="logo-img">
          <span class="logo-text" v-show="!isCollapse">vinphy</span>
        </div>
        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
          :collapse="isCollapse"
        >
          <el-menu-item index="1" @click="handleMenuClick('home')">
            <el-icon><Monitor /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="2" v-if="can('modules')" @click="handleMenuClick('components')">
            <el-icon><User /></el-icon>
            <span>模块管理</span>
          </el-menu-item>
          <el-menu-item index="3" v-if="can('logs')" @click="handleMenuClick('logs')">
            <el-icon><Goods /></el-icon>
            <span>日志管理</span>
          </el-menu-item>
          <el-menu-item index="4" v-if="can('test')" @click="handleMenuClick('test')">
            <el-icon><Goods /></el-icon>
            <span>测试</span>
          </el-menu-item>
          <el-menu-item index="5" v-if="can('bit')" @click="handleMenuClick('bitTest')">
            <el-icon><Goods /></el-icon>
            <span>符合性测试</span>
          </el-menu-item>
          <el-menu-item index="6" v-if="can('er')" @click="handleMenuClick('sqlErDiagram')">
            <el-icon><DataAnalysis /></el-icon>
            <span>SQL ER图</span>
          </el-menu-item>
          
          <!-- 项目管理菜单 -->
          <el-sub-menu index="7" v-if="can('projects')">
            <template #title>
              <el-icon><Folder /></el-icon>
              <span>项目管理</span>
            </template>
            <el-menu-item index="7-1" @click="handleMenuClick('projects')">
              <el-icon><List /></el-icon>
              <span>项目列表</span>
            </el-menu-item>
            <el-menu-item index="7-2" @click="handleMenuClick('project-add')">
              <el-icon><Plus /></el-icon>
              <span>新增项目</span>
            </el-menu-item>
          </el-sub-menu>
          
          <el-menu-item index="8" v-if="isAdmin" @click="handleMenuClick('users')">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主要内容区 -->
      <el-container>
        <el-header class="header">
          <div class="header-left">
            <el-icon class="toggle-sidebar" @click="toggleSidebar">
              <Fold v-if="!isCollapse" />
              <Expand v-else />
            </el-icon>
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
              <el-breadcrumb-item>{{ currentPage }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <div class="header-right">
            <el-dropdown>
              <span class="user-info">
                <el-avatar :size="32" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
                <span class="username">{{ user?.username || '未登录' }}</span>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-if="user" @click="router.push('/permission')">权限管理</el-dropdown-item>
                  <el-dropdown-item v-if="user" @click="router.push('/dashboard')">个人信息</el-dropdown-item>
                  <el-dropdown-item v-if="user" @click="router.push('/dashboard')">修改密码</el-dropdown-item>
                  <el-dropdown-item divided v-if="user" @click="onLogout">退出登录</el-dropdown-item>
                  <el-dropdown-item v-else @click="router.push('/login')">登录</el-dropdown-item>
                  <el-dropdown-item v-else @click="router.push('/register')">注册</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>

        <el-main class="main">
          <router-view></router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Monitor, User, Goods, List, Setting, Fold, Expand, DataAnalysis, Folder, Plus } from '@element-plus/icons-vue'
import { getCurrentUser, clearToken, clearCurrentUser, userRef } from './utils/auth'

const router = useRouter()
const isCollapse = ref(false)
const activeMenu = ref('1')
const currentPage = ref('仪表盘')
const user = computed(() => userRef.value)
const isAdmin = computed(() => (user.value?.role || '') === 'admin')

const can = (key) => {
  // 简单基于角色的控制：admin全部可见，普通用户隐藏权限管理
  if (isAdmin.value) return true
  const allow = ['dashboard', 'modules', 'logs', 'test', 'bit', 'er', 'projects']
  return allow.includes(key)
}

const handleMenuClick = (route) => {
  router.push(`/${route}`)
  // 更新当前页面名称
  const pageNames = {
    home: '首页',
    components: '模块管理',
    logs: '日志管理',
    test: '测试',
    bitTest: 'bit测试',
    sqlErDiagram: 'SQL ER图',
    projects: '项目列表',
    'project-add': '新增项目',
    users: '用户管理',
    permission: '权限管理'
  }
  currentPage.value = pageNames[route]
}

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

const onLogout = () => {
  clearToken();
  clearCurrentUser();
  router.replace('/login')
}
</script>

<style>
.app {
  height: 100vh;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
}

.layout-container {
  height: 100%;
}

.aside {
  background-color: #304156;
  transition: width 0.3s;
  overflow: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  background: #2b3649;
}

.logo.is-collapse {
  justify-content: center;
}

.logo-img {
  width: 32px;
  height: 32px;
  margin-right: 12px;
}

.logo-text {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
}

.el-menu-vertical {
  border-right: none;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.toggle-sidebar {
  font-size: 20px;
  cursor: pointer;
  margin-right: 20px;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.username {
  margin-left: 8px;
  font-size: 14px;
  color: #606266;
}

.main {
  background-color: #f0f2f5;
  padding: 20px;
}

/* 自定义滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

::-webkit-scrollbar-track {
  background: #f0f2f5;
}
</style> 