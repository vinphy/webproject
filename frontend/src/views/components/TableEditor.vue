<template>
    <div class="table-editor">
      <el-table :data="modelValue" border style="width: 100%">
        <el-table-column 
          v-for="(col, index) in columns" 
          :key="index" 
          :label="col"
        >
          <template #default="{ row }">
            <el-input v-model="row[col]" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ $index }">
            <el-button 
              size="small" 
              type="danger" 
              @click="removeRow($index)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-button class="add-row-btn" @click="addRow">添加行</el-button>
    </div>
  </template>
  
  <script setup>
  const props = defineProps({
    modelValue: {
      type: Array,
      required: true
    },
    columns: {
      type: Array,
      required: true
    }
  })
  
  const emit = defineEmits(['update:modelValue'])
  
  // 添加新行
  const addRow = () => {
    const newRow = {}
    props.columns.forEach(col => {
      newRow[col] = ''
    })
    emit('update:modelValue', [...props.modelValue, newRow])
  }
  
  // 删除行
  const removeRow = (index) => {
    const newValue = [...props.modelValue]
    newValue.splice(index, 1)
    emit('update:modelValue', newValue)
  }
  </script>
  
  <style scoped>
  .add-row-btn {
    margin-top: 10px;
  }
  </style>