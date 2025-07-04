<template>
  <el-dialog
    v-model="dialogVisible"
    :title="currentNode?.name + ' 参数配置'"
    width="800px"
    destroy-on-close
    @close="handleClose"
  >
    <div class="config-content">
      <!-- 根据subtype显示不同的配置界面 -->
      <DynamicForm
        ref="dynamicFormRef"
        :ui-schema="currentNode?.ui_schema || []"
        :initial-data="getDatabaseCreateInitialData()"
        :sql-template="currentNode?.sql_template"
        @submit="onDatabaseCreateSubmit"
      />
    </div>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="saveConfig">确定</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import DynamicForm from '../components/DynamicForm.vue'

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  node: {
    type: Object,
    default: null
  },
  databaseList: {
    type: Array,
    default: () => []
  },
  getTablesByDatabase: {
    type: Function,
    required: true
  },
  getColumnsByDatabaseTable: {
    type: Function,
    required: true
  }
})

// Emits
const emit = defineEmits(['update:visible', 'save'])

// 响应式数据
const currentNode = ref(null)
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const dynamicFormRef = ref(null)

// 监听节点变化
watch(() => props.node, (newNode) => {
  if (newNode) {
    currentNode.value = { ...newNode }
    
    // 确保parameters数组存在且至少有一个元素
    if (!currentNode.value.parameters) {
      currentNode.value.parameters = [{
        name: '',
        value: ''
      }]
    }
    
    // 自动兜底：如果没有数据库名，自动选择第一个
    if (!currentNode.value.databaseName && props.databaseList.length > 0) {
      currentNode.value.databaseName = props.databaseList[0]
    }
    // 自动兜底：如果有数据库名但没有表名，且不是创建数据库操作，自动选择第一个表
    if (currentNode.value.databaseName && currentNode.value.subType !== 'database') {
      const tables = props.getTablesByDatabase(currentNode.value.databaseName)
      if (tables.length > 0 && !currentNode.value.tableName) {
        currentNode.value.tableName = tables[0]
      }
    }
    // 动态注入数据库下拉框的options
    if (Array.isArray(currentNode.value.ui_schema)) {
      currentNode.value.ui_schema = currentNode.value.ui_schema.map(item => {
        // 数据库名下拉
        if (item.key === 'databaseName' && item.type === 'select') {
          return {
            ...item,
            options: props.databaseList.map(db => ({ label: db, value: db })),
            onChange: handleDatabaseChange
          }
        }
        // 表名下拉
        if (item.key === 'tableName' && item.type === 'select') {
          const tables = props.getTablesByDatabase(currentNode.value.databaseName)
          return {
            ...item,
            options: tables.map(tb => ({ label: tb, value: tb })),
            onChange: handleTableChange
          }
        }
        // table-editor字段名下拉
        if (item.type === 'table-editor' && Array.isArray(item.columns)) {
          const columns = item.columns.map(col => {
            if (col.key === 'fieldName' && col.type === 'select') {
              // 字段名下拉联动表名 - 初始为空，由watch异步填充
              return {
                ...col,
                options: [] // 初始为空，由watch异步填充
              }
            }
            return col
          })
          return {
            ...item,
            columns
          }
        }
        return item
      })
    }
  }
}, { immediate: true })

// 监听数据库名和表名变化，异步更新字段列表
watch([() => currentNode.value?.databaseName, () => currentNode.value?.tableName], async ([databaseName, tableName]) => {
  console.log('数据库名或表名变化:', { databaseName, tableName })
  if (databaseName && tableName && Array.isArray(currentNode.value?.ui_schema)) {
    try {
      // 异步获取字段列表
      const fieldList = await props.getColumnsByDatabaseTable(databaseName, tableName) || []
      console.log('获取到的字段列表:', fieldList)
      
      // 将字段名数组转换为label-value格式
      const fieldOptions = fieldList.map(field => ({
        label: field,
        value: field
      }))
      
      // 更新ui_schema中的字段名下拉选项
      currentNode.value.ui_schema = currentNode.value.ui_schema.map(item => {
        if (item.type === 'table-editor' && Array.isArray(item.columns)) {
          const columns = item.columns.map(col => {
            if (col.key === 'fieldName' && col.type === 'select') {
              return {
                ...col,
                options: fieldOptions
              }
            }
            return col
          })
          return {
            ...item,
            columns
          }
        }
        return item
      })
    } catch (error) {
      console.error('获取字段列表失败:', error)
    }
  }
}, { immediate: true })

// 处理数据库名变更
function handleDatabaseChange(val) {
  console.log('数据库名变更:', val)
  // 更新表名下拉
  const tables = props.getTablesByDatabase(val)
  const newTableName = tables.length > 0 ? tables[0] : ''
  
  // 更新当前节点
  currentNode.value = {
    ...currentNode.value,
    databaseName: val,
    tableName: newTableName
  }
  
  // 触发ui_schema更新
  if (Array.isArray(currentNode.value.ui_schema)) {
    currentNode.value.ui_schema = [...currentNode.value.ui_schema]
  }
}
// 处理表名变更
function handleTableChange(val) {
  console.log('表名变更:', val)
  // 更新当前节点的表名
  currentNode.value = {
    ...currentNode.value,
    tableName: val
  }
  // 触发ui_schema更新（table-editor字段名下拉联动）
  if (Array.isArray(currentNode.value.ui_schema)) {
    currentNode.value.ui_schema = [...currentNode.value.ui_schema]
  }
}

