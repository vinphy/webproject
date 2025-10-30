<template>
  <div class="home">
    <div class="main-container">
      <!-- 左侧区域 -->
      <div class="left-section">
        <!-- 项目执行进度 -->
        <el-card class="panel section-left-top" shadow="hover">
      <template #header>
            <span>项目执行进度</span>
          </template>
          <div class="left-top-row">
            <div class="table-wrap single">
              <el-table :data="statsRows" size="small">
                <el-table-column prop="name" label="" />
              </el-table>
            </div>
            <div class="chart-wrap single">
              <div ref="lineChartRef" class="chart"></div>
            </div>
            <div class="chart-wrap single">
              <div ref="barChartRef" class="chart"></div>
            </div>
        </div>
        </el-card>

        <!-- 工作柜台 -->
        <el-card class="panel section-left-bottom" shadow="hover">
          <template #header>
            <span>工作台</span>
          </template>
          <div class="workbench-grid">
            <div class="tile tile-a" @click="navigateToProjects">
              <el-icon><Monitor /></el-icon>
              <span>项目管理</span>
            </div>
            <div class="tile tile-b" @click="navigateToTestCases">
              <el-icon><User /></el-icon>
              <span>测试用例</span>
            </div>
            <div class="tile tile-c" @click="navigateToTestResults">
              <el-icon><Goods /></el-icon>
              <span>测试结果</span>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 右侧区域 -->
      <div class="right-section">
        <!-- 测试人员基本信息 -->
        <el-card class="panel section-right-top" shadow="hover">
          <template #header>
            <span>测试人员基本信息</span>
          </template>
          <div class="profile">
            <div class="avatar-col">
              <el-avatar src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
              <div class="edit-avatar">
                <el-icon><EditPen /></el-icon>
                <span>修改头像</span>
              </div>
            </div>
            <div class="info-col">
              <div class="info-item ">姓名：{{ user?.username || '未登录' }}</div>
              <div class="info-item">角色：{{ user?.role || '-' }}</div>
              <div class="info-item">邮箱：{{ user?.email || '-' }}</div>
              <div class="info-item">已创建项目：{{ createdCount }} 个</div>
            </div>
          </div>
        </el-card>

        <!-- 当前正在测试的项目 -->
        <el-card class="panel section-right-bottom" shadow="hover">
          <template #header>
            <span>当前正在测试的项目</span>
          </template>
          <HomeProjectItem/>
    </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed, watch } from 'vue'
import { userRef, api } from '../utils/auth'
import { Monitor, User, Goods, DataAnalysis, Setting, List, EditPen } from '@element-plus/icons-vue'
import HomeProjectItem from './childernVue.vue/HomeProjectItem.vue'
import { useRouter } from 'vue-router'
// import * as echarts from 'echarts'

const user = ref(null)
const router = useRouter()

// 项目统计数据
const projectStats = ref({
  total: 0,
  completed: 0,
  inProgress: 0,
  pending: 0
})

// 月度统计数据
const monthlyStats = ref([])

// 更新statsRows数据，使用从后端获取的真实数据
const statsRows = computed(() => [
  { name: '项目总数', type: 'title' },
  { name: projectStats.value.total.toString(), type: 'value' },
  { name: '已完成', type: 'title' },
  { name: projectStats.value.completed.toString(), type: 'value' },
  { name: '进行中', type: 'title' },
  { name: projectStats.value.inProgress.toString(), type: 'value' },
  { name: '待开始', type: 'title' },
  { name: projectStats.value.pending.toString(), type: 'value' }
])

// 获取项目统计数据
const fetchProjectStats = async () => {
  try {
    const { data } = await api.get('/api/home/project-stats')
    if (data) {
      projectStats.value = data
    }
  } catch (error) {
    console.error('获取项目统计数据失败:', error)
    // 使用默认数据
    projectStats.value = {
      total: 0,
      completed: 0,
      inProgress: 0,
      pending: 0
    }
  }
}

