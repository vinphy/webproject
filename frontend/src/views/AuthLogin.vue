<template>
  <!--
    登录页整体采用居中布局与浅灰背景；
    卡片内包含品牌区、表单区与辅助链接。
  -->
  <AuthCard title="欢迎登录" subtitle="请输入账户信息以进入系统">

      <!-- 登录表单：包含规则校验、回车提交、加载状态与错误提示 -->
      <el-form ref="formRef" :model="form" :rules="rules" label-width="0" class="login-form" @keyup.enter.native="onSubmit">
        <el-form-item prop="username">
          <el-input v-model.trim="form.username" placeholder="用户名 / 邮箱" clearable autocomplete="username">
            <template #prefix><el-icon><User /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" :type="showPwd ? 'text' : 'password'" placeholder="密码" autocomplete="current-password">
            <template #prefix><el-icon><Lock /></el-icon></template>
            <template #suffix>
              <el-icon class="clickable" @click="showPwd = !showPwd"><View v-if="!showPwd" /><Hide v-else /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <div class="row between">
          <el-checkbox v-model="remember">记住我</el-checkbox>
          <el-link type="primary" :underline="false" @click="goRegister">没有账号？去注册</el-link>
        </div>
        <el-form-item>
          <el-button type="primary" class="submit-btn" :loading="loading" @click="onSubmit">登 录</el-button>
        </el-form-item>
      </el-form>

      <template #tips>
        <el-alert v-if="hint" :title="hint" type="info" show-icon :closable="false" />
      </template>
    </AuthCard>
</template>

<script setup>
// 说明：
// - 提升用户体验：加入输入校验、回车提交、加载态与错误反馈
// - 细节处理：显示/隐藏密码、记住我（可扩展为本地记忆用户名）
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, View, Hide } from '@element-plus/icons-vue'
import { api, setToken, setCurrentUser } from '../utils/auth'
import AuthCard from '../components/AuthCard.vue'

const router = useRouter()
const formRef = ref()
const form = reactive({ username: '', password: '' })
const loading = ref(false)
const showPwd = ref(false)
const remember = ref(true)
const hint = ref('')

// 表单校验规则：基础必填 + 长度约束
const rules = {
  username: [
    { required: true, message: '请输入用户名/邮箱', trigger: 'blur' },
    { min: 2, max: 50, message: '长度 2-50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' }
  ]
}

onMounted(() => {
  // 记住我：可扩展为记忆用户名
  const lastUser = localStorage.getItem('last_username')
  if (lastUser) form.username = lastUser
  hint.value = '管理员账号：admin / 123456'
})

const goRegister = () => router.push('/register')

const onSubmit = async () => {
  if (!formRef.value) return
  try {
    // 先进行前端校验
    await formRef.value.validate()
  } catch {
    return
  }
  loading.value = true
  try {
    // OAuth2 密码模式（表单-urlencoded）
    const data = new URLSearchParams()
    data.append('username', form.username)
    data.append('password', form.password)
    const res = await api.post('/api/auth/login', data, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
    setToken(res.data.access_token)
    // 拉取用户信息并缓存
    const me = await api.get('/api/auth/me')
    setCurrentUser(me.data)
    // 记住我：保存最近用户名
    if (remember.value) localStorage.setItem('last_username', form.username)
    // 跳转首页
    router.replace('/home')
  } catch (e) {
    // 统一错误反馈
    const msg = e?.response?.data?.detail || '登录失败，请检查账号或稍后重试'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.row { display: flex; align-items: center;
  }
.row.between { justify-content: space-between; }
.submit-btn { width: 100%; }
.clickable { cursor: pointer; }
.tips { margin-top: 6px; }
</style> 