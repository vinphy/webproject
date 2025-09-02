<template>
  <div class="project-detail-container">
    <!-- 上半部分：左7右3布局 -->
    <div class="upper-section">
      <!-- 左上部分：上8下2布局 -->
      <div class="left-section">
        <!-- 左上上部分：项目基本信息 (占80%) -->
        <div class="left-upper">
          <el-card class="info-card">
            <template #header>
              <div class="card-header">
                <span class="section-title">项目基本信息</span>
                <el-tag :type="getStatusType(project.status)" size="large">{{ project.status }}</el-tag>
              </div>
            </template>
            
            <div class="info-grid">
              <div class="info-row">
                <div class="info-item">
                  <label>项目名称</label>
                  <span class="info-value">{{ project.name }}</span>
                </div>
                <div class="info-item">
                  <label>项目类型</label>
                  <span class="info-value">{{ project.type }}</span>
                </div>
                <div class="info-item">
                  <label>优先级</label>
                  <el-tag :type="getPriorityType(project.priority)" size="small">{{ project.priority }}</el-tag>
                </div>
              </div>
              
              <div class="info-row">
                <div class="info-item">
                  <label>项目负责人</label>
                  <span class="info-value">{{ project.manager }}</span>
                </div>
                <div class="info-item">
                  <label>创建时间</label>
                  <span class="info-value">{{ project.createTime }}</span>
                </div>
                <div class="info-item">
                  <label>预计完成</label>
                  <span class="info-value">{{ project.expectedEndTime || '未设置' }}</span>
                </div>
              </div>
              
              <div class="info-row full-width">
                <div class="info-item">
                  <label>项目描述</label>
                  <p class="description">{{ project.description }}</p>
                </div>
              </div>
              
              <div class="info-row full-width" v-if="project.tags && project.tags.length">
                <div class="info-item">
                  <label>项目标签</label>
                  <div class="tags-container">
                    <el-tag v-for="tag in project.tags" :key="tag" size="small" style="margin-right: 8px;">
                      {{ tag }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </div>
        
        <!-- 左上下部分：项目统计 (占20%) -->
        <div class="left-lower">
          <el-card class="stats-card">
            <template #header>
              <span class="section-title">项目统计</span>
            </template>
            <div class="stats-grid">
              <div class="stat-item">
                <div class="stat-number">{{ project.totalTasks || 0 }}</div>
                <div class="stat-label">总任务数</div>
              </div>
              <div class="stat-item">
                <div class="stat-number completed">{{ project.completedTasks || 0 }}</div>
                <div class="stat-label">已完成</div>
              </div>
              <div class="stat-item">
                <div class="stat-number in-progress">{{ project.inProgressTasks || 0 }}</div>
                <div class="stat-label">进行中</div>
              </div>
              <div class="stat-item">
                <div class="stat-number pending">{{ project.pendingTasks || 0 }}</div>
                <div class="stat-label">待开始</div>
              </div>
            </div>
          </el-card>
        </div>
      </div>
      
      <!-- 右上部分：项目进度 -->
      <div class="right-section">
        <el-card class="progress-card">
          <template #header>
            <span class="section-title">项目进度</span>
          </template>
          
          <div class="progress-content">
            <div class="progress-main">
              <div class="progress-label">整体进度</div>
              <el-progress 
                :percentage="project.progress" 
                :status="getProgressStatus(project.progress)"
                :stroke-width="24"
                class="main-progress"
              />
              <div class="progress-text">{{ project.progress }}%</div>
            </div>
            
            <div class="progress-timeline">
              <div class="timeline-item">
                <div class="timeline-dot completed"></div>
                <div class="timeline-content">
                  <div class="timeline-title">需求分析</div>
                  <div class="timeline-date">2024-01-15 ~ 2024-01-20</div>
                </div>
              </div>
              <div class="timeline-item">
                <div class="timeline-dot completed"></div>
                <div class="timeline-content">
                  <div class="timeline-title">系统设计</div>
                  <div class="timeline-date">2024-01-21 ~ 2024-01-25</div>
                </div>
              </div>
              <div class="timeline-item">
                <div class="timeline-dot in-progress"></div>
                <div class="timeline-content">
                  <div class="timeline-title">核心开发</div>
                  <div class="timeline-date">2024-01-26 ~ 2024-02-15</div>
                </div>
              </div>
              <div class="timeline-item">
                <div class="timeline-dot pending"></div>
                <div class="timeline-content">
                  <div class="timeline-title">系统测试</div>
                  <div class="timeline-date">2024-02-16 ~ 2024-03-01</div>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>
    
    <!-- 下半部分：任务管理 -->
    <div class="lower-section" v-if="hasTaskData">
      <el-card class="tasks-card">
        <template #header>
          <div class="card-header">
            <span class="section-title">任务管理</span>
            <div class="header-actions">
              <el-button type="primary" @click="addTask" size="small">
                <el-icon><Plus /></el-icon>
                添加任务
              </el-button>
              <el-button @click="router.go(-1)" size="small">
                <el-icon><Back /></el-icon>
                返回
              </el-button>
            </div>
          </div>
        </template>
        
        <el-table :data="tasks" style="width: 100%" v-loading="loading">
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
    </div>
    
    <!-- 返回按钮（当没有任务数据时显示） -->
    <div class="no-task-actions" v-if="!hasTaskData">
      <el-button @click="router.go(-1)" type="primary">
        <el-icon><Back /></el-icon>
        返回
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Back } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const loading = ref(false)

