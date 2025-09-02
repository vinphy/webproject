<template>
  <div class="project-detail-container">
    <!-- 上半部分：左7右3布局 -->
    <div class="upper-section">
      <!-- 左上部分：上7下3布局（已按您后来修改为6/4，这里保留您当前设置） -->
      <div class="left-section">
        <!-- 左上上部分：项目基本信息 + 动态图表 -->
        <div class="left-upper">
          <el-card class="info-card">
            <template #header>
              <div class="card-header">
                <span class="section-title">项目基本信息</span>
                <el-tag :type="getStatusType(project.status)" size="large">{{ project.status }}</el-tag>
              </div>
            </template>

            <!-- 动态图表区：CPU折线图 + 水位图 -->
            <div class="charts-row">
              <div class="chart-box">
                <div class="chart-title">CPU 使用率</div>
                <div ref="cpuLineRef" class="chart-cpu-line"></div>
              </div>
              <div class="chart-box">
                <div class="chart-title">资源占用（水位）</div>
                <div class="water-wrapper">
                  <div class="water-circle">
                    <div class="wave" :style="waterWaveStyle"></div>
                    <div class="water-text">{{ waterLevel }}%</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 原有信息网格 -->
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
        
        <!-- 左上下部分：测试用例滚动列表 -->
        <div class="left-lower">
          <el-card class="stats-card">
            <template #header>
              <span class="section-title">测试用例</span>
            </template>
            <div class="cases-scroller" ref="casesScrollerRef">
              <div class="case-item" v-for="item in visibleCases" :key="item.id">
                <div class="case-name">{{ item.name }}</div>
                <div class="case-status">
                  <el-tag :type="getTaskStatusType(item.status)">{{ item.status }}</el-tag>
                </div>
                <div class="case-progress">
                  <el-progress :percentage="item.progress" :stroke-width="6" />
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </div>
      
      <!-- 右上部分：回执动态日志 -->
      <div class="right-section">
        <el-card class="progress-card">
          <template #header>
            <span class="section-title">回执日志</span>
          </template>
          <div class="logs-pane" ref="logsPaneRef">
            <div class="log-line" v-for="(log, idx) in logs" :key="idx">{{ log }}</div>
          </div>
        </el-card>
      </div>
    </div>
    
    <!-- 下半部分：任务管理（有数据时追加显示） -->
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
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
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

// 动态图表 refs
const cpuLineRef = ref(null)
let cpuChart = null

// 水位图（CSS 实现）数据
const waterLevel = ref(62) // 初始水位百分比
const waterWaveStyle = computed(() => ({
  transform: `translate(-50%, -${waterLevel.value}%)`,
}))

// 动态日志
const logs = ref([])
const logsPaneRef = ref(null)

// 测试用例滚动列表
const allCases = ref([
  { id: 1, name: '登录功能-正向', status: '已完成', progress: 100 },
  { id: 2, name: '注册功能-异常邮箱', status: '进行中', progress: 65 },
  { id: 3, name: '权限校验-越权访问', status: '进行中', progress: 45 },
  { id: 4, name: 'SQL注入检测', status: '待开始', progress: 0 },
  { id: 5, name: 'XSS防护', status: '待开始', progress: 0 },
  { id: 6, name: '接口稳定性-压测', status: '进行中', progress: 30 },
  { id: 7, name: '批量导入-边界值', status: '已完成', progress: 100 },
  { id: 8, name: '导出报告-多格式', status: '待开始', progress: 0 },
])
const visibleCases = ref(allCases.value.slice(0, 6))
const casesScrollerRef = ref(null)

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

