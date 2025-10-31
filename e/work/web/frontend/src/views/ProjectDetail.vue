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
              <div class="top-row">
                <div class="water-left">
                  <div class="chart-title">资源占用（水位）</div>
                  <div class="water-wrapper">
                    <div class="water-circle">
                      <!-- 多层水波效果 -->
                      <div class="water-background"></div>
                      <div class="wave wave-1" :style="waveStyle1"></div>
                      <div class="wave wave-2" :style="waveStyle2"></div>
                      <div class="wave wave-3" :style="waveStyle3"></div>
                      <div class="water-text">{{ waterLevel }}%</div>
                      <!-- 水位指示器 -->
                      <div class="water-indicator" :style="indicatorStyle"></div>
                    </div>
                    <!-- 水位图例 -->
                    <div class="water-legend">
                      <div class="legend-item">
                        <span class="legend-color" style="background: #3ba0ff;"></span>
                        <span class="legend-text">当前水位</span>
                      </div>
                      <div class="legend-item">
                        <span class="legend-color" style="background: #ff6b6b;"></span>
                        <span class="legend-text">警戒水位</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="gpu-right">
                  <div class="chart-title">GPU 使用率</div>
                  <div ref="gpuLineRef" class="chart-gpu-line"></div>
                </div>
              </div>
              <div class="bottom-row">
                <div class="execution-item">
                  <div class="execution-item-title">执行项</div>
                  <div class="execution-item-content">
                    <div class="execution-item-content-title">执行项</div>
                    <div class="execution-item-content-content">
                      <div class="execution-item-content-content-title">执行项</div>
                      <div class="execution-item-content-content-content">
                        <div class="execution-item-content-content-content-title">执行项</div>
                        <div class="execution-item-content-content-content-content">
                          <div class="execution-item-content-content-content-content-title">执行项</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="bottom-row">
                <div class="execution-item">
                  <div class="execution-item-title">执行项</div>
                  <div class="execution-item-content">
                    <div class="execution-item-content-title">执行项</div>
                    <div class="execution-item-content-content">
                      <div class="execution-item-content-content-title">执行项</div>
                      <div class="execution-item-content-content-content">
                        <div class="execution-item-content-content-content-title">执行项</div>
                        <div class="execution-item-content-content-content-content">
                          <div class="execution-item-content-content-content-content-title">执行项</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>