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
      </div>

      <el-table :data="filteredProjects" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="项目ID" width="80" />
        <el-table-column prop="name" label="项目名称" min-width="200" />
        <el-table-column prop="description" label="项目描述" min-width="300" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="120">
          <template #default="scope">
            <el-progress :percentage="scope.row.progress" :status="getProgressStatus(scope.row.progress)" />
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="viewProject(scope.row)">查看</el-button>
            <el-button size="small" type="primary" @click="editProject(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteProject(scope.row)">删除</el-button>
          </template>
        </el-table-column>
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
import { ref, computed, onMounted } from 'vue'
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

// 模拟项目数据
const projects = ref([
  {
    id: 1,
    name: '智能测试平台',
    description: '基于AI的自动化测试平台，支持多种测试类型和报告生成',
    status: '进行中',
    progress: 75,
    createTime: '2024-01-15 10:30:00'
  },
  {
    id: 2,
    name: '数据管理系统',
    description: '企业级数据管理解决方案，包含数据采集、存储、分析功能',
    status: '已完成',
    progress: 100,
    createTime: '2024-01-10 14:20:00'
  },
  {
    id: 3,
    name: '移动端应用',
    description: '跨平台移动应用开发项目，支持iOS和Android',
    status: '待开始',
    progress: 0,
    createTime: '2024-01-20 09:15:00'
  }
])

const filteredProjects = computed(() => {
  let filtered = projects.value

  if (searchQuery.value) {
    filtered = filtered.filter(project => 
      project.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      project.description.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(project => project.status === statusFilter.value)
  }

  return filtered
})

const getStatusType = (status) => {
  const types = {
    '进行中': 'warning',
    '已完成': 'success',
    '待开始': 'info'
  }
  return types[status] || 'info'
}

const getProgressStatus = (progress) => {
  if (progress === 100) return 'success'
  if (progress >= 80) return 'warning'
  return ''
}

const viewProject = (project) => {
  router.push(`/project-detail/${project.id}`)
}

const editProject = (project) => {
  router.push(`/project-edit/${project.id}`)
}

const deleteProject = async (project) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除项目"${project.name}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 这里应该调用删除API
    const index = projects.value.findIndex(p => p.id === project.id)
    if (index > -1) {
      projects.value.splice(index, 1)
      ElMessage.success('删除成功')
    }
  } catch {
    // 用户取消删除
  }
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

onMounted(() => {
  total.value = projects.value.length
})
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
  gap: 16px;
  margin-bottom: 20px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
  