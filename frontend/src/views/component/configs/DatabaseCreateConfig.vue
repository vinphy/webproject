<template>
  <div class="config-section">
    <div class="section-header">
      <h4>数据库参数配置</h4>
    </div>
    <div class="section-content">
      <div class="parameter-item" v-for="field in uiSchema" :key="field.key">
        <div class="param-label">{{ field.label }}：</div>
        <div class="param-input">
          <template v-if="field.type === 'input'">
            <el-input 
              v-model="formData[field.key]" 
              :placeholder="'请输入' + field.label"
              :required="field.required"
              @input="updateNodeData"
            />
          </template>
          <template v-else-if="field.key === 'charset'">
            <el-select 
              v-model="formData[field.key]" 
              :placeholder="'请选择' + field.label"
              :required="field.required"
              @change="updateNodeData"
            >
              <el-option label="utf8" value="utf8" />
              <el-option label="utf8mb4" value="utf8mb4" />
              <el-option label="latin1" value="latin1" />
              <el-option label="gbk" value="gbk" />
            </el-select>
          </template>
          <template v-else-if="field.key === 'collation'">
            <el-select 
              v-model="formData[field.key]" 
              :placeholder="'请选择' + field.label"
              :required="field.required"
              @change="updateNodeData"
            >
              <el-option label="utf8_general_ci" value="utf8_general_ci" />
              <el-option label="utf8mb4_general_ci" value="utf8mb4_general_ci" />
              <el-option label="latin1_swedish_ci" value="latin1_swedish_ci" />
              <el-option label="gbk_chinese_ci" value="gbk_chinese_ci" />
            </el-select>
          </template>
        </div>
      </div>
      
      <div class="sql-preview">
        <h4>SQL预览</h4>
        <el-input 
          type="textarea" 
          :rows="3" 
          :model-value="buildSQL()" 
          readonly 
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'

const props = defineProps({
  node: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:node'])

// UI Schema定义
const uiSchema = [
  { key: 'databaseName', label: '数据库名', type: 'input', required: true },
  { key: 'charset', label: '字符集', type: 'select', required: true },
  { key: 'collation', label: '排序规则', type: 'select' }
]

// 表单数据
const formData = reactive({
  databaseName: props.node.databaseName || '',
  charset: 'utf8mb4',
  collation: 'utf8mb4_general_ci'
})

// SQL模板
const sqlTemplate = "CREATE DATABASE {{databaseName}} CHARACTER SET {{charset}} COLLATE {{collation}};"

// 生成SQL
function buildSQL() {
  let sql = sqlTemplate
  Object.keys(formData).forEach(key => {
    sql = sql.replace(`{{${key}}}`, formData[key] || '')
  })
  return sql
}

// 更新节点数据
function updateNodeData() {
  const updatedNode = { ...props.node }
  updatedNode.databaseName = formData.databaseName
  updatedNode.parameters = [
    { name: 'charset', value: formData.charset },
    { name: 'collation', value: formData.collation }
  ]
  updatedNode.sql = buildSQL()
  emit('update:node', updatedNode)
}

// 监听node变化
watch(() => props.node, (newNode) => {
  if (newNode) {
    formData.databaseName = newNode.databaseName || ''
    if (newNode.parameters) {
      const charset = newNode.parameters.find(p => p.name === 'charset')
      const collation = newNode.parameters.find(p => p.name === 'collation')
      if (charset) formData.charset = charset.value
      if (collation) formData.collation = collation.value
    } else {
      // 如果没有参数，使用默认值
      formData.charset = 'utf8mb4'
      formData.collation = 'utf8mb4_general_ci'
    }
    // 确保初始化时更新节点数据
    updateNodeData()
  }
}, { immediate: true })
</script>

<style scoped>
.parameter-item {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.param-label {
  width: 120px;
  text-align: right;
  padding-right: 12px;
  color: #606266;
}

.param-input {
  flex: 1;
  max-width: 300px;
}

.sql-preview {
  margin-top: 30px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 4px;
}

.sql-preview h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 14px;
}
</style> 