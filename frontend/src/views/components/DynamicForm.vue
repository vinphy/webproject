<template>
    <div class="form-container">
    <el-form 
      :model="formData" 
      label-width="150px"
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
          :rules="item.required ? item.multiple ? [{ required: true, type: 'array', min: 1, message: `${item.label}不能为空` }] : [{ required: true, message: `${item.label}不能为空` }] : []"
          v-if="!(item.key === 'sortFields' || item.key === 'sortOrder') || (item.key === 'sortFields' || item.key === 'sortOrder') && formData.groupBy && formData.groupBy.length > 0"
        >
          <el-select 
            v-model="formData[item.key]" 
            :placeholder="`请选择${item.label}`"
            :multiple="item.multiple"
            :allow-create="item['allow-create'] && formData.operation === 'add'"
            :filterable="item['allow-create']"
            @change="(val) => handleSelectChange(item, val)"
          >
            <!-- 优先使用配置的options -->
            <template v-if="item.options && item.options.length > 0">
              <el-option 
                v-for="opt in item.options" 
                :key="opt.value" 
                :label="opt.label" 
                :value="opt.value" 
              />
            </template>
            <!-- 否则尝试从availableColumnsMap中获取字段列表 -->
            <template v-else-if="(item.key === 'sortFields' || item.key === 'groupBy') && formData.databaseName && formData.tableName && availableColumnsMap[formData.tableName]">
              <el-option 
                v-for="column in availableColumnsMap[formData.tableName]" 
                :key="column" 
                :label="column" 
                :value="column"
              />
            </template>
            <!-- 否则尝试从availableColumnsMap中获取字段列表（通用情况） -->
            <template v-else-if="(item.key === 'fieldName' || item.key === 'columns' || item.key === 'subqueryField' || item.key === 'targetField') && formData.databaseName && formData.tableName && availableColumnsMap[formData.tableName]">
              <el-option 
                v-for="column in availableColumnsMap[formData.tableName]" 
                :key="column" 
                :label="column" 
                :value="column"
              />
            </template>
          </el-select>
        </el-form-item>
        
        <!-- 表格编辑器 -->
        <el-form-item 
          v-else-if="item.type === 'table-editor' " 
          :label="item.label" 
          :prop="item.key"
          :rules="item.required ? [{ required: true, type: 'array', min: 1, message: `${item.label}不能为空` }] : []"
        >
          <TableEditor 
            v-model="formData[item.key] " 
            :columns="item.columns"
            :available-tables="availableTables"
            :available-columns-map="availableColumnsMap"
            :show-constraint="item.key !== 'conditions' && item.key !== 'fields' && item.key !== 'caseConditions' && item.key !== 'havingConditions' && item.key !== 'whereConditions' && item.key !== 'orderFields'"
          />
        </el-form-item>
        
        <!-- 文本域 -->
        <el-form-item 
          v-else-if="item.type === 'textarea'" 
          :label="item.label" 
          :prop="item.key"
          :rules="item.required ? [{ required: true, message: `${item.label}不能为空` }] : []"
          v-if="!(item.key === 'tableSubquery') || (item.key === 'tableSubquery' && formData.isSubquery)"
        >
          <el-input
            v-model="formData[item.key]"
            type="textarea"
            :rows="5"
            :placeholder="item.placeholder"
          />
        </el-form-item>
        
        <!-- 复选框 -->
        <el-form-item 
          v-else-if="item.type === 'checkbox'" 
          :label="item.label" 
          :prop="item.key"
        >
          <el-checkbox v-model="formData[item.key]">{{ item.label }}</el-checkbox>
        </el-form-item>
      </template>
    </el-form>
    <div class="sql-preview">
        <h4>SQL预览</h4>
        <el-input 
          type="textarea" 
          :rows="3" 
          :model-value="sqlPreview" 
          readonly 
        />
      </div>
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
  
  // 计算SQL语句
  const sqlPreview = computed(() => {
    return buildSQL()
  })

  // 初始化表单数据
  function buildFormData(schema, initial) {
    const data = { ...formData.value } // 保留原有数据
    schema.forEach(item => {
      // 优先级：initial > defaultValue > 空
      if (initial[item.key] !== undefined && initial[item.key] !== '') {
        data[item.key] = initial[item.key]
      } else if (item.defaultValue !== undefined) {
        data[item.key] = item.defaultValue
      } else if (data[item.key] === undefined) {
        if (item.type === 'table-editor') {
          data[item.key] = []
        } else if (item.type === 'select' && item.multiple) {
          data[item.key] = []
        } else {
          data[item.key] = ''
        }
      }
      // 否则保留原有值
    })
    return data
  }
  
  watch([
    () => props.uiSchema,
    () => props.initialData
  ], ([newSchema, newInitial]) => {
    console.log('DynamicForm - uiSchema变化:', newSchema)
    console.log('DynamicForm - initialData变化:', newInitial)
    formData.value = buildFormData(newSchema, newInitial)
    console.log('DynamicForm - formData:', formData.value)
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

  // 监听columns变化，确保SQL预览更新
  watch(
    () => formData.value.columns,
    (newColumns) => {
      console.log('columns变化:', newColumns)
      // 触发SQL预览更新
      console.log('SQL预览:', sqlPreview.value)
    },
    { deep: true }
  )
  
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
    console.log('生成SQL时的formData:', formData.value)
    console.log('使用的SQL模板:', props.sqlTemplate)
    
    // 检查是否是创建表
    const isCreateTable = props.sqlTemplate && props.sqlTemplate.includes('CREATE TABLE')
    
    // 如果是创建表，使用自动拼接方式，确保约束条件正确添加
    if (isCreateTable) {
      const databaseName = formData.value.databaseName || ''
      const tableName = formData.value.tableName || 'table_name'
      const fields = formData.value.columns || formData.value.fields || []
      
      console.log('使用的字段数据:', fields)

      if (!fields.length) return '-- 请添加字段'

      // 字段定义
      const fieldLines = []
      const pkFields = []
      const uniqueFields = []
      const foreignKeys = []

      fields.forEach(f => {
        const name = f.fieldName || f.name || f['字段名']
        const type = f.dataType || f.fieldType || f.type || f['类型']
        const length = f.length ? `(${f.length})` : ''

        let line = `\`${name}\` ${type}${length}`

        // 约束
        if (f.notNull) line += ' NOT NULL'
        if (f.primaryKey) {
          line += ' PRIMARY KEY'
          pkFields.push(name)
        }
        if (f.autoIncrement) line += ' AUTO_INCREMENT'
        if (f.unique) line += ' UNIQUE'
        if (f.default) line += ` DEFAULT ${f.default}`
        
        // 注释
        if (f.comment) {
          line += ` COMMENT '${f.comment}'`
        }
        
        // 外键约束
        if (f.hasForeignKey && f.foreignKey && f.foreignKey.table && f.foreignKey.column) {
          foreignKeys.push(`FOREIGN KEY (\`${name}\`) REFERENCES \`${f.foreignKey.table}\`(\`${f.foreignKey.column}\`)`)
        }
        
        fieldLines.push(line)
      })

      // 表级约束
      if (pkFields.length && !fields.some(f => f.primaryKey)) {
        fieldLines.push(`PRIMARY KEY (${pkFields.map(n => `\`${n}\``).join(', ')})`)
      }
      if (uniqueFields.length) fieldLines.push(`UNIQUE (${uniqueFields.map(n => `\`${n}\``).join(', ')})`)
      if (foreignKeys.length) fieldLines.push(...foreignKeys)

      // 拼接完整SQL
      let sql = ''
      if (databaseName) {
        sql += `USE \`${databaseName}\`;\n`
      }
      sql += `CREATE TABLE ${databaseName ? `\`${databaseName}\`.` : ''}\`${tableName}\` (\n  ${fieldLines.join(',\n  ')}\n);`
      console.log('创建表生成的SQL:', sql)
      return sql
    }
    
    // 其他情况使用模板
    if (props.sqlTemplate) {
      try {
        // 为创建索引添加isPrimaryKey计算
        const templateData = {
          ...formData.value,
          // 只有在创建索引时才根据indexType设置isPrimaryKey，删除索引时保持用户的选择
          isPrimaryKey: formData.value.isPrimaryKey !== undefined ? formData.value.isPrimaryKey : (formData.value.indexType === 'PRIMARY KEY'),
          // 为修改数据表添加操作类型的布尔值
          isAdd: formData.value.operation === 'add',
          isModify: formData.value.operation === 'modify',
          isDrop: formData.value.operation === 'drop',
          // 处理批量插入的valueRows，转换为数组
          valueRows: formData.value.valueRows ? formData.value.valueRows.split('\n').filter(row => row.trim()) : [],
          // 处理批量新增的records，转换为数组
          records: formData.value.records ? formData.value.records.split('\n').filter(row => row.trim()) : [],
          // 确保sortFields是数组
          sortFields: Array.isArray(formData.value.sortFields) ? formData.value.sortFields : []
        }
        // 注册Handlebars助手函数
        Handlebars.registerHelper('isString', function(value) {
          return typeof value === 'string';
        });
        
        // 替换模板中的条件判断语法
        let templateStr = props.sqlTemplate
        // 替换 operation == 'add' 为 isAdd
        templateStr = templateStr.replace(/\{\{#if operation == 'add'}}/g, '{{#if isAdd}}')
        templateStr = templateStr.replace(/\{\{\/if}}/g, '{{/if}}')
        // 替换 operation == 'modify' 为 isModify
        templateStr = templateStr.replace(/\{\{#if operation == 'modify'}}/g, '{{#if isModify}}')
        // 替换 operation == 'drop' 为 isDrop
        templateStr = templateStr.replace(/\{\{#if operation == 'drop'}}/g, '{{#if isDrop}}')
        
        const template = Handlebars.compile(templateStr)
        const sql = template(templateData)
        console.log('使用模板生成的SQL:', sql)
        return sql
      } catch (e) {
        console.error('SQL模板渲染错误:', e)
        return 'SQL模板渲染出错'
      }
    }

    // 默认情况
    const databaseName = formData.value.databaseName || ''
    if (databaseName) {
      return `CREATE DATABASE \`${databaseName}\`;`
    }
    return '-- 请配置参数'
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
.form-container {
  width: 100%;
  padding: 0;
  box-sizing: border-box;
}

.el-form {
  width: 100%;
}

.el-form-item {
  margin-bottom: 20px;
}

.el-form-item__content {
  flex: 1;
}

/* 文本域样式 */
.el-textarea {
  width: 100%;
}

/* 表子查询文本域 */
.el-form-item__content .el-textarea {
  width: 100%;
  min-height: 120px;
}

.sql-preview {
  margin-top: 30px;
  padding: 18px 20px 16px 20px;
  background: #f8f9fa;
  border-radius: 6px;
  box-shadow: 0 2px 8px 0 rgba(0,0,0,0.04);
  border: 1px solid #e4e7ed;
  width: 100%;
  box-sizing: border-box;
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