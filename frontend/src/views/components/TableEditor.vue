<template>
    <div class="table-editor">
      <el-table :data="modelValue" border style="width: 100%">
        <el-table-column 
          v-for="col in columns" 
          :key="col.key" 
          :label="col.name"
          :width="getColWidth(col)"
        >
          <template #default="{ row }">
            <!-- 输入框 -->
            <el-input 
              v-if="col.type === 'input'" 
              v-model="row[col.key]" 
            />
            
            <!-- 下拉选择框 -->
            <el-select 
              v-else-if="col.type === 'select'" 
              v-model="row[col.key]" 
              style="width: 100%"
            >
              <el-option 
                v-for="option in col.options" 
                :key="option" 
                :label="option" 
                :value="option"
              />
            </el-select>
            
            <!-- 复选框 -->
            <el-checkbox 
              v-else-if="col.type === 'checkbox'" 
              v-model="row[col.key]" 
              :true-label="true" 
              :false-label="false"
            />
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
  
  // 列宽设置
  const getColWidth = (col) => {
    if (col.type === 'input') return 120
    if (col.type === 'select') return 160
    if (col.type === 'checkbox') return 80
    return 120
  }
  
  // 添加新行
  const addRow = () => {
    const newRow = {}
    props.columns.forEach(col => {
      if (col.type === 'checkbox') {
        newRow[col.key] = false
      } else {
        newRow[col.key] = ''
      }
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
  .table-editor {
    margin-bottom: 20px;
  }
  
  .add-row-btn {
    margin-top: 10px;
  }
  
  :deep(.el-radio-group) {
    display: flex;
    justify-content: center;
  }
  
  :deep(.el-radio) {
    margin-right: 10px;
  }
  
  :deep(.el-select) {
    width: 100%;
  }
  
  :deep(.el-checkbox) {
    display: flex;
    justify-content: center;
  }
  </style>