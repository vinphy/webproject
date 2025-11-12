<template>
  <div class="er-diagram-modeler">
    <!-- 工具栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="addNewTable">
        <img src="@/assets/definition.png" class="table-icon" />
        新建表
      </el-button>
      <el-button @click="generateSQL" icon="Document">生成SQL</el-button>
      <el-button @click="exportImage" icon="Picture">导出图片</el-button>
      <el-button @click="clearAll" icon="Delete">清空</el-button>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧：表结构管理 -->
      <div class="left-panel">
        <div class="panel-header">
          <h5>表结构管理</h5>
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

      <!-- 右侧：ER图显示 -->
      <div class="right-panel">
        <div class="panel-header">
          <h5>ER图预览</h5>
        </div>
        <div class="er-diagram-container">
          <div class="er-canvas">
            <div 
              v-for="table in tables" 
              :key="table.id"
              class="er-table-node"
              :style="{
                left: table.position.x + 'px',
                top: table.position.y + 'px'
              }"
              @mousedown="startDrag(table.id, $event)"
            >
              <div class="er-table-header">
                {{ table.name }}
              </div>
<div class="er-table-fields">
                <div 
                  v-for="field in table.fields" 
                  :key="field.id"
                  class="er-field"
                >
                  <span class="field-name">{{ field.name }}</span>
                  <span class="field-type">{{ field.type }}</span>
                  <span v-if="field.primaryKey" class="pk-indicator">������</span>
                  <span v-if="field.unique" class="unique-indicator">������</span>
                </div>
              </div>
            </div>
            
            <!-- 关系连线 -->
            <svg class="relationship-lines">
              <line 
                v-for="(relation, index) in relationships" 
                :key="index"
                :x1="relation.source.x"
                :y1="relation.source.y"
                :x2="relation.target.x"
                :y2="relation.target.y"
                stroke="#007bff"
                stroke-width="2"
              />
            </svg>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowRight, CircleCheck, Key, Lock, More, Close } from '@element-plus/icons-vue'

// 表数据
const tables = ref([])
const activeTableId = ref(null)
const draggingTableId = ref(null)
const dragOffset = reactive({ x: 0, y: 0 })
const activeAdvancedField = ref(null)
const advancedOptionsPosition = reactive({ top: 0, left: 0 })

// 索引相关变量
const activeIndexTableId = ref(null)
const newIndex = reactive({
  name: '',
  fields: [],
  unique: false
})

