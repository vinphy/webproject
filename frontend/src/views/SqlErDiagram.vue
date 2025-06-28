<template>
  <div class="sql-er-diagram">
    <div class="header">
      <h2>SQL实体关系图生成器</h2>
      <p>导入SQL文件或输入SQL语句，自动生成数据库实体关系图</p>
    </div>

    <div class="main-container">
      <!-- 左侧：SQL输入区域 -->
      <div class="sql-input-section">
        <div class="input-header">
          <h3>SQL输入</h3>
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

        <!-- SQL文本输入 -->
        <div class="sql-textarea">
          <el-input
            v-model="sqlText"
            type="textarea"
            :rows="15"
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

        <!-- Vue Flow 图表容器 -->
        <div class="diagram-container" ref="diagramContainer">
          <VueFlow
            v-model="elements"
            :default-viewport="{ zoom: 1 }"
            :min-zoom="0.2"
            :max-zoom="4"
            :node-types="nodeTypes"
            :edge-types="edgeTypes"
            @connect="onConnect"
            @node-drag-stop="onNodeDragStop"
            @pane-click="onPaneClick"
            class="vue-flow-diagram"
          >
            <template #node-custom="nodeProps">
              <TableNode 
                :data="nodeProps.data" 
                :selected="nodeProps.selected"
                @node-click="onNodeClick"
              />
            </template>
            
            <Background pattern-color="#aaa" gap="20" />
            <MiniMap />
            <Controls />
          </VueFlow>
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
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { VueFlow, useVueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { MiniMap } from '@vue-flow/minimap'
import { Controls } from '@vue-flow/controls'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/minimap/dist/style.css'
import '@vue-flow/controls/dist/style.css'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Delete, Upload, Grid, Download } from '@element-plus/icons-vue'
import TableNode from '../components/TableNode.vue'
import axios from 'axios'

export default {
  name: 'SqlErDiagram',
  components: {
    VueFlow,
    Background,
    MiniMap,
    Controls,
    TableNode,
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

    // Vue Flow 相关
    const elements = ref([])
    const nodeTypes = {
      custom: TableNode
    }
    const edgeTypes = {}

    // 计算属性
    const hasNodes = computed(() => elements.value.some(el => el.type === 'custom'))

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
        const response = await axios.post('/api/sql/parse', {
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
    }

    const selectTable = (tableName) => {
      selectedTable.value = tableName
      selectedTableData.value = parsedTables.value.find(t => t.name === tableName)
      tableDetailVisible.value = true
    }

    const generateErDiagram = () => {
      const nodes = []
      const edges = []
      let nodeId = 1
      let edgeId = 1

      // 生成节点
      parsedTables.value.forEach((table, index) => {
        const node = {
          id: `table-${nodeId}`,
          type: 'custom',
          position: { x: 100 + index * 300, y: 100 + index * 200 },
          data: {
            tableName: table.name,
            columns: table.columns,
            primaryKey: table.primaryKey,
            foreignKeys: table.foreignKeys || []
          }
        }
        nodes.push(node)
        nodeId++
      })

      // 生成关系边
      parsedTables.value.forEach(table => {
        if (table.foreignKeys) {
          table.foreignKeys.forEach(fk => {
            const sourceNode = nodes.find(n => n.data.tableName === table.name)
            const targetNode = nodes.find(n => n.data.tableName === fk.referencedTable)
            
            if (sourceNode && targetNode) {
              const edge = {
                id: `edge-${edgeId}`,
                source: sourceNode.id,
                target: targetNode.id,
                type: 'smoothstep',
                animated: true,
                style: { stroke: '#409EFF', strokeWidth: 2 },
                label: `${fk.column} → ${fk.referencedColumn}`,
                labelStyle: { fill: '#409EFF', fontWeight: 600 }
              }
              edges.push(edge)
              edgeId++
            }
          })
        }
      })

      elements.value = [...nodes, ...edges]
    }

    const autoLayout = () => {
      // 简单的自动布局算法
      const nodes = elements.value.filter(el => el.type === 'custom')
      const cols = Math.ceil(Math.sqrt(nodes.length))
      
      nodes.forEach((node, index) => {
        const row = Math.floor(index / cols)
        const col = index % cols
        node.position = {
          x: 100 + col * 350,
          y: 100 + row * 250
        }
      })
    }

    const exportDiagram = () => {
      // 导出图表为图片
      ElMessage.info('导出功能开发中...')
    }

    const clearDiagram = () => {
      elements.value = []
    }

    const onConnect = (params) => {
      // 处理连接
      console.log('连接:', params)
    }

    const onNodeDragStop = (event, node) => {
      // 节点拖拽结束
      console.log('节点拖拽:', node)
    }

    const onPaneClick = () => {
      // 画布点击
    }

    const onNodeClick = (nodeId) => {
      // 节点点击
      console.log('节点点击:', nodeId)
    }

    return {
      sqlText,
      parsing,
      parsedTables,
      selectedTable,
      tableDetailVisible,
      selectedTableData,
      uploadRef,
      diagramContainer,
      elements,
      nodeTypes,
      edgeTypes,
      hasNodes,
      handleFileChange,
      handleSqlInput,
      parseSql,
      clearSql,
      selectTable,
      autoLayout,
      exportDiagram,
      clearDiagram,
      onConnect,
      onNodeDragStop,
      onPaneClick,
      onNodeClick
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
}

.header {
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
}

.main-container {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.sql-input-section {
  width: 400px;
  background: white;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.input-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.input-header h3 {
  margin: 0;
  color: #303133;
}

.input-actions {
  display: flex;
  gap: 10px;
}

.file-upload {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.sql-textarea {
  flex: 1;
  padding: 20px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.sql-textarea .el-textarea {
  flex: 1;
}

.parse-result {
  padding: 20px;
  border-top: 1px solid #e4e7ed;
  max-height: 300px;
  overflow-y: auto;
}

.parse-result h4 {
  margin: 0 0 15px 0;
  color: #303133;
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
}

.diagram-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
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
}

.vue-flow-diagram {
  width: 100%;
  height: 100%;
}

.table-detail h4 {
  margin: 0 0 20px 0;
  color: #303133;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .sql-input-section {
    width: 350px;
  }
}

@media (max-width: 768px) {
  .main-container {
    flex-direction: column;
  }
  
  .sql-input-section {
    width: 100%;
    height: 300px;
  }
}
</style> 