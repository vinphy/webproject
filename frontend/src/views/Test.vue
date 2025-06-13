<template>
  <div class="data-screen">
    <!-- 顶部标题 -->
    <div class="header">
      <h1>数据监控大屏</h1>
      <div class="time">{{ currentTime }}</div>
    </div>

    <!-- 主要内容区 -->
    <div class="content">
      <!-- 左侧面板 -->
      <div class="left-panel">
        <el-card class="data-card">
          <template #header>
            <div class="card-header">
              <span>系统状态</span>
            </div>
          </template>
          <div class="status-list">
            <div class="status-item" v-for="(item, index) in systemStatus" :key="index">
              <div class="status-chart" v-if="item.type === 'circle'">
                <div class="circle-progress" :style="{
                  background: `conic-gradient(${getStatusColor(item.status)} ${item.percentage}%, rgba(255, 255, 255, 0.1) ${item.percentage}%)`
                }">
                  <div class="circle-inner">
                    <span class="percentage">{{ item.percentage }}%</span>
                  </div>
                </div>
              </div>
              <div class="battery-container" v-if="item.type === 'battery'">
                <div class="battery">
                  <div class="battery-level" :style="{
                    width: item.percentage + '%',
                    backgroundColor: getStatusColor(item.status)
                  }"></div>
                </div>
              </div>
              <div class="status-info">
                <span class="label">{{ item.label }}</span>
                <span class="value" :class="item.status">{{ item.value }}</span>
                <span class="description">{{ item.description }}</span>
              </div>
            </div>
          </div>
        </el-card>
        <el-card class="data-card">
          <template #header>
            <div class="card-header">
              <span>实时监控</span>
            </div>
          </template>
          <div class="monitor-chart">
            <!-- 这里可以集成echarts等图表库 -->
            <div class="chart-mock">
              <div class="chart-line" v-for="i in 20" :key="i" :style="{ height: Math.random() * 100 + '%' }"></div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 中间面板 -->
      <div class="center-panel">
        <el-card class="data-card main-card">
          <template #header>
            <div class="card-header">
              <span>核心指标</span>
            </div>
          </template>
          <div class="main-indicators">
            <div class="indicator" v-for="(item, index) in mainIndicators" :key="index">
              <div class="indicator-title">{{ item.title }}</div>
              <div class="indicator-value">{{ item.value }}</div>
              <div class="indicator-trend" :class="item.trend">
                {{ item.trend === 'up' ? '↑' : '↓' }} {{ item.rate }}
              </div>
            </div>
          </div>
        </el-card>
        <el-card class="data-card">
          <template #header>
            <div class="card-header">
              <span>告警信息</span>
            </div>
          </template>
          <div class="alert-list">
            <div class="alert-item" v-for="(alert, index) in alerts" :key="index" :class="alert.level">
              <span class="alert-time">{{ alert.time }}</span>
              <span class="alert-content">{{ alert.content }}</span>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 右侧面板 -->
      <div class="right-panel">
        <el-card class="data-card">
          <template #header>
            <div class="card-header">
              <span>资源使用率</span>
            </div>
          </template>
          <div class="resource-usage">
            <div class="resource-item" v-for="(item, index) in resourceUsage" :key="index">
              <div class="resource-info">
                <span class="resource-name">{{ item.name }}</span>
                <span class="resource-value">{{ item.value }}%</span>
              </div>
              <el-progress :percentage="item.value" :color="item.color" />
            </div>
          </div>
        </el-card>
        <el-card class="data-card">
          <template #header>
            <div class="card-header">
              <span>任务队列</span>
            </div>
          </template>
          <div class="task-queue">
            <div class="task-item" v-for="(task, index) in tasks" :key="index">
              <span class="task-name">{{ task.name }}</span>
              <span class="task-status" :class="task.status">{{ task.status }}</span>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div> 
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

// 当前时间
const currentTime = ref(new Date().toLocaleString())
let timer = null

// 系统状态数据
const systemStatus = ref([
  { 
    label: 'CPU使用率', 
    value: '45%', 
    status: 'normal',
    type: 'battery',
    percentage: 45,
    description: '当前CPU使用率处于正常水平，系统运行稳定'
  },
  { 
    label: '内存使用率', 
    value: '62%', 
    status: 'warning',
    type: 'circle',
    percentage: 62,
    description: '内存使用率较高，建议及时清理'
  },
  { 
    label: '磁盘使用率', 
    value: '78%', 
    status: 'danger',
    type: 'circle',
    percentage: 78,
    description: '磁盘空间不足，请及时处理'
  },
  { 
    label: '网络状态', 
    value: '正常', 
    status: 'normal',
    type: 'circle',
    percentage: 100,
    description: '网络连接正常，延迟较低'
  }
])

