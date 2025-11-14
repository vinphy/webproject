<template>
  <div class="sql-er-diagram">
    <!-- <div class="header">
      <h2>SQL实体关系图生成器</h2>
      <p>导入SQL文件或输入SQL语句，自动生成数据库实体关系图</p>
    </div> -->

    <div class="main-container">
      <!-- 左侧：Tab页功能区域 -->
      <div class="left-panel">
        <!-- Tab标题栏 - 移动到顶部 -->
        <div class="tab-header">
          <el-tabs v-model="activeTab" class="modeling-tabs">
            <el-tab-pane label="SQL导入" name="sql"></el-tab-pane>
            <el-tab-pane label="图形建模" name="modeling"></el-tab-pane>
          </el-tabs>
        </div>

        <!-- Tab内容区域 -->
        <div class="tab-content-container">
          <!-- SQL导入标签页 -->
          <div v-if="activeTab === 'sql'" class="sql-section">
            <!-- 文件上传 -->
            <div class="file-upload">
              <el-upload
                ref="uploadRef"
                :auto-upload="false"
                :show-file-list="false"
                accept=".sql,.txt"
                @change="handleFileChange"
              >
                <el-button type="success">
                  <el-icon><Upload /></el-icon>
                  选择SQL文件
                </el-button>
                <template #tip>
                  <div class="el-upload__tip">
                    支持 .sql 和 .txt 文件，或直接在下方输入SQL语句
                  </div>
                </template>
              </el-upload>
            </div>

            <div class="input-header">
              <div class="input-actions">
                <el-button type="primary" @click="parseSql" :loading="parsing">
                  <el-icon><Search /></el-icon>
                  解析SQL
                </el-button>
                <el-button @click="clearSql">
                  <el-icon><Delete /></el-icon>
                  清空
                </el-button>
              </div>
            </div>

            <!-- SQL文本输入 -->
            <div class="sql-textarea">
              <el-input
                v-model="sqlText"
                type="textarea"
                :rows="10"
                placeholder="请输入SQL语句，支持CREATE TABLE、ALTER TABLE等DDL语句..."
                @input="handleSqlInput"
              />
            </div>

            <!-- 解析结果预览 -->
            <div v-if="parsedTables.length > 0" class="parse-result">
              <h4>解析结果预览</h4>
              <div class="table-list">
                <div 
                  v-for="table in parsedTables" 
                  :key="table.name"
                  class="table-item"
                  :class="{ 'selected': selectedTable === table.name }"
                  @click="selectTable(table.name)"
                >
                  <div class="table-header">
                    <span class="table-name">{{ table.name }}</span>
                    <span class="table-count">{{ table.columns.length }} 字段</span>
                  </div>
                  <div class="table-columns">
                    <div 
                      v-for="column in table.columns.slice(0, 3)" 
                      :key="column.name"
                      class="column-item"
                    >
                      <span class="column-name">{{ column.name }}</span>
                      <span class="column-type">{{ column.type }}</span>
                    </div>
                    <div v-if="table.columns.length > 3" class="more-columns">
                      +{{ table.columns.length - 3 }} 更多字段
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 图形建模标签页 -->
          <div v-if="activeTab === 'modeling'" class="modeling-section">
            <div class="modeling-header">
              <h3>图形建模</h3>
              <div class="modeling-actions">
                <el-button type="primary" @click="addNewTable">
                  <el-icon><Plus /></el-icon>
                  新建表
                </el-button>
              </div>
            </div>

            <!-- 表列表 -->
            <div class="table-panel">
              <div 
                v-for="table in tables" 
                :key="table.id"
                class="table-panel-item"
                :class="{ 'active': activeTableId === table.id }"
                @click="setActiveTable(table.id)"
              >
                <div class="table-panel-header">
                  <div class="table-title">
                    <el-input
                      v-model="table.name"
                      placeholder="表名"
                      size="small"
                      @input="updateTableName(table.id, $event)"
                    />
                  </div>
                  <div class="table-actions">
                    <el-button type="danger" size="small" @click.stop="removeTable(table.id)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>

                <!-- 字段列表 -->
                <div class="fields-section">
                  <div class="fields-header">
                    <span>字段</span>
                    <el-button size="small" @click.stop="addField(table.id)">
                      <el-icon><Plus /></el-icon>
                      添加字段
                    </el-button>
                  </div>
                  <div class="fields-list">
                    <div 
                      v-for="field in table.fields" 
                      :key="field.id"
                      class="field-item"
                    >
                      <div class="field-info">
                        <el-input
                          v-model="field.name"
                          placeholder="字段名"
                          size="small"
                        />
                        <el-select v-model="field.type" placeholder="数据类型" size="small">
                          <el-option label="INT" value="INT" />
                          <el-option label="VARCHAR" value="VARCHAR" />
                          <el-option label="TEXT" value="TEXT" />
                          <el-option label="DATE" value="DATE" />
                          <el-option label="DATETIME" value="DATETIME" />
                          <el-option label="DECIMAL" value="DECIMAL" />
                        </el-select>
                      </div>
                      <div class="field-actions">
                        <el-checkbox v-model="field.nullable">可空</el-checkbox>
                        <el-button type="danger" size="small" @click.stop="removeField(table.id, field.id)">
                          <el-icon><Delete /></el-icon>
                        </el-button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 索引列表 -->
                <div class="indexes-section">
                  <div class="indexes-header">
                    <span>索引</span>
                    <el-button size="small" @click.stop="addIndex(table.id)">
                      <el-icon><Plus /></el-icon>
                      添加索引
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：ER图绘制区域 -->
      <div class="er-diagram-section">
        <div class="diagram-header">
          <h3>实体关系图</h3>
          <div class="diagram-actions">
            <el-button @click="autoLayout" :disabled="!hasNodes">
              <el-icon><Grid /></el-icon>
              自动布局
            </el-button>
            <el-button @click="exportDiagram" :disabled="!hasNodes">
              <el-icon><Download /></el-icon>
              导出图片
            </el-button>
            <el-button @click="clearDiagram" :disabled="!hasNodes">
              <el-icon><Delete /></el-icon>
              清空图表
            </el-button>
          </div>
        </div>

        <!-- 自定义ER图容器 -->
        <div class="diagram-container" ref="diagramContainer">
          <div class="diagram-canvas" ref="diagramCanvas">
            <!-- 连接线 -->
            <svg class="connections-layer" :width="canvasWidth" :height="canvasHeight">
              <defs>
                <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                  <polygon points="0 0, 10 3.5, 0 7" fill="#409EFF" />
                </marker>
              </defs>
              <g>
                <path
                  v-for="connection in connections"
                  :key="connection.id"
                  :d="connection.path"
                  class="connection-path"
                  :marker-end="'url(#arrowhead)'"
                  stroke="#409EFF"
                  stroke-width="2"
                  fill="none"
                />
              </g>
            </svg>
            
            <!-- 表格节点 -->
            <div
              v-for="table in tableNodes"
              :key="table.id"
              class="table-node"
              :style="{
                left: table.x + 'px',
                top: table.y + 'px'
              }"
              @mousedown="startDrag($event, table)"
              @click="selectTableNode(table)"
              :class="{ 'selected': selectedTableNode === table.id }"
            >
              <div class="table-header">
                <div class="table-icon">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M3 3h18v18H3V3zm16 16V5H5v14h14z"/>
                    <path d="M7 7h10v2H7V7zm0 4h10v2H7v-2zm0 4h7v2H7v-2z"/>
                  </svg>
                </div>
                <span class="table-name">{{ table.name }}</span>
                <div class="table-actions" v-if="table.primaryKey">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="#f56c6c">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                  </svg>
                </div>
              </div>
              <div class="table-columns">
                <div 
                  v-for="column in table.columns.slice(0, 5)" 
                  :key="column.name"
                  class="column-row"
                  :class="{
                    'primary-key': isPrimaryKey(table, column.name),
                    'foreign-key': isForeignKey(table, column.name)
                  }"
                >
                  <div class="column-info">
                    <span class="column-name">{{ column.name }}</span>
                    <span class="column-type">{{ column.type }}</span>
                  </div>
                  <div class="column-constraints">
                    <span v-if="!column.nullable" class="constraint not-null">NOT NULL</span>
                    <span v-if="isPrimaryKey(table, column.name)" class="constraint pk">PK</span>
                    <span v-if="isForeignKey(table, column.name)" class="constraint fk">FK</span>
                  </div>
                </div>
                <div v-if="table.columns.length > 5" class="more-columns">
                  +{{ table.columns.length - 5 }} 更多字段
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 表格详情对话框 -->
    <el-dialog
      v-model="tableDetailVisible"
      title="表格详情"
      width="600px"
    >
      <div v-if="selectedTableData" class="table-detail">
        <h4>{{ selectedTableData.name }}</h4>
        <el-table :data="selectedTableData.columns" border>
          <el-table-column prop="name" label="字段名" width="150" />
          <el-table-column prop="type" label="数据类型" width="120" />
          <el-table-column prop="nullable" label="允许空值" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.nullable ? 'danger' : 'success'">
                {{ scope.row.nullable ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="default" label="默认值" width="120" />
          <el-table-column prop="comment" label="注释" />
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Delete, Upload, Grid, Download } from '@element-plus/icons-vue'
import axios from 'axios'

export default {
  name: 'SqlErDiagram',
  components: {
    Search,
    Delete,
    Upload,
    Grid,
    Download
  },
  setup() {
    // 响应式数据
    const sqlText = ref('')
    const parsing = ref(false)
    const parsedTables = ref([])
    const selectedTable = ref('')
    const tableDetailVisible = ref(false)
    const selectedTableData = ref(null)
    const uploadRef = ref(null)
    const diagramContainer = ref(null)
    const diagramCanvas = ref(null)


    // 添加activeTab响应式变量
    const activeTab = ref('sql')

    // 图表相关
    const tableNodes = ref([])
    const connections = ref([])
    const selectedTableNode = ref(null)
    const canvasWidth = ref(1200)
    const canvasHeight = ref(800)
    const isDragging = ref(false)
    const dragTarget = ref(null)
    const dragOffset = ref({ x: 0, y: 0 })

    // 计算属性
    const hasNodes = computed(() => tableNodes.value.length > 0)

    // 方法
    const handleFileChange = (file) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        sqlText.value = e.target.result
      }
      reader.readAsText(file.raw)
    }

    const handleSqlInput = () => {
      // SQL输入变化时的处理
    }

    const parseSql = async () => {
      if (!sqlText.value.trim()) {
        ElMessage.warning('请输入SQL语句')
        return
      }

      parsing.value = true
      try {
        const response = await axios.post('http://localhost:8000/api/sql/parse', {
          sql: sqlText.value
        })
        
        if (response.data.success) {
          parsedTables.value = response.data.tables
          ElMessage.success(`成功解析 ${parsedTables.value.length} 个表`)
          generateErDiagram()
        } else {
          ElMessage.error(response.data.message || 'SQL解析失败')
        }
      } catch (error) {
        console.error('SQL解析错误:', error)
        ElMessage.error('SQL解析失败，请检查语法')
      } finally {
        parsing.value = false
      }
    }

    const clearSql = () => {
      sqlText.value = ''
      parsedTables.value = []
      selectedTable.value = ''
      clearDiagram()
    }

    const selectTable = (tableName) => {
      selectedTable.value = tableName
      selectedTableData.value = parsedTables.value.find(t => t.name === tableName)
      tableDetailVisible.value = true
    }

    const generateErDiagram = () => {
      tableNodes.value = []
      connections.value = []
      let nodeId = 1

      // 生成表格节点
      parsedTables.value.forEach((table, index) => {
        const node = {
          id: `table-${nodeId}`,
          name: table.name,
          columns: table.columns,
          primaryKey: table.primaryKey,
          foreignKeys: table.foreignKeys || [],
          x: 100 + (index % 3) * 350,
          y: 100 + Math.floor(index / 3) * 300
        }
        tableNodes.value.push(node)
        nodeId++
      })

      // 生成连接线
      let connectionId = 1
      parsedTables.value.forEach(table => {
        if (table.foreignKeys) {
          table.foreignKeys.forEach(fk => {
            const sourceNode = tableNodes.value.find(n => n.name === table.name)
            const targetNode = tableNodes.value.find(n => n.name === fk.referencedTable)
            
            if (sourceNode && targetNode) {
              const connection = {
                id: `connection-${connectionId}`,
                source: sourceNode.id,
                target: targetNode.id,
                sourceTable: table.name,
                targetTable: fk.referencedTable,
                sourceColumn: fk.column,
                targetColumn: fk.referencedColumn,
                path: calculatePath(sourceNode, targetNode)
              }
connections.value.push(connection)
              connectionId++
            }
          })
        }
      })
    }

    const calculatePath = (source, target) => {
      const startX = source.x + 200 // 表格宽度的一半
      const startY = source.y + 150 // 表格高度的一半
      const endX = target.x + 200
      const endY = target.y + 150
      
      const midX = (startX + endX) / 2
      
      return `M ${startX} ${startY} C ${midX} ${startY} ${midX} ${endY} ${endX} ${endY}`
    }

    const isPrimaryKey = (table, columnName) => {
      return table.primaryKey && table.primaryKey.includes(columnName)
    }

    const isForeignKey = (table, columnName) => {
      return table.foreignKeys && table.foreignKeys.some(fk => fk.column === columnName)
    }

    const selectTableNode = (node) => {
      selectedTableNode.value = node.id
      selectTable(node.name)
    }

    const startDrag = (event, node) => {
      isDragging.value = true
      dragTarget.value = node
      const rect = event.target.getBoundingClientRect()
      dragOffset.value = {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top
      }
      
      document.addEventListener('mousemove', handleDrag)
      document.addEventListener('mouseup', stopDrag)
    }

    const handleDrag = (event) => {
      if (!isDragging.value || !dragTarget.value) return
      
      const containerRect = diagramCanvas.value.getBoundingClientRect()
      const newX = event.clientX - containerRect.left - dragOffset.value.x
      const newY = event.clientY - containerRect.top - dragOffset.value.y
      
      dragTarget.value.x = Math.max(0, newX)
      dragTarget.value.y = Math.max(0, newY)
      
      // 更新连接线
      updateConnections()
    }

    const stopDrag = () => {
      isDragging.value = false
      dragTarget.value = null
      document.removeEventListener('mousemove', handleDrag)
      document.removeEventListener('mouseup', stopDrag)
    }

    const updateConnections = () => {
      connections.value.forEach(connection => {
        const sourceNode = tableNodes.value.find(n => n.id === connection.source)
        const targetNode = tableNodes.value.find(n => n.id === connection.target)
        if (sourceNode && targetNode) {
          connection.path = calculatePath(sourceNode, targetNode)
        }
      })
    }

    const autoLayout = () => {
      const nodes = tableNodes.value
      const cols = Math.ceil(Math.sqrt(nodes.length))
      
      nodes.forEach((node, index) => {
        const row = Math.floor(index / cols)
        const col = index % cols
        node.x = 100 + col * 350
        node.y = 100 + row * 300
      })
      
      updateConnections()
    }

    const exportDiagram = () => {
      ElMessage.info('导出功能开发中...')
    }

    const clearDiagram = () => {
      tableNodes.value = []
      connections.value = []
      selectedTableNode.value = null
    }

    onMounted(() => {
      // 初始化画布尺寸
      if (diagramContainer.value) {
        canvasWidth.value = diagramContainer.value.clientWidth
        canvasHeight.value = diagramContainer.value.clientHeight
      }
    })

    return {
      sqlText,
      parsing,
      parsedTables,
      selectedTable,
      tableDetailVisible,
      selectedTableData,
      uploadRef,
      diagramContainer,
      diagramCanvas,
      tableNodes,
      connections,
      selectedTableNode,
      canvasWidth,
      canvasHeight,
      hasNodes,
      handleFileChange,
      handleSqlInput,
      parseSql,
      clearSql,
      selectTable,
      selectTableNode,
      isPrimaryKey,
      isForeignKey,
      startDrag,
      autoLayout,
      exportDiagram,
      clearDiagram,
      activeTab,
    }
  }
}
</script>

