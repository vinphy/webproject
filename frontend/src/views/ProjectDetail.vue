<template>
  <div class="project-detail-container">
    <!-- 上半部分：左7右3布局 -->
    <div class="upper-section">
      <!-- 左上部分：上7下3布局（保持您当前6/4比例） -->
      <div class="left-section">
        <!-- 左上上部分：项目信息 + 水位图在左 + CPU 折线图在下 -->
        <div class="left-upper">
          <el-card class="info-card">
            <template #header>
              <div class="card-header">
                <span class="section-title">项目基本信息</span>
                <el-tag :type="getStatusType(project.status)" size="large">{{ project.status }}</el-tag>
              </div>
            </template>

            <!-- 项目详细信息 -->
            <div class="project-info">
              <div class="info-grid">
                <div class="info-item">
                  <span class="info-label">项目ID：</span>
                  <span class="info-value">{{ project.id }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">项目名称：</span>
                  <span class="info-value">{{ project.name }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">项目类型：</span>
                  <span class="info-value">{{ project.type   }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">测试负责人：</span>
                  <span class="info-value">{{ project.manager }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">优先级：</span>
                  <el-tag :type="getPriorityType(project.priority)" size="small">{{ project.priority }}</el-tag>
                </div>
                <div class="info-item">
                  <span class="info-label">创建时间：</span>
                  <span class="info-value">{{ project.createTime }}</span>
                </div>
                <div class="info-item full-width">
                  <span class="info-label">项目描述：</span>
                  <span class="info-value">{{ project.description }}</span>
                </div>
                <div class="info-item full-width" v-if="project.step2Selections && Object.keys(project.step2Selections).length > 0">
                  <span class="info-label">执行项：</span>
                  <div class="execution-items-container">
                    <el-tag v-if="project.step2Selections.vuln"  size="small" class="execution-item">漏洞扫描</el-tag>
                    <el-tag v-if="project.step2Selections.fuzz"  size="small" class="execution-item">模糊测试</el-tag>
                    <el-tag v-if="project.step2Selections.cases"  size="small" class="execution-item">测试用例</el-tag>
                  </div>
                </div>
              </div>
            </div>

            <div class="charts-vertical">
              <div class="top-row">
                <div class="water-left">
                  <!-- 修改水位图的HTML结构 -->
                  <div class="water-wrapper">
                    <div class="water-circle">
                      <div class="water-container">
                        <div class="water-fill" :style="{ height: waterLevel + '%' }">
                          <div class="wave wave-1"></div>
                          <div class="wave wave-2"></div>
                          <div class="wave wave-3"></div>
                        </div>
                      </div>
                      <div class="water-text">{{ waterLevel }}%</div>
                      <div class="water-indicator"></div>
                    </div>
                  </div>
                </div>
                <div class="gpu-right">
                  <div class="chart-title">GPU 使用率</div>
                  <div ref="gpuLineRef" class="chart-gpu-line"></div>
                </div>
              </div>
              <!-- <div class="bottom-row">
                <div class="chart-title">CPU 使用率</div>
                <div ref="cpuLineRef" class="chart-cpu-line full"></div>
              </div> -->
            </div>
          </el-card>
        </div>
        
        <!-- 左上下部分：测试用例滚动列表（显示全部，可手动滚动） -->
        <div class="left-lower">
          <el-card class="stats-card">
            <template #header>
              <span class="section-title">测试用例</span>
            </template>
            <div class="cases-scroller" ref="casesScrollerRef">
              <div class="case-item" v-for="item in allCases" :key="item.id">
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
      
      <!-- 右上部分：运行监控（仅日志，GPU 已在左上展示） -->
      <div class="right-section">
        <el-card class="progress-card">
          <template #header>
            <div class="card-header">
              <span class="section-title">运行监控</span>
              <!-- 固定在运行监控标题右侧的操作按钮 -->
              <div class="fixed-header-actions">
                <el-button @click="executeProject" type="success" size="small">
                  <el-icon><VideoPlay /></el-icon>
                  执行
                </el-button>
                <el-button @click="deleteProject" type="danger" size="small">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
                <el-button @click="router.go(-1)" type="primary" size="small">
                  <el-icon><Back /></el-icon>
                  返回
                </el-button>
              </div>
            </div>
          </template>
          <div class="right-monitor">
            <!-- 项目运行状态信息 -->
            <div class="monitor-info">
              <div class="monitor-item">
                <span class="monitor-label">运行状态：</span>
                <el-tag :type="getStatusType(project.status)" size="small">{{ project.status }}</el-tag>
              </div>
              <div class="monitor-item">
                <span class="monitor-label">总体进度：</span>
                <el-progress :percentage="project.progress" :stroke-width="8" />
              </div>
              <div class="monitor-item">
                <span class="monitor-label">预期完成：</span>
                <span class="monitor-value">{{ project.expectedEndTime }}</span>
              </div>
              <div class="monitor-item">
                <span class="monitor-label">已用时间：</span>
                <span class="monitor-value">{{ getElapsedTime() }}</span>
              </div>
            </div>
            
            <div class="logs-block">
              <div class="chart-title">回执日志</div>
              <div class="logs-pane" ref="logsPaneRef">
                <div class="log-line" v-for="(log, idx) in logs" :key="idx">{{ log }}</div>
              </div>
            </div>
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

    <!-- 新增：静态图片卡片（5秒后显示） -->
    <div class="lower-section" v-if="showImages">
      <el-card class="images-card">
        <template #header>
          <span class="section-title">结果图片</span>
        </template>
        <div class="images-grid">
          <div class="img-cell" v-for="(img, idx) in staticImages" :key="idx">
            <img :src="img" alt="static" />
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed ,nextTick} from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Back, VideoPlay, Delete } from '@element-plus/icons-vue'
import { getProjectDetail } from '@/api/project'  // 导入API函数

const router = useRouter()
const route = useRoute()
const loading = ref(false)

// 计算是否有任务数据
const hasTaskData = computed(() => tasks.value && tasks.value.length > 0)

// 动态图表 refs
const cpuLineRef = ref(null)
const gpuLineRef = ref(null)
let cpuChart = null
let gpuChart = null

// 修改JavaScript逻辑部分
// 水位图（CSS 实现）数据
const waterLevel = ref(62)
// 移除原有的waterWaveStyle计算属性

const waterWaveStyle = computed(() => ({ transform: `translate(-50%, -${waterLevel.value}%)` }))

// 动态日志
const logs = ref([])
const logsPaneRef = ref(null)

// 测试用例列表（显示全部，可滚动）
const allCases = ref([
  { id: 1, name: '登录功能-正向', status: '已完成', progress: 100 },
  { id: 2, name: '注册功能-异常邮箱', status: '进行中', progress: 65 },
  { id: 3, name: '权限校验-越权访问', status: '进行中', progress: 45 },
  { id: 4, name: 'SQL注入检测', status: '待开始', progress: 0 },
  { id: 5, name: 'XSS防护', status: '待开始', progress: 0 },
  { id: 6, name: '接口稳定性-压测', status: '进行中', progress: 30 },
  { id: 7, name: '批量导入-边界值', status: '已完成', progress: 100 },
  { id: 8, name: '导出报告-多格式', status: '待开始', progress: 0 },
  { id: 9, name: '权限边界-组合', status: '进行中', progress: 40 },
  { id: 10, name: '报告模板-多语言', status: '待开始', progress: 0 },
])

// 项目数据（从API获取）
const project = ref({
  id: 0,
  name: '',
  description: '',
  status: '待开始',
  type: '',
  priority: '中',
  manager: '',
  createTime: '',
  expectedEndTime: '',
  progress: 0,
  tags: [],
  step2Selections:{},
})

// 模拟任务数据（下半部分按需显示）
const tasks = ref([])

// 获取项目详情
const fetchProjectDetail = async () => {
  loading.value = true
  try {
    const projectId = route.params.id || 1  // 从路由参数获取项目ID
    const response = await getProjectDetail(projectId)
    console.log('API响应:', response.data)  // 调试用
    console.log('success字段:', response.data.success)  // 调试用

    if (response.data.success && response.data.data) {
      const projectData = response.data.data
      console.log(projectData)

      // 解析项目数据
      project.value = {
        id: projectData.project_code,
        name: projectData.name,
        description: projectData.description || '',
        status: projectData.status || '待开始',
        type: projectData.project_type || '',
        priority: projectData.priority || '中',
        manager: projectData.test_leader || projectData.owner_name || '',
        createTime: projectData.created_at ? new Date(projectData.created_at).toLocaleString() : '',
        expectedEndTime: projectData.end_date || '',
        progress: projectData.progress || 0,
        executionItems: projectData.execution_items || [],  // 执行项
        step2Selections: projectData.step2Selections || {}
      }
    } else {
      ElMessage.error(response.message || '获取项目详情失败')
    }
  } catch (error) {
    console.error('获取项目详情失败:', error)
    ElMessage.error('获取项目详情失败，请检查网络连接')
  } finally {
    loading.value = false
  }
}

const getStatusType = (s) => ({ '进行中': 'warning', '已完成': 'success', '待开始': 'info' }[s] || 'info')
const getPriorityType = (p) => ({ '低': 'info', '中': 'warning', '高': 'danger', '紧急': 'danger' }[p] || 'info')
const getTaskStatusType = (s) => ({ '已完成': 'success', '进行中': 'warning', '待开始': 'info' }[s] || 'info')

// 计算已用时间
const getElapsedTime = () => {
  const start = new Date(project.value.createTime)
  const now = new Date()
  const diff = now - start
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  return `${days}天${hours}小时`
}

// 执行项目
const executeProject = () => {
  ElMessage.success('开始执行项目...')
  // 这里可以添加执行项目的逻辑
}

// 删除项目
const deleteProject = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个项目吗？删除后无法恢复！',
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    ElMessage.success('项目已删除')
    router.go(-1)
  } catch {
    ElMessage.info('已取消删除')
  }
}

