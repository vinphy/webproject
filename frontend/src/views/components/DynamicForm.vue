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
    }
  })
  
  const emit = defineEmits(['submit', 'update'])
  
  const formRef = ref(null)
  const formData = ref({})
  
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
    try {
      // 注册辅助函数：判断是否字符串
      Handlebars.registerHelper('isString', function(value) {
        return typeof value === 'string';
      });
      // 注册辅助函数：判断是否最后一个
      Handlebars.registerHelper('unlessLast', function(index, array, options) {
        if (index !== array.length - 1) {
          return options.fn(this);
        }
        return '';
      });
      // 如果有sql_template，优先用模板
      if (props.sqlTemplate) {
        const template = Handlebars.compile(props.sqlTemplate)
        return template(formData.value)
      }
      // 否则自动拼接
      const tableName = formData.value.tableName || 'table_name'
      const fields = formData.value.fields || []
      const columns = fields.map(f => f.fieldName).filter(Boolean)
      const values = fields.map(f => {
        if (typeof f.fieldType === 'number' || /^[0-9.]+$/.test(f.fieldType)) {
          return f.fieldType
        }
        return `'${f.fieldType}'`
      })
      if (columns.length === 0) return '-- 请选择参数'
      return `INSERT INTO ${tableName} (${columns.join(', ')}) VALUES (${values.join(', ')});`
    } catch (e) {
      return 'SQL渲染出错'
    }
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