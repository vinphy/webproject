<template>
  <!-- 注册页采用与登录页一致的居中浅灰背景与卡片风格，保留注册表单与密码强度提示 -->
  <AuthCard title="创建账户" subtitle="填写信息完成注册并自动登录">

      <!-- 表单：用户名/邮箱/密码/确认密码/角色（可选） -->
      <el-form ref="formRef" :model="form" :rules="rules" label-width="0" class="login-form" @keyup.enter.native="onSubmit">
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
        <!-- <el-form-item>
          <el-input v-model="form.role" placeholder="注册码" style="width: 100%" clearable class="role-select">
            <template #prefix><el-icon><View /></el-icon></template>
          </el-input>
        </el-form-item> -->

        <el-form-item prop="role">
          <!-- 只读输入用于显示已选文件名，点击弹出文件选择框 -->
          <el-input v-model="form.role" placeholder="注册码（点击选择文件）" readonly class="role-select" @click="onChooseFile">
            <template #prefix><el-icon><View /></el-icon></template>
            <template #suffix>
              <el-icon v-if="selectedFile" class="clickable" @click.stop="clearSelectedFile">×</el-icon>
            </template>
          </el-input>
          <!-- 隐藏的文件输入框 -->
          <input ref="fileInput" type="file" style="display:none" @change="onFileChange" />
        </el-form-item>

        <div class="row between">
          <div class="strength">
            <span style="color: #8a97a8;">密码强度：</span>
            <el-tag :type="strengthTag.type" size="small">{{ strengthTag.text }}</el-tag>
          </div>
          <el-link type="primary" :underline="false" @click="goLogin">已有账号？去登录</el-link>
        </div>

        <el-form-item>
          <el-button type="primary" class="submit-btn" :loading="loading" @click="onSubmit">注册并登录</el-button>
        </el-form-item>
      </el-form>

      <template #tips>
        <!-- 这里可以放置额外提示或链接 -->
      </template>
    </AuthCard>
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
import AuthCard from '../components/AuthCard.vue'

const router = useRouter()
const formRef = ref()
const form = reactive({ username: '', email: '', password: '', confirm: '', role: '' })
const loading = ref(false)
const showPwd = ref(false)
const fileInput = ref(null)
const selectedFile = ref(null)

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
    // 注册：如果选择了文件则使用 FormData 上传，否则使用 JSON
    if (selectedFile.value) {
      const fd = new FormData()
      fd.append('username', form.username)
      fd.append('email', form.email)
      fd.append('password', form.password)
      fd.append('role_file', selectedFile.value)
      await api.post('/api/auth/register', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    } else {
      await api.post('/api/auth/register', { username: form.username, email: form.email, password: form.password, role: form.role })
    }
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

// 文件选择相关
const onChooseFile = () => {
  if (fileInput.value) fileInput.value.click()
}

const onFileChange = (e) => {
  const f = e.target.files && e.target.files[0]
  if (f) {
    selectedFile.value = f
    // 仅显示文件名（浏览器不允许获取本地完整路径）
    form.role = f.name
  }
}

const clearSelectedFile = () => {
  selectedFile.value = null
  form.role = ''
  if (fileInput.value) fileInput.value.value = ''
}
</script>

<style scoped>
.row { display: flex; align-items: center;
  }
.row.between { justify-content: space-between; }
.submit-btn { width: 100%; }
.clickable { cursor: pointer; }
.tips { margin-top: 6px; }
.submit-btn { 
  width: 100%;
  margin: 15px 0 0 0;
  }
</style> 