const addTask = () => {
  ElMessage.info('添加任务功能待实现')
  setTimeout(() => {
    tasks.value.push({ id: Date.now(), name: '新任务', assignee: '新成员', status: '待开始', progress: 0, startTime: new Date().toLocaleString(), endTime: '待定' })
    setTimeout(() => { const lower = document.querySelector('.lower-section'); lower && lower.scrollIntoView({ behavior: 'smooth' }) }, 100)
  }, 500)
}

const viewTask = (t) => ElMessage.info(`查看任务：${t.name}`)
const editTask = (t) => ElMessage.info(`编辑任务：${t.name}`)

let cpuTimer = null, gpuTimer = null, waterTimer = null, casesTimer = null, logsTimer = null

// 动态日志追加：若用户未上滑则自动滚到底；若用户正在查看历史则不打断
const isNearBottom = (el) => (el.scrollHeight - el.scrollTop - el.clientHeight) < 40
const appendLog = (txt) => {
  logs.value.push(`[${new Date().toLocaleTimeString()}] ${txt}`)
  requestAnimationFrame(() => {
    const el = logsPaneRef.value
    if (el && isNearBottom(el)) el.scrollTop = el.scrollHeight
  })
}

// 五秒后展示静态图片
const showImages = ref(false)
const staticImages = [
new URL('/src/assets/gnuradio.png', import.meta.url).href,
  new URL('/src/assets/gnuradio.png', import.meta.url).href,
  new URL('/src/assets/gnuradio.png', import.meta.url).href,
  new URL('/src/assets/gnuradio.png', import.meta.url).href,
]

