<template>
  <!-- 注册页：统一居中布局，卡片内包含品牌区 + 表单 + 辅助链接 -->
  <div class="register-page">
    <el-card class="register-card" shadow="hover">
      <div class="brand">
        <el-avatar :size="48" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
        <div class="brand-text">
          <div class="title">创建账户</div>
          <div class="subtitle">填写信息完成注册并自动登录</div>
        </div>
      </div>

      <!-- 表单：用户名/邮箱/密码/确认密码/角色（可选） -->
      <el-form ref="formRef" :model="form" :rules="rules" label-width="0" class="register-form" @keyup.enter.native="onSubmit">
        <el-form-item prop="username">
          <el-input v-model.trim="form.username" placeholder="用户名" clearable>
            <template #prefix><el-icon><User /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item prop="email">
          <el-input v-model.trim="form.email" placeholder="邮箱" clearable>
            <template #prefix><el-icon><Message /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" :type="showPwd ? 'text' : 'password'" placeholder="设置密码">
            <template #prefix><el-icon><Lock /></el-icon></template>
            <template #suffix>
              <el-icon class="clickable" @click="showPwd = !showPwd"><View v-if="!showPwd" /><Hide v-else /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item prop="confirm">
          <el-input v-model="form.confirm" :type="showPwd ? 'text' : 'password'" placeholder="确认密码">
            <template #prefix><el-icon><Lock /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-select v-model="form.role" placeholder="选择角色（可选）" style="width: 100%" clearable>
            <el-option label="admin" value="admin" />
            <el-option label="user" value="user" />
          </el-select>
        </el-form-item>

        <div class="row between">
          <div class="strength">
            <span>密码强度：</span>
            <el-tag :type="strengthTag.type" size="small">{{ strengthTag.text }}</el-tag>
          </div>
          <el-link type="primary" :underline="false" @click="goLogin">已有账号？去登录</el-link>
        </div>

        <el-form-item>
          <el-button type="primary" class="submit-btn" :loading="loading" @click="onSubmit">注册并登录</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
// 说明：
// - 增强注册体验：规范的校验（必填、邮箱格式、密码一致/强度）与加载态
// - 成功后自动执行登录流程并跳转首页
import { reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Message, Lock, View, Hide } from '@element-plus/icons-vue'
import { api, setToken, setCurrentUser } from '../utils/auth'

const router = useRouter()
const formRef = ref()
const form = reactive({ username: '', email: '', password: '', confirm: '', role: '' })
const loading = ref(false)
const showPwd = ref(false)

// 简单密码强度估算：长度 + 字符类别
const strengthScore = computed(() => {
  let s = 0
  if (form.password.length >= 6) s += 1
  if (/[A-Z]/.test(form.password)) s += 1
  if (/[a-z]/.test(form.password)) s += 1
  if (/[0-9]/.test(form.password)) s += 1
  if (/[^A-Za-z0-9]/.test(form.password)) s += 1
  return s
})
const strengthTag = computed(() => {
  if (!form.password) return { text: '无', type: 'info' }
  if (strengthScore.value <= 2) return { text: '弱', type: 'danger' }
  if (strengthScore.value === 3) return { text: '中', type: 'warning' }
  return { text: '强', type: 'success' }
})

// 表单校验规则
const validateConfirm = (rule, value, callback) => {
  if (value !== form.password) callback(new Error('两次输入的密码不一致'))
  else callback()
}
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 30, message: '长度 2-30 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请设置密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' }
  ],
  confirm: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' }
  ]
}

const goLogin = () => router.push('/login')

const onSubmit = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  loading.value = true
  try {
    // 注册
    await api.post('/api/auth/register', { username: form.username, email: form.email, password: form.password, role: form.role })
    // 注册后直接登录
    const data = new URLSearchParams()
    data.append('username', form.username)
    data.append('password', form.password)
    const res = await api.post('/api/auth/login', data, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
    setToken(res.data.access_token)
    const me = await api.get('/api/auth/me')
    setCurrentUser(me.data)
    router.replace('/home')
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '注册失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page { height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(180deg, #f6f8fc 0%, #eef2f8 100%); }
.register-card { width: 460px; padding: 8px 10px; }
.brand { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.brand-text .title { font-size: 18px; font-weight: 700; color: #2b3a4b; }
.brand-text .subtitle { color: #8a97a8; font-size: 12px; }
.register-form { margin-top: 8px; }
.row { display: flex; align-items: center; }
.row.between { justify-content: space-between; }
.submit-btn { width: 100%; }
.clickable { cursor: pointer; }
.strength { color: #606a78; font-size: 12px; display: flex; align-items: center; gap: 6px; }
</style> 