// 计算是否有任务数据
const hasTaskData = computed(() => {
  return tasks.value && tasks.value.length > 0
})

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

const addTask = () => {
  ElMessage.info('添加任务功能待实现')
  // 模拟添加任务后显示下半部分
  setTimeout(() => {
    // 这里可以添加实际的任务数据
    tasks.value.push({
      id: Date.now(),
      name: '新任务',
      assignee: '新成员',
      status: '待开始',
      progress: 0,
      startTime: new Date().toLocaleString(),
      endTime: '待定'
    })
    // 滚动到下半部分
    setTimeout(() => {
      const lowerSection = document.querySelector('.lower-section')
      if (lowerSection) {
        lowerSection.scrollIntoView({ behavior: 'smooth' })
      }
    }, 100)
  }, 500)
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
    // 初始时清空任务数据，只显示上半部分
    tasks.value = []
  }, 500)
})
</script>

<style scoped>
.project-detail-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 0;
  box-sizing: border-box;
  overflow: hidden;
}

/* 上半部分：左7右3布局 */
.upper-section {
  height: 90vh;
  display: flex;
  gap: 0;
  margin-bottom: 0;
  border-bottom: 2px solid #ebeef5;
  min-height: 0;
}

/* 左侧部分：上8下2布局 */
.left-section {
  flex: 7;
  display: flex;
  flex-direction: column;
  gap: 0;
  border-right: 2px solid #ebeef5;
  min-height: 0;
}

.left-upper {
  flex: 6;
  border-bottom: 2px solid #ebeef5;
  min-height: 0;
}

.left-lower {
  flex: 4;
  min-height: 0;
}

/* 右侧部分 */
.right-section {
  flex: 3;
  min-height: 0;
}

/* 下半部分 */
.lower-section {
  min-height: 0;
}

/* 无任务数据时的返回按钮 */
.no-task-actions {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
}

/* 卡片样式 */
.info-card, .stats-card, .progress-card, .tasks-card {
  height: 100%;
  margin: 0;
  border-radius: 0;
  border: none;
}

/* 卡片标题 */
:deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 2px solid #ebeef5;
  background: #fafafa;
  border-radius: 0;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* 信息网格布局 */
.info-grid {
  padding: 20px;
  height: calc(100% - 60px);
  overflow-y: auto;
  min-height: 0;
}

.info-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-shrink: 0;
}

.info-row.full-width {
  flex-direction: column;
}

.info-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item label {
  font-weight: 600;
  color: #606266;
  font-size: 14px;
}

.info-value {
  color: #303133;
  font-size: 15px;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #409EFF;
}

.description {
  margin: 0;
  color: #606266;
  line-height: 1.6;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #67C23A;
}

.tags-container {
  margin-top: 8px;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  padding: 15px;
  height: calc(100% - 60px);
  overflow-y: auto;
  min-height: 0;
}

.stat-item {
  text-align: center;
  padding: 10px 8px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 6px;
  border: 1px solid #dee2e6;
}

.stat-number {
  font-size: 20px;
  font-weight: 700;
  color: #409EFF;
  margin-bottom: 6px;
}

.stat-number.completed { color: #67C23A; }
.stat-number.in-progress { color: #E6A23C; }
.stat-number.pending { color: #909399; }

.stat-label {
  color: #606266;
  font-size: 11px;
  font-weight: 500;
}

/* 进度卡片 */
.progress-content {
  padding: 20px;
  height: calc(100% - 60px);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  min-height: 0;
}

.progress-main {
  text-align: center;
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.progress-main {
  text-align: center;
  margin-bottom: 30px;
}

.progress-label {
  font-weight: 600;
  margin-bottom: 15px;
  color: #303133;
  font-size: 16px;
}

.main-progress {
  margin-bottom: 10px;
}

.progress-text {
  font-size: 18px;
  font-weight: 700;
  color: #409EFF;
}

/* 时间线 */
.progress-timeline {
  flex: 1;
  overflow-y: auto;
  padding-top: 10px;
}

.timeline-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 20px;
  position: relative;
}

.timeline-item:not(:last-child)::after {
  content: '';
  position: absolute;
  left: 6px;
  top: 20px;
  bottom: -20px;
  width: 2px;
  background: #e4e7ed;
}

.timeline-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  margin-right: 12px;
  margin-top: 3px;
  flex-shrink: 0;
}

.timeline-dot.completed { background: #67C23A; }
.timeline-dot.in-progress { background: #E6A23C; }
.timeline-dot.pending { background: #909399; }

.timeline-content {
  flex: 1;
}

.timeline-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
  font-size: 14px;
}

.timeline-date {
  color: #909399;
  font-size: 12px;
}

/* 任务表格 */
:deep(.el-table th), :deep(.el-table td) {
  font-size: 13px;
}

:deep(.el-tag) {
  padding: 2px 8px;
}

/* 表格容器 */
:deep(.el-table) {
  height: calc(100% - 60px);
}

:deep(.el-table__body-wrapper) {
  overflow-y: auto;
  min-height: 0;
}

/* 响应式调整 */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .info-row {
    flex-direction: column;
    gap: 15px;
  }
}
</style>
    