onMounted(() => {
  // 获取项目详情数据
  fetchProjectDetail()
  
  // 1) 日志先启动，确保无论图表是否出错都能看到日志
  const samples = ['拉取代码...OK','安装依赖...OK','启动容器 runner-01...OK','分发批次 #13...OK','执行 login_case...OK (320ms)','执行 add_role...OK (640ms)','执行 sql_scan...WARN','生成报告...OK','归档制品...OK']
  let i = 0
  appendLog('初始化运行监控...')
  logsTimer = setInterval(() => { appendLog(samples[i % samples.length]); i++ }, 1200)

  // 2) 图表初始化加守护，失败不影响日志
  try {
    if (cpuLineRef.value && typeof echarts !== 'undefined') {
      const cpu = echarts.init(cpuLineRef.value); cpuChart = cpu
      const xData = Array.from({ length: 30 }, (_, k) => k + 1)
      let cpuSeries = Array.from({ length: 30 }, () => Math.round(20 + Math.random() * 40))
      cpu.setOption({ animation: true, tooltip: { trigger: 'axis' }, grid: { left: 30, right: 10, top: 20, bottom: 20 }, xAxis: { type: 'category', data: xData, axisLabel: { show: false } }, yAxis: { type: 'value', min: 0, max: 100 }, series: [{ type: 'line', smooth: true, data: cpuSeries, areaStyle: {}, name: 'CPU%' }] })
      cpuTimer = setInterval(() => { cpuSeries.shift(); const n = Math.max(0, Math.min(100, cpuSeries.at(-1) + Math.round(-10 + Math.random() * 20))); cpuSeries.push(n); waterLevel.value = Math.round(n * 0.8); cpu.setOption({ series: [{ data: cpuSeries }] }) }, 1200)
    }
  } catch (e) { console.warn('CPU 图表初始化失败，已忽略：', e) }

  try {
    if (gpuLineRef.value && typeof echarts !== 'undefined') {
      const gpu = echarts.init(gpuLineRef.value); gpuChart = gpu
      const xData = Array.from({ length: 30 }, (_, k) => k + 1)
      let gpuSeries = Array.from({ length: 30 }, () => Math.round(10 + Math.random() * 60))
      gpu.setOption({ animation: true, tooltip: { trigger: 'axis' }, grid: { left: 30, right: 10, top: 10, bottom: 20 }, xAxis: { type: 'category', data: xData, axisLabel: { show: false } }, yAxis: { type: 'value', min: 0, max: 100 }, series: [{ type: 'line', smooth: true, data: gpuSeries, areaStyle: { opacity: 0.2 }, name: 'GPU%', lineStyle: { color: '#9b59b6' }, itemStyle: { color: '#9b59b6' } }] })
      gpuTimer = setInterval(() => { gpuSeries.shift(); const n = Math.max(0, Math.min(100, gpuSeries.at(-1) + Math.round(-10 + Math.random() * 20))); gpuSeries.push(n); gpu.setOption({ series: [{ data: gpuSeries }] }) }, 1300)
    }
  } catch (e) { console.warn('GPU 图表初始化失败，已忽略：', e) }

  // 3) 用例状态动态推进（用户可自由滚动）
  casesTimer = setInterval(() => {
    allCases.value.forEach(c => {
      if (c.status === '进行中') { c.progress = Math.min(100, c.progress + Math.round(Math.random() * 8)); if (c.progress >= 100) c.status = '已完成' }
      else if (c.status === '待开始' && Math.random() > 0.92) { c.status = '进行中'; c.progress = 5 }
    })
  }, 2200)

  // 4) 自适应
  const onResize = () => { cpuChart && cpuChart.resize(); gpuChart && gpuChart.resize() }
  window.addEventListener('resize', onResize)

  setTimeout(() => { 
    showImages.value = true 
    // 等待DOM更新完成后再滚动
    nextTick(() => {
      setTimeout(() => {
        const imagesSection = document.querySelector('.images-card')
        if (imagesSection) {
          imagesSection.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
          })
        }
      }, 100)
    })
  }, 5000)
})