<style scoped>
.sql-er-diagram {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
  margin-top:-4px;
  margin-left: -4px;
}

/* .header {
  padding: 20px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  text-align: center;
}

.header h2 {
  margin: 0 0 10px 0;
  color: #303133;
}

.header p {
  margin: 0;
  color: #606266;
} */

.main-container {
  flex: 1;
  display: flex;
  overflow: hidden;
  height:100%;
}

/* 左侧面板 - 固定20%宽度 */
.left-panel {
  width: 20%;
  min-width: 300px; /* 设置最小宽度防止过小 */
  max-width: 400px; /* 设置最大宽度防止过大 */
  background: white;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  flex-shrink: 0; /* 防止收缩 */
}

/* Tab标题栏 - 移动到顶部 */
.tab-header {
  flex-shrink: 0; /* 防止标题栏收缩 */
  border-bottom: 1px solid #e4e7ed;
  background: white;
}

.modeling-tabs {
  margin: 0;
}

:deep(.el-tabs) {
  --el-tabs-header-height: 43px;
}

:deep(.el-tabs__header) {
  margin: 0;
}

:deep(.el-tabs__nav-wrap) {
  padding: 0 20px;
}

/* Tab内容区域 */
.tab-content-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* SQL导入区域 */
.sql-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.file-upload {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.input-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.input-header h3 {
  margin: 0;
  color: #303133;
}

.input-actions {
  display: flex;
  gap: 10px;
}

.sql-textarea {
  flex: 1;
  padding: 20px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sql-textarea .el-textarea {
  flex: 1;
}

.parse-result {
  padding: 20px;
  border-top: 1px solid #e4e7ed;
  flex: 1;
  overflow-y: auto;
  min-height: 0; /* 重要：允许flex子项收缩 */
}

.parse-result h4 {
  margin: 0 0 15px 0;
  color: #303133;
}

:deep(.sql-textarea .el-textarea__inner) {
  height: 200px !important;
  resize: vertical;
}

/* 图形建模区域 */
.modeling-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modeling-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.modeling-header h3 {
  margin: 0;
  color: #303133;
}

.modeling-actions {
  display: flex;
  gap: 10px;
}

.table-panel {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.table-panel-item {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  margin-bottom: 15px;
  overflow: hidden;
  transition: all 0.3s;
}

.table-panel-item:hover {
  border-color: #409EFF;
}

.table-panel-item.active {
  border-color: #409EFF;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.table-panel-header {
  padding: 15px;
  background: #f5f7fa;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e4e7ed;
}

.table-title {
  flex: 1;
}

.table-actions {
  display: flex;
  gap: 5px;
}

.fields-section, .indexes-section {
  padding: 15px;
}

.fields-header, .indexes-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.fields-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.field-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border: 1px solid #f0f0f0;
  border-radius: 4px;
  background: #fafafa;
}

.field-info {
  display: flex;
  gap: 10px;
  flex: 1;
}

.field-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.table-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.table-item {
  padding: 15px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.table-item:hover {
  border-color: #409EFF;
  background: #f0f9ff;
}

.table-item.selected {
  border-color: #409EFF;
  background: #e6f7ff;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.table-name {
  font-weight: 600;
  color: #303133;
}

.table-count {
  font-size: 12px;
  color: #909399;
  background: #f4f4f5;
  padding: 2px 8px;
  border-radius: 10px;
}

.table-columns {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.column-item {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #606266;
}

.column-name {
  font-weight: 500;
}

.column-type {
  color: #909399;
}

.more-columns {
  font-size: 12px;
  color: #909399;
  text-align: center;
  padding: 5px 0;
}

.er-diagram-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  min-width: 0; /* 重要：允许flex子项收缩 */
}

.diagram-header {
  padding: 10px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.diagram-header h3 {
  margin: 0;
  color: #303133;
}

.diagram-actions {
  display: flex;
  gap: 10px;
}

.diagram-container {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: #fafafa;
}

.diagram-canvas {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: auto;
}

.connections-layer {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
  z-index: 1;
}

.connection-path {
  pointer-events: stroke;
  cursor: pointer;
}

.table-node {
  position: absolute;
  background: white;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  min-width: 200px;
  max-width: 300px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: move;
  overflow: hidden;
  z-index: 2;
}

.table-node:hover {
  border-color: #409EFF;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
  transform: translateY(-2px);
}

.table-node.selected {
  border-color: #409EFF;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.table-node .table-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 14px;
}

.table-node .table-icon {
  display: flex;
  align-items: center;
}

.table-node .table-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: white;
}

.table-node .table-actions {
  display: flex;
  align-items: center;
}

.table-node .table-columns {
  max-height: 300px;
  overflow-y: auto;
}

.table-node .column-row {
  padding: 8px 16px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background-color 0.2s;
}

.table-node .column-row:hover {
  background-color: #f8f9fa;
}

.table-node .column-row:last-child {
  border-bottom: none;
}

.table-node .column-row.primary-key {
  background-color: #fef0f0;
  border-left: 3px solid #f56c6c;
}

.table-node .column-row.foreign-key {
  background-color: #f0f9ff;
  border-left: 3px solid #409EFF;
}

.table-node .column-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.table-node .column-name {
  font-weight: 500;
  font-size: 13px;
  color: #303133;
}

.table-node .column-type {
  font-size: 11px;
  color: #909399;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.table-node .column-constraints {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.table-node .constraint {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: 500;
  text-transform: uppercase;
}

.table-node .constraint.not-null {
  background-color: #fef0f0;
  color: #f56c6c;
}

.table-node .constraint.pk {
  background-color: #f56c6c;
  color: white;
}

.table-node .constraint.fk {
  background-color: #409EFF;
  color: white;
}

.table-node .more-columns {
  font-size: 12px;
  color: #909399;
  text-align: center;
  padding: 8px 16px;
}

.table-detail h4 {
  margin: 0 0 20px 0;
  color: #303133;
}

/* 滚动条样式 */
.table-node .table-columns::-webkit-scrollbar {
  width: 4px;
}

.table-node .table-columns::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.table-node .table-columns::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 2px;
}

.table-node .table-columns::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .left-panel {
    width: 25%; /* 在小屏幕上稍微增加宽度 */
    min-width: 280px;
  }
}
@media (max-width: 768px) {
  .main-container {
    flex-direction: column;
  }
  
  .left-panel {
    width: 100%;
    height: 40%;
    max-width: none;
    min-width: auto;
  }
  
  .er-diagram-section {
    height: 60%;
  }
}


/* 建模内容区域 */
.modeling-section {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modeling-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}
.modeling-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  min-height: 0;
}

</style>