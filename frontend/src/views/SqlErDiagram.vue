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
            <!-- <div class="modeling-header">
              
            </div> -->
            <div class="modeling-actions">
              <el-button type="primary" @click="addNewTable">
                <img src="@/assets/definition.png" class="table-icon" />
                新建表
              </el-button>
            </div>  
            <div class="table-list">             
              <div 
                v-for="table in tables" 
                :key="table.id"
                class="table-card"
                :class="{ active: activeTableId === table.id }"
              >
              
                <!-- 表标题栏 - 添加折叠功能 -->
                <div class="table-header" @click.stop="toggleTableCollapse(table.id)">
                  <div class="table-title-area">
                    <el-icon class="collapse-icon" :class="{ rotated: table.collapsed }">
                      <ArrowRight />
                    </el-icon>
                    <el-input 
                      v-model="table.name" 
                      size="small" 
                      placeholder="表名"
                      @click.stop
                      @input="updateTableName(table.id, $event)"
                    />
                  </div>
                  <div class="table-actions" @click.stop>
                    <el-button size="small" type="danger" text @click="removeTable(table.id)">删除</el-button>
                  </div>
                </div>
                
                <!-- 字段区域 - 根据折叠状态显示 -->
                <div class="fields-section" v-show="!table.collapsed">
                  <div class="fields-header">
                    <span>字段列表</span>
                    <div class="field-buttons">
                      <el-button size="small" type="primary" text @click="addField(table.id)" icon="Plus">添加字段</el-button>
                      <el-button size="small" type="success" text @click="addIndex(table.id)" icon="Plus">添加索引</el-button>
                    </div>
                  </div>
                  <div class="fields-list">
                    <!-- 可编辑的字段行 -->
                    <div 
                      v-for="field in table.fields" 
                      :key="field.id"
                      class="field-item editable-field"
                    >
                      <div class="field-editor">
                        <el-input 
                          v-model="field.name" 
                          size="small" 
                          placeholder="字段名"
                          class="field-name-input"
                        />
                        <el-select 
                          v-model="field.type" 
                          size="small" 
                          placeholder="类型"
                          class="field-type-select"
                        >
                          <el-option label="INT" value="INT"></el-option>
                          <el-option label="VARCHAR" value="VARCHAR"></el-option>
                          <el-option label="TEXT" value="TEXT"></el-option>
                          <el-option label="DATE" value="DATE"></el-option>
                          <el-option label="DATETIME" value="DATETIME"></el-option>
                          <el-option label="DECIMAL" value="DECIMAL"></el-option>
                          <el-option label="BOOLEAN" value="BOOLEAN"></el-option>
                        </el-select>
                        <div class="field-options">
                          <!-- 使用图标按钮替代文字按钮 -->
                          <el-button 
                            size="mini" 
                            :type="field.nullable ? 'primary' : 'default'" 
                            text 
                            @click.stop="toggleFieldOption(field, 'nullable')"
                            title="允许为空"
                          >
                            <el-icon><CircleCheck /></el-icon>
                          </el-button>
                          <el-button 
                            size="mini" 
                            :type="field.primaryKey ? 'primary' : 'default'" 
                            text 
                            @click.stop="toggleFieldOption(field, 'primaryKey')"
                            title="主键"
                          >
                            <el-icon><Key /></el-icon>
                          </el-button>
