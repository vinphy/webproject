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
                :key="typeof option === 'object' ? option.value : option" 
                :label="typeof option === 'object' ? option.label : option" 
                :value="typeof option === 'object' ? option.value : option"
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
        <el-table-column label="操作" width="160">
          <template #default="{ row, $index }">
            <el-button 
              size="small" 
              @click="openConstraintDialog(row, $index)"
            >约束</el-button>
            <el-button 
              size="small" 
              type="danger" 
              @click="removeRow($index)"
            >删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-button class="add-row-btn" @click="addRow">添加行</el-button>

      <!-- 约束配置弹窗 -->
      <el-dialog 
        v-model="constraintDialogVisible"
        title="字段约束配置"
        width="500px"
        destroy-on-close
      >
        <el-form :model="editingConstraint" label-width="100px">
          <!-- 主键配置 -->
          <el-form-item label="主键">         <el-checkbox 
              v-model="editingConstraint.primary"           @change="handlePrimaryChange"    />
            <span style="margin-left:10px; color: #993999; font-size: 12px;">
              设置为主键
            </span>
          </el-form-item>
          
          <!-- 主键自增配置 -->
          <el-form-item label="自增" :disabled="!editingConstraint.primary">         <el-checkbox 
              v-model="editingConstraint.autoIncrement"    />
            <span style="margin-left:10px; color: #993999; font-size: 12px;">
              自动递增
            </span>
          </el-form-item>
          
          <!-- 唯一约束 -->
          <el-form-item label="唯一">         <el-checkbox 
              v-model="editingConstraint.unique"    />
            <span style="margin-left:10px; color: #993999; font-size: 12px;">
              唯一约束
            </span>
          </el-form-item>
          
          <!-- 可空配置 -->
          <el-form-item label="允许为空">         <el-checkbox 
              v-model="editingConstraint.nullable"    />
            <span style="margin-left:10px; color: #993999; font-size: 12px;">
              允许NULL值
            </span>
          </el-form-item>
          
          <!-- 默认值 -->
          <el-form-item label="默认值">         <el-input 
              v-model="editingConstraint.default" 
              placeholder="请输入默认值"      />
          </el-form-item>
          
          <!-- 外键配置 -->
          <el-form-item label="外键">         <el-checkbox 
              v-model="editingConstraint.hasForeignKey"           @change="handleForeignKeyChange"    />
            <span style="margin-left:10px; color: #993999; font-size: 12px;">
              外键约束
            </span>
          </el-form-item>
          
          <!-- 外键详细配置 -->
          <template v-if="editingConstraint.hasForeignKey">          <el-form-item label="关联表">
              <el-select
                v-model="editingConstraint.foreignKey.table"
                placeholder="选择关联表"
                style="width: 200px"
                @change="onForeignTableChange"
              >
                <el-option
                  v-for="table in availableTables"
                  :key="table"
                  :label="table"
                  :value="table"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="关联字段">
              <el-select
                v-model="editingConstraint.foreignKey.column"
                placeholder="选择关联字段"
                style="width: 200px"
                :disabled="!editingConstraint.foreignKey.table"
              >
                <el-option
                  v-for="col in availableColumnsMap[editingConstraint.foreignKey.table] || []"
                  :key="col"
                  :label="col"
                  :value="col"
                />
              </el-select>
            </el-form-item>
          </template>
        </el-form>
        
        <template #footer>
          <span class="dialog-footer">        <el-button @click="constraintDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="saveConstraint">保存</el-button>
          </span>
        </template>
      </el-dialog>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import { ElDialog, ElForm, ElFormItem, ElCheckbox, ElInput, ElButton, ElMessage } from 'element-plus'

  const props = defineProps({
    modelValue: {
      type: Array,
      required: true
    },
    columns: {
      type: Array,
      required: true
    },
    availableTables: {
      type: Array,
      default: () => []
    },
    availableColumnsMap: {
      type: Object,
      default: () => ({})
    }
  })
  
  const emit = defineEmits(['update:modelValue'])
  
  const constraintDialogVisible = ref(false)
  const editingConstraint = ref({})
  let editingIndex = -1

  const openConstraintDialog = (row, index) => {
    editingConstraint.value = JSON.parse(JSON.stringify(row.constraint || {
      primary: false,
      unique: false,
      autoIncrement: false,
      nullable: true,
      default: '',
      hasForeignKey: false,
      foreignKey: { table: '', column: '' }
    }))
    editingIndex = index
    constraintDialogVisible.value = true
  }

  const saveConstraint = () => {
    if (editingIndex !== -1) {
      const newValue = [...props.modelValue]
      newValue[editingIndex].constraint = JSON.parse(JSON.stringify(editingConstraint.value))
      emit('update:modelValue', newValue)
      console.log('打印约束参数')
      console.log(newValue)
      ElMessage.success('约束配置已保存')
    }
    constraintDialogVisible.value = false
  }

  // 处理主键变化
  const handlePrimaryChange = (value) => {
    if (!value) {
      // 如果取消主键，同时取消自增
      editingConstraint.value.autoIncrement = false
    }
  }

  // 处理外键变化
  const handleForeignKeyChange = (value) => {
    if (!value) {
      // 如果取消外键，清空外键配置
      editingConstraint.value.foreignKey = { table: '', column: '' }
    }
  }
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
    
    // 初始化约束对象
    newRow.constraint = {
      primary: false,
      unique: false,
      autoIncrement: false,
      nullable: true,
      default: '',
      hasForeignKey: false,
      foreignKey: { table: '', column: '' }
    }
    
    emit('update:modelValue', [...props.modelValue, newRow])
  }
  
  // 删除行
  const removeRow = (index) => {
    const newValue = [...props.modelValue]
    newValue.splice(index, 1)
    emit('update:modelValue', newValue)
  }

  function getTableData() {
    return {
      modelValue
    }
  }
  defineExpose({ getTableData })

  // methods
  const onForeignTableChange = (table) => {
    editingConstraint.value.foreignKey.column = ''
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

  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap:10
  }
  </style>