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
              <el-table :data="statsRows" size="small" border>
                <el-table-column prop="label" label="指标" width="120" />
                <el-table-column prop="value" label="数量" />
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
            <span>工作柜台</span>
          </template>
          <div class="workbench-grid">
            <div class="tile tile-a"><el-icon><Monitor /></el-icon><span>新建项目</span></div>
            <div class="tile tile-b"><el-icon><User /></el-icon><span>我的任务</span></div>
            <div class="tile tile-c"><el-icon><Goods /></el-icon><span>导入用例</span></div>
            <div class="tile tile-d"><el-icon><DataAnalysis /></el-icon><span>统计报表</span></div>
            <div class="tile tile-e"><el-icon><Setting /></el-icon><span>系统设置</span></div>
            <div class="tile tile-f"><el-icon><List /></el-icon><span>更多功能</span></div>
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
            <el-avatar :size="72" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
            <div class="info">
              <div class="name">{{ user?.username || '未登录' }}</div>
              <div class="meta">角色：{{ user?.role || '-' }}</div>
              <div class="meta">邮箱：{{ user?.email || '-' }}</div>
            </div>
          </div>
        </el-card>

        <!-- 当前正在测试的项目 -->
        <el-card class="panel section-right-bottom" shadow="hover">
          <template #header>
            <span>当前正在测试的项目</span>
          </template>
          <el-form :model="currentProject" label-width="80px" label-position="left" class="project-form" inline size="small">
            <el-form-item label="项目名称" class="pf-item"><el-input v-model="currentProject.name" disabled /></el-form-item>
            <el-form-item label="负责人" class="pf-item"><el-input v-model="currentProject.owner" disabled /></el-form-item>
            <el-form-item label="进度" class="pf-item"><el-input v-model="currentProject.progress" disabled /></el-form-item>
          </el-form>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { userRef } from '../utils/auth'
import { Monitor, User, Goods, DataAnalysis, Setting, List } from '@element-plus/icons-vue'

const user = computed(() => userRef.value)

const statsRows = ref([
  { label: '项目总数', value: 120 },
  { label: '已完成', value: 75 },
  { label: '进行中', value: 30 },
  { label: '待开始', value: 15 }
])

const monthlyNewProjects = [12, 18, 22, 17, 25, 30, 28, 26, 24, 20, 18, 16]

const lineChartRef = ref(null)
const barChartRef = ref(null)

const currentProject = ref({ name: 'XX系统测试', owner: '张三', progress: '65%' })

onMounted(() => {
  const lineChart = echarts.init(lineChartRef.value)
  const barChart = echarts.init(barChartRef.value)
  const xAxis = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月']

  lineChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 30, right: 10, top: 10, bottom: 20 },
    xAxis: { type: 'category', data: xAxis },
    yAxis: { type: 'value' },
    series: [{ name: '新建项目', type: 'line', smooth: true, data: monthlyNewProjects }]
  })

  barChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 30, right: 10, top: 10, bottom: 20 },
    xAxis: { type: 'category', data: xAxis },
    yAxis: { type: 'value' },
    series: [{ name: '新建项目', type: 'bar', data: monthlyNewProjects }]
  })

  const onResize = () => { lineChart.resize(); barChart.resize() }
  window.addEventListener('resize', onResize)
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
  flex: 0 0 70%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.right-section {
  flex: 0 0 30%;
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
  flex: 0 0 40%;
  min-height: 0;
}

.section-right-bottom {
  flex: 0 0 60%;
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
  flex: 0 0 25%;
  min-width: 0;
}

.chart-wrap.single:nth-child(2) {
  flex: 0 0 45%;
}

.chart-wrap.single:nth-child(3) {
  flex: 0 0 30%;
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

/* 工作柜台网格 */
.workbench-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  height: 100%;
  align-content: center;
}

.tile {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  color: #fff;
  border-radius: 8px;
  aspect-ratio: 1 / 1;
  min-height: 60px;
  max-height: 80px;
}

.tile .el-icon {
  font-size: 18px;
  margin-bottom: 4px;
}

.tile span {
  font-size: 11px;
}

.tile-a { background: #409EFF; }
.tile-b { background: #67C23A; }
.tile-c { background: #E6A23C; }
.tile-d { background: #F56C6C; }
.tile-e { background: #909399; }
.tile-f { background: #1F2D3D; }

/* 用户信息 */
.profile {
  display: flex;
  align-items: center;
  height: 100%;
}

.profile .info {
  margin-left: 12px;
}

.profile .name {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 6px;
}

.profile .meta {
  color: #666;
  font-size: 11px;
  margin-top: 2px;
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

/* 表格样式调整 */
.el-table {
  font-size: 12px;
}

.el-table .el-table__header-wrapper {
  height: 32px;
}

.el-table .el-table__body-wrapper {
  height: calc(100% - 32px);
}
</style> 