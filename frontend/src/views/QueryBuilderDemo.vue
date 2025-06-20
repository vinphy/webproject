<template>
  <div class="query-builder-demo">
    <h2>SQL条件可视化构建器（Query Builder Demo）</h2>
    <div class="toolbar">
      <el-button size="small" @click="addRootGroup" type="primary">添加分组(括号)</el-button>
      <el-button size="small" @click="addRootCondition" type="success">添加条件</el-button>
    </div>
    <div class="builder-area">
      <ConditionGroup
        v-if="conditionBuilder"
        :group="conditionBuilder"
        :fields="fields"
        :operators="operators"
        :removable="false"
        @update="val => conditionBuilder = val"
      />
    </div>
    <div class="sql-preview">
      <h4>SQL预览</h4>
      <el-input type="textarea" :rows="3" :model-value="buildWhereSQL(conditionBuilder)" readonly />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, h } from 'vue'
import { ElButton, ElInput, ElSelect, ElOption, ElMessage } from 'element-plus'

// 字段、运算符配置
const fields = [
  { name: 'name', label: '姓名', type: 'string' },
  { name: 'age', label: '年龄', type: 'number' },
  { name: 'score', label: '分数', type: 'number' }
]
const operators = [
  { value: '=', label: '=' },
  { value: '!=', label: '!=' },
  { value: '>', label: '>' },
  { value: '<', label: '<' },
  { value: 'LIKE', label: 'LIKE' }
]

const conditionBuilder = ref(null)

const addRootGroup = () => {
  if (!conditionBuilder.value) {
    conditionBuilder.value = reactive({ type: 'group', logic: 'AND', children: [] })
    return;
  }
  conditionBuilder.value.children.push({ type: 'group', logic: 'AND', children: [] })
}
const addRootCondition = () => {
  if (!conditionBuilder.value) {
    conditionBuilder.value = reactive({ type: 'group', logic: 'AND', children: [] })
  }
  conditionBuilder.value.children.push({ type: 'condition', field: '', operator: '=', value: '' })
}

// 递归分组组件
const ConditionGroup = {
  props: ['group', 'fields', 'operators', 'removable'],
  emits: ['update', 'remove'],
  setup(props, { emit }) {
    const addCondition = () => {
      props.group.children.push({
        type: 'condition',
        field: '',
        operator: '=',
        value: ''
      })
      emit('update', props.group)
    }
    const addGroup = () => {
      props.group.children.push({
        type: 'group',
        logic: 'AND',
        children: []
      })
      emit('update', props.group)
    }
    const removeItem = idx => {
      props.group.children.splice(idx, 1)
      emit('update', props.group)
    }
    const updateChild = (idx, val) => {
      props.group.children[idx] = val
      emit('update', props.group)
    }
    const handleRemoveSelf = () => {
      emit('remove')
    }
    return () => h('div', { class: 'condition-group', style: 'border:1px solid #e4e7ed;padding:10px;margin-bottom:8px;border-radius:6px;background:#fafbfc;' }, [
      h('div', { style: 'margin-bottom:6px;display:flex;align-items:center;gap:8px;' }, [
        h('span', '分组('),
        h(ElSelect, {
          modelValue: props.group.logic,
          style: 'width:80px;margin:0 4px',
          onChange: val => { props.group.logic = val; emit('update', props.group) }
        }, () => [
          h(ElOption, { value: 'AND', label: 'AND' }),
          h(ElOption, { value: 'OR', label: 'OR' })
        ]),
        h('span', ')'),
        h(ElButton, { type: 'primary', size: 'small', style: 'margin-left:8px', onClick: addCondition }, () => '添加条件'),
        h(ElButton, { type: 'success', size: 'small', style: 'margin-left:4px', onClick: addGroup }, () => '嵌套分组'),
        props.removable ? h(ElButton, { type: 'danger', size: 'small', style: 'margin-left:4px', onClick: handleRemoveSelf }, () => '删除分组') : null
      ]),
      ...props.group.children.map((item, idx) =>
        item.type === 'group'
          ? h(ConditionGroup, {
              group: item,
              fields: props.fields,
              operators: props.operators,
              removable: true,
              onUpdate: val => updateChild(idx, val),
              onRemove: () => removeItem(idx)
            })
          : h(ConditionItem, {
              condition: item,
              fields: props.fields,
              operators: props.operators,
              onUpdate: val => updateChild(idx, val),
              onRemove: () => removeItem(idx)
            })
      )
    ])
  }
}
// 单个条件组件
const ConditionItem = {
  props: ['condition', 'fields', 'operators'],
  emits: ['update', 'remove'],
  setup(props, { emit }) {
    const update = (key, val) => {
      props.condition[key] = val
      emit('update', props.condition)
    }
    return () => h('div', { class: 'condition-item', style: 'margin-bottom:6px;display:flex;align-items:center;gap:6px;' }, [
      h(ElSelect, {
        modelValue: props.condition.field,
        placeholder: '选择字段',
        style: 'width:120px',
        onChange: val => update('field', val)
      }, () => props.fields.map(f => h(ElOption, { value: f.name, label: f.label }))),
      h(ElSelect, {
        modelValue: props.condition.operator,
        placeholder: '符号',
        style: 'width:90px',
        onChange: val => update('operator', val)
      }, () => props.operators.map(op => h(ElOption, { value: op.value, label: op.label }))),
      h(ElInput, {
        modelValue: props.condition.value,
        placeholder: '参数值',
        style: 'width:80px',
        onInput: val => update('value', val)
      }),
      h(ElButton, { type: 'danger', size: 'small', onClick: () => emit('remove') }, () => '删除')
    ])
  }
}
// SQL生成
function buildWhereSQL(group) {
  if (!group || !group.children || !group.children.length) return ''
  return group.children.map(item => {
    if (item.type === 'group') {
      return '(' + buildWhereSQL(item) + ')'
    } else {
      return `${item.field} ${item.operator} '${item.value}'`
    }
  }).join(' ' + group.logic + ' ')
}
</script>

<style scoped>
.query-builder-demo {
  max-width: 800px;
  margin: 40px auto;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.08);
  padding: 32px 32px 24px 32px;
}
.toolbar {
  margin-bottom: 18px;
}
.builder-area {
  margin-bottom: 18px;
}
.sql-preview {
  margin-top: 18px;
}
</style> 