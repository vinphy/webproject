<template>
    <div class="app-container">
      <h1>动态表单配置演示</h1>
      
      <el-radio-group v-model="formType" class="radio-group">
        <el-radio-button label="database">数据库配置</el-radio-button>
        <el-radio-button label="table">表配置</el-radio-button>
      </el-radio-group>
      
      <div class="form-container">
        <DynamicForm 
          :ui-schema="currentSchema" 
          :initial-data="initialData"
          @submit="handleSubmit"
        />
      </div>
    </div>
</template>
  
<script setup>
  import { ref, computed } from 'vue'
  import DynamicForm from './components/DynamicForm.vue'
  
  // 表单类型切换
  const formType = ref('database')
  
  // 两种不同的配置方案
  const schemaMap = {
    database: [
      { "key": "databaseName", "label": "数据库名", "type": "input", "required": true },
      { "key": "charset", "label": "字符集", "type": "input", "required": true },
      { "key": "collation", "label": "排序规则", "type": "input" }
    ],
    table: [
      { "key": "databaseName", "label": "数据库名", "type": "input", "required": true },
      { "key": "tableName", "label": "表名", "type": "input", "required": true },
      { "key": "fields", "label": "字段定义", "type": "table-editor", "columns": ["字段名", "类型", "主键", "非空"] }
    ]
  }
  
  // 当前使用的配置
  const currentSchema = computed(() => schemaMap[formType.value])
  
  // 初始数据
  const initialData = ref({
    databaseName: 'my_database',
    charset: 'utf8mb4',
    fields: [
      { "字段名": "id", "类型": "int", "主键": "是", "非空": "是" },
      { "字段名": "name", "类型": "varchar(255)", "主键": "否", "非空": "是" }
    ]
  })
  
  // 提交处理
  const handleSubmit = (formData) => {
    console.log('提交数据:', formData)
    ElMessage.success('配置已提交: ' + JSON.stringify(formData, null, 2))
  }
</script>
  
<style scoped>
  .app-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
  }
  .radio-group {
    margin-bottom: 20px;
  }
  .form-container {
    border: 1px solid #ebeef5;
    border-radius: 4px;
    padding: 20px;
  }
</style>