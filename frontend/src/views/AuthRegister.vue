<template>
  <div style="display:flex;justify-content:center;align-items:center;height:100vh;background:#f5f7fa">
    <el-card style="width:420px">
      <h3 style="margin-bottom:12px">注册</h3>
      <el-form :model="form" label-width="80px" @keyup.enter.native="onSubmit">
        <el-form-item label="用户名">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role" placeholder="可选">
            <el-option label="admin" value="admin" />
            <el-option label="user" value="user" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="onSubmit">注册并登录</el-button>
          <el-button link @click="$router.push('/login')">去登录</el-button>
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
const form = reactive({ username: '', email: '', password: '', role: '' })
const loading = ref(false)

const onSubmit = async () => {
  if (!form.username || !form.email || !form.password) return
  loading.value = true
  try {
    await api.post('/api/auth/register', form)
    // 注册后直接登录
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
    ElMessage.error(e?.response?.data?.detail || '注册失败')
  } finally {
    loading.value = false
  }
}
</script> 