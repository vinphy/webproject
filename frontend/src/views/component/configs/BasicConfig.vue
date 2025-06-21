<template>
  <div class="config-section">
    <div class="section-header">
      <h4>字段配置</h4>
      <el-button type="primary" size="small" @click="addParameter">添加参数</el-button>
    </div>
    <div class="section-content">
      <div class="parameter-header">
        <span class="param-col">字段名</span>
        <span class="param-col">字段值</span>
        <span class="param-col">操作</span>
      </div>
      <div v-for="(param, index) in node.parameters" :key="index" class="parameter-item">
        <el-input v-model="param.name" placeholder="字段名" class="param-col" />
        <el-input v-model="param.value" placeholder="字段值" class="param-col" />
        <div class="param-col">
          <el-button type="danger" size="small" @click="removeParameter(index)">删除</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  node: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:node'])

const addParameter = () => {
  const updatedNode = { ...props.node }
  if (!updatedNode.parameters) {
    updatedNode.parameters = []
  }
  updatedNode.parameters.push({ name: '', value: '' })
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