onBeforeUnmount(() => {
  cpuTimer && clearInterval(cpuTimer)
  gpuTimer && clearInterval(gpuTimer)
  waterTimer && clearInterval(waterTimer)
  casesTimer && clearInterval(casesTimer)
  logsTimer && clearInterval(logsTimer)
  cpuChart && cpuChart.dispose()
  gpuChart && gpuChart.dispose()
})
</script>

<style scoped>
.project-detail-container { 
  min-height: 100vh; 
  display: flex; 
  flex-direction: column; 
  padding: 0; 
  box-sizing: border-box; 
  overflow-x: hidden; 
}

/* 上半部分：左7右3布局 - 修复高度问题 */
.upper-section { 
  height: 90vh; 
  display: flex; 
  gap: 0; 
  margin-bottom: 0; 
  border-bottom: 2px solid #ebeef5; 
  min-height: 0; 
  flex-shrink: 0; /* 防止被压缩 */
}

/* 左侧部分：上6下4布局（当前比例） */
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
  display: flex; 
  flex-direction: column; 
}
.left-lower { 
  flex: 4; 
  min-height: 0; 
  display: flex; 
  flex-direction: column; 
}
.left-upper .el-card, .left-lower .el-card, .right-section .el-card { 
  display: flex; 
  flex-direction: column; 
  height: 100%;
}
.left-upper .el-card :deep(.el-card__body), .left-lower .el-card :deep(.el-card__body), .right-section .el-card :deep(.el-card__body) {
  display: flex; 
  flex-direction: column; 
  min-height: 0; 
  flex: 1;
}