<el-button 
                            size="mini" 
                            :type="field.unique ? 'primary' : 'default'" 
                            text 
                            @click.stop="toggleFieldOption(field, 'unique')"
                            title="唯一约束"
                          >
                            <el-icon><Lock /></el-icon>
                          </el-button>
                          <el-button 
                            size="mini" 
                            type="text" 
                            @click.stop="showAdvancedOptions(field, $event)"
                            title="更多选项"
                            class="more-options-btn"
                          >
                            <el-icon><More /></el-icon>
                          </el-button>
                          <el-button 
                            size="mini" 
                            type="danger" 
                            text 
                            @click.stop="removeField(table.id, field.id)"
                            title="删除字段"
                            class="delete-field-btn"
                          >
                            <el-icon><Close /></el-icon>
                          </el-button>
                        </div>
                      </div>
                    </div>
                    
                    <!-- 索引列表 -->
                    <div v-if="table.indices && table.indices.length > 0" class="indices-section">
                      <div class="indices-header">
                        <span>索引列表</span>
                      </div>
                      <div v-for="index in table.indices" :key="index.id" class="index-item">
                        <div class="index-editor">
                          <el-input 
                            v-model="index.name" 
                            size="small" 
                            placeholder="索引名称"
                            class="index-name-input"
                          />
                          <el-select 
                            v-model="index.fields" 
                            size="small" 
                            multiple
                            placeholder="选择字段"
                            class="index-fields-select"
                            :popper-append-to-body="false"
                          >
                            <el-option 
                              v-for="field in table.fields" 
                              :key="field.id"
                              :label="field.name" 
                              :value="field.id"
                            ></el-option>
                          </el-select>
                          <el-checkbox 
                            v-model="index.unique" 
                            class="index-unique-checkbox"
                            title="唯一索引"
                          ></el-checkbox>
                          <el-button 
                            size="mini" 
                            type="danger" 
                            text 
                            @click.stop="removeIndex(table.id, index.id)"
                            title="删除索引"
                            class="delete-index-btn"
                          >
                            <el-icon><Close /></el-icon>
                          </el-button>
                        </div>
                      </div>
                    </div>
                    
                    <!-- 索引添加框 -->
                    <div v-if="activeIndexTableId === table.id" class="index-add-panel">
                      <div class="index-add-header">
                        <span>添加索引</span>
                        <el-button size="mini" text @click="closeIndexAddPanel" icon="Close"></el-button>
                      </div>
                      <div class="index-add-content">
                        <div class="index-add-item">
                          <label>索引名称:</label>
                          <el-input v-model="newIndex.name" size="small" placeholder="请输入索引名称"></el-input>
                        </div>
                        <div class="index-add-item">
                          <label>选择字段:</label>
                          <el-select 
                            v-model="newIndex.fields" 
                            size="small" 
                            multiple
                            placeholder="请选择字段"
                            class="index-add-select"
                            :popper-append-to-body="false"
                          >
                            <el-option 
                              v-for="field in table.fields" 
                              :key="field.id"
                              :label="field.name" 
                              :value="field.id"
                            ></el-option>
                          </el-select>
                        </div>
                        <div class="index-add-item">
                          <el-checkbox v-model="newIndex.unique">唯一索引</el-checkbox>
                        </div>
                        <div class="index-add-buttons">
                          <el-button size="small" type="primary" @click="confirmAddIndex(table.id)">确认添加</el-button>
                          <el-button size="small" @click="closeIndexAddPanel">取消</el-button>
                        </div>
                      </div>
                    </div>
                    
                    <!-- 高级选项悬浮框 -->
                    <div 
                      v-if="activeAdvancedField" 
                      class="advanced-options-panel"
                      :style="{ top: advancedOptionsPosition.top + 'px', left: advancedOptionsPosition.left + 'px' }"
                    >
                      <div class="advanced-header">
                        <span>高级选项</span>
                        <el-button size="mini" text @click="closeAdvancedOptions" icon="Close"></el-button>
                      </div>
                      <div class="advanced-content">
                        <div class="option-item">
                          <label>默认值:</label>
                          <el-input v-model="activeAdvancedField.defaultValue" size="small" placeholder="默认值"></el-input>
                        </div>
                        <div class="option-item">
                          <el-checkbox v-model="activeAdvancedField.autoIncrement">自增</el-checkbox>
                        </div>
                        <div class="option-item">
                          <el-checkbox v-model="activeAdvancedField.unsigned">无符号</el-checkbox>
                        </div>
                        <div class="option-item">
                          <label>长度:</label>
                          <el-input-number 
                            v-model="activeAdvancedField.length" 
                            size="small" 
                            :min="1" 
                            :max="65535"
                          ></el-input-number> 
                        </div>
                      </div>
                    </div>
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
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
// import { Search, Delete, Upload, Grid, Download } from '@element-plus/icons-vue'
import axios from 'axios'
import { Search, Delete,Upload, Grid,Download, ArrowRight, CircleCheck, Key, Lock, More, Close ,Plus } from '@element-plus/icons-vue'

