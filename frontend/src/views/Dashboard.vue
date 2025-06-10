<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>总用户数</span>
              <el-tag type="success">实时</el-tag>
            </div>
          </template>
          <div class="card-content">
            <div class="number">1,234</div>
            <div class="trend">
              <span class="up">↑ 12%</span>
              <span class="text">较上周</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>总订单数</span>
              <el-tag type="warning">今日</el-tag>
            </div>
          </template>
          <div class="card-content">
            <div class="number">256</div>
            <div class="trend">
              <span class="up">↑ 8%</span>
              <span class="text">较昨日</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>总收入</span>
              <el-tag type="info">本月</el-tag>
            </div>
          </template>
          <div class="card-content">
            <div class="number">¥89,432</div>
            <div class="trend">
              <span class="up">↑ 23%</span>
              <span class="text">较上月</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">
              <span>活跃用户</span>
              <el-tag type="danger">实时</el-tag>
            </div>
          </template>
          <div class="card-content">
            <div class="number">423</div>
            <div class="trend">
              <span class="down">↓ 3%</span>
              <span class="text">较昨日</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>销售趋势</span>
              <el-radio-group v-model="timeRange" size="small">
                <el-radio-button label="week">本周</el-radio-button>
                <el-radio-button label="month">本月</el-radio-button>
                <el-radio-button label="year">全年</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-placeholder">
            <!-- 这里可以集成echarts等图表库 -->
            <div class="chart-mock">
              <div class="chart-bar" v-for="i in 7" :key="i" :style="{ height: Math.random() * 100 + '%' }"></div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>用户分布</span>
            </div>
          </template>
          <div class="chart-placeholder">
            <!-- 这里可以集成echarts等图表库 -->
            <div class="chart-pie">
              <div class="pie-segment" v-for="i in 4" :key="i" :style="{ transform: `rotate(${i * 90}deg)` }"></div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const timeRange = ref('week')
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stat-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-content {
  text-align: center;
}

.number {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin: 10px 0;
}

.trend {
  font-size: 14px;
  color: #909399;
}

.trend .up {
  color: #67C23A;
  margin-right: 8px;
}

.trend .down {
  color: #F56C6C;
  margin-right: 8px;
}

.chart-row {
  margin-top: 20px;
}

.chart-placeholder {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-mock {
  display: flex;
  align-items: flex-end;
  height: 200px;
  width: 100%;
  gap: 10px;
}

.chart-bar {
  flex: 1;
  background-color: #409EFF;
  border-radius: 4px 4px 0 0;
  transition: height 0.3s;
}

.chart-pie {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: conic-gradient(
    #409EFF 0% 25%,
    #67C23A 25% 50%,
    #E6A23C 50% 75%,
    #F56C6C 75% 100%
  );
}
</style> 