// 模拟任务数据（下半部分按需显示）
const tasks = ref([
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

const viewTask = (task) => { ElMessage.info(`查看任务：${task.name}`) }
const editTask = (task) => { ElMessage.info(`编辑任务：${task.name}`) }

let cpuTimer = null
let waterTimer = null
let casesTimer = null
let logsTimer = null

onMounted(() => {
  // CPU 折线图
  const line = echarts.init(cpuLineRef.value)
  cpuChart = line
  const xData = Array.from({ length: 30 }, (_, i) => i + 1)
  let cpuSeries = Array.from({ length: 30 }, () => Math.round(20 + Math.random() * 40))
  line.setOption({
    animation: true,
    tooltip: { trigger: 'axis' },
    grid: { left: 30, right: 10, top: 20, bottom: 20 },
    xAxis: { type: 'category', data: xData, axisLabel: { show: false } },
    yAxis: { type: 'value', min: 0, max: 100, splitLine: { show: true } },
    series: [{ type: 'line', smooth: true, data: cpuSeries, areaStyle: {}, name: 'CPU%' }]
  })
  cpuTimer = setInterval(() => {
    cpuSeries.shift()
    const next = Math.max(0, Math.min(100, cpuSeries[cpuSeries.length - 1] + Math.round(-10 + Math.random() * 20)))
    cpuSeries.push(next)
    waterLevel.value = Math.round(next * 0.8)
    line.setOption({ series: [{ data: cpuSeries }] })
  }, 1200)

  // 水位动画（CSS）
  waterTimer = setInterval(() => {
    // 轻微波动
    const delta = Math.round(-2 + Math.random() * 4)
    waterLevel.value = Math.max(0, Math.min(100, waterLevel.value + delta))
  }, 1800)

  // 测试用例滚动与状态更新
  casesTimer = setInterval(() => {
    // 轮播可视用例
    allCases.value.push(allCases.value.shift())
    visibleCases.value = allCases.value.slice(0, 6)
    // 随机推进进行中用例
    allCases.value.forEach(c => {
      if (c.status === '进行中') {
        c.progress = Math.min(100, c.progress + Math.round(Math.random() * 10))
        if (c.progress >= 100) c.status = '已完成'
      } else if (c.status === '待开始' && Math.random() > 0.9) {
        c.status = '进行中'; c.progress = 5
      }
    })
  }, 2000)

  // 动态日志追加
  const sampleLogs = [
    '正在创建测试环境...OK',
    '拉取最新代码...OK',
    '启动容器: case-runner-01...OK',
    '分发测试用例批次 #12...OK',
    '执行用例 login_success...OK (320ms)',
    '执行用例 rbac_role_add...OK (742ms)',
    '执行用例 sql_injection_scan...WARN (低危)',
    '汇总报告生成中...OK',
    '上传报告到对象存储...OK',
  ]
  const appendLog = (text) => {
    logs.value.push(`[${new Date().toLocaleTimeString()}] ${text}`)
    // 自动滚屏
    requestAnimationFrame(() => {
      const el = logsPaneRef.value
      if (el) el.scrollTop = el.scrollHeight
    })
  }
  let idx = 0
  logsTimer = setInterval(() => {
    appendLog(sampleLogs[idx % sampleLogs.length])
    idx++
  }, 1200)

  // 自适应
  const onResize = () => { cpuChart && cpuChart.resize() }
  window.addEventListener('resize', onResize)
})

onBeforeUnmount(() => {
  cpuTimer && clearInterval(cpuTimer)
  waterTimer && clearInterval(waterTimer)
  casesTimer && clearInterval(casesTimer)
  logsTimer && clearInterval(logsTimer)
  if (cpuChart) { cpuChart.dispose(); cpuChart = null }
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

.section-title { font-size: 18px; font-weight: 600; color: #303133; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-actions { display: flex; gap: 12px; }

/* 动态图表区 */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  padding: 16px 16px 0 16px;
}
.chart-box { background: #fff; border: 1px solid #ebeef5; border-radius: 8px; padding: 10px; }
.chart-title { font-size: 13px; color: #606266; margin-bottom: 6px; }
.chart-cpu-line { width: 100%; height: 140px; }

/* CSS 水位图 */
.water-wrapper { display: flex; justify-content: center; align-items: center; }
.water-circle {
  position: relative; width: 120px; height: 120px; border-radius: 50%;
  background: radial-gradient(closest-side, #e8f3ff 92%, transparent 93% 100%), conic-gradient(#3ba0ff 0%, #3ba0ff 0%);
  overflow: hidden; border: 1px solid #cfe3ff;
}
.wave {
  position: absolute; left: 50%; bottom: 0; width: 200%; height: 200%;
  background: rgba(59,160,255,0.4);
  transform: translate(-50%, -60%);
  border-radius: 45% 55% 40% 60% / 55% 45% 55% 45%;
  animation: waveMove 4s linear infinite;
}
.water-text { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-weight: 700; color: #3b6db3; }
@keyframes waveMove {
  0% { transform: translate(-50%, -60%) rotate(0deg); }
  100% { transform: translate(-50%, -60%) rotate(360deg); }
}

/* 信息网格布局 */
.info-grid { padding: 20px; height: calc(100% - 60px); overflow-y: auto; min-height: 0; }
.info-row { display: flex; gap: 20px; margin-bottom: 20px; flex-shrink: 0; }
.info-row.full-width { flex-direction: column; }
.info-item { flex: 1; display: flex; flex-direction: column; gap: 8px; }
.info-item label { font-weight: 600; color: #606266; font-size: 14px; }
.info-value { color: #303133; font-size: 15px; padding: 8px 12px; background: #f8f9fa; border-radius: 6px; border-left: 3px solid #409EFF; }
.description { margin: 0; color: #606266; line-height: 1.6; padding: 12px; background: #f8f9fa; border-radius: 6px; border-left: 3px solid #67C23A; }
.tags-container { margin-top: 8px; }

/* 测试用例滚动列表 */
.cases-scroller { height: calc(100% - 60px); overflow-y: auto; padding: 12px 16px; }
.case-item { display: grid; grid-template-columns: 1.5fr 0.8fr 1.7fr; align-items: center; gap: 12px; padding: 8px 10px; border-bottom: 1px dashed #e5e7eb; }
.case-name { color: #303133; font-size: 13px; }
.case-status { text-align: center; }
.case-progress { }

/* 日志面板 */
.logs-pane { height: calc(100% - 60px); overflow-y: auto; padding: 12px 16px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size: 12px; color: #2c3e50; background: #fafafa; border-left: 3px solid #e6eef7; }
.log-line { padding: 4px 0; white-space: pre-wrap; }

/* 任务表格 */
:deep(.el-table th), :deep(.el-table td) { font-size: 13px; }
:deep(.el-tag) { padding: 2px 8px; }
:deep(.el-table) { height: calc(100% - 60px); }
:deep(.el-table__body-wrapper) { overflow-y: auto; min-height: 0; }

/* 响应式调整 */
@media (max-width: 1200px) {
  .info-row { flex-direction: column; gap: 15px; }
}
</style>
    