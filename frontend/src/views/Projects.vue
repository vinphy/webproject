<template>
  <div class="projects-container">
    <div class="page-header">
      <h2>项目列表</h2>
      <el-button type="primary" @click="router.push('/project-add')">
        <el-icon><Plus /></el-icon>
        新增项目
      </el-button>
        </div>
        
    <el-card class="projects-card">
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索项目名称或描述"
          style="width: 300px"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select v-model="statusFilter" placeholder="状态筛选" style="width: 150px">
          <el-option label="全部" value="" />
          <el-option label="进行中" value="进行中" />
          <el-option label="已完成" value="已完成" />
          <el-option label="待开始" value="待开始" />
        </el-select>

        <div class="spacer"></div>

        <el-button type="success" :disabled="selectedRows.length === 0" @click="executeSelected">
          执行所选（{{ selectedRows.length }}）
            </el-button>
        </div>
  
        <el-table
        :data="filteredProjects"
          style="width: 100%"
        v-loading="loading"
        row-key="id"
        class="projects-table"
        @selection-change="onSelectionChange"
        @row-dblclick="onRowDblClick"
      >
        <!-- 多选 -->
        <el-table-column type="selection" width="46" align="left" header-align="left" />

        <!-- 执行项（从新建时的配置里读取） -->
        <el-table-column label="执行项" min-width="80" align="left" header-align="left">
          <template #default="{ row }">
            <template v-if="getExecFlags(row).vuln"><el-tag type="success" size="small">漏洞扫描</el-tag></template>
            <template v-if="getExecFlags(row).fuzz"><el-tag type="warning" size="small">模糊测试</el-tag></template>
            <template v-if="getExecFlags(row).cases"><el-tag type="primary" size="small">测试用例</el-tag></template>
            <template v-if="!getExecFlags(row).any"><el-tag size="small">未选择</el-tag></template>
          </template>
        </el-table-column>

        <!-- ID、名称、描述 -->
        <el-table-column prop="id" label="项目ID" width="120" class-name="col-id" align="left" header-align="left" />
        <el-table-column prop="name" label="项目名称" min-width="150" align="left" header-align="left" />

        
        <!-- 状态、进度、创建时间 -->
        <el-table-column prop="status" label="状态" width="100" align="left" header-align="left">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="140" align="left" header-align="left">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" :status="getProgressStatus(row.progress)" />
            </template>
          </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="160" align="left" header-align="left" />

        <el-table-column prop="description" label="项目描述" min-width="360" show-overflow-tooltip align="left" header-align="left" />

        <!-- 去掉操作列 -->
        </el-table>
  
      <div class="pagination">
          <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
  
const router = useRouter()
const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedRows = ref([])

const projects = ref([])

const loadProjects = () => {
  try {
    const saved = localStorage.getItem('projects')
    if (saved && saved !== 'null' && saved !== 'undefined') {
      const parsed = JSON.parse(saved)
      projects.value = Array.isArray(parsed) ? parsed : []
    } else {
      // 初始化默认数据（仅首次）
      projects.value = [
        { id: 1, name: '智能测试平台', description: '基于AI的自动化测试平台，支持多种测试类型和报告生成', status: '进行中', progress: 75, createTime: '2024-01-15 10:30:00' },
        { id: 2, name: '数据管理系统', description: '企业级数据管理解决方案，包含数据采集、存储、分析功能', status: '已完成', progress: 100, createTime: '2024-01-10 14:20:00' },
        { id: 3, name: '移动端应用', description: '跨平台移动应用开发项目，支持iOS和Android', status: '待开始', progress: 0, createTime: '2024-01-20 09:15:00' }
      ]
      localStorage.setItem('projects', JSON.stringify(projects.value))
    }
    total.value = projects.value.length
  } catch (e) {
    ElMessage.error('加载项目数据失败')
  }
}

const saveProjects = () => {
  try {
    localStorage.setItem('projects', JSON.stringify(projects.value))
  } catch {}
    }
    
const filteredProjects = computed(() => {
  let filtered = projects.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    filtered = filtered.filter(p =>
      (p.name || '').toLowerCase().includes(q) ||
      (p.description || '').toLowerCase().includes(q)
    )
  }
  if (statusFilter.value) {
    filtered = filtered.filter(p => p.status === statusFilter.value)
  }
  return filtered
})

const onSelectionChange = (rows) => {
  selectedRows.value = rows
  }
  
const executeSelected = () => {
  const ids = selectedRows.value.map(r => r.id).join(', ')
  if (!ids) return
  ElMessage.success(`已触发执行：${ids}`)
  }
  
const getStatusType = (status) => {
  const types = { '进行中': 'warning', '已完成': 'success', '待开始': 'info' }
  return types[status] || 'info'
      }

const getProgressStatus = (progress) => {
  if (progress === 100) return 'success'
  if (progress >= 80) return 'warning'
  return ''
}

// 从项目的 config.step2Selections 提取执行项标记
const getExecFlags = (row) => {
  const s = row?.config?.step2Selections || {}
  const vuln = !!s.vuln
  const fuzz = !!s.fuzz
  const cases = !!s.cases
  return { vuln, fuzz, cases, any: vuln || fuzz || cases }
  }
  
  const handleSizeChange = (val) => {
    pageSize.value = val
  currentPage.value = 1
  }
const handleCurrentChange = (val) => { currentPage.value = val }
  
const onRowDblClick = (row) => {
  router.push(`/project-detail/${row.id}`)
  }
  
onMounted(() => { loadProjects() })
onActivated(() => { loadProjects() })
  </script>
  
  <style scoped>
.projects-container {
  padding: 20px;
  }
  
.page-header {
    display: flex;
  justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
  }
  
.projects-card {
    margin-bottom: 20px;
  }
  
.search-bar {
    display: flex;
    align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  }
.search-bar .spacer {
  flex: 1 1 auto;
  }
  
.pagination {
    display: flex;
  justify-content: center;
  margin-top: 20px;
}

/* 统一表头/表体的布局与内边距，确保左对齐基线一致 */
.projects-table :deep(.el-table__header .el-table__cell),
.projects-table :deep(.el-table__body .el-table__cell) {
  padding: 8px 12px;          /* 一致的左右内边距 */
  text-align: left;           /* 强制左对齐 */
  }
  
/* 禁止 cell 内部被无意设置为 flex 导致的两端对齐等问题 */
.projects-table :deep(.el-table__header .cell),
.projects-table :deep(.el-table__body .cell) {
  display: block;             /* 避免继承到 flex 布局 */
  text-align: left;           /* 再次确保文本左对齐 */
  padding: 0;                 /* 让 padding 由外层 el-table__cell 统一管理 */
}

/* 表头稍大更醒目（左对齐由列属性控制） */
.projects-table :deep(.el-table__header .cell) {
  font-size: 14px;
  font-weight: 600;
  }
  
/* 表体略小于表头，统一左对齐由列属性保证 */
.projects-table :deep(.el-table__body .cell) {
    font-size: 12px;
  line-height: 20px;
  }
  
/* ID 列固定不换行，等宽数字方便比对 */
.projects-table :deep(.col-id .cell) {
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
  }
  </style>
  