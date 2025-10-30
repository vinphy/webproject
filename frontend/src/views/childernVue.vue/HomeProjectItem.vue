<template>
  <div class="test-container">
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th class="id-column">编号</th>
            <th class="code-column">项目编号</th>
            <th class="progress-column">项目进度</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="project in projectsData" :key="project.id">
            <td class="id-column">{{ project.id }}</td>
            <td class="code-column">{{ project.projectCode }}</td>
            <td class="progress-column">
              <div class="progress-wrapper">
                <div class="progress-container">
                  <div 
                    class="progress-bar" 
                    :style="{
                      width: `${project.progress}%`, 
                      backgroundColor: getProgressColor(project.progress, project.status)
                    }"
                  ></div>
                </div>
                <div class="progress-info">
                  <span class="progress-text">{{ project.progress }}%</span>
                  <span :class="['status', project.status]">{{ getStatusText(project.status) }}</span>
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="loading" class="loading-container">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <span>正在加载项目数据...</span>
      </div>
      <div v-else-if="projectsData.length === 0" class="empty-container">
        <el-icon><DocumentRemove /></el-icon>
        <span>暂无项目数据</span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { api } from '../../utils/auth'
import { Loading, DocumentRemove } from '@element-plus/icons-vue'

export default {
  name: 'HomeProjectItem',
  setup() {
    const projectsData = ref([])
    const loading = ref(true)

    // 获取当前测试项目数据
    const fetchCurrentTestingProjects = async () => {
      try {
        loading.value = true
        const { data } = await api.get('/api/home/current-testing-projects?limit=10')
        
        if (data && data.success) {
          projectsData.value = data.data
          console.log('成功获取项目数据:', data.data.length, '个项目')
        } else {
          console.error('获取项目数据失败:', data?.error)
          projectsData.value = [] // 失败时设置为空数组
        }
      } catch (error) {
        console.error('获取当前测试项目数据失败:', error)
        projectsData.value = [] // 异常时设置为空数组
      } finally {
        loading.value = false
      }
    }

    // 进度条颜色映射
    const getProgressColor = (progress, status) => {
      if (status === "completed") return "#2ecc71";
      if (status === "not-started") return "#f39c12";
      if (progress < 30) return "#e74c3c";
      if (progress < 70) return "#f39c12";
      return "#2ecc71";
    }

    // 状态文本映射
    const getStatusText = (status) => {
      const statusMap = {
        "completed": "已完成",
        "in-progress": "进行中", 
        "not-started": "未开始"
      };
      return statusMap[status] || status;
    }

    onMounted(() => {
      fetchCurrentTestingProjects()
    })

    return {
      projectsData,
      loading,
      getProgressColor,
      getStatusText
    }
  },
  components: {
    Loading,
    DocumentRemove
  }
}
</script>

<style scoped>
.test-container {
  width: 85%;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.table-container {
  overflow-x: auto;
  overflow-y: auto;
  max-height: 500px;
  position: relative;
  min-height: 200px;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 100%;
  table-layout: fixed;
}

thead {
  position: sticky;
  top: 0;
  z-index: 10;
}

th {
  background-color: #f8f9fa;
  padding: 12px 10px;
  text-align: left;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #e9ecef;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

td {
  padding: 10px;
  border-bottom: 1px solid #e9ecef;
  color: #555;
  font-size: 13px;
  vertical-align: middle;
}

/* 列宽调整 */
.id-column {
  width: 8%;
  min-width: 30px;
}

.code-column {
  width: 30%;
  min-width: 120px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.progress-column {
  width: 55%;
  min-width: 180px;
}

.progress-wrapper {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.progress-container {
  width: 100%;
  height: 6px;
  background-color: #e9ecef;
  border-radius: 3px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.progress-text {
  font-size: 12px;
  font-weight: 500;
  color: #666;
  flex-shrink: 0;
}

.status {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
  white-space: nowrap;
}

.completed {
  background-color: #e7f6e9;
  color: #2ecc71;
}

.in-progress {
  background-color: #ebf5ff;
  color: #3498db;
}

.not-started {
  background-color: #fef3e8;
  color: #f39c12;
}

tr:nth-child(even) {
  background-color: #fafafa;
}

tr:hover {
  background-color: #f1f7ff;
  transition: background-color 0.2s;
}

/* 加载和空状态样式 */
.loading-container, .empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #666;
}

.loading-icon {
  font-size: 24px;
  margin-bottom: 8px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-container .el-icon {
  font-size: 24px;
  margin-bottom: 8px;
  color: #999;
}

/* 响应式设计 */
@media (max-width: 768px) {
  th, td {
    padding: 8px 6px;
    font-size: 12px;
  }
  
  .id-column {
    width: 12%;
  }
  
  .code-column {
    width: 28%;
  }
  
  .progress-column {
    width: 60%;
  }
  
  .progress-text {
    font-size: 11px;
  }
  
  .status {
    font-size: 10px;
    padding: 2px 6px;
  }
}

@media (max-width: 480px) {
  .test-container {
    border-radius: 6px;
  }
  
  th, td {
    padding: 6px 4px;
    font-size: 11px;
  }
  
  .progress-container {
    height: 5px;
  }
  
  .progress-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
}
</style>