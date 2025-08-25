<template>
  <div style="display:flex;justify-content:center;align-items:center;height:100vh;background:#f5f7fa">
    <el-card style="width:360px">
      <h3 style="margin-bottom:12px">登录</h3>
      <el-form :model="form" @keyup.enter.native="onSubmit">
        <el-form-item label="用户名">
          <el-input v-model="form.username" autocomplete="username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" autocomplete="current-password" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="onSubmit">登录</el-button>
          <el-button link @click="$router.push('/register')">去注册</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api, setToken, setCurrentUser } from '../utils/auth'

const router = useRouter()
const form = reactive({ username: '', password: '' })
const loading = ref(false)

const onSubmit = async () => {
  if (!form.username || !form.password) return
  loading.value = true
  try {
    const data = new URLSearchParams()
    data.append('username', form.username)
    data.append('password', form.password)
    const res = await api.post('/api/auth/login', data, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
    setToken(res.data.access_token)
    const me = await api.get('/api/auth/me')
    setCurrentUser(me.data)
    router.replace('/dashboard')
  } catch (e) {
    console.error(e)
    ElMessage.error(e?.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script> 