// 根据subtype获取对应的配置组件
const getConfigComponent = () => {
  if (!currentNode.value) return BasicConfig
  
  const { type, subType } = currentNode.value
  
  // 根据type和subType返回不同的配置组件
  if (type === 'create' && subType === 'database') {
    return DatabaseCreateConfig
  }
  
  switch (type) {
    case 'select':
      return SelectConfig
    case 'create':
      return CreateConfig
    case 'insert':
      return InsertConfig
    case 'update':
      return UpdateConfig
    case 'delete':
      return DeleteConfig
    default:
      return BasicConfig
  }
}

// 数据库切换处理
const onDatabaseChange = async () => {
  console.log('数据库切换:', currentNode.value.databaseName)
  
  // 如果是创建数据库操作，不需要处理表名
  if (currentNode.value.subType === 'database') {
    return
  }
  
  // 清空当前表名
  currentNode.value.tableName = ''
  
  // 如果选择了数据库，加载该数据库的表列表
  if (currentNode.value.databaseName) {
    // 如果不是create类型，自动选择第一个表
    if (currentNode.value.type !== 'create') {
      const tables = props.getTablesByDatabase(currentNode.value.databaseName)
      console.log(`数据库 ${currentNode.value.databaseName} 的表列表:`, tables)
      if (tables.length > 0) {
        currentNode.value.tableName = tables[0]
        console.log('自动选择第一个表:', tables[0])
      }
    }
  }
}

// 更新节点数据
const updateNode = (updatedNode) => {
  currentNode.value = { ...currentNode.value, ...updatedNode }
}

// 保存配置
const saveConfig = () => {
  if (!currentNode.value) return

  // select类型参数校验
  if (currentNode.value.type === 'select') {
    const names = currentNode.value.parameters.map(p => p.name)
    const hasEmpty = names.some(n => !n)
    const hasDuplicate = names.length !== new Set(names).size
    if (hasEmpty) {
      ElMessage.error('列名不能为空，请选择具体字段')
      return
    }
    if (hasDuplicate) {
      ElMessage.error('不能选择重复的列名')
      return
    }
  }
  
  // 创建数据库参数校验
  if (currentNode.value.type === 'create' ) {
    // 只校验databaseName，charset和collation交由DynamicForm的表单校验
    if (!currentNode.value.databaseName) {
      ElMessage.error('数据库名不能为空')
      return
    }
    // 获取表单所有数据和sql
    if (dynamicFormRef.value && dynamicFormRef.value.getFormDataWithSql) {
      const allFormData = dynamicFormRef.value.getFormDataWithSql()
      Object.assign(currentNode.value, allFormData)
      console.log("==",allFormData)
      currentNode.value.parameters = Object.keys(allFormData)
        .filter(key => key !== 'sql')
        .map(key => ({ name: key, value: allFormData[key] }))
    }
  }

  // 触发保存事件
  emit('save', currentNode.value)
  handleClose()
}

// 关闭对话框
const handleClose = () => {
  dialogVisible.value = false
}

function getDatabaseCreateInitialData() {
  const params = currentNode.value?.parameters || []
  const paramMap = Object.fromEntries(params.map(p => [p.name, p.value]))
  const data = {}
  if (Array.isArray(currentNode.value?.ui_schema)) {
    currentNode.value.ui_schema.forEach(item => {
      data[item.key] =
        currentNode.value[item.key] ||
        paramMap[item.key] ||
        (item.type === 'input' && item.key === 'charset' ? 'utf8mb4' : '')
    })
  }
  return data
}

function onDatabaseCreateSubmit(formData) {
  // 直接将formData合并到currentNode.value
  Object.assign(currentNode.value, formData)
  // 生成SQL
  if (currentNode.value.sql_template) {
    let sql = currentNode.value.sql_template
    Object.keys(formData).forEach(key => {
      sql = sql.replace(`{{${key}}}`, formData[key] || '')
    })
    currentNode.value.sql = sql
  } else {
    currentNode.value.sql = `CREATE DATABASE ${formData.databaseName} CHARACTER SET ${formData.charset} COLLATE ${formData.collation};`
  }
  // 同步所有参数到parameters，便于模型图显示
  currentNode.value.parameters = Object.keys(formData)
    .map(key => ({ name: key, value: formData[key] }))
  // 触发保存
  emit('save', currentNode.value)
  handleClose()
}
</script>

<style scoped>
.config-content {
  padding: 20px;
}

.config-section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-header h4 {
  margin: 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
  position: relative;
  padding-left: 12px;
}

.section-header h4::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 16px;
  background: #409EFF;
  border-radius: 2px;
}

.table-name-row .label {
  font-size: 16px;
  color: #303133;
  font-weight: 600;
  white-space: nowrap;
}

.section-content {
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style> 