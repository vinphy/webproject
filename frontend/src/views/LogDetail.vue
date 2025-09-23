<template>
  <div class="log-detail-container">
    <el-page-header @back="goBack" content="日志详情" />

    <el-card class="detail-card" v-if="logItem">
      <template #header>
        <div class="card-header">
          <span>日志 #{{ logItem.id }}</span>
          <el-tag :type="typeTag">{{ logItem.type }}</el-tag>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="时间">{{ logItem.createdAt }}</el-descriptions-item>
        <el-descriptions-item label="类型">{{ logItem.type }}</el-descriptions-item>
        <el-descriptions-item label="来源">{{ logItem.source }}</el-descriptions-item>
        <el-descriptions-item label="用户">{{ logItem.user }}</el-descriptions-item>
      </el-descriptions>

      <div class="section">
        <h4>内容</h4>
        <el-input v-model="message" type="textarea" :rows="6" readonly />
      </div>
    </el-card>

    <el-empty v-else description="未找到该日志" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const logItem = ref(null)
const message = ref('')

const loadLog = () => {
  const id = Number(route.params.id)
  const saved = localStorage.getItem('logs')
  if (!saved) return
  try {
    const list = JSON.parse(saved)
    const found = (Array.isArray(list) ? list : []).find(it => Number(it.id) === id)
    if (found) {
      logItem.value = found
      message.value = found.message || ''
    }
  } catch {}
}

const typeTag = computed(() => {
  const t = logItem.value?.type
  const map = { '操作日志': 'primary', '运行日志': 'success', '异常日志': 'danger', '正常日志': 'info' }
  return map[t] || 'info'
})

const goBack = () => router.back()

onMounted(loadLog)
</script>

<style scoped>
.log-detail-container { padding: 20px; }
.detail-card { margin-top: 12px; }
.card-header { display: flex; align-items: center; justify-content: space-between; }
.section { margin-top: 16px; }
.section h4 { margin: 0 0 8px; color: #303133; }
</style> 