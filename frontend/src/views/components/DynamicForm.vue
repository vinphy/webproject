<template>
    <el-form 
      :model="formData" 
      label-width="120px"
      ref="formRef"
      @submit.prevent="submitForm"
    >
      <template v-for="(item, index) in uiSchema" :key="index">
        <!-- 普通输入框 -->
        <el-form-item 
          v-if="item.type === 'input'" 
          :label="item.label" 
          :prop="item.key"
          :rules="item.required ? [{ required: true, message: `${item.label}不能为空` }] : []"
        >
          <el-input v-model="formData[item.key]" :placeholder="`请输入${item.label}`" />
        </el-form-item>
        
        <!-- 下拉选择框 -->
        <el-form-item 
          v-else-if="item.type === 'select'" 
          :label="item.label" 
          :prop="item.key"
          :rules="item.required ? [{ required: true, message: `${item.label}不能为空` }] : []"
        >
          <el-select 
            v-model="formData[item.key]" 
            :placeholder="`请选择${item.label}`"
            @change="(val) => handleSelectChange(item, val)"
          >
            <el-option 
              v-for="opt in item.options || []" 
              :key="opt.value" 
              :label="opt.label" 
              :value="opt.value" 
            />
          </el-select>
        </el-form-item>
        
        <!-- 表格编辑器 -->
        <el-form-item 
          v-if="item.type === 'table-editor'" 
          :label="item.label" 
          :prop="item.key"
        >
          <TableEditor 
            v-model="formData[item.key]" 
            :columns="item.columns"
            :available-tables="availableTables"
            :available-columns-map="availableColumnsMap"
          />
        </el-form-item>
      </template>
    </el-form>
    <div class="sql-preview">
        <h4>SQL预览</h4>
        <el-input 
          type="textarea" 
          :rows="3" 
          :model-value="buildSQL()" 
          readonly 
        />
      </div>
  </template>
  
  <script setup>
  import { ref, watch, computed, defineExpose } from 'vue'
  import { ElMessage } from 'element-plus'
  import TableEditor from './TableEditor.vue'
  import Handlebars from 'handlebars'
  
  const props = defineProps({
    uiSchema: {
      type: Array,
      required: true
    },
    initialData: {
      type: Object,
      default: () => ({})
    },
    sqlTemplate: {
      type: String,
      default: ''
    },
    // 新增外键下拉数据
    getTablesByDatabase: {
      type: Function,
      default: () => async (dbName) => []
    },
    getColumnsByDatabaseTable: {
      type: Function,
      default: () => async (dbName, tableName) => []
    }
  })
  
  const emit = defineEmits(['submit', 'update'])
  
  const formRef = ref(null)
  const formData = ref({})
  
  // 新增外键下拉数据
  const availableTables = ref([])
  const availableColumnsMap = ref({})

  // 初始化表单数据
  function buildFormData(schema, initial) {
    const data = {}
    schema.forEach(item => {
      // 优先级：initial > defaultValue > 空
      data[item.key] =
        initial[item.key] !== undefined && initial[item.key] !== ''
          ? initial[item.key]
          : (item.defaultValue !== undefined ? item.defaultValue : (item.type === 'table-editor' ? [] : ''))
    })
    return data
  }
  
  watch([
    () => props.uiSchema,
    () => props.initialData
  ], ([newSchema, newInitial]) => {
    formData.value = buildFormData(newSchema, newInitial)
    if (formRef.value) {
      formRef.value.clearValidate && formRef.value.clearValidate()
    }
  }, { immediate: true })

  // 新增外键下拉数据
  watch([
    () => formData.value.databaseName,
    () => props.uiSchema
  ], async ([databaseName, uiSchema]) => {
    if (!databaseName) return
    // 获取所有表
    if (typeof window.getTablesByDatabase === 'function') {
      availableTables.value = window.getTablesByDatabase(databaseName)
    } else if (props.getTablesByDatabase) {
      availableTables.value = props.getTablesByDatabase(databaseName)
    } else {
      availableTables.value = []
    }
    // 获取所有表的字段
    const map = {}
    for (const table of availableTables.value) {
      if (typeof window.getColumnsByDatabaseTable === 'function') {
        map[table] = await window.getColumnsByDatabaseTable(databaseName, table)
      } else if (props.getColumnsByDatabaseTable) {
        map[table] = await props.getColumnsByDatabaseTable(databaseName, table)
      } else {
        map[table] = []
      }
    }
    availableColumnsMap.value = map
  }, { immediate: true })
  
  // 提交表单（保留submit事件，兼容老用法）
  const submitForm = async () => {
    try {
      await formRef.value.validate()
      emit('submit', formData.value)
    } catch (error) {
      ElMessage.error('请检查表单填写是否正确')
    }
  }

  // 生成SQL
  function buildSQL() {
    // 1. 优先用模板
    if (props.sqlTemplate) {
      try {
        const template = Handlebars.compile(props.sqlTemplate)
        return template(formData.value)
      } catch (e) {
        return 'SQL模板渲染出错'
      }
    }

    // 2. 自动拼接
    const tableName = formData.value.tableName || 'table_name'
    const fields = formData.value.fields || []

    if (!fields.length) return '-- 请添加字段'

    // 字段定义
    const fieldLines = []
    const pkFields = []
    const uniqueFields = []
    const foreignKeys = []

    fields.forEach(f => {
      const name = f.fieldName || f.name || f['字段名']
      const type = f.fieldType || f.type || f['类型']
      const length = f.length ? `(${f.length})` : ''
      const constraint = f.constraint || {}

      let line = `\`${name}\` ${type}${length}`

      // 约束
      if (constraint.nullable === false || constraint.notNull) line += ' NOT NULL'
      if (constraint.nullable === true) line += ' NULL'
      if (constraint.unique) uniqueFields.push(name)
      if (constraint.autoIncrement) line += ' AUTO_INCREMENT'
      if (constraint.default !== undefined && constraint.default !== '') line += ` DEFAULT '${constraint.default}'`
      fieldLines.push(line)

      // 主键
      if (constraint.primary) pkFields.push(name)

      // 外键
      if (constraint.hasForeignKey && constraint.foreignKey && constraint.foreignKey.table && constraint.foreignKey.column) {
        foreignKeys.push(
          `FOREIGN KEY (\`${name}\`) REFERENCES \`${constraint.foreignKey.table}\`(\`${constraint.foreignKey.column}\`)`
        )
      }
    })

    // 表级约束
    if (pkFields.length) fieldLines.push(`PRIMARY KEY (${pkFields.map(n => `\`${n}\``).join(', ')})`)
    if (uniqueFields.length) fieldLines.push(`UNIQUE (${uniqueFields.map(n => `\`${n}\``).join(', ')})`)
    if (foreignKeys.length) fieldLines.push(...foreignKeys)

    // 拼接完整SQL
    return `CREATE TABLE \`${tableName}\` (\n  ${fieldLines.join(',\n  ')}\n);`
  }

  // 暴露方法供父组件获取表单数据
  function getFormDataWithSql() {
    return {
      ...formData.value,
      sql: buildSQL()
    }
  }
  
  // 处理下拉框变化事件
  function handleSelectChange(item, value) {
    console.log('下拉框变化:', item.key, value)
    // 更新表单数据
    formData.value[item.key] = value
    // 如果有onChange回调，执行它
    if (item.onChange && typeof item.onChange === 'function') {
      item.onChange(value)
    }
  }
  
  defineExpose({ getFormDataWithSql })
  </script>

<style scoped>
.sql-preview {
  margin-top: 30px;
  padding: 18px 20px 16px 20px;
  background: #f8f9fa;
  border-radius: 6px;
  box-shadow: 0 2px 8px 0 rgba(0,0,0,0.04);
  border: 1px solid #e4e7ed;
}
.sql-preview h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 15px;
  font-weight: 600;
}
.sql-preview .el-input__wrapper {
  background: #fff;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
}
</style>