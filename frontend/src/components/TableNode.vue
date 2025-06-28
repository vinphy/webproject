<template>
  <div 
    class="table-node"
    :class="{ 'selected': selected }"
    @click="$emit('node-click', data.tableName)"
  >
    <!-- 表头 -->
    <div class="table-header">
      <div class="table-icon">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
          <path d="M3 3h18v18H3V3zm16 16V5H5v14h14z"/>
          <path d="M7 7h10v2H7V7zm0 4h10v2H7v-2zm0 4h7v2H7v-2z"/>
        </svg>
      </div>
      <span class="table-name">{{ data.tableName }}</span>
      <div class="table-actions">
        <div class="primary-key-indicator" v-if="data.primaryKey">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="#f56c6c">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- 字段列表 -->
    <div class="table-columns">
      <div 
        v-for="column in data.columns" 
        :key="column.name"
        class="column-row"
        :class="{
          'primary-key': isPrimaryKey(column.name),
          'foreign-key': isForeignKey(column.name)
        }"
      >
        <div class="column-info">
          <span class="column-name">{{ column.name }}</span>
          <span class="column-type">{{ column.type }}</span>
        </div>
        <div class="column-constraints">
          <span v-if="!column.nullable" class="constraint not-null">NOT NULL</span>
          <span v-if="column.default" class="constraint default">DEFAULT</span>
          <span v-if="isPrimaryKey(column.name)" class="constraint pk">PK</span>
          <span v-if="isForeignKey(column.name)" class="constraint fk">FK</span>
        </div>
      </div>
    </div>

    <!-- 外键关系提示 -->
    <div v-if="data.foreignKeys && data.foreignKeys.length > 0" class="foreign-keys-info">
      <div class="fk-count">{{ data.foreignKeys.length }} 个外键关系</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TableNode',
  props: {
    data: {
      type: Object,
      required: true
    },
    selected: {
      type: Boolean,
      default: false
    }
  },
  emits: ['node-click'],
  setup(props) {
    const isPrimaryKey = (columnName) => {
      return props.data.primaryKey && props.data.primaryKey.includes(columnName)
    }

    const isForeignKey = (columnName) => {
      return props.data.foreignKeys && props.data.foreignKeys.some(fk => fk.column === columnName)
    }

    return {
      isPrimaryKey,
      isForeignKey
    }
  }
}
</script>

<style scoped>
.table-node {
  background: white;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  min-width: 200px;
  max-width: 300px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
  overflow: hidden;
}

.table-node:hover {
  border-color: #409EFF;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
  transform: translateY(-2px);
}

.table-node.selected {
  border-color: #409EFF;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.table-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 14px;
}

.table-icon {
  display: flex;
  align-items: center;
}

.table-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.table-actions {
  display: flex;
  align-items: center;
}

.primary-key-indicator {
  display: flex;
  align-items: center;
}

.table-columns {
  max-height: 300px;
  overflow-y: auto;
}

.column-row {
  padding: 8px 16px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background-color 0.2s;
}

.column-row:hover {
  background-color: #f8f9fa;
}

.column-row:last-child {
  border-bottom: none;
}

.column-row.primary-key {
  background-color: #fef0f0;
  border-left: 3px solid #f56c6c;
}

.column-row.foreign-key {
  background-color: #f0f9ff;
  border-left: 3px solid #409EFF;
}

.column-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.column-name {
  font-weight: 500;
  font-size: 13px;
  color: #303133;
}

.column-type {
  font-size: 11px;
  color: #909399;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.column-constraints {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.constraint {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: 500;
  text-transform: uppercase;
}

.constraint.not-null {
  background-color: #fef0f0;
  color: #f56c6c;
}

.constraint.default {
  background-color: #f0f9ff;
  color: #409EFF;
}

.constraint.pk {
  background-color: #f56c6c;
  color: white;
}

.constraint.fk {
  background-color: #409EFF;
  color: white;
}

.foreign-keys-info {
  background-color: #f0f9ff;
  border-top: 1px solid #e4e7ed;
  padding: 8px 16px;
  text-align: center;
}

.fk-count {
  font-size: 11px;
  color: #409EFF;
  font-weight: 500;
}

/* 滚动条样式 */
.table-columns::-webkit-scrollbar {
  width: 4px;
}

.table-columns::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.table-columns::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 2px;
}

.table-columns::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .table-node {
    min-width: 180px;
    max-width: 250px;
  }
  
  .table-header {
    padding: 10px 12px;
    font-size: 13px;
  }
  
  .column-row {
    padding: 6px 12px;
  }
  
  .column-name {
    font-size: 12px;
  }
  
  .column-type {
    font-size: 10px;
  }
}
</style> 