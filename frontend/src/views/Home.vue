<template>
  <div class="home">
    <el-card class="welcome-card">
      <template #header>
        <div class="card-header">
          <h2>欢迎使用 Vue + Python Demo</h2>
        </div>
      </template>
      <div class="card-content">
        <p>这是一个使用Vue 3和Python FastAPI构建的全栈项目示例。</p>
        <el-button type="primary" @click="testBackend">测试后端连接</el-button>
        <p v-if="message" class="message">{{ message }}</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const message = ref('')

const testBackend = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/hello')
    message.value = response.data.message
  } catch (error) {
    message.value = '连接后端失败：' + error.message
  }
}
</script>

<style scoped>
.home {
  max-width: 800px;
  margin: 0 auto;
}

.welcome-card {
  margin-top: 20px;
}

.card-header {
  text-align: center;
}

.card-content {
  text-align: center;
}

.message {
  margin-top: 20px;
  color: #409EFF;
}
</style> 