/* 右侧部分 */
.right-section { 
  flex: 3; 
  min-height: 0; 
}

/* 卡片与标题 */
.info-card, .stats-card, .progress-card, .tasks-card { 
  height: 100%; 
  margin: 0; 
  border-radius: 0; 
  border: none; 
}
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

/* 固定在运行监控标题右侧的操作按钮 */
.fixed-header-actions {
  position: fixed;
  top: 76px;
  right: 20px;
  display: flex;
  gap: 8px;
  z-index: 2000;
  background: rgba(255, 255, 255, 0.95);
  padding: 8px 12px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #ebeef5;
}

.header-actions {
  display: flex; 
  gap: 12px; 
}

/* 项目详细信息 */
.project-info { 
  padding: 16px; 
  border-bottom: 1px solid #ebeef5; 
  margin-bottom: 12px; 
  flex-shrink: 0; /* 防止被压缩 */
}
.info-grid { 
  display: grid; 
  grid-template-columns: 1fr 1fr; 
  gap: 12px; 
}
.info-item { 
  display: flex; 
  align-items: center; 
  gap: 8px; 
}
.info-item.full-width { 
  grid-column: 1 / -1; 
}
.info-label { 
  font-size: 13px; 
  color: #606266; 
  font-weight: 500; 
  min-width: 80px; 
}
.info-value { 
  font-size: 13px; 
  color: #303133; 
}
.tags-container { 
  display: flex; 
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 8px;
}
.tag-item { 
  margin: 0;
  background-color: #f0f9ff;
  border-color: #91d5ff;
  color: #1890ff;
}

/* 左上：水位+GPU 同行，CPU 在下；确保滚动容器生效 */
.charts-vertical { 
  display: flex; 
  flex-direction: column; 
  flex: 1; 
  padding: 12px 16px; 
  gap: 12px; 
  min-height: 0; 
}
.top-row { 
  display: flex; 
  gap: 16px; 
  align-items: stretch; 
  min-height: 0; 
}
.water-left { 
  width: 200px; 
  flex: 0 0 auto; 
}
.gpu-right { 
  flex: 1 1 0; 
  min-width: 0; 
  display: flex; 
  flex-direction: column; 
}
.chart-gpu-line { 
  width: 100%; 
  height: 140px; 
}
.bottom-row { 
  flex: 1; 
  min-height: 0; 
}
.chart-title { 
  font-size: 13px; 
  color: #606266; 
  margin: 4px 0 6px; 
}

