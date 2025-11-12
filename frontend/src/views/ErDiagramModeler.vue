<template>
  <div class="er-diagram-modeler">
    <!-- 工具栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="addNewTable" icon="Plus">新建表</el-button>
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
            @click="setActiveTable(table.id)"
          >
            <div class="table-header">
              <span class="table-name">{{ table.name }}</span>
              <div class="table-actions">
                <el-button size="small" type="danger" text @click="removeTable(table.id)" icon="Delete"></el-button>
              </div>
            </div>
            <div class="fields-section">
              <div class="fields-header">
                <span>字段列表</span>
                <el-button size="small" type="primary" text @click="addField(table.id)" icon="Plus">添加字段</el-button>
              </div>
              <div class="fields-list">
                <div 
                  v-for="field in table.fields" 
                  :key="field.id"
                  class="field-item"
                >
                  <div class="field-info">
                    <span class="field-name">{{ field.name }}</span>
                    <span class="field-type">{{ field.type }}</span>
                    <span v-if="field.primaryKey" class="pk-badge">PK</span>
                    <span v-if="field.foreignKey" class="fk-badge">FK</span>
                  </div>
                  <div class="field-actions">
                    <el-button size="mini" text @click="editField(table.id, field.id)" icon="Edit"></el-button>
                    <el-button size="mini" text type="danger" @click="removeField(table.id, field.id)" icon="Delete"></el-button>
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
                  <span v-if="field.primaryKey" class="pk-indicator">🔑</span>
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

    <!-- 添加/编辑字段对话框 -->
    <el-dialog 
      :title="fieldDialog.title" 
      v-model="fieldDialog.visible"
      width="500px"
    >
      <el-form :model="fieldDialog.form" label-width="80px">
        <el-form-item label="字段名">
          <el-input v-model="fieldDialog.form.name" placeholder="请输入字段名"></el-input>
        </el-form-item>
        <el-form-item label="数据类型">
          <el-select v-model="fieldDialog.form.type" placeholder="请选择数据类型">
            <el-option label="INT" value="INT"></el-option>
            <el-option label="VARCHAR" value="VARCHAR"></el-option>
            <el-option label="TEXT" value="TEXT"></el-option>
            <el-option label="DATE" value="DATE"></el-option>
            <el-option label="DATETIME" value="DATETIME"></el-option>
            <el-option label="DECIMAL" value="DECIMAL"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="长度">
          <el-input-number v-model="fieldDialog.form.length" :min="1"></el-input-number>
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="fieldDialog.form.primaryKey">主键</el-checkbox>
          <el-checkbox v-model="fieldDialog.form.foreignKey">外键</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="fieldDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="saveField">保存</el-button>
      </template>
    </el-dialog>

    <!-- 添加表对话框 -->
    <el-dialog 
      title="新建表" 
      v-model="tableDialog.visible"
      width="400px"
    >
      <el-form :model="tableDialog.form" label-width="80px">
        <el-form-item label="表名">
          <el-input v-model="tableDialog.form.name" placeholder="请输入表名"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="tableDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="saveTable">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'

// 表数据
const tables = ref([])
const activeTableId = ref(null)
const draggingTableId = ref(null)
const dragOffset = reactive({ x: 0, y: 0 })

// 对话框状态
const fieldDialog = reactive({
  visible: false,
  title: '添加字段',
  form: {
    name: '',
    type: 'VARCHAR',
    length: 255,
    primaryKey: false,
    foreignKey: false
  },
  tableId: null,
  fieldId: null
})

const tableDialog = reactive({
  visible: false,
  form: {
    name: ''
  }
})

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

// 表操作方法
const addNewTable = () => {
  tableDialog.visible = true
  tableDialog.form.name = ''
}

const saveTable = () => {
  if (tableDialog.form.name.trim()) {
    const newTable = {
      id: Date.now().toString(),
      name: tableDialog.form.name,
      fields: [],
      position: { x: 100 + tables.value.length * 200, y: 100 }
    }
    tables.value.push(newTable)
    setActiveTable(newTable.id)
    tableDialog.visible = false
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

// 字段操作方法
const addField = (tableId) => {
  fieldDialog.visible = true
  fieldDialog.title = '添加字段'
  fieldDialog.tableId = tableId
  fieldDialog.fieldId = null
  fieldDialog.form = {
    name: '',
    type: 'VARCHAR',
    length: 255,
    primaryKey: false,
    foreignKey: false
  }
}

const editField = (tableId, fieldId) => {
  const table = tables.value.find(t => t.id === tableId)
  if (table) {
    const field = table.fields.find(f => f.id === fieldId)
    if (field) {
      fieldDialog.visible = true
      fieldDialog.title = '编辑字段'
      fieldDialog.tableId = tableId
      fieldDialog.fieldId = fieldId
      fieldDialog.form = { ...field }
    }
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

const saveField = () => {
  if (fieldDialog.form.name.trim()) {
    const table = tables.value.find(t => t.id === fieldDialog.tableId)
    if (table) {
      if (fieldDialog.fieldId) {
        // 编辑字段
        const field = table.fields.find(f => f.id === fieldDialog.fieldId)
        if (field) {
          Object.assign(field, fieldDialog.form)
        }
      } else {
        // 添加新字段
        const newField = {
          id: Date.now().toString(),
          ...fieldDialog.form
        }
        table.fields.push(newField)
      }
      fieldDialog.visible = false
    }
  }
}

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
      if (field.length) {
        sql += `(${field.length})`
      }
      if (field.primaryKey) {
        sql += ' PRIMARY KEY'
      }
      if (index < table.fields.length - 1) {
        sql += ','
      }
      sql += '\n'
    })
    sql += ');\n\n'
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

.main-content {
  flex: 1;
  display: flex;
  height: calc(100vh - 200px);
  min-height: 500px;
}

.left-panel {
  width: 350px;
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
  padding: 10px 15px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-name {
  font-weight: 600;
  color: #303133;
}

.fields-section {
  padding: 10px 15px;
}

.fields-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 12px;
  color: #606266;
}

.fields-list {
  max-height: 200px;
  overflow-y: auto;
}

.field-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 0;
  border-bottom: 1px dashed #e4e7ed;
}

.field-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.field-name {
  font-weight: 500;
}

.field-type {
  color: #909399;
  font-size: 11px;
}

.pk-badge, .fk-badge {
  padding: 1px 4px;
  border-radius: 2px;
  font-size: 10px;
  color: white;
}

.pk-badge {
  background: #f56c6c;
}

.fk-badge {
  background: #e6a23c;
}

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

.field-actions {
  opacity: 0;
  transition: opacity 0.3s;
}

.field-item:hover .field-actions {
  opacity: 1;
}
</style>