export default {
  name: 'SqlErDiagram',
  components: {
    Search,
    Delete,
    Upload,
    Grid,
    Download,
    ArrowRight,
    CircleCheck,
    Key,
    Lock,
    More,
    Close,
    Plus
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
    // 添加图形建模相关的响应式数据
    const tables = ref([])
    const activeTableId = ref(null)
    const activeIndexTableId = ref(null)
    const activeAdvancedField = ref(null)
    const advancedOptionsPosition = ref({ top: 0, left: 0 })

    const newIndex = ref({
      name: '',
      fields: [],
      unique: false
    })

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

    // 表折叠功能
    const toggleTableCollapse = (tableId) => {
      const table = tables.value.find(t => t.id === tableId)
      if (table) {
        table.collapsed = !table.collapsed
      }
    }

    const setActiveTable = (tableId) => {
      activeTableId.value = tableId
    }
    const removeTable = (tableId) => {
      const index = tables.value.findIndex(t => t.id === tableId)
      if (index !== -1) {
        tables.value.splice(index, 1)
        if (activeTableId.value === tableId) {
          activeTableId.value = null
        }

        // 新增：同步更新ER图
        if (activeTab.value === 'modeling') {
          convertModelingTablesToErNodes()
        }
      }
    }

    const updateTableName = (tableId, newName) => {
      const table = tables.value.find(t => t.id === tableId)
      if (table) {
        table.name = newName

        // 新增：同步更新ER图
        if (activeTab.value === 'modeling') {
          convertModelingTablesToErNodes()
        }
      }
    }
    // 字段操作方法
    const addField = (tableId) => {
      const table = tables.value.find(t => t.id === tableId)
      if (table) {
        const newField = {
          id: Date.now().toString(),
          name: `field_${table.fields.length + 1}`,
          type: 'VARCHAR',
          primaryKey: false,
          nullable: true,
          unique: false,
          autoIncrement: false,
          unsigned: false,
          length: 255,
          defaultValue: null
        }
        table.fields.push(newField)

        // 新增：同步更新ER图
        if (activeTab.value === 'modeling') {
          convertModelingTablesToErNodes()
        }
      }
    }

    const removeField = (tableId, fieldId) => {
      const table = tables.value.find(t => t.id === tableId)
      if (table) {
        const index = table.fields.findIndex(f => f.id === fieldId)
        if (index !== -1) {
          table.fields.splice(index, 1)

          // 新增：同步更新ER图
          if (activeTab.value === 'modeling') {
            convertModelingTablesToErNodes()
          }
        }
      }
    }

    const toggleFieldOption = (field, option) => {
      field[option] = !field[option]

      // 新增：同步更新ER图
      if (activeTab.value === 'modeling') {
        convertModelingTablesToErNodes()
      }
    }

    // 索引操作方法
    const addIndex = (tableId) => {
      activeIndexTableId.value = tableId
      newIndex.value = {
        name: `index_${tables.value.find(t => t.id === tableId)?.indices?.length || 0 + 1}`,
        fields: [],
        unique: false
      }
    }

    const confirmAddIndex = (tableId) => {
      const table = tables.value.find(t => t.id === tableId)
      if (table && newIndex.value.name && newIndex.value.fields.length > 0) {
        const index = {
          id: Date.now().toString(),
          name: newIndex.value.name,
          fields: newIndex.value.fields,
          unique: newIndex.value.unique
        }
        if (!table.indices) table.indices = []
        table.indices.push(index)
        closeIndexAddPanel()

        // 新增：同步更新ER图
        if (activeTab.value === 'modeling') {
          convertModelingTablesToErNodes()
        }
      } else {
        ElMessage.warning('请填写索引名称并选择至少一个字段')
      }
    }

    const closeIndexAddPanel = () => {
      activeIndexTableId.value = null
      newIndex.value = {
        name: '',
        fields: [],
        unique: false
      }
    }

    const removeIndex = (tableId, indexId) => {
      const table = tables.value.find(t => t.id === tableId)
      if (table && table.indices) {
        const index = table.indices.findIndex(i => i.id === indexId)
        if (index !== -1) {
          table.indices.splice(index, 1)

           // 新增：同步更新ER图
          if (activeTab.value === 'modeling') {
            convertModelingTablesToErNodes()
          }
        }
      }
    }

    // 高级选项方法
    const showAdvancedOptions = (field, event) => {
      activeAdvancedField.value = field
      advancedOptionsPosition.value = {
        top: event.clientY,
        left: event.clientX
      }
      
      // 修复：使用持续监听器而不是一次性监听器
      nextTick(() => {
        document.addEventListener('click', handleClickOutside)
      })
    }

    const closeAdvancedOptions = () => {
      activeAdvancedField.value = null
      // 修复：移除点击外部关闭监听器
      document.removeEventListener('click', handleClickOutside)
    }

    // 修复：点击外部关闭高级选项面板
    const handleClickOutside = (event) => {
      const advancedPanel = document.querySelector('.advanced-options-panel')
      if (advancedPanel && !advancedPanel.contains(event.target)) {
        closeAdvancedOptions()
      }
    }

    // 表折叠功能
    // const toggleTableCollapse = (tableId) => {
    //   const table = tables.value.find(t => t.id === tableId)
    //   if (table) {
    //     table.collapsed = !table.collapsed
    //   }
    // }

    // 新增：将图形建模表转换为ER图节点
    const convertModelingTablesToErNodes = () => {
      tableNodes.value = []
      connections.value = []
      let nodeId = 1

      // 转换图形建模表为ER图节点
      tables.value.forEach((table, index) => {
        // 提取主键字段
        const primaryKeyFields = table.fields.filter(field => field.primaryKey).map(field => field.name)
        
        // 转换字段格式
        const columns = table.fields.map(field => ({
          name: field.name,
          type: field.type,
          nullable: field.nullable,
          defaultValue: field.defaultValue,
          autoIncrement: field.autoIncrement,
          unsigned: field.unsigned,
          length: field.length
        }))

        const node = {
          id: `table-${nodeId}`,
          name: table.name,
          columns: columns,
          primaryKey: primaryKeyFields,
          foreignKeys: [], // 图形建模暂时不支持外键关系
          x: table.position?.x || 100 + (index % 3) * 350,
          y: table.position?.y || 100 + Math.floor(index / 3) * 300
        }
        tableNodes.value.push(node)
        nodeId++
      })
    }

    // 新增：监听activeTab变化，切换到图形建模时自动生成ER图
    watch(activeTab, (newTab) => {
      if (newTab === 'modeling' && tables.value.length > 0) {
        convertModelingTablesToErNodes()
      }
    })

    // 表操作方法
    const addNewTable = () => {
      const newTable = {
        id: Date.now().toString(),
        name: `table_${tables.value.length + 1}`,
        collapsed: false, // 默认展开状态
        fields: [
          {
            id: Date.now().toString() + '_3',
            name: 'created_at',
            type: 'DATETIME',
            primaryKey: false,
            nullable: false,
            unique: false,
            autoIncrement: false,
            unsigned: false,
            length: null,
            defaultValue: 'CURRENT_TIMESTAMP'
          }
        ],
        indices: [], // 添加索引数组
        position: { x: 100 + tables.value.length * 200, y: 100 }
      }
      tables.value.push(newTable)
      setActiveTable(newTable.id)

      // 新增：同步更新ER图
      if (activeTab.value === 'modeling') {
        convertModelingTablesToErNodes()
      }
    }

    

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
       // 新增的图形建模数据
      tables,
      activeTableId,
      activeIndexTableId,
      activeAdvancedField,
      advancedOptionsPosition,
      newIndex,
      
      // 新增的方法
      addNewTable,
      setActiveTable,
      removeTable,
      updateTableName,
      addField,
      removeField,
      toggleFieldOption,
      addIndex,
      confirmAddIndex,
      closeIndexAddPanel,
      removeIndex,
      showAdvancedOptions,
      closeAdvancedOptions,
      toggleTableCollapse
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
  justify-content: flex-end;  /*让内容靠右对齐 */
  margin-top: 10px;
  margin-right: 10px;
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
/* .fields-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
} */
 /* .field-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border: 1px solid #f0f0f0;
  border-radius: 4px;
  background: #fafafa;
} */
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
.table-icon {
  width: 16px;
  height: 16px;
  margin-right: 5px;
}
/* 表格卡片样式 */
/* .table-card {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  margin: 10px;
  background: white;
  transition: all 0.3s;
} */
 .table-card.active {
  border-color: #409EFF;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}
.table-card:hover {
  border-color: #409EFF;
}
/* 表头样式 */
.table-header {
  padding: 12px 16px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}
.table-title-area {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}
.collapse-icon {
  transition: transform 0.3s;
}
.collapse-icon.rotated {
  transform: rotate(90deg);
}
/* 字段区域样式 */
.fields-section {
  padding: 0;
}
/* .fields-header {
  padding: 12px 16px;
  background: #fafafa;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
} */
/* .field-buttons {
  display: flex;
  gap: 8px;
} */
/* .fields-list {
  padding: 16px;
} */
/* 字段编辑样式 */
/* .field-item {
  margin-bottom: 8px;
} */
.field-editor {
  display: flex;
  gap: 8px;
  align-items: center;
}
.field-name-input {
  flex: 2;
}
.field-type-select {
  flex: 1;
}
.field-options {
  display: flex;
  gap: 4px;
}
/* 索引样式 */
.indices-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed #e4e7ed;
}
.indices-header {
  margin-bottom: 12px;
  font-weight: 500;
  color: #606266;
}
.index-item {
  margin-bottom: 8px;
}
.index-editor {
  display: flex;
  gap: 8px;
  align-items: center;
}
.index-name-input {
  flex: 1;
}
.index-fields-select {
  flex: 2;
}
.index-unique-checkbox {
  margin-left: 8px;
}
/* 添加索引面板样式 */
.index-add-panel {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  margin-top: 12px;
  background: #f8f9fa;
}
/* .index-add-header {
  padding: 8px 12px;
  background: #e6f7ff;
  border-bottom: 1px solid #bae7ff;
  display: flex;
  justify-content: space-between;
  align-items: center;
} */
/* .index-add-content {
  padding: 12px;
} */
/* .index-add-item {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
} */
.index-add-item label {
  min-width: 80px;
  font-size: 14px;
  color: #606266;
}
.index-add-select {
  flex: 1;
}
.index-add-buttons {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}
/* 高级选项面板样式 */
.advanced-options-panel {
  position: fixed;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  min-width: 200px;
}
.advanced-header {
  padding: 8px 12px;
  /* background: #f5f7fa; */
  /* border-bottom: 1px solid #e4e7ed; */
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.advanced-content {
  padding: 12px;
}
.option-item {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.option-item label {
  min-width: 60px;
  font-size: 14px;
  color: #606266;
}
/**----- */
.er-diagram-modeler {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.toolbar {
  padding: 10px 20px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  gap: 10px;
}

.table-icon {
  width: 16px;
  height: 16px;
  margin-right: 5px;
}

.main-content {
  flex: 1;
  display: flex;
  height: calc(100vh - 200px);
  min-height: 500px;
}

.left-panel {
  width: 400px;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
}

.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 15px 20px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
}

.panel-header h5 {
  margin: 0;
  color: #303133;
}

.table-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.table-card {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s;
}

.table-card:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.table-card.active {
  border-color: #409eff;
  background: #f0f9ff;
}

.table-header {
  padding: 8px 12px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  user-select: none;
}
.table-title-area {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
}

.collapse-icon {
  transition: transform 0.3s;
  font-size: 12px;
  color: #909399;
}

.collapse-icon.rotated {
  transform: rotate(90deg);
}

.table-actions {
  flex-shrink: 0;
}

.table-actions .el-button {
  padding: 4px 8px;
  font-size: 12px;
}
.fields-section {
  padding: 8px 12px;
}

.fields-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  font-size: 12px;
  color: #606266;
}

.fields-list {
max-height: 300px;
  overflow-y: auto;
}

.editable-field {
  display: flex;
  align-items: center;
  padding: 4px 0;
  border-bottom: 1px dashed #e4e7ed;
  gap: 6px;
}

.field-editor {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
min-width: 0;
  overflow: hidden;
}

.field-name-input {
  width: 90px;
  min-width: 90px;
  flex-shrink: 0;
}

.field-type-select {
  width: 85px;
  min-width: 85px;
  flex-shrink: 0;
}
.field-options {
  display: flex;
  gap: 1px;
  flex-shrink: 0;
  margin-left: auto;
  flex-wrap: nowrap;
}

.field-options .el-button {
  padding: 1px 3px;
  min-width: 20px;
  height: 18px;
  flex-shrink: 0;
}

.field-options .el-icon {
  font-size: 10px;
}
.field-options {
  display: flex;
  gap: 2px;
  flex-shrink: 0;
  margin-left: auto;
}

.field-options .el-button {
  padding: 2px 4px;
  min-width: 24px;
  height: 20px;
  flex-shrink: 0;
}

.field-options .el-icon {
  font-size: 12px;
}

.more-options-btn,
.delete-field-btn {
  font-weight: bold;
}

.delete-field-btn .el-icon {
  color: #f56c6c;
}

.advanced-options-panel {
  position: fixed;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 10px;
  z-index: 1000;
  min-width: 200px;
}

.advanced-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-size: 12px;
  font-weight: 600;
}

.advanced-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.option-item label {
  font-size: 12px;
  min-width: 60px;
}

.unique-indicator {
  font-size: 10px;
  color: #67c23a;
}

/* 其他样式保持不变 */
.er-diagram-container {
  flex: 1;
  position: relative;
  overflow: auto;
  background: #f8f9fa;
}

.er-canvas {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 400px;
}

.er-table-node {
  position: absolute;
  width: 200px;
  background: white;
  border: 2px solid #409eff;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: move;
  user-select: none;
}

.er-table-header {
  background: #409eff;
  color: white;
  padding: 8px 12px;
  font-weight: 600;
  border-radius: 4px 4px 0 0;
}

.er-table-fields {
  padding: 8px 0;
}

.er-field {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 12px;
  font-size: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.er-field:last-child {
  border-bottom: none;
}

.pk-indicator {
  font-size: 10px;
  color: #c23a3a;
}

.relationship-lines {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

/* 字段按钮组样式 */
.field-buttons {
  display: flex;
  gap: 8px;
}

/* 索引相关样式 */
.indices-section {
  margin-top: 16px;
  border-top: 1px solid #e0e0e0;
  padding-top: 12px;
}

.indices-header {
  font-weight: 500;
  margin-bottom: 10px;
  font-size: 12px;
  color: #666;
}

.index-item {
  margin-bottom: 0px;
  padding: 0px;
  background: #f8f9fa;
  border-radius: 4px;
}

.index-editor {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  min-width: 0;
}

.index-name-input {
  width: 100px;
  min-width: 100px;
  flex-shrink: 0;
}

.index-fields-select {
  flex: 1;
  min-width: 150px;
  max-width: 200px;
}

.index-fields-select :deep(.el-select__tags) {
  max-width: 100%;
  overflow: hidden;
  padding-left: 0;
  margin-left: 0;
}

.index-fields-select :deep(.el-tag) {
  max-width: 70px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin: 1px 4px 1px 0;
}

.index-fields-select :deep(.el-select .el-input__inner) {
  padding-left: 8px;
}

.index-add-select {
  flex: 1;
  min-width: 0;
}

.index-add-select :deep(.el-select__tags) {
  max-width: 100%;
  overflow: hidden;
  padding-left: 0;
  margin-left: 0;
}

.index-add-select :deep(.el-tag) {
  max-width: 70px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin: 1px 4px 1px 0;
}

.index-add-select :deep(.el-select .el-input__inner) {
  padding-left: 8px;
}

.index-unique-checkbox {
  flex-shrink: 0;
  margin-left: 8px;
}

.index-unique-checkbox .el-checkbox__label {
  display: inline;
}

.delete-index-btn {
  flex-shrink: 0;
  margin-left: auto;
}

/* 索引添加面板样式 */
.index-add-panel {
  margin-top: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 12px;
  background: #f8f9fa;
  width: 100%;
  box-sizing: border-box;
}

.index-add-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-weight: 600;
  font-size: 14px;
}

.index-add-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.index-add-item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.index-add-item label {
  width: 80px;
  font-size: 12px;
  color: #666;
  flex-shrink: 0;
  text-align: right;
}

.index-add-item .el-input,
.index-add-item .el-select {
  flex: 1;
  min-width: 0;
}

.index-add-item .el-checkbox {
  margin-left: 88px; /* 对齐到标签后面 */
}

.index-add-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #e0e0e0;
}
</style>