/* CSS 水位图 */
/* 修改水位图的CSS样式 */
.water-wrapper { 
  display: flex; 
  justify-content: left; 
  align-items: center; 
}
.water-circle { 
  position: relative; 
  width: 120px; 
  height: 120px; 
  border-radius: 50%; 
  background: radial-gradient(closest-side, #f8fbff 85%, #e8f3ff 86% 92%, transparent 93% 100%); 
  border: 2px solid #cfe3ff; 
  box-shadow: 0 4px 12px rgba(59, 160, 255, 0.15); 
  overflow: hidden; 
}
.water-container {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}
.water-fill {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  background: linear-gradient(to top, #3ba0ff, #64b5ff);
  transition: height 0.8s ease-in-out;
}
.wave {
  position: absolute;
  bottom: 0;
  left: -100%;
  width: 300%;
  height: 40px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 45% 50% 40% 55%;
  animation: waveMove 6s linear infinite;
}
.wave-1 {
  animation-delay: 0s;
  opacity: 0.6;
  height: 35px;
}
.wave-2 {
  animation-delay: 2s;
  opacity: 0.4;
  height: 30px;
}
.wave-3 {
  animation-delay: 4s;
  opacity: 0.2;
  height: 25px;
}
.water-text { 
  position: absolute; 
  top: 50%; 
  left: 50%; 
  transform: translate(-50%, -50%); 
  font-weight: 700; 
  color: #3b6db3; 
  font-size: 18px; 
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8);
  z-index: 10;
}
.water-indicator {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80%;
  height: 80%;
  border-radius: 50%;
  border: 2px dashed rgba(59, 160, 255, 0.3);
  pointer-events: none;
}
@keyframes waveMove { 
  0% { transform: translateX(0) rotate(0deg); } 
  50% { transform: translateX(33.33%) rotate(180deg); } 
  100% { transform: translateX(66.66%) rotate(360deg); } 
}

/* 左下：测试用例滚动列表 */
.cases-scroller { 
  flex: 1; 
  min-height: 0; 
  overflow-y: auto; 
  padding: 12px 16px; 
}
.case-item { 
  display: grid; 
  grid-template-columns: 1.6fr 0.8fr 1.6fr; 
  align-items: center; 
  gap: 12px; 
  padding: 8px 10px; 
  border-bottom: 1px dashed #e5e7eb;
}
.case-name { 
  color: #303133; 
  font-size: 13px; 
}
.case-status { 
  text-align: center; 
}

/* 右侧：运行监控（日志可滚动） */
.right-monitor { 
  display: flex; 
  flex-direction: column; 
  height: 100%; 
  padding: 12px 16px; 
  gap: 12px; 
}
.monitor-info { 
  padding: 12px; 
  background: #f8f9fa; 
  border-radius: 6px; 
  margin-bottom: 8px; 
  flex-shrink: 0; /* 防止被压缩 */
}
.monitor-item { 
  display: flex; 
  align-items: center; 
  gap: 8px; 
  margin-bottom: 8px; 
}
.monitor-item:last-child { 
  margin-bottom: 0; 
}
.monitor-label { 
  font-size: 12px; 
  color: #606266; 
  font-weight: 500; 
  min-width: 80px; 
}
.monitor-value { 
  font-size: 12px; 
  color: #303133; 
}
.logs-block { 
  flex: 1; 
  min-height: 0; 
  display: flex; 
  flex-direction: column; 
}
.logs-pane { 
  flex: 1; 
  min-height: 0; 
  overflow-y: auto; 
  padding: 12px 16px; 
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; 
  font-size: 12px; 
  color: #2c3e50; 
  background: #fafafa; 
  border-left: 3px solid #e6eef7; 
}
.log-line { 
  padding: 4px 0; 
  white-space: pre-wrap; 
}

/* 任务表格 */
:deep(.el-table th), :deep(.el-table td) { 
  font-size: 13px; 
}
:deep(.el-tag) { 
  padding: 2px 8px; 
}
:deep(.el-table) { 
  height: calc(100% - 60px); 
}
:deep(.el-table__body-wrapper) { 
  overflow-y: auto; 
  min-height: 0; 
}

/* 静态图片 2x2 区域（在下半部分卡片中显示） */
.images-card { 
  border: none; 
  border-radius: 0; 
}
.images-grid { 
  display: grid; 
  grid-template-columns: 1fr 1fr; 
  grid-template-rows: 1fr 1fr; 
  gap: 10px; 
  padding: 10px 16px 16px; 
}
.img-cell { 
  background: #fff; 
  border: 1px solid #ebeef5; 
  border-radius: 6px; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  padding: 8px; 
}
.img-cell img { 
  max-width: 100%; 
  max-height: 100%; 
  object-fit: contain; 
}

/* 响应式 */
@media (max-width: 1200px) { 
  .water-left { width: 140px; } 
  .chart-cpu-line.full { height: 140px; } 
}
</style>