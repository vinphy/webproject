<template>
  <div class="logs-container">
    <div class="page-header">
      <h2>日志管理</h2>
    </div>

    <el-card class="logs-card">
      <div class="search-bar">
        <el-input
          v-model="keyword"
          placeholder="搜索关键字（内容、来源、用户）"
          style="width: 300px"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select v-model="typeFilter" placeholder="日志类型" style="width: 160px" clearable>
          <el-option label="全部类型" value="" />
          <el-option label="操作日志" value="操作日志" />
          <el-option label="运行日志" value="运行日志" />
          <el-option label="异常日志" value="异常日志" />
          <el-option label="正常日志" value="正常日志" />
        </el-select>

        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
        />

        <div class="spacer"></div>

        <el-button @click="resetFilters">重置</el-button>
      </div>

      <el-table
        :data="pagedLogs"
        style="width: 100%"
        v-loading="loading"
        row-key="id"
        class="logs-table"
        @row-dblclick="onRowDblClick"
      >
        <el-table-column prop="id" label="ID" width="120" class-name="col-id" align="left" header-align="left" />
        <el-table-column prop="type" label="类型" width="120" align="left" header-align="left">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.type)" size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="时间" width="180" align="left" header-align="left" />
        <el-table-column prop="source" label="来源" width="160" align="left" header-align="left" show-overflow-tooltip />
        <el-table-column prop="user" label="用户" width="140" align="left" header-align="left" />
        <el-table-column prop="message" label="内容" min-width="360" align="left" header-align="left" show-overflow-tooltip />
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="filteredTotal"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)
const keyword = ref('')
const typeFilter = ref('')
const dateRange = ref([])
const currentPage = ref(1)
const pageSize = ref(10)

// 简单本地数据源，后续可替换为接口
const logs = ref([])

const loadLogs = () => {
  try {
    loading.value = true
    const saved = localStorage.getItem('logs')
    if (saved && saved !== 'null' && saved !== 'undefined') {
      const parsed = JSON.parse(saved)
      logs.value = Array.isArray(parsed) ? parsed : []
    } else {
      // 初始化示例日志
      const now = new Date()
      const fmt = (d) => `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}:${String(d.getSeconds()).padStart(2,'0')}`
      const demo = [
        { id: 1, type: '操作日志', createdAt: fmt(new Date(now.getTime()-3600_000)), source: '项目管理', user: 'admin', message: '创建项目：智能测试平台' },
        { id: 2, type: '运行日志', createdAt: fmt(new Date(now.getTime()-1800_000)), source: '任务调度', user: 'system', message: '开始执行漏洞扫描任务#42' },
        { id: 3, type: '异常日志', createdAt: fmt(new Date(now.getTime()-1200_000)), source: '接口服务', user: 'system', message: '请求超时：/api/run/start 504' },
        { id: 4, type: '正常日志', createdAt: fmt(new Date(now.getTime()-600_000)), source: '监控服务', user: 'system', message: 'CPU使用率 35%，内存 62%' },
        { id: 5, type: '操作日志', createdAt: fmt(new Date(now.getTime()-300_000)), source: '用例管理', user: 'tester', message: '更新测试用例：登录功能-正向' }
      ]
      logs.value = demo
      localStorage.setItem('logs', JSON.stringify(logs.value))
    }
  } catch (e) {
    ElMessage.error('加载日志失败')
  } finally {
    loading.value = false
  }
}

const inDateRange = (createdAt) => {
  if (!dateRange.value || dateRange.value.length !== 2) return true
  const [start, end] = dateRange.value
  const t = new Date(createdAt.replace(/-/g,'/')).getTime()
  const s = new Date(`${start} 00:00:00`.replace(/-/g,'/')).getTime()
  const e = new Date(`${end} 23:59:59`.replace(/-/g,'/')).getTime()
  return t >= s && t <= e
}

const filteredLogs = computed(() => {
  let data = logs.value
  if (keyword.value) {
    const q = keyword.value.toLowerCase()
    data = data.filter(l =>
      (l.message || '').toLowerCase().includes(q) ||
      (l.source || '').toLowerCase().includes(q) ||
      (l.user || '').toLowerCase().includes(q)
    )
  }
  if (typeFilter.value) {
    data = data.filter(l => l.type === typeFilter.value)
  }
  data = data.filter(l => inDateRange(l.createdAt))
  // 按时间倒序
  return [...data].sort((a,b) => new Date(b.createdAt) - new Date(a.createdAt))
})

const filteredTotal = computed(() => filteredLogs.value.length)

const pagedLogs = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredLogs.value.slice(start, start + pageSize.value)
})

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}
const handleCurrentChange = (val) => { currentPage.value = val }

const getTypeTag = (type) => {
  const map = { '操作日志': 'primary', '运行日志': 'success', '异常日志': 'danger', '正常日志': 'info' }
  return map[type] || 'info'
}

const resetFilters = () => {
  keyword.value = ''
  typeFilter.value = ''
  dateRange.value = []
  currentPage.value = 1
}

const onRowDblClick = (row) => {
  router.push(`/logs/${row.id}`)
}

onMounted(() => loadLogs())
onActivated(() => loadLogs())
</script>

<style scoped>
.logs-container { padding: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h2 { margin: 0; color: #303133; }
.logs-card { margin-bottom: 20px; }
.search-bar { display: flex; align-items: center; gap: 16px; margin-bottom: 20px; }
.search-bar .spacer { flex: 1 1 auto; }
.pagination { display: flex; justify-content: center; margin-top: 20px; }

/* 与系统其他表格保持一致的左对齐与内边距 */
.logs-table :deep(.el-table__header .el-table__cell),
.logs-table :deep(.el-table__body .el-table__cell) { padding: 8px 12px; text-align: left; }
.logs-table :deep(.el-table__header .cell),
.logs-table :deep(.el-table__body .cell) { display: block; text-align: left; padding: 0; }
.logs-table :deep(.el-table__header .cell) { font-size: 14px; font-weight: 600; }
.logs-table :deep(.el-table__body .cell) { font-size: 12px; line-height: 20px; }
.logs-table :deep(.col-id .cell) { white-space: nowrap; font-variant-numeric: tabular-nums; }
</style> 