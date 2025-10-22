<template>
  <div class="auth-page">
    <el-card class="login-card" shadow="hover">
      <div class="brand">
        <el-avatar :size="68" :src="logo" />
        <div class="brand-text">
          <div class="title">{{ title }}</div>
          <div class="subtitle">{{ subtitle }}</div>
        </div>
      </div>

      <div class="content">
        <slot />
      </div>

      <div class="tips">
        <slot name="tips" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import logo from '../assets/logo.svg'

const props = defineProps({
  title: { type: String, default: '欢迎' },
  subtitle: { type: String, default: '' }
})
</script>

<style scoped>
.auth-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #dde5f4 0%, #dde5f4 100%);
}
.login-card {
  width: 420px;
  padding: 30px 35px;
  background-color: #f1f7fe;
  box-shadow: 0 0 2em #e6e9f9;
  border-radius: 30px;
  min-height: auto;
}
.brand {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 35px;
  background: transparent;
  padding: 5px 0;
}
:deep(.el-avatar) {
  background: transparent !important;
}
.brand-text .title {
  font-size: 22px;
  font-weight: 700;
  color: #2b3a4b;
}
.brand-text .subtitle {
  color: #8a97a8;
  font-size: 14px;
  margin-top: 4px;
}
.content { margin-top: 10px; }
:deep(.el-input){
  --el-input-height: 52px;
  font-size: 16px;
}
:deep(.el-input__wrapper){
  border-radius:16px;
  padding:0 16px;
}



</style>
