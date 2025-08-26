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
    </div>
  </div>
</template>

<script>
export default {
  name: 'TestView',
  data() {
    return {
      projectsData: [
        { id: 1, projectCode: "PROJ-2023-001", progress: 100, status: "completed" },
        { id: 2, projectCode: "PROJ-2023-002", progress: 75, status: "in-progress" },
        { id: 3, projectCode: "PROJ-2023-003", progress: 30, status: "in-progress" },
        { id: 4, projectCode: "PROJ-2023-004", progress: 0, status: "not-started" },
        { id: 5, projectCode: "PROJ-2023-005", progress: 100, status: "completed" },
        { id: 6, projectCode: "PROJ-2023-006", progress: 45, status: "in-progress" },
        { id: 7, projectCode: "PROJ-2023-007", progress: 90, status: "in-progress" },
        { id: 8, projectCode: "PROJ-2023-008", progress: 10, status: "in-progress" },
        { id: 9, projectCode: "PROJ-2023-009", progress: 0, status: "not-started" },
        { id: 10, projectCode: "PROJ-2023-010", progress: 100, status: "completed" }
      ]
    }
  },
  methods: {
    getProgressColor(progress, status) {
      if (status === "completed") return "#2ecc71";
      if (status === "not-started") return "#f39c12";
      if (progress < 30) return "#e74c3c";
      if (progress < 70) return "#f39c12";
      return "#2ecc71";
    },
    getStatusText(status) {
      const statusMap = {
        "completed": "已完成",
        "in-progress": "进行中",
        "not-started": "未开始"
      };
      return statusMap[status] || status;
    }
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