// 点击外部关闭高级选项
const handleClickOutside = (event) => {
  const advancedPanel = document.querySelector('.advanced-options-panel')
  if (advancedPanel && !advancedPanel.contains(event.target) && 
      !event.target.closest('.more-options-btn')) {
    closeAdvancedOptions()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  
  // 默认激活第一个表
  if (tables.value.length > 0 && !activeTableId.value) {
    setActiveTable(tables.value[0].id)
  }
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// 表操作方法
const addNewTable = () => {
  const newTable = {
    id: Date.now().toString(),
    name: `table_${tables.value.length + 1}`,
    collapsed: false, // 默认展开状态
    fields: [
      {
        id: Date.now().toString() + '_1',
        name: 'id',
        type: 'INT',
        primaryKey: true,
        nullable: false,
        unique: false,
        autoIncrement: true,
        unsigned: true,
        length: 11,
        defaultValue: ''
      },
      {
        id: Date.now().toString() + '_2',
        name: 'name',
        type: 'VARCHAR',
        primaryKey: false,
        nullable: false,
        unique: false,
        autoIncrement: false,
        unsigned: false,
        length: 255,
        defaultValue: ''
      },
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
}

const updateTableName = (tableId, newName) => {
  const table = tables.value.find(t => t.id === tableId)
  if (table) {
    table.name = newName
  }
}

const removeTable = (tableId) => {
  const index = tables.value.findIndex(table => table.id === tableId)
  if (index !== -1) {
    tables.value.splice(index, 1)
    if (activeTableId.value === tableId) {
      activeTableId.value = tables.value.length > 0 ? tables.value[0].id : null
    }
  }
}

const setActiveTable = (tableId) => {
  activeTableId.value = tableId
}

// 表折叠功能
const toggleTableCollapse = (tableId) => {
  const table = tables.value.find(t => t.id === tableId)
  if (table) {
    table.collapsed = !table.collapsed
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
      defaultValue: ''
    }
    table.fields.push(newField)
}
}
const removeField = (tableId, fieldId) => {
  const table = tables.value.find(t => t.id === tableId)
  if (table) {
    const index = table.fields.findIndex(f => f.id === fieldId)
    if (index !== -1) {
      table.fields.splice(index, 1)
    }
  }
}

const toggleFieldOption = (field, option) => {
  field[option] = !field[option]
  
  // 确保主键和唯一约束的逻辑正确
  if (option === 'primaryKey' && field.primaryKey) {
    field.nullable = false // 主键不能为空
  }
}

const showAdvancedOptions = (field, event) => {
  activeAdvancedField.value = field
  // 根据按钮位置计算悬浮框位置
  const rect = event.target.getBoundingClientRect()
  advancedOptionsPosition.top = rect.bottom + 5
  advancedOptionsPosition.left = rect.left
}

const closeAdvancedOptions = () => {
  activeAdvancedField.value = null
}

// 计算关系连线
const relationships = computed(() => {
  const relations = []
  tables.value.forEach(table => {
    table.fields.forEach(field => {
      if (field.foreignKey) {
        // 简化的关系计算，实际应该根据外键关联的表和字段
        const sourceTable = tables.value.find(t => t.id === table.id)
        const targetTable = tables.value.find(t => t.id !== table.id) // 简化逻辑
        
        if (sourceTable && targetTable) {
          relations.push({
            source: {
              x: sourceTable.position.x + 150,
              y: sourceTable.position.y + 30
            },
            target: {
              x: targetTable.position.x,
              y: targetTable.position.y + 30
            }
          })
        }
      }
    })
  })
  return relations
})

// 拖拽功能
const startDrag = (tableId, event) => {
  draggingTableId.value = tableId
  const table = tables.value.find(t => t.id === tableId)
  if (table) {
    dragOffset.x = event.clientX - table.position.x
    dragOffset.y = event.clientY - table.position.y
    document.addEventListener('mousemove', onDrag)
    document.addEventListener('mouseup', stopDrag)
  }
}

const onDrag = (event) => {
  if (draggingTableId.value) {
    const table = tables.value.find(t => t.id === draggingTableId.value)
    if (table) {
      table.position.x = event.clientX - dragOffset.x
      table.position.y = event.clientY - dragOffset.y
    }
  }
}

const stopDrag = () => {
  draggingTableId.value = null
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
}

// 工具方法
const generateSQL = () => {
  let sql = ''
  tables.value.forEach(table => {
    sql += `CREATE TABLE ${table.name} (\n`
    table.fields.forEach((field, index) => {
      sql += `  ${field.name} ${field.type}`
      if (field.length && field.type !== 'TEXT' && field.type !== 'DATE' && field.type !== 'DATETIME') {
        sql += `(${field.length})`
      }
      if (field.unsigned) {
sql += ' UNSIGNED'
      }
      if (!field.nullable) {
        sql += ' NOT NULL'
      }
if (field.unique) {
        sql += ' UNIQUE'
      }
      if (field.autoIncrement) {
        sql += ' AUTO_INCREMENT'
      }
      if (field.defaultValue) {
        sql += ` DEFAULT ${field.defaultValue}`
      }
      if (field.primaryKey) {
        sql += ' PRIMARY KEY'
      }
      if (index < table.fields.length - 1) {
        sql += ','
      }
      sql += '\n'
    })
    
    // 添加索引定义
    if (table.indices && table.indices.length > 0) {
      table.indices.forEach((index, idx) => {
        const fieldNames = index.fields.map(fieldId => {
          const field = table.fields.find(f => f.id === fieldId)
          return field ? field.name : ''
        }).filter(name => name).join(', ')
        
        if (fieldNames) {
          if (idx === 0 && table.fields.length > 0) {
            sql += ','
          }
          sql += `\n  ${index.unique ? 'UNIQUE ' : ''}INDEX ${index.name} (${fieldNames})`
          if (idx < table.indices.length - 1) {
            sql += ','
          }
        }
      })
    }
    
    sql += '\n);\n\n'
  })
  
  // 这里可以显示SQL或复制到剪贴板
  ElMessage.success('SQL已生成，请查看控制台')
  console.log('生成的SQL:\n', sql)
}

const exportImage = () => {
  ElMessage.info('导出图片功能待实现')
}

const clearAll = () => {
  tables.value = []
  activeTableId.value = null
}
// 索引操作方法
const addIndex = (tableId) => {
  activeIndexTableId.value = tableId
  // 重置新索引数据
  newIndex.name = `index_${Date.now().toString().slice(-4)}`
  newIndex.fields = []
  newIndex.unique = false
}

const confirmAddIndex = (tableId) => {
  const table = tables.value.find(t => t.id === tableId)
  if (table) {
    if (newIndex.fields.length === 0) {
      ElMessage.warning('请至少选择一个字段')
      return
    }
    
    const index = {
      id: Date.now().toString(),
      name: newIndex.name || `index_${table.indices.length + 1}`,
      fields: [...newIndex.fields],
      unique: newIndex.unique
    }
    table.indices.push(index)
    closeIndexAddPanel()
    ElMessage.success('索引添加成功')
  }
}

const removeIndex = (tableId, indexId) => {
  const table = tables.value.find(t => t.id === tableId)
  if (table) {
    const index = table.indices.findIndex(i => i.id === indexId)
    if (index !== -1) {
      table.indices.splice(index, 1)
      ElMessage.success('索引删除成功')
    }
  }
}

const closeIndexAddPanel = () => {
  activeIndexTableId.value = null
  newIndex.name = ''
  newIndex.fields = []
  newIndex.unique = false
}
</script>

<style scoped>
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

/* 移除下拉框的滚动条 */
/* :deep(.el-select-dropdown) {
  max-height: 200px;
  overflow-y: auto;
}

:deep(.el-select-dropdown::-webkit-scrollbar) {
  width: 6px;
}

:deep(.el-select-dropdown::-webkit-scrollbar-track) {
  background: #f1f1f1;
  border-radius: 3px;
}

:deep(.el-select-dropdown::-webkit-scrollbar-thumb) {
  background: #c1c1c1;
  border-radius: 3px;
}

:deep(.el-select-dropdown::-webkit-scrollbar-thumb:hover) {
  background: #a8a8a8;
} */
</style>