// 获取月度统计数据
const fetchMonthlyStats = async () => {
  try {
    const { data } = await api.get('/api/home/monthly-stats', {
      params: { months: 12 }
    })
    
    if (data && data.success) {
      monthlyStats.value = data.data
      updateCharts()
    } else {
      console.error('获取月度统计数据失败:', data?.error)
      // 使用默认数据
      monthlyStats.value = generateDefaultMonthlyData()
      updateCharts()
    }
  } catch (error) {
    console.error('获取月度统计数据失败:', error)
    // 使用默认数据
    monthlyStats.value = generateDefaultMonthlyData()
    updateCharts()
  }
}

// 生成默认月度数据（用于错误处理）
const generateDefaultMonthlyData = () => {
  const currentDate = new Date()
  const data = []
  
  // 生成最近12个月的默认数据，全部为0
  for (let i = 11; i >= 0; i--) {
    const date = new Date(currentDate.getFullYear(), currentDate.getMonth() - i, 1)
    data.push({
      year: date.getFullYear(),
      month: date.getMonth() + 1,
      count: 0,  // 全部设为0，而不是随机数
      label: `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}`
    })
  }
  
  return data
}

// 更新图表数据
const updateCharts = () => {
  if (!lineChart.value || !barChart.value || monthlyStats.value.length === 0) return
  
  // 正确排序：按时间顺序从早到晚
  const sortedStats = [...monthlyStats.value].sort((a, b) => {
    if (a.year !== b.year) return a.year - b.year
    return a.month - b.month
  })
  
  const xAxisData = sortedStats.map(item => {
    // 显示为"01月"格式，而不是"2024-01"
    return `${item.month.toString().padStart(2, '0')}月`
  })
  const seriesData = sortedStats.map(item => item.count)
  
  console.log('月度统计数据:', sortedStats) // 调试信息
  
  // 更新折线图
  lineChart.value.setOption({
    xAxis: { 
      data: xAxisData,
      axisLabel: {
        rotate: 45
      }
    },
    series: [{ data: seriesData }]
  })
  
  // 更新柱状图
  barChart.value.setOption({
    xAxis: { 
      data: xAxisData,
      axisLabel: {
        rotate: 45
      }
    },
    series: [{ data: seriesData }]
  })
}

// 图表实例
const lineChart = ref(null)
const barChart = ref(null)
const lineChartRef = ref(null)
const barChartRef = ref(null)

