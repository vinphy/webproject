<template>
  <div class="project-detail-container">
    <div class="page-header">
      <h2>项目详情</h2>
      <div class="header-actions">
        <el-button type="primary" @click="editProject">编辑项目</el-button>
        <el-button @click="router.go(-1)">返回</el-button>
      </div>
    </div>

    <div class="detail-content" v-loading="loading">
      <!-- 基本信息卡片 -->
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
            <el-tag :type="getStatusType(project.status)">{{ project.status }}</el-tag>
          </div>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="info-item">
              <label>项目名称：</label>
              <span>{{ project.name }}</span>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="info-item">
              <label>项目类型：</label>
              <span>{{ project.type }}</span>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="info-item">
              <label>优先级：</label>
              <el-tag :type="getPriorityType(project.priority)">{{ project.priority }}</el-tag>
            </div>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="info-item">
              <label>项目负责人：</label>
              <span>{{ project.manager }}</span>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="info-item">
              <label>创建时间：</label>
              <span>{{ project.createTime }}</span>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="info-item">
              <label>预计完成：</label>
              <span>{{ project.expectedEndTime || '未设置' }}</span>
            </div>
          </el-col>
        </el-row>
        
        <div class="info-item full-width">
          <label>项目描述：</label>
          <p class="description">{{ project.description }}</p>
        </div>
        
        <div class="info-item full-width" v-if="project.tags && project.tags.length">
          <label>项目标签：</label>
          <div class="tags-container">
            <el-tag v-for="tag in project.tags" :key="tag" size="small" style="margin-right: 8px;">
              {{ tag }}
            </el-tag>
          </div>
        </div>
      </el-card>

      <!-- 进度信息卡片 -->
      <el-card class="progress-card">
        <template #header>
          <span>进度信息</span>
        </template>
        
        <div class="progress-info">
          <div class="progress-item">
            <div class="progress-label">整体进度</div>
            <el-progress 
              :percentage="project.progress" 
              :status="getProgressStatus(project.progress)"
              :stroke-width="20"
            />
          </div>
          
          <el-row :gutter="20" class="progress-stats">
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-number">{{ project.totalTasks || 0 }}</div>
                <div class="stat-label">总任务数</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-number completed">{{ project.completedTasks || 0 }}</div>
                <div class="stat-label">已完成</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-number in-progress">{{ project.inProgressTasks || 0 }}</div>
                <div class="stat-label">进行中</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-number pending">{{ project.pendingTasks || 0 }}</div>
                <div class="stat-label">待开始</div>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-card>

      <!-- 任务列表卡片 -->
      <el-card class="tasks-card">
        <template #header>
          <div class="card-header">
            <span>任务列表</span>
            <el-button size="small" type="primary" @click="addTask">添加任务</el-button>
          </div>
        </template>
        
        <el-table :data="tasks" style="width: 100%">
          <el-table-column prop="name" label="任务名称" min-width="200" />
          <el-table-column prop="assignee" label="负责人" width="120" align="center" />
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="scope">
              <el-tag :type="getTaskStatusType(scope.row.status)">
                {{ scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="progress" label="进度" width="140" align="center">
            <template #default="scope">
              <el-progress :percentage="scope.row.progress" :stroke-width="8" />
            </template>
          </el-table-column>
          <el-table-column prop="startTime" label="开始时间" width="180" align="center" />
          <el-table-column prop="endTime" label="结束时间" width="180" align="center" />
          <el-table-column label="操作" width="150" fixed="right" align="center">
            <template #default="scope">
              <el-button size="small" @click="viewTask(scope.row)">查看</el-button>
              <el-button size="small" type="primary" @click="editTask(scope.row)">编辑</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 备注信息卡片 -->
      <el-card class="remarks-card" v-if="project.remarks">
        <template #header>
          <span>备注信息</span>
        </template>
        <p class="remarks-content">{{ project.remarks }}</p>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const loading = ref(false)

// 模拟项目数据
const project = ref({
  id: 1,
  name: '智能测试平台',
  description: '基于AI的自动化测试平台，支持多种测试类型和报告生成。该平台集成了机器学习算法，能够自动识别测试用例的优先级，优化测试执行顺序，提高测试效率。',
  status: '进行中',
  type: '自动化测试',
  priority: '高',
  manager: '张三',
  createTime: '2024-01-15 10:30:00',
  expectedEndTime: '2024-03-15 18:00:00',
  progress: 75,
  tags: ['Web应用', 'AI', '自动化'],
  remarks: '这是一个重要的测试平台项目，需要重点关注性能和稳定性。',
  totalTasks: 12,
  completedTasks: 9,
  inProgressTasks: 2,
  pendingTasks: 1
})

// 模拟任务数据
const tasks = ref([
  {
    id: 1,
    name: '需求分析',
    assignee: '张三',
    status: '已完成',
    progress: 100,
    startTime: '2024-01-15 10:30:00',
    endTime: '2024-01-20 18:00:00'
  },
  {
    id: 2,
    name: '系统设计',
    assignee: '李四',
    status: '已完成',
    progress: 100,
    startTime: '2024-01-21 09:00:00',
    endTime: '2024-01-25 18:00:00'
  },
  {
    id: 3,
    name: '核心功能开发',
    assignee: '王五',
    status: '进行中',
    progress: 80,
    startTime: '2024-01-26 09:00:00',
    endTime: '2024-02-15 18:00:00'
  },
  {
    id: 4,
    name: '测试用例编写',
    assignee: '赵六',
    status: '进行中',
    progress: 60,
    startTime: '2024-02-01 09:00:00',
    endTime: '2024-02-20 18:00:00'
  },
  {
    id: 5,
    name: '系统测试',
    assignee: '钱七',
    status: '待开始',
    progress: 0,
    startTime: '2024-02-16 09:00:00',
    endTime: '2024-03-01 18:00:00'
  }
])

const getStatusType = (status) => {
  const types = {
    '进行中': 'warning',
    '已完成': 'success',
    '待开始': 'info'
  }
  return types[status] || 'info'
}

const getPriorityType = (priority) => {
  const types = {
    '低': 'info',
    '中': 'warning',
    '高': 'danger',
    '紧急': 'danger'
  }
  return types[priority] || 'info'
}

const getProgressStatus = (progress) => {
  if (progress === 100) return 'success'
  if (progress >= 80) return 'warning'
  return ''
}

const getTaskStatusType = (status) => {
  const types = {
    '已完成': 'success',
    '进行中': 'warning',
    '待开始': 'info'
  }
  return types[status] || 'info'
}

const editProject = () => {
  router.push(`/project-edit/${project.value.id}`)
}

const addTask = () => {
  ElMessage.info('添加任务功能待实现')
}

const viewTask = (task) => {
  ElMessage.info(`查看任务：${task.name}`)
}

const editTask = (task) => {
  ElMessage.info(`编辑任务：${task.name}`)
}

onMounted(() => {
  const projectId = route.params.id
  loading.value = true
  
  // 模拟加载数据
  setTimeout(() => {
    loading.value = false
  }, 500)
})
</script>

<style scoped>
.project-detail-container {
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
  font-size: 22px;
  font-weight: 700;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 卡片标题更突出 */
:deep(.el-card__header) {
  padding: 14px 16px;
  font-weight: 600;
  font-size: 15px;
  border-bottom: 1px solid #ebeef5;
}

.info-card, .progress-card, .tasks-card, .remarks-card {
  margin-bottom: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 信息行排版优化：右对齐标签，留固定宽度 */
.info-item {
  margin-bottom: 14px;
  display: flex;
  align-items: flex-start;
}

.info-item.full-width {
  flex-direction: column;
}

.info-item label {
  font-weight: 600;
  color: #606266;
  width: 100px;
  text-align: right;
  margin-right: 8px;
}

.info-item span {
  color: #303133;
}

.description {
  margin: 8px 0 0 0;
  color: #606266;
  line-height: 1.6;
}

.tags-container {
  margin-top: 8px;
}

.progress-info {
  padding: 20px 0;
}

.progress-item {
  margin-bottom: 24px;
}

.progress-label {
  font-weight: 600;
  margin-bottom: 10px;
  color: #303133;
}

.progress-stats {
  margin-top: 10px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-number {
  font-size: 22px;
  font-weight: 700;
  color: #409EFF;
  margin-bottom: 6px;
}

.stat-number.completed { color: #67C23A; }
.stat-number.in-progress { color: #E6A23C; }
.stat-number.pending { color: #909399; }

.stat-label {
  color: #606266;
  font-size: 13px;
}

/* 表格与标签的视觉优化 */
:deep(.el-table th), :deep(.el-table td) {
  font-size: 13px;
}

:deep(.el-tag) {
  padding: 2px 8px;
}

.remarks-content {
  color: #606266;
  line-height: 1.6;
  margin: 0;
}
</style>
    