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
        :initial-data="getInitialData()"
        :sql-template="currentNode?.sql_template"
        :get-tables-by-database="props.getTablesByDatabase"
        :get-columns-by-database-table="props.getColumnsByDatabaseTable"
        @submit="onSubmit"
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
  },
  getViewsByDatabase: {
    type: Function,
    default: () => []
  },
  getIndexesByDatabaseTable: {
    type: Function,
    default: () => []
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
watch(() => props.node, async (newNode) => {
  console.log('节点变化:', newNode)
  if (newNode) {
    currentNode.value = { ...newNode }
    console.log('currentNode:', currentNode.value)
    console.log('currentNode.ui_schema:', currentNode.value.ui_schema)
    
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
      console.log('处理ui_schema:', currentNode.value.ui_schema)
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
        // 视图名称下拉
        if (item.key === 'viewName' && item.type === 'select') {
          return {
            ...item,
            options: [], // 初始为空，由watch异步填充
            onChange: handleViewChange
          }
        }
        // 索引名称下拉
        if (item.key === 'oldIndexName' && item.type === 'select') {
          return {
            ...item,
            options: [], // 初始为空，由watch异步填充
            onChange: handleOldIndexNameChange
          }
        }
        // 删除操作中的索引名称下拉
        if (item.key === 'indexName' && item.type === 'select') {
          return {
            ...item,
            options: [], // 初始为空，由watch异步填充
            onChange: handleIndexNameChange
          }
        }
        // 关联表名下拉
        if (item.key === 'joinTableName' && item.type === 'select') {
          const tables = props.getTablesByDatabase(currentNode.value.databaseName)
          return {
            ...item,
            options: tables.map(tb => ({ label: tb, value: tb })),
            onChange: handleJoinTableNameChange
          }
        }
        // 字段选择下拉（用于创建视图）
        if (item.key === 'columns' && item.type === 'select' && item.multiple) {
          return {
            ...item,
            options: [], // 初始为空，由watch异步填充
            onChange: handleColumnsChange
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
      console.log('处理后的ui_schema:', currentNode.value.ui_schema)
      
      // 当节点被打开时，尝试获取字段列表、视图列表和索引列表
          if (currentNode.value.databaseName) {
            try {
              // 异步获取视图列表
              const views = props.getViewsByDatabase(currentNode.value.databaseName) || []
              console.log('获取到的视图列表:', views)
              
              // 将视图名数组转换为label-value格式
              const viewOptions = views.map(view => ({
                label: view,
                value: view
              }))
              
              // 更新ui_schema中的视图名称下拉选项
              currentNode.value.ui_schema = currentNode.value.ui_schema.map(item => {
                if (item.key === 'viewName' && item.type === 'select') {
                  return {
                    ...item,
                    options: viewOptions
                  }
                }
                return item
              })
            } catch (error) {
              console.error('获取视图列表失败:', error)
            }
          }
          
          // 当节点被打开时，尝试获取索引列表
          if (currentNode.value.databaseName && currentNode.value.tableName) {
            try {
              // 异步获取索引列表
              const indexes = props.getIndexesByDatabaseTable(currentNode.value.databaseName, currentNode.value.tableName) || []
              console.log('获取到的索引列表:', indexes)
              
              // 将索引名数组转换为label-value格式
              const indexOptions = indexes.map(index => ({
                label: index,
                value: index
              }))
              
              // 更新ui_schema中的索引名称下拉选项
              currentNode.value.ui_schema = currentNode.value.ui_schema.map(item => {
                if (item.key === 'oldIndexName' && item.type === 'select') {
                  return {
                    ...item,
                    options: indexOptions
                  }
                }
                // 删除操作中的索引名称下拉
                if (item.key === 'indexName' && item.type === 'select') {
                  return {
                    ...item,
                    options: indexOptions
                  }
                }
                // 处理是否主键索引复选框
                if (item.key === 'isPrimaryKey' && item.type === 'checkbox') {
                  return {
                    ...item,
                    onChange: handleIsPrimaryKeyChange
                  }
                }
                return item
              })
            } catch (error) {
              console.error('获取索引列表失败:', error)
            }
          }
          
          // 当节点被打开时，尝试获取字段列表
          if (currentNode.value.databaseName && currentNode.value.tableName) {
            try {
              // 异步获取主表字段列表
              const mainFieldList = await props.getColumnsByDatabaseTable(currentNode.value.databaseName, currentNode.value.tableName) || []
              console.log('获取到的主表字段列表:', mainFieldList)
              
              // 生成带表名的主表字段选项
              const tableName = currentNode.value.tableName
              const mainFieldOptions = mainFieldList.map(field => ({
                label: `${tableName}.${field}`,
                value: `${tableName}.${field}`
              }))
              
              // 初始化所有字段选项为主表字段选项
              let allFieldOptions = [...mainFieldOptions]
              
              // 如果有关联表，也添加关联表的字段
              if (currentNode.value.joinTableName) {
                const joinFieldList = await props.getColumnsByDatabaseTable(currentNode.value.databaseName, currentNode.value.joinTableName) || []
                console.log('获取到的关联表字段列表:', joinFieldList)
                
                // 生成带表名的关联表字段选项
                const joinTableName = currentNode.value.joinTableName
                const joinFieldOptions = joinFieldList.map(field => ({
                  label: `${joinTableName}.${field}`,
                  value: `${joinTableName}.${field}`
                }))
                
                // 合并主表和关联表字段选项
                allFieldOptions = [...mainFieldOptions, ...joinFieldOptions]
              }
              
              // 更新ui_schema中的字段名下拉选项
              currentNode.value.ui_schema = currentNode.value.ui_schema.map(item => {
                // 处理table-editor中的字段名（包括查询条件表格和关联条件）
                if (item.type === 'table-editor' && Array.isArray(item.columns)) {
                  const columns = item.columns.map(col => {
                    if (col.key === 'mainField' && col.type === 'select') {
                      return {
                        ...col,
                        options: mainFieldOptions
                      }
                    }
                    if ((col.key === 'fieldName' || col.key === 'field') && col.type === 'select') {
                      return {
                        ...col,
                        options: allFieldOptions
                      }
                    }
                    return col
                  })
                  return {
                    ...item,
                    columns
                  }
                }
                // 处理创建视图中的字段选择
                if (item.key === 'columns' && item.type === 'select' && item.multiple) {
                  return {
                    ...item,
                    options: mainFieldOptions
                  }
                }
                // 处理查询字段的下拉多选
                if (item.key === 'fields' && item.type === 'select' && item.multiple) {
                  return {
                    ...item,
                    options: allFieldOptions
                  }
                }
                // 处理修改数据表中的字段名下拉框
                if (item.key === 'fieldName' && item.type === 'select') {
                  return {
                    ...item,
                    options: mainFieldOptions
                  }
                }
                return item
              })
            } catch (error) {
              console.error('获取字段列表失败:', error)
            }
          }
    } else {
      console.log('ui_schema不是数组:', currentNode.value.ui_schema)
    }
  }
}, { immediate: true })

// 监听数据库名和表名变化，异步更新字段列表
watch([() => currentNode.value?.databaseName, () => currentNode.value?.tableName], async ([databaseName, tableName]) => {
  console.log('数据库名或表名变化:', { databaseName, tableName })
  if (databaseName && tableName && Array.isArray(currentNode.value?.ui_schema)) {
    try {
      // 异步获取主表字段列表
      const mainFieldList = await props.getColumnsByDatabaseTable(databaseName, tableName) || []
      console.log('获取到的主表字段列表:', mainFieldList)
      
      // 生成带表名的主表字段选项
      const mainFieldOptions = mainFieldList.map(field => ({
        label: `${tableName}.${field}`,
        value: `${tableName}.${field}`
      }))
      
      // 初始化所有字段选项为主表字段选项
      let allFieldOptions = [...mainFieldOptions]
      
      // 如果有关联表，也添加关联表的字段
      if (currentNode.value.joinTableName) {
        const joinFieldList = await props.getColumnsByDatabaseTable(databaseName, currentNode.value.joinTableName) || []
        console.log('获取到的关联表字段列表:', joinFieldList)
        
        // 生成带表名的关联表字段选项
        const joinTableName = currentNode.value.joinTableName
        const joinFieldOptions = joinFieldList.map(field => ({
          label: `${joinTableName}.${field}`,
          value: `${joinTableName}.${field}`
        }))
        
        // 合并主表和关联表字段选项
        allFieldOptions = [...mainFieldOptions, ...joinFieldOptions]
      }
      
      // 更新ui_schema中的字段名下拉选项
      currentNode.value.ui_schema = currentNode.value.ui_schema.map(item => {
        // 处理table-editor中的字段名（包括查询条件表格和关联条件）
        if (item.type === 'table-editor' && Array.isArray(item.columns)) {
          const columns = item.columns.map(col => {
            if (col.key === 'mainField' && col.type === 'select') {
              return {
                ...col,
                options: mainFieldOptions
              }
            }
            if ((col.key === 'fieldName' || col.key === 'field') && col.type === 'select') {
              return {
                ...col,
                options: allFieldOptions
              }
            }
            return col
          })
          return {
            ...item,
            columns
          }
        }
        // 处理创建视图中的字段选择
        if (item.key === 'columns' && item.type === 'select' && item.multiple) {
          return {
            ...item,
            options: mainFieldOptions
          }
        }
        // 处理查询字段的下拉多选
        if (item.key === 'fields' && item.type === 'select' && item.multiple) {
          return {
            ...item,
            options: allFieldOptions
          }
        }
        // 处理修改数据表中的字段名下拉框
        if (item.key === 'fieldName' && item.type === 'select') {
          return {
            ...item,
            options: mainFieldOptions
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
  
  // 更新当前节点，重置视图名
  currentNode.value = {
    ...currentNode.value,
    databaseName: val,
    tableName: [], // 重置表名为空数组
    viewName: [], // 重置视图名为空数组
    columns: [] // 清空字段选择
  }
  
  // 触发ui_schema更新
  if (Array.isArray(currentNode.value.ui_schema)) {
    // 更新表名下拉选项
      currentNode.value.ui_schema = currentNode.value.ui_schema.map(item => {
        if (item.key === 'tableName' && item.type === 'select') {
          return {
            ...item,
            options: tables.map(tb => ({ label: tb, value: tb }))
          }
        }
        // 更新视图名下拉选项
        if (item.key === 'viewName' && item.type === 'select') {
          const views = props.getViewsByDatabase(val) || []
          return {
            ...item,
            options: views.map(view => ({ label: view, value: view }))
          }
        }
        // 清空字段选择下拉选项
        if (item.key === 'columns' && item.type === 'select' && item.multiple) {
          return {
            ...item,
            options: []
          }
        }
        return item
      })
  }
}
// 处理表名变更
async function handleTableChange(val) {
  console.log('表名变更:', val)
  // 更新当前节点的表名
  currentNode.value = {
    ...currentNode.value,
    tableName: val,
    oldIndexName: '' // 重置旧索引名
  }
  // 触发ui_schema更新（table-editor字段名下拉联动）
  if (Array.isArray(currentNode.value.ui_schema)) {
    // 如果是多选，取第一个表来获取字段列表
    const firstTableName = Array.isArray(val) && val.length > 0 ? val[0] : val
    
    // 更新字段选择下拉框的选项
    try {
      if (firstTableName) {
        const fields = await props.getColumnsByDatabaseTable(currentNode.value.databaseName, firstTableName) || []
        console.log('获取到的字段列表:', fields)
        
        // 生成带表名的字段选项
        const tableName = firstTableName
        const fieldOptions = fields.map(field => ({
          label: `${tableName}.${field}`,
          value: `${tableName}.${field}`
        }))
        
        // 先处理查询字段和条件字段的选项
        let joinFieldOptions = []
        if (currentNode.value.joinTableName) {
          const joinFields = await props.getColumnsByDatabaseTable(currentNode.value.databaseName, currentNode.value.joinTableName) || []
          const joinTableName = currentNode.value.joinTableName
          joinFieldOptions = joinFields.map(field => ({
            label: `${joinTableName}.${field}`,
            value: `${joinTableName}.${field}`
          }))
        }
        
        // 合并主表和关联表字段选项
        const allFieldOptions = [...fieldOptions, ...joinFieldOptions]
        
        // 更新ui_schema
        currentNode.value.ui_schema = currentNode.value.ui_schema.map(item => {
          if (item.key === 'columns' && item.type === 'select' && item.multiple) {
            return {
              ...item,
              options: fieldOptions
            }
          }
          // 处理查询字段的下拉多选
          if (item.key === 'fields' && item.type === 'select' && item.multiple) {
            return {
              ...item,
              options: allFieldOptions
            }
          }
          // 处理关联条件的主表字段下拉
          if (item.key === 'joinConditions' && item.type === 'table-editor' && Array.isArray(item.columns)) {
            const columns = item.columns.map(col => {
              if (col.key === 'mainField' && col.type === 'select') {
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
          // 处理条件的字段名下拉
          if (item.key === 'conditions' && item.type === 'table-editor' && Array.isArray(item.columns)) {
            const columns = item.columns.map(col => {
              if (col.key === 'fieldName' && col.type === 'select') {
                return {
                  ...col,
                  options: allFieldOptions
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
    } catch (error) {
      console.error('获取字段列表失败:', error)
    }
    
    // 更新索引名称下拉框的选项
    try {
      if (firstTableName) {
        const indexes = props.getIndexesByDatabaseTable(currentNode.value.databaseName, firstTableName) || []
        console.log('获取到的索引列表:', indexes)
        currentNode.value.ui_schema = currentNode.value.ui_schema.map(item => {
          if (item.key === 'oldIndexName' && item.type === 'select') {
            return {
              ...item,
              options: indexes.map(index => ({ label: index, value: index }))
            }
          }
          // 删除操作中的索引名称下拉
          if (item.key === 'indexName' && item.type === 'select') {
            return {
              ...item,
              options: indexes.map(index => ({ label: index, value: index }))
            }
          }
          return item
        })
      }
    } catch (error) {
      console.error('获取索引列表失败:', error)
    }
  }
}

// 处理字段选择变更
function handleColumnsChange(val) {
  console.log('字段选择变更:', val)
  console.log('变更前的currentNode:', currentNode.value)
  // 更新当前节点的字段选择，保留其他字段
  currentNode.value = {
    ...currentNode.value,
    columns: val
  }
  console.log('变更后的currentNode:', currentNode.value)
}

// 处理视图名称变更
function handleViewChange(val) {
  console.log('视图名称变更:', val)
  // 更新当前节点的视图名
  currentNode.value = {
    ...currentNode.value,
    viewName: val
  }
}

// 处理旧索引名称变更
function handleOldIndexNameChange(val) {
  console.log('旧索引名称变更:', val)
  // 更新当前节点的旧索引名
  currentNode.value = {
    ...currentNode.value,
    oldIndexName: val
  }
}

// 处理索引名称变更
function handleIndexNameChange(val) {
  console.log('索引名称变更:', val)
  // 更新当前节点的索引名
  currentNode.value = {
    ...currentNode.value,
    indexName: val
  }
}

// 处理是否主键索引变更
function handleIsPrimaryKeyChange(val) {
  console.log('是否主键索引变更:', val)
  // 更新当前节点的是否主键索引状态
  currentNode.value = {
    ...currentNode.value,
    isPrimaryKey: val
  }
}

// 处理关联表名变更
async function handleJoinTableNameChange(val) {
  console.log('关联表名变更:', val)
  // 更新当前节点的关联表名
  currentNode.value = {
    ...currentNode.value,
    joinTableName: val
  }
  // 触发ui_schema更新（关联表字段下拉联动）
  if (Array.isArray(currentNode.value.ui_schema) && currentNode.value.databaseName && val) {
    try {
      const fields = await props.getColumnsByDatabaseTable(currentNode.value.databaseName, val) || []
      console.log('获取到的关联表字段列表:', fields)
      
      // 生成带表名的字段选项
      const joinTableName = val
      const joinFieldOptions = fields.map(field => ({
        label: `${joinTableName}.${field}`,
        value: `${joinTableName}.${field}`
      }))
      
      // 生成关联表字段的下拉选项（用于关联条件）
      const joinFieldOptionsForCondition = fields.map(field => ({
        label: `${joinTableName}.${field}`,
        value: `${joinTableName}.${field}`
      }))
      
      // 先获取主表字段选项
      let mainFieldOptions = []
      if (currentNode.value.tableName) {
        const mainTableName = Array.isArray(currentNode.value.tableName) ? currentNode.value.tableName[0] : currentNode.value.tableName
        const mainFields = await props.getColumnsByDatabaseTable(currentNode.value.databaseName, mainTableName) || []
        mainFieldOptions = mainFields.map(field => ({
          label: `${mainTableName}.${field}`,
          value: `${mainTableName}.${field}`
        }))
      }
      
      // 合并主表和关联表字段选项
      const allFieldOptions = [...mainFieldOptions, ...joinFieldOptions]
      
      // 更新ui_schema
      currentNode.value.ui_schema = currentNode.value.ui_schema.map(item => {
        // 处理关联条件的关联表字段下拉
        if (item.key === 'joinConditions' && item.type === 'table-editor' && Array.isArray(item.columns)) {
          const columns = item.columns.map(col => {
            if (col.key === 'joinField' && col.type === 'select') {
              return {
                ...col,
                options: joinFieldOptionsForCondition
              }
            }
            return col
          })
          return {
            ...item,
            columns
          }
        }
        // 处理查询字段的下拉多选（添加关联表字段）
        if (item.key === 'fields' && item.type === 'select' && item.multiple) {
          return {
            ...item,
            options: allFieldOptions
          }
        }
        // 处理条件的字段名下拉（添加关联表字段）
        if (item.key === 'conditions' && item.type === 'table-editor' && Array.isArray(item.columns)) {
          const columns = item.columns.map(col => {
            if (col.key === 'fieldName' && col.type === 'select') {
              return {
                ...col,
                options: allFieldOptions
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
      console.error('获取关联表字段列表失败:', error)
    }
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

    // 调用DynamicForm组件的方法获取表单数据和SQL
    if (dynamicFormRef.value && dynamicFormRef.value.getFormDataWithSql) {
      const allFormData = dynamicFormRef.value.getFormDataWithSql()
      Object.assign(currentNode.value, allFormData)
      console.log("获取到的表单数据:", allFormData)
      
      // 更新parameters数组，便于模型图显示
      currentNode.value.parameters = Object.keys(allFormData)
        .filter(key => key !== 'sql')
        .map(key => ({ name: key, value: allFormData[key] }))
    }

    // 特殊校验：数据库名不能为空
    if (currentNode.value.databaseName === '' || currentNode.value.databaseName === undefined) {
      ElMessage.error('数据库名不能为空')
      return
    }

    // 特殊校验：表名不能为空（除了创建数据库操作）
    if (currentNode.value.subType !== 'database' && (currentNode.value.tableName === '' || currentNode.value.tableName === undefined || (Array.isArray(currentNode.value.tableName) && currentNode.value.tableName.length === 0))) {
      ElMessage.error('表名不能为空')
      return
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

function getInitialData() {
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

function onSubmit(formData) {
  // 直接将formData合并到currentNode.value
  Object.assign(currentNode.value, formData)
  // 生成SQL
  if (currentNode.value.sql_template) {
    let sql = currentNode.value.sql_template
    
    console.log('当前节点信息:', {
      type: currentNode.value.type,
      subType: currentNode.value.subType,
      isPrimaryKey: currentNode.value.isPrimaryKey,
      formData: formData
    })
    
    // 处理删除索引的特殊情况
    if (currentNode.value.type === 'delete' && currentNode.value.subType === 'index') {
      // 获取表名（如果是数组，取第一个）
      const tableName = Array.isArray(currentNode.value.tableName) ? currentNode.value.tableName[0] : currentNode.value.tableName
      
      console.log('删除索引操作:', {
        isPrimaryKey: currentNode.value.isPrimaryKey,
        databaseName: currentNode.value.databaseName,
        tableName: tableName,
        indexName: currentNode.value.indexName,
        ifExists: currentNode.value.ifExists
      })
      
      if (currentNode.value.isPrimaryKey) {
        // 生成删除主键索引的SQL
        sql = `${currentNode.value.databaseName ? `USE \`${currentNode.value.databaseName}\`;\n` : ''}ALTER TABLE \`${tableName}\` DROP PRIMARY KEY;`
        console.log('生成的主键索引删除SQL:', sql)
      } else {
        // 生成删除普通索引的SQL
        sql = `${currentNode.value.databaseName ? `USE \`${currentNode.value.databaseName}\`;\n` : ''}ALTER TABLE \`${tableName}\` DROP INDEX${currentNode.value.ifExists ? ' IF EXISTS' : ''} \`${currentNode.value.indexName}\`;`
        console.log('生成的普通索引删除SQL:', sql)
      }
    } else {
      // 处理其他情况
      Object.keys(formData).forEach(key => {
        sql = sql.replace(`{{${key}}}`, formData[key] || '')
      })
    }
    
    currentNode.value.sql = sql
    console.log('最终生成的SQL:', currentNode.value.sql)
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