// 初始化图表
const initCharts = () => {
  if (!lineChartRef.value || !barChartRef.value) return
  
  lineChart.value = echarts.init(lineChartRef.value)
  barChart.value = echarts.init(barChartRef.value)
  
  // 使用空数据初始化，等待真实数据
  const emptyXAxis = Array.from({length: 12}, (_, i) => `${(i + 1).toString().padStart(2, '0')}月`)
  const emptyData = Array(12).fill(0)
  
  // 折线图配置
  lineChart.value.setOption({
    tooltip: { 
      trigger: 'axis',
      formatter: '{b}<br/>{a}: {c}个'
    },
    grid: { left: 30, right: 10, top: 20, bottom: 20 },
    xAxis: { 
      type: 'category', 
      data: emptyXAxis,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: { type: 'value' },
    series: [{ 
      name: '新建项目', 
      type: 'line', 
      smooth: true, 
      data: emptyData,
      itemStyle: {
        color: '#409EFF'
      },
      lineStyle: {
        color: '#409EFF'
      }
    }]
  })
  
  // 柱状图配置
  barChart.value.setOption({
    tooltip: { 
      trigger: 'axis',
      formatter: '{b}<br/>{a}: {c}个'
    },
    grid: { left: 30, right: 10, top: 20, bottom: 20 },
    xAxis: { 
      type: 'category', 
      data: emptyXAxis,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: { type: 'value' },
    series: [{ 
      name: '新建项目', 
      type: 'bar', 
      data: emptyData,
      itemStyle: {
        color: '#67C23A'
      }
    }]
  })
  
  // 监听窗口大小变化
  const onResize = () => { 
    lineChart.value?.resize()
    barChart.value?.resize()
  }
  window.addEventListener('resize', onResize)
}

// 监听月度数据变化，自动更新图表
watch(monthlyStats, () => {
  updateCharts()
}, { deep: true })

// 导航函数
const navigateToProjects = () => router.push('/projects')
const navigateToTestCases = () => router.push('/test-cases')
const navigateToTestResults = () => router.push('/test-results')

const createdCount = ref(12)

onMounted(() => {
  // 初始化图表
  initCharts()
  
  // 获取项目统计数据
  fetchProjectStats()
  
  // 获取月度统计数据
  fetchMonthlyStats()

  // 获取用户信息
  ;(async () => {
    try {
      const { data } = await api.get('/api/home/profile')
      if (data) {
        user.value = { username: data.name, email: data.email, role: data.role }
        createdCount.value = data.createdProjectsCount || 0
      }
    } catch (e) {
      user.value = userRef.value
    }
  })()
})
</script>

<style>
.home {
  height: 100%;
  padding: 8px;
  box-sizing: border-box;
  overflow: hidden;
}

.main-container {
  display: flex;
  height: 100%;
  gap: 8px;
}

.left-section {
  flex: 0 0 65%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.right-section {
  flex: 0 0 35%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 左侧布局：上下各50% */
.section-left-top {
  flex: 0 0 50%;
  min-height: 0;
}

.section-left-bottom {
  flex: 0 0 50%;
  min-height: 0;
}

/* 右侧布局：上40%，下60% */
.section-right-top {
  flex: 0 0 30%;
  min-height: 0;
}

.section-right-bottom {
  flex: 0 0 70%;
  min-height: 0;
}

/* 卡片样式重置 */
.panel {
  height: 100% !important;
  display: flex !important;
  flex-direction: column !important;
  margin: 0 !important;
}

.panel .el-card__body {
  flex: 1 !important;
  display: flex !important;
  flex-direction: column !important;
  padding: 8px !important;
  overflow: hidden !important;
}

/* 项目执行进度区域 */
.left-top-row {
  display: flex;
  gap: 8px;
  height: 100%;
  min-height: 0;
}

.table-wrap.single {
  flex: 0 0 11%;
  min-width: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 0;
  margin: 0;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.12), 0 0 6px rgba(0, 0, 0, 0.04);
}

.table-wrap.single .el-table {
  flex: 1;
  width: 100%;
  height: 100%;
  border: none !important;
}

.table-wrap.single .el-table .el-table__inner-wrapper {
  height: 100% !important;  /* 修复：从0改为100% */
  border: none !important;
}

.table-wrap.single .el-table .el-table__header-wrapper {
  height: auto !important;  /* 修复：从0改为auto */
  display: block !important;  /* 修复：从none改为block */
}

.table-wrap.single .el-table .el-table__body-wrapper {
  height: calc(100% - 40px) !important;  /* 减去表头高度 */
  overflow: auto;
}

.table-wrap.single .el-table .el-table__cell {
  border: none !important;
  padding: 6px 4px !important;
  margin: 0 !important;
  height: auto !important;  /* 修复：从固定高度改为auto */
  line-height: 1.5 !important;
  font-size: 13px !important;
}

/* 表格行样式 */
.table-wrap.single .el-table .el-table__row:nth-child(odd) .el-table__cell {
  font-weight: 600;
  color: #303133;
  background-color: #f5f7fa;
  text-align: center;
  font-size: 15px !important;
}

.table-wrap.single .el-table .el-table__row:nth-child(even) .el-table__cell {
  font-weight: bold;
  color: #409EFF;
  text-align: center;
  font-size: 16px !important;
}

.chart-wrap.single:nth-child(2) {
  flex: 0 0 38%;
}
 
.chart-wrap.single:nth-child(3) {
  flex: 0 0 55%;
}

.chart-wrap.single {
  min-width: 0;
  height: 100%;
}

.chart {
  width: 100%;
  height: 100px !important;
  min-height: 80px;
  max-height: 120px;
}

.chart-wrap.single:nth-child(2) .chart {
  height: calc(100% - 20px) !important;
  margin: 10px 0px 10px 15px !important;
  min-height: unset !important;
  max-height: unset !important;
}

.chart-wrap.single:nth-child(3) .chart {
  height: calc(100% - 20px) !important;
  margin: 10px 0px 10px 0px !important;
  min-height: unset !important;
  max-height: unset !important;
}

/* 工作柜台网格 */
.workbench-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: 1fr; /* 单行，撑满高度 */
  gap: 20px;
  height: 100%;
  align-items: stretch; /* 子项拉伸至满高 */
}

/* 工作柜台卡片内边距加大，仅作用于工作台面板 */
.section-left-bottom .el-card__body {
  padding: 16px !important;
}

/* 工作台块：更大的内边距、轻边框与更柔和的文本颜色 */
.tile {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  height: 100%;
  padding: 12px;
  color: #2c3e50; /* 深色文本，适配浅色背景 */
  border: 1px solid #e5e7eb; /* 轻边框增强层次 */
  border-radius: 10px;
}

.tile .el-icon {
  font-size: 38px; /* 放大图标 */
  margin: 0; /* 居中时不需要额外外边距 */
}

.tile span {
  font-size: 15px; /* 放大文字 */
  font-weight: 600;
}

/* 低饱和度浅色背景 */
.tile-a { background: #e8f1ff; } /* 柔和浅蓝 */
.tile-b { background: #eaf7ea; } /* 柔和浅绿 */
.tile-c { background: #fff4e5; } /* 柔和浅橙 */
.tile-d { background: #F56C6C; }
.tile-e { background: #909399; }
.tile-f { background: #1F2D3D; }

/* 右上信息卡片布局 */
.profile {
  display: flex;
  height: 100%;
  gap: 12px;
  align-items: center;
}

.avatar-col {
  flex: 0 0 40%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.avatar-col .el-avatar {
  width: 55%;
  height: auto;
  aspect-ratio: 1 / 1;
}

.edit-avatar {
  display: flex;
  align-items: center;
  margin-top: 8px;
  color: #409EFF;
  font-size: 12px;
  cursor: pointer;
}

.edit-avatar .el-icon {
  font-size: 14px;
  margin-right: 4px;
}

.info-col {
  flex: 0 0 60%;
  display: grid;
  grid-template-rows: repeat(4, 1fr);
  row-gap: 6px;
  align-content: center;
}

.info-item {
  display: flex;
  align-items: center;
  color: #303133;
  font-size: 14px;
}



/* 项目表单 */
.project-form {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 8px;
}

.project-form .pf-item {
  margin: 0;
}

.project-form .pf-item .el-input {
  width: 100%;
}

/* 表格样式调整 - 仅针对特定表格 */
.table-wrap.single .el-table {
  font-size: 14px;
}

.table-wrap.single .el-table .el-table__header-wrapper {
  height: 0 !important;
  display: none !important;
}

.table-wrap.single .el-table .el-table__body-wrapper {
  height: 100% !important;
  overflow: hidden;
}

/* 移除全局表格样式，避免影响其他页面 */
/* .el-table .el-table__row:nth-child(odd) .el-table__cell {
  color: #303133;
  background-color: #f5f7fa;
  text-align: center;
}

.el-table .el-table__row:nth-child(even) .el-table__cell {
  font-weight: bold;
  color: #409EFF;
  text-align: center;
  font-size: 16px;
} */

/* 卡片标题样式优化 */
.panel .el-card__header {
  padding: 14px 16px !important;
  box-sizing: border-box;
}

.panel .el-card__header span {
  position: relative;
  display: inline-block;
  padding-left: 12px;
  font-weight: 700;
  font-size: 18px;
  color: #303133;
  line-height: 1.4;
}

.panel .el-card__header span::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 22px;
  background: #409EFF;
  border-radius: 2px;
}

/* 右上卡片中部分割线（竖线），贴合上下边线 */
.section-right-top .profile {
  position: relative;
}
.section-right-top .profile::after {
  content: '';
  position: absolute;
  top: -8px; /* 补齐卡片body内边距，贴合上边线 */
  bottom: -8px; /* 补齐卡片body内边距，贴合下边线 */
  left: calc(37% + 8px); /* 40%列宽 + body左内边距 */
  width: 1px;
  background: var(--el-card-border-color, #EBEEF5);
}
</style>