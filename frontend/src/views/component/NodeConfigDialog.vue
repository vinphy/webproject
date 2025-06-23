<template>
  <el-dialog
    v-model="dialogVisible"
    :title="currentNode?.name + ' 参数配置'"
    width="800px"
    destroy-on-close
    @close="handleClose"
  >
    <div class="config-content">
      <!-- 基础配置 -->
      <div class="config-section">
        <div class="section-header">
          <div class="table-name-row" style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
            <span class="label" style="min-width: 60px;">数据库：</span>
            <el-select 
              v-model="currentNode.databaseName" 
              :placeholder="currentNode.type === 'create' ? '选择或输入数据库名称' : '选择数据库'"
              :filterable="currentNode.type === 'create'"
              :allow-create="currentNode.type === 'create'"
              :default-first-option="currentNode.type === 'create'"
              style="width: 200px"
              @change="onDatabaseChange"
            >
              <el-option 
                v-for="db in databaseList" 
                :key="db" 
                :label="db" 
                :value="db" 
              />
            </el-select>
            <span class="label" style="min-width: 60px;">表名：</span>
            <el-select 
              v-model="currentNode.tableName" 
              :placeholder="currentNode.type === 'create' ? '选择或输入表名' : '选择表名'"
              :filterable="currentNode.type === 'create'"
              :allow-create="currentNode.type === 'create'"
              :default-first-option="currentNode.type === 'create'"
              style="width: 200px"
            >
              <el-option 
                v-for="table in getTablesByDatabase(currentNode.databaseName)" 
                :key="table" 
                :label="table" 
                :value="table" 
              />
            </el-select>
          </div>
        </div>
      </div>

      <!-- 根据subtype显示不同的配置界面 -->
      <component 
        :is="getConfigComponent()" 
        :node="currentNode"
        :database-list="databaseList"
        :get-tables-by-database="getTablesByDatabase"
        :get-columns-by-database-table="getColumnsByDatabaseTable"
        @update:node="updateNode"
      />

      <!-- 条件配置 -->
      <div class="config-section" v-if="currentNode.type !== 'create'">
        <div class="section-header">
          <h4>条件语句</h4>
        </div>
        <div class="section-content">
          <el-input
            v-model="currentNode.condition"
            type="textarea"
            :rows="3"
            placeholder="请输入WHERE条件，例如: id = 1 AND status = 'active'"
          />
        </div>
      </div>
    </div>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="saveConfig">确定</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import BasicConfig from './configs/BasicConfig.vue'
import SelectConfig from './configs/SelectConfig.vue'
import CreateConfig from './configs/CreateConfig.vue'
import InsertConfig from './configs/InsertConfig.vue'
import UpdateConfig from './configs/UpdateConfig.vue'
import DeleteConfig from './configs/DeleteConfig.vue'

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  node: {
    type: Object,
    default: null
  },
  databaseList: {
    type: Array,
    default: () => []
  },
  getTablesByDatabase: {
    type: Function,
    required: true
  },
  getColumnsByDatabaseTable: {
    type: Function,
    required: true
  }
})

// Emits
const emit = defineEmits(['update:visible', 'save'])

// 响应式数据
const currentNode = ref(null)
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

// 监听节点变化
watch(() => props.node, (newNode) => {
  if (newNode) {
    currentNode.value = { ...newNode }
    
    // 确保parameters数组存在且至少有一个元素
    if (!currentNode.value.parameters) {
      currentNode.value.parameters = [{
        name: '',
        value: ''
      }]
    }
    
    // 自动兜底：如果没有数据库名，自动选择第一个
    if (!currentNode.value.databaseName && props.databaseList.length > 0) {
      currentNode.value.databaseName = props.databaseList[0]
    }
    // 自动兜底：如果有数据库名但没有表名，自动选择第一个表
    if (currentNode.value.databaseName) {
      const tables = props.getTablesByDatabase(currentNode.value.databaseName)
      if (tables.length > 0 && !currentNode.value.tableName) {
        currentNode.value.tableName = tables[0]
      }
    }
  }
}, { immediate: true })

// 根据subtype获取对应的配置组件
const getConfigComponent = () => {
  if (!currentNode.value) return BasicConfig
  
  const { type, subType } = currentNode.value
  
  // 根据type和subType返回不同的配置组件
  switch (type) {
    case 'select':
      return SelectConfig
    case 'create':
      return CreateConfig
    case 'insert':
      return InsertConfig
    case 'update':
      return UpdateConfig
    case 'delete':
      return DeleteConfig
    default:
      return BasicConfig
  }
}

// 数据库切换处理
const onDatabaseChange = async () => {
  console.log('数据库切换:', currentNode.value.databaseName)
  
  // 清空当前表名
  currentNode.value.tableName = ''
  
  // 如果选择了数据库，加载该数据库的表列表
  if (currentNode.value.databaseName) {
    // 如果不是create类型，自动选择第一个表
    if (currentNode.value.type !== 'create') {
      const tables = props.getTablesByDatabase(currentNode.value.databaseName)
      console.log(`数据库 ${currentNode.value.databaseName} 的表列表:`, tables)
      if (tables.length > 0) {
        currentNode.value.tableName = tables[0]
        console.log('自动选择第一个表:', tables[0])
      }
    }
  }
}

// 更新节点数据
const updateNode = (updatedNode) => {
  currentNode.value = { ...currentNode.value, ...updatedNode }
}

// 保存配置
const saveConfig = () => {
  if (!currentNode.value) return

  // select类型参数校验
  if (currentNode.value.type === 'select') {
    const names = currentNode.value.parameters.map(p => p.name)
    const hasEmpty = names.some(n => !n)
    const hasDuplicate = names.length !== new Set(names).size
    if (hasEmpty) {
      ElMessage.error('列名不能为空，请选择具体字段')
      return
    }
    if (hasDuplicate) {
      ElMessage.error('不能选择重复的列名')
      return
    }
  }

  // 触发保存事件
  emit('save', currentNode.value)
  handleClose()
}

// 关闭对话框
const handleClose = () => {
  dialogVisible.value = false
}
</script>

<style scoped>
.config-content {
  padding: 20px;
}

.config-section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-header h4 {
  margin: 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
  position: relative;
  padding-left: 12px;
}

.section-header h4::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 16px;
  background: #409EFF;
  border-radius: 2px;
}

.table-name-row .label {
  font-size: 16px;
  color: #303133;
  font-weight: 600;
  white-space: nowrap;
}

.section-content {
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style> 