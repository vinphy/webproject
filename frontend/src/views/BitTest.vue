<template>
  <div class="compliance-test">
    <!-- 顶部按钮组 -->
    <div class="button-group">
      <el-button type="primary" @click="startTest" :loading="isTesting">
        <el-icon><VideoPlay /></el-icon>
        开始测试
      </el-button>
      <el-button type="danger" @click="stopTest" :disabled="!isTesting">
        <el-icon><VideoPause /></el-icon>
        停止测试
      </el-button>
      <el-button type="success" @click="exportExcel">
        <el-icon><Document /></el-icon>
        导出Excel
      </el-button>
      <el-button type="warning" @click="exportWord">
        <el-icon><Document /></el-icon>
        导出Word
      </el-button>
    </div>

    <!-- 测试结果表格 -->
    <el-table
      :data="tableData"
      style="width: 100%"
      border
      v-loading="isLoading"
    >
      <el-table-column prop="projectName" label="项目名称" min-width="180" />
      <el-table-column prop="type" label="类型" width="120">
        <template #default="{ row }">
          <el-tag :type="getTypeTag(row.type)">{{ row.type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="result" label="结果" width="120">
        <template #default="{ row }">
          <el-tag :type="getResultTag(row.result)">{{ row.result == 0 ? '不通过' : '通过' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="300" show-overflow-tooltip />
    </el-table>

    <!-- 分页 -->
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
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { VideoPlay, VideoPause, Document } from '@element-plus/icons-vue'

// 表格数据
const tableData = ref([])
const isLoading = ref(false)
const isTesting = ref(false)

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 获取测试数据
const fetchTestData = async () => {
  isLoading.value = true
  try {
    const response = await fetch(`http://localhost:8000/api/test/list?page=${currentPage.value}&size=${pageSize.value}`)
    if (!response.ok) {
      throw new Error('获取测试数据失败')
    }
    const data = await response.json()
    if (data.status === 'success') {
      tableData.value = data.data.items
      total.value = data.data.total
    } else {
      throw new Error(data.message || '获取测试数据失败')
    }
  } catch (error) {
    console.error('获取测试数据失败:', error)
    ElMessage.error('获取测试数据失败：' + error.message)
  } finally {
    isLoading.value = false
  }
}

// 开始测试
const startTest = async () => {
  try {
    isTesting.value = true
    const response = await fetch('http://localhost:8000/api/test/start', {
      method: 'POST'
    })
    if (!response.ok) {
      throw new Error('启动测试失败')
    }
    const data = await response.json()
    if (data.status === 'success') {
      ElMessage.success('测试已启动')
      // 开始轮询测试结果
      startPolling()
    } else {
      throw new Error(data.message || '启动测试失败')
    }
  } catch (error) {
    console.error('启动测试失败:', error)
    ElMessage.error('启动测试失败：' + error.message)
    isTesting.value = false
  }
}

// 停止测试
const stopTest = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/test/stop', {
      method: 'POST'
    })
    if (!response.ok) {
      throw new Error('停止测试失败')
    }
    const data = await response.json()
    if (data.status === 'success') {
      ElMessage.success('测试已停止')
      isTesting.value = false
      stopPolling()
    } else {
      throw new Error(data.message || '停止测试失败')
    }
  } catch (error) {
    console.error('停止测试失败:', error)
    ElMessage.error('停止测试失败：' + error.message)
  }
}

// 导出Excel
const exportExcel = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/test/export/excel')
    if (!response.ok) {
      throw new Error('导出Excel失败')
    }
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = '符合性测试报告.xlsx'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('Excel导出成功')
  } catch (error) {
    console.error('导出Excel失败:', error)
    ElMessage.error('导出Excel失败：' + error.message)
  }
}

// 导出Word
const exportWord = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/test/export/word')
    if (!response.ok) {
      throw new Error('导出Word失败')
    }
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = '符合性测试报告.docx'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('Word导出成功')
  } catch (error) {
    console.error('导出Word失败:', error)
    ElMessage.error('导出Word失败：' + error.message)
  }
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  fetchTestData()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchTestData()
}

// 获取类型标签样式
const getTypeTag = (type) => {
  const typeMap = {
    '功能测试': 'primary',
    '性能测试': 'success',
    '安全测试': 'warning',
    '兼容性测试': 'info'
  }
  return typeMap[type] || 'default'
}

// 获取结果标签样式
const getResultTag = (result) => {
  const resultMap = {
    '通过': 'success',
    '失败': 'danger',
    '警告': 'warning',
    '未测试': 'info'
  }
  return resultMap[result] || 'default'
}

// 轮询测试结果
let pollingTimer = null
const startPolling = () => {
  pollingTimer = setInterval(() => {
    fetchTestData()
  }, 5000) // 每5秒更新一次
}

const stopPolling = () => {
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
}

// 组件挂载时获取数据
onMounted(() => {
  fetchTestData()
})

// 组件卸载时清理
onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.compliance-test {
  padding: 20px;
}

.button-group {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-table) {
  margin-top: 20px;
}

:deep(.el-tag) {
  text-align: center;
  min-width: 60px;
}
</style> 