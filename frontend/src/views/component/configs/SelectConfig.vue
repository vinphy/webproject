<template>
  <div class="config-section">
    <div class="section-header">
      <h4>查询字段配置</h4>
      <el-button type="primary" size="small" @click="addParameter">添加字段</el-button>
    </div>
    <div class="section-content">
      <div class="parameter-header">
        <span class="param-col">列名</span>
        <span class="param-col">操作</span>
      </div>
      <div v-for="(param, index) in node.parameters" :key="index" class="parameter-item">
        <el-select
          v-model="param.name"
          placeholder="选择列名"
          class="param-col"
          style="width: 100%"
          :disabled="!node.databaseName || !node.tableName || node.parameters.some((p, i) => p.name === col && i !== index)"
          filterable
          @focus="async () => { param._columns = await getColumnsByDatabaseTable(node.databaseName, node.tableName) }"
        >
          <el-option
            v-for="col in param._columns || []"
            :key="col"
            :label="col"
            :value="col"
          />
        </el-select>
        <div class="param-col">
          <el-button type="danger" size="small" @click="removeParameter(index)">删除</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  node: {
    type: Object,
    required: true
  },
  getColumnsByDatabaseTable: {
    type: Function,
    required: true
  }
})

const emit = defineEmits(['update:node'])

const addParameter = async () => {
  const updatedNode = { ...props.node }
  if (!updatedNode.parameters) {
    updatedNode.parameters = []
  }
  const param = { name: '', value: '', _columns: [] }
  if (updatedNode.databaseName && updatedNode.tableName) {
    param._columns = await props.getColumnsByDatabaseTable(updatedNode.databaseName, updatedNode.tableName)
  }
  updatedNode.parameters.push(param)
  emit('update:node', updatedNode)
}

const removeParameter = (index) => {
  const updatedNode = { ...props.node }
  updatedNode.parameters.splice(index, 1)
  emit('update:node', updatedNode)
}
</script>

<style scoped>
.parameter-header {
  display: flex;
  padding: 8px 0;
  border-bottom: 1px solid #e4e7ed;
  margin-bottom: 10px;
}

.parameter-header span {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.parameter-item {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  align-items: center;
}

.param-col {
  flex: 1;
  min-width: 0;
}

.param-col:last-child {
  flex: 0 0 80px;
  text-align: center;
}
</style> 