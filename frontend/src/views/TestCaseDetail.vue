<template>
  <div class="case-detail-container">
    <el-page-header @back="router.back()" content="测试用例详情" class="page-header" />

    <div class="grid">
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <div class="title-left">
              <h3 class="title">{{ detail.name || '未命名用例' }}</h3>
              <el-tag :type="statusTagType" size="small">{{ detail.status || '草稿' }}</el-tag>
              <el-tag v-if="detail.type" size="small" class="ml8">{{ detail.type }}</el-tag>
            </div>
            <div class="actions">
              <el-button type="primary" size="small" @click="runCase">
                <el-icon><VideoPlay /></el-icon> 执行
              </el-button>
              <el-button size="small" @click="editCase">
                <el-icon><Edit /></el-icon> 编辑
              </el-button>
              <el-button type="danger" size="small" @click="deleteCase">
                <el-icon><Delete /></el-icon> 删除
              </el-button>
            </div>
          </div>
        </template>

        <div class="info-grid">
          <div class="info-item"><span class="label">用例ID</span><span class="value">{{ detail.id }}</span></div>
          <div class="info-item"><span class="label">创建时间</span><span class="value">{{ detail.createTime || '-' }}</span></div>
          <div class="info-item"><span class="label">维护人</span><span class="value">{{ detail.owner || '未指定' }}</span></div>
          <div class="info-item"><span class="label">优先级</span><span class="value"><el-tag size="small">{{ detail.priority || '中' }}</el-tag></span></div>
          <div class="info-item full"><span class="label">描述</span><span class="value">{{ detail.description || '—' }}</span></div>
        </div>
      </el-card>

      <div class="right-col">
        <el-card class="steps-card">
          <template #header>
            <span class="section-title">步骤与断言</span>
          </template>
          <div class="steps">
            <div class="step" v-for="(s, idx) in steps" :key="idx">
              <div class="step-head">
                <el-tag type="info" size="small">步骤 {{ idx + 1 }}</el-tag>
                <span class="step-title">{{ s.title }}</span>
              </div>
              <div class="step-body">
                <div class="kv"><span class="k">操作</span><span class="v">{{ s.action }}</span></div>
                <div class="kv" v-if="s.input"><span class="k">输入</span><span class="v code">{{ s.input }}</span></div>
                <div class="kv" v-if="s.expect"><span class="k">期望</span><span class="v">{{ s.expect }}</span></div>
              </div>
            </div>
            <div v-if="steps.length === 0" class="empty">暂无步骤</div>
          </div>
        </el-card>

        <el-card class="history-card">
          <template #header>
            <span class="section-title">执行历史</span>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="(h, i) in history"
              :key="i"
              :timestamp="h.time"
              :type="h.result === '通过' ? 'success' : (h.result === '失败' ? 'danger' : 'info')"
            >
              <div class="hist-item">
                <span class="res" :class="{ pass: h.result==='通过', fail: h.result==='失败' }">{{ h.result }}</span>
                <span class="cost">耗时 {{ h.duration }}</span>
              </div>
            </el-timeline-item>
          </el-timeline>
          <div v-if="history.length === 0" class="empty">暂无执行记录</div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { VideoPlay, Edit, Delete } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const detail = ref({})
const steps = ref([])
const history = ref([])

const statusTagType = computed(() => ({ '草稿': 'info', '可执行': 'success', '禁用': 'danger' }[detail.value.status] || 'info'))

const loadDetail = () => {
  const id = Number(route.params.id)
  try {
    const saved = localStorage.getItem('test_cases')
    const arr = saved ? JSON.parse(saved) : []
    const found = Array.isArray(arr) ? arr.find(x => Number(x.id) === id) : null
    if (found) {
      detail.value = found
      // demo data to make the page look alive
      steps.value = [
        { title: '准备数据', action: '构造 SQL 语句', input: 'INSERT INTO users(name) VALUES("张三")', expect: '语法校验通过' },
        { title: '执行语句', action: '执行 SQL', expect: '受影响行数 = 1' },
        { title: '查询验证', action: 'SELECT 校验', expect: '返回包含新记录' }
      ]
      history.value = [
        { time: '2024-01-20 14:12:33', result: '通过', duration: '320ms' },
        { time: '2024-01-18 10:01:05', result: '通过', duration: '301ms' }
      ]
    } else {
      detail.value = { id, name: '未找到用例', status: '草稿' }
      steps.value = []
      history.value = []
      ElMessage.warning('未在本地数据中找到该用例')
    }
  } catch (e) {
    ElMessage.error('加载用例详情失败')
  }
}

const runCase = () => {
  ElMessage.success('开始执行用例...')
}

const editCase = () => {
  ElMessage.info('编辑功能开发中')
}

const deleteCase = async () => {
  try {
    await ElMessageBox.confirm('确认删除此用例？', '提示', { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' })
    const saved = localStorage.getItem('test_cases')
    const arr = saved ? JSON.parse(saved) : []
    const next = Array.isArray(arr) ? arr.filter(x => String(x.id) !== String(detail.value.id)) : []
    localStorage.setItem('test_cases', JSON.stringify(next))
    ElMessage.success('已删除')
    router.replace('/test-cases')
  } catch {}
}

onMounted(loadDetail)
</script>

<style scoped>
.case-detail-container { padding: 20px; }
.page-header { margin-bottom: 12px; }

.grid { display: grid; grid-template-columns: 7fr 5fr; gap: 16px; }

.el-card { border: none; }
:deep(.el-card__header) { padding: 14px 16px; border-bottom: 2px solid #ebeef5; background: #fafafa; }

.card-header { display: flex; justify-content: space-between; align-items: center; }
.title-left { display: flex; align-items: center; gap: 8px; }
.title { margin: 0; font-size: 18px; color: #303133; }
.ml8 { margin-left: 8px; }

.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; padding: 12px 16px; }
.info-item { display: flex; align-items: center; gap: 8px; }
.info-item.full { grid-column: 1 / -1; }
.label { color: #606266; min-width: 72px; font-size: 13px; }
.value { color: #303133; font-size: 13px; }

.right-col { display: grid; gap: 16px; }
.section-title { font-weight: 600; color: #303133; }

.steps { padding: 12px 16px; display: grid; gap: 12px; }
.step { border: 1px dashed #e5e7eb; border-radius: 6px; padding: 10px 12px; background: #fff; }
.step-head { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.step-title { font-weight: 600; color: #303133; }
.step-body .kv { display: grid; grid-template-columns: 72px 1fr; gap: 8px; margin: 4px 0; font-size: 13px; }
.k { color: #606266; }
.v { color: #303133; }
.v.code { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }

.hist-item { display: flex; gap: 10px; align-items: center; }
.res { font-weight: 600; }
.res.pass { color: #52c41a; }
.res.fail { color: #f56c6c; }
.cost { color: #606266; font-size: 12px; }

.empty { color: #909399; font-size: 13px; text-align: center; padding: 16px 0; }

@media (max-width: 1200px) {
  .grid { grid-template-columns: 1fr; }
}
</style> 