// 主要指标数据
const mainIndicators = ref([
  { title: '在线用户', value: '1,234', trend: 'up', rate: '12%' },
  { title: '今日访问', value: '8,567', trend: 'up', rate: '8%' },
  { title: '系统负载', value: '65%', trend: 'down', rate: '5%' },
  { title: '响应时间', value: '120ms', trend: 'down', rate: '3%' }
])

// 告警信息
const alerts = ref([
  { time: '10:30', content: '服务器CPU使用率超过80%', level: 'warning' },
  { time: '10:25', content: '数据库连接数接近上限', level: 'danger' },
  { time: '10:20', content: '网络延迟异常', level: 'info' }
])

// 资源使用率
const resourceUsage = ref([
  { name: 'CPU', value: 45, color: '#67C23A' },
  { name: '内存', value: 62, color: '#E6A23C' },
  { name: '磁盘', value: 78, color: '#F56C6C' },
  { name: '网络', value: 35, color: '#409EFF' }
])

// 任务队列
const tasks = ref([
  { name: '数据备份', status: 'running' },
  { name: '日志清理', status: 'pending' },
  { name: '系统更新', status: 'completed' },
  { name: '安全扫描', status: 'failed' }
])

// 获取状态颜色
const getStatusColor = (status) => {
  const colors = {
    normal: '#67C23A',
    warning: '#E6A23C',
    danger: '#F56C6C'
  }
  return colors[status] || colors.normal
}

// 更新时间
onMounted(() => {
  timer = setInterval(() => {
    currentTime.value = new Date().toLocaleString()
  }, 1000)
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})
</script>

<style scoped>
.data-screen {
  height: 100vh;
  background: #1a1a1a;
  color: #fff;
  padding: 20px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h1 {
  font-size: 24px;
  margin: 0;
  background: linear-gradient(90deg, #409EFF, #67C23A);
  -webkit-background-clip: text;
  color: transparent;
}

.time {
  font-size: 18px;
  color: #909399;
}

.content {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;
  gap: 20px;
  height: calc(100vh - 100px);
}

.data-card {
  background: rgba(255, 255, 255, 0.05);
  border: none;
  margin-bottom: 20px;
}

.data-card :deep(.el-card__header) {
  background: rgba(255, 255, 255, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 10px 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #fff;
}

.status-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.status-item {
  display: flex;
  align-items: center;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  gap: 20px;
}

.status-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.status-chart {
  width: 60px;
  height: 60px;
  flex-shrink: 0;
}

.circle-progress {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.circle-inner {
  width: 80%;
  height: 80%;
  background: #1a1a1a;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.percentage {
  font-size: 12px;
  color: #fff;
}

.battery-container {
  width: 60px;
  flex-shrink: 0;
}

.battery {
  width: 60px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  padding: 2px;
  position: relative;
}

.battery::after {
  content: '';
  position: absolute;
  right: -6px;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 8px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 0 2px 2px 0;
}

.battery-level {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.label {
  font-size: 14px;
  color: #909399;
}

.value {
  font-size: 16px;
  font-weight: bold;
  color: #fff;
}

.description {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

.monitor-chart {
  height: 200px;
}

.chart-mock {
  display: flex;
  align-items: flex-end;
  height: 100%;
  gap: 2px;
}

.chart-line {
  flex: 1;
  background: #409EFF;
  border-radius: 2px 2px 0 0;
  transition: height 0.3s;
}

.main-indicators {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.indicator {
  text-align: center;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

.indicator-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.indicator-value {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 10px;
}

.indicator-trend {
  font-size: 12px;
}

.indicator-trend.up {
  color: #67C23A;
}

.indicator-trend.down {
  color: #F56C6C;
}

.alert-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.alert-item {
  padding: 10px;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.alert-item.warning {
  background: rgba(230, 162, 60, 0.1);
  border: 1px solid rgba(230, 162, 60, 0.2);
}

.alert-item.danger {
  background: rgba(245, 108, 108, 0.1);
  border: 1px solid rgba(245, 108, 108, 0.2);
}

.alert-item.info {
  background: rgba(144, 147, 153, 0.1);
  border: 1px solid rgba(144, 147, 153, 0.2);
}

.alert-time {
  color: #909399;
  font-size: 12px;
}

.resource-usage {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.resource-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.resource-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.resource-name {
  color: #909399;
}

.resource-value {
  font-weight: bold;
}

.task-queue {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.task-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

.task-status {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.task-status.running {
  background: #409EFF;
}

.task-status.pending {
  background: #909399;
}

.task-status.completed {
  background: #67C23A;
}

.task-status.failed {
  background: #F56C6C;
}

/* 自定义滚动条 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
}
</style> 