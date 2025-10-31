// ... existing code ...
// 获取项目详情
const fetchProjectDetail = async () => {
  loading.value = true
  try {
    const projectId = route.params.id || 1  // 从路由参数获取项目ID
    const response = await getProjectDetail(projectId)
    
    // 修复：axios响应数据在response.data中
    console.log('API响应:', response.data)  // 调试用
    console.log('success字段:', response.data.success)  // 调试用
    
    if (response.data.success && response.data.data) {
      const projectData = response.data.data
      
      // 解析项目数据 - 修复id字段赋值错误
      project.value = {
        id: projectData.id,  // 修复：使用正确的id字段
        name: projectData.name,
        description: projectData.description || '',
        status: projectData.status || '待开始',
        type: projectData.project_type || '',
        priority: projectData.priority || '中',
        manager: projectData.test_leader || projectData.owner_name || '',
        createTime: projectData.created_at ? new Date(projectData.created_at).toLocaleString() : '',
        expectedEndTime: projectData.end_date || '',
        progress: projectData.progress || 0,
        executionItems: projectData.execution_items || []  // 执行项
      }
    } else {
      ElMessage.error(response.data.message || '获取项目详情失败')
    }
  } catch (error) {
    console.error('获取项目详情失败:', error)
    ElMessage.error('获取项目详情失败，请检查网络连接')
  } finally {
    loading.value = false
  }
}
// ... existing code ...