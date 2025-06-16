<template>
  <div class="app">
    <el-container class="layout-container">
      <!-- 侧边栏 -->
      <el-aside width="220px" class="aside">
        <div class="logo">
          <img src="./assets/logo.svg" alt="Logo" class="logo-img">
          <span class="logo-text">vinphy</span>
        </div>
        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
        >
          <el-menu-item index="1" @click="handleMenuClick('dashboard')">
            <el-icon><Monitor /></el-icon>
            <span>仪表盘</span>
          </el-menu-item>
          <el-menu-item index="2" @click="handleMenuClick('components')">
            <el-icon><User /></el-icon>
            <span>模块管理</span>
          </el-menu-item>
          <el-menu-item index="3" @click="handleMenuClick('logs')">
            <el-icon><Goods /></el-icon>
            <span>日志管理</span>
          </el-menu-item>
          <el-menu-item index="3" @click="handleMenuClick('test')">
            <el-icon><Goods /></el-icon>
            <span>测试</span>
          </el-menu-item>
          <el-menu-item index="4" @click="handleMenuClick('bitTest')">
            <el-icon><Goods /></el-icon>
            <span>符合性测试</span>
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
                <span class="username">vinphy</span>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item>个人信息</el-dropdown-item>
                  <el-dropdown-item>修改密码</el-dropdown-item>
                  <el-dropdown-item divided>退出登录</el-dropdown-item>
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Monitor, User, Goods, List, Setting, Fold, Expand } from '@element-plus/icons-vue'

const router = useRouter()
const isCollapse = ref(false)
const activeMenu = ref('1')
const currentPage = ref('仪表盘')

const handleMenuClick = (route) => {
  router.push(`/${route}`)
  // 更新当前页面名称
  const pageNames = {
    dashboard: '仪表盘',
    components: '模块管理',
    logs: '日志管理',
    test: '测试',
    bitTest:'bit测试'
  }
  currentPage.value = pageNames[route]
}

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
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