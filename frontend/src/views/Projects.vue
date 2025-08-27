<template>
    <div class="project-management-layout">
  
      <!-- 主内容区域 -->
      <main class="main-content">
        <!-- 页面标题 -->
        <div class="page-title-container">
          <h1 class="page-title">项目列表</h1>
          <p class="page-description">管理所有项目信息、测试进度及相关测试用例</p>
        </div>
        
        <!-- 顶部筛选栏 -->
        <div class="filter-bar">
          <!-- 左侧新增按钮 -->
          <el-button 
            type="primary" 
            class="add-button"
            @click="handleAddProject"
          >
            创建测试项目
          </el-button>
  
          <!-- 右侧搜索框 -->
          <div class="filter-right-group">
            <el-button 
              type="success" 
              class="add-button"
              @click="handleAddProject" 
              style="margin-right: 10px;"
            >
             执行
            </el-button>
            <el-input
              v-model="searchKeyword"
              placeholder="任务名称"
              class="search-input"
              suffix-icon="el-icon-search"
            />
            <el-button :icon="Search" type="primary" style="margin-left: 10px;" />
          </div>
        </div>
  
        <!-- 项目列表 -->
        <el-table
          :data="projectTableData"
          border
          style="width: 100%"
          class="project-table"
        >
          <el-table-column
            type="selection"
            width="55"
            align="center"
          />
  
          <el-table-column
            prop="projectNo"
            label="项目编号"
            align="center"
          />
  
          <el-table-column
            prop="projectName"
            label="项目名称"
            align="center"
          />
  
          <el-table-column
            prop="projectPhase"
            label="项目阶段"
            align="center"
          />
  
          <el-table-column
            prop="creator"
            label="创建人"
            align="center"
          />
  
          <el-table-column
            prop="createTime"
            label="创建时间"
            align="center"
          />
  
          <el-table-column
            label="进度"
            align="center"
            width="200"
          >
            <template #default="scope">
              <div class="progress-container">
                <el-progress
                  :percentage="calculateProjectProgress(scope.row)"
                  stroke-width="6"
                  class="progress-bar"
                />
              
              </div>
            </template>
          </el-table-column>
        </el-table>
  
        <!-- 分页 -->
        <div class="pagination-bar">
          <!-- 左侧红色提示文字 -->
          <div class="required-tip">* 测试任务执行中有可修改</div>
          
          <!-- 右侧分页控件 -->
          <el-pagination
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            :current-page="currentPage"
            :page-sizes="[10, 20, 50, 100]"
            :page-size="pageSize"
            layout="total, sizes, prev, pager, next, jumper"
            :total="total"
          />
        </div>
      </main>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { ElMessageBox, ElMessage } from 'element-plus'
  import {
    Check,
    Delete,
    Edit,
    Message,
    Search,
    Star,
  } from '@element-plus/icons-vue'
  
  // 左侧导航数据
  const activeNav = ref('project')
  
  // 筛选条件
  const phaseOptions = ref([
    { label: '功能测试', value: 'functional' },
    { label: '性能测试', value: 'performance' },
    { label: '安全测试', value: 'security' }
  ])
  const selectedPhase = ref('')
  const searchKeyword = ref('')
  
  // 表格数据
  const projectTableData = ref([
    {
      id: 1,
      projectNo: 'CSBG-QC-2023090001',
      projectName: '数据库测试',
      projectPhase: '功能测试',
      creator: 'admin',
      createTime: '2025-04-06 00:00:00',
      testCases: [
        {
          caseName: '功能验证',
          testStatus: '未开始',
          testResult: '/',
          testProgress: 20
        },
        {
          caseName: '兼容性测试',
          testStatus: '执行中',
          testResult: '/',
          testProgress: 50
        },
        {
          caseName: '边界测试',
          testStatus: '已完成',
          testResult: '通过',
          testProgress: 100
        }
      ]
    },
    {
      id: 2,
      projectNo: 'CSBG-QC-2023090002',
      projectName: '接口测试',
      projectPhase: '性能测试',
      creator: 'admin',
      createTime: '2025-04-06 00:00:00',
      testCases: [
        {
          caseName: '高并发测试',
          testStatus: '已完成',
          testResult: '未通过',
          testProgress: 100
        }
      ]
    },
    {
      id: 3,
      projectNo: 'CSBG-QC-2023090003',
      projectName: 'UI测试',
      projectPhase: '功能测试',
      creator: 'admin',
      createTime: '2025-04-10 00:00:00',
      testCases: [
        {
          caseName: '布局测试',
          testStatus: '执行中',
          testResult: '/',
          testProgress: 30
        },
        {
          caseName: '响应式测试',
          testStatus: '未开始',
          testResult: '/',
          testProgress: 0
        }
      ]
    }
  ])
  
  // 计算项目总进度
  const calculateProjectProgress = (project) => {
    if (!project.testCases || project.testCases.length === 0) {
      return 0;
    }
    
    const total = project.testCases.reduce((sum, item) => sum + item.testProgress, 0);
    return Math.round(total / project.testCases.length);
  }
  
  // 分页数据
  const currentPage = ref(1)
  const pageSize = ref(10)
  const total = ref(20)
  
  // 方法
  const handleAddProject = () => {
    ElMessage.info('新增项目')
  }
  
  const handleView = (row) => {
    ElMessage.info(`查看项目：${row.projectName}`)
  }
  
  const handleEdit = (row) => {
    ElMessage.info(`执行项目：${row.projectName}`)
  }
  
  const handleShare = (row) => {
    ElMessage.info(`生成报告：${row.projectName}`)
  }
  
  const handleDownload = (row) => {
    ElMessage.info(`分享项目：${row.projectName}`)
  }
  
  const handleDelete = (row) => {
    ElMessageBox.confirm(
      '此操作将删除项目日志, 是否继续?',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(() => {
      ElMessage({
        type: 'success',
        message: '删除成功!'
      })
    }).catch(() => {
      ElMessage({
        type: 'info',
        message: '已取消删除'
      })
    })
  }
  
  const handleCaseView = (row) => {
    ElMessage.info(`查看用例：${row.caseName}`)
  }
  
  const handleSizeChange = (val) => {
    pageSize.value = val
    // 可在此处调用接口获取新数据
  }
  
  const handleCurrentChange = (val) => {
    currentPage.value = val
    // 可在此处调用接口获取新数据
  }
  
  onMounted(() => {
    // 模拟初始化数据加载
  })
  </script>
  
  <style scoped>
  .project-management-layout {
    display: flex;
    height: 100vh;
    background-color: #f5f7fa;
  }
  
  /* 主内容 */
  .main-content {
    flex: 1;
    padding: 30px 25px;
    overflow: auto;
  }
  
  /* 页面标题 */
  .page-title-container {
    margin-bottom: 25px;
    padding-bottom: 15px;
    border-bottom: 1px solid #e5e6eb;
  }
  
  .page-title {
    font-size: 24px;
    font-weight: 600;
    color: #1d2129;
    margin: 0 0 8px 0;
  }
  
  .page-description {
    font-size: 13px;
    color: #86909c;
    margin: 0;
    font-weight: normal;
  }
  
  /* 筛选栏 */
  .filter-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
    padding: 15px 20px;
    background-color: #fff;
    border-radius: 4px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  }
  
  /* 按钮和输入框字体 */
  .el-button, .el-input__inner, .el-select {
    font-size: 13px !important;
    font-weight: normal !important;
  }
  
  /* 新增按钮 */
  .add-button {
    display: flex;
    align-items: center;
  }
  
  /* 右侧筛选组 */
  .filter-right-group {
    display: flex;
    align-items: center;
  }
  
  .filter-select {
    width: 160px;
    margin-right: 10px;
  }
  
  .filter-button {
    margin-right: 20px;
  }
  
  .search-input {
    width: 200px;
  }
  
  /* 表格样式 */
  .project-table {
    --el-table-header-text-color: #666;
    --el-table-row-hover-bg: #f9fafc;
    margin-bottom: 20px;
  }
  
  /* 表格内容字体 */
  .el-table th, .el-table td {
    font-size: 13px !important;
    font-weight: normal !important;
  }
  
  /* 进度条容器 */
  .progress-container {
    display: flex;
    align-items: center;
    width: 100%;
    padding: 0 5px;
  }
  
  /* 进度条样式 */
  .progress-bar {
    flex: 1;
    margin-right: 10px;
  }
  
  /* 百分比文字 */
  .progress-percentage {
    font-size: 12px;
    color: #666;
    min-width: 40px;
    text-align: right;
  }
  
  .test-case-table {
    margin-top: 10px;
    --el-table-header-text-color: #666;
    --el-table-row-hover-bg: #f9fafc;
  }
  
  /* 分页 */
  .pagination-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 16px;
    padding-top: 15px;
    border-top: 1px solid #e5e6eb;
  }
  
  /* 分页控件字体 */
  .el-pagination {
    font-size: 12px !important;
  }
  
  .el-pagination button, .el-pagination span {
    font-weight: normal !important;
  }
  
  /* 左侧红色提示文字 */
  .required-tip {
    color: #ff4949;
    font-size: 12px;
    font-weight: normal !important;
  }
  
  /* Element Plus 样式覆盖 */
  .el-select .el-input {
    width: 100%;
  }
  
  .el-pagination {
    margin: 0;
  }
  
  /* 响应式调整 */
  @media (max-width: 768px) {
    .filter-bar {
      flex-direction: column;
      align-items: flex-start;
      gap: 15px;
    }
    
    .filter-right-group {
      width: 100%;
      flex-wrap: wrap;
      gap: 10px;
    }
    
    .search-input {
      width: 100%;
    }
    
    .pagination-bar {
      flex-direction: column;
      align-items: flex-start;
      gap: 10px;
    }
  }
  </style>
  