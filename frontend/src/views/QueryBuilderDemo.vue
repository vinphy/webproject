<template>
  <div class="query-builder-demo">
    <h2>自定义sql参数配置</h2>
    <div class="toolbar">
      <el-select v-model="selectedTables" multiple placeholder="选择表" style="width: 320px; margin-right: 16px">
        <el-option v-for="t in tableOptions" :key="t.value" :label="t.label" :value="t.value" />
      </el-select>
      <el-button size="small" @click="addRootGroup" type="primary">添加分组(括号)</el-button>
      <el-button size="small" @click="addRootCondition" type="success">添加条件</el-button>
      <el-button size="small" @click="addOrderBy" type="info">添加排序</el-button>
    </div>
    <div class="builder-area">
      <ConditionGroup
        v-if="conditionBuilder"
        :group="conditionBuilder"
        :fields="filteredFields"
        :operators="operators"
        :table-map="tableMap"
        :support-agg="true"
        :support-subquery="true"
        :removable="false"
        @update="val => conditionBuilder = val"
      />
    </div>
    <div class="order-by-area" v-if="orderByList.length">
      <h4>排序字段</h4>
      <div v-for="(ob, idx) in orderByList" :key="idx" style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
        <el-select v-model="ob.field" placeholder="选择字段" style="width:180px">
          <el-option v-for="f in filteredFields" :key="f.name" :label="f.label" :value="f.name" />
        </el-select>
        <el-select v-model="ob.order" placeholder="排序方式" style="width:100px">
          <el-option label="升序" value="asc" />
          <el-option label="降序" value="desc" />
        </el-select>
        <el-button type="danger" size="small" @click="orderByList.splice(idx,1)">删除</el-button>
      </div>
    </div>
    <div class="sql-preview">
      <h4>SQL预览</h4>
      <el-input type="textarea" :rows="8" :model-value="buildFullSQL()" readonly />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, h, computed } from 'vue'
import { ElButton, ElInput, ElSelect, ElOption, ElMessage } from 'element-plus'

// TPC-H风格表结构
const tableOptions = [
  { value: 'part', label: 'part' },
  { value: 'supplier', label: 'supplier' },
  { value: 'partsupp', label: 'partsupp' },
  { value: 'nation', label: 'nation' },
  { value: 'region', label: 'region' }
]
const tableMap = {
  part: [
    { name: 'p_partkey', label: '零件编号', type: 'number' },
    { name: 'p_mfgr', label: '生产者', type: 'string' },
    { name: 'p_size', label: '大小', type: 'number', values: Array.from({length:50},(_,i)=>i+1) },
    { name: 'p_type', label: '类型', type: 'string', values: ['ECONOMY ANODIZED STEEL','STANDARD POLISHED COPPER','SMALL BRUSHED BRASS','LARGE BURNISHED TIN'] }
  ],
  supplier: [
    { name: 's_suppkey', label: '供应商编号', type: 'number' },
    { name: 's_acctbal', label: '帐户余额', type: 'number' },
    { name: 's_name', label: '供应商名', type: 'string' },
    { name: 's_address', label: '地址', type: 'string' },
    { name: 's_phone', label: '电话', type: 'string' },
    { name: 's_comment', label: '备注', type: 'string' },
    { name: 's_nationkey', label: '国家编号', type: 'number' }
  ],
  partsupp: [
    { name: 'ps_partkey', label: '零件编号', type: 'number' },
    { name: 'ps_suppkey', label: '供应商编号', type: 'number' },
    { name: 'ps_supplycost', label: '供应成本', type: 'number' }
  ],
  nation: [
    { name: 'n_nationkey', label: '国家编号', type: 'number' },
    { name: 'n_name', label: '国家名', type: 'string' },
    { name: 'n_regionkey', label: '地区编号', type: 'number' }
  ],
  region: [
    { name: 'r_regionkey', label: '地区编号', type: 'number' },
    { name: 'r_name', label: '地区名', type: 'string', values: ['AFRICA','AMERICA','ASIA','EUROPE','MIDDLE EAST'] }
  ]
}

const selectedTables = ref(['part','supplier','partsupp','nation','region'])

const filteredFields = computed(() => {
  // 合并所有选中表的字段
  return selectedTables.value.flatMap(t => tableMap[t]||[])
})

const operators = [
  { value: '=', label: '=' },
  { value: '!=', label: '!=' },
  { value: '>', label: '>' },
  { value: '<', label: '<' },
  { value: '>=', label: '>=' },
  { value: '<=', label: '<=' },
  { value: 'LIKE', label: 'LIKE(模糊)' },
  { value: 'IN', label: 'IN(多选)' },
  { value: 'BETWEEN', label: '区间' }
]

const aggFuncs = [ '', 'min', 'max', 'sum', 'count', 'avg' ]

const conditionBuilder = ref(null)
const orderByList = ref([])

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
const addOrderBy = () => {
  orderByList.value.push({ field: '', order: 'asc' })
}

// 递归分组组件
const ConditionGroup = {
  props: ['group', 'fields', 'operators', 'tableMap', 'supportAgg', 'supportSubquery', 'removable'],
  emits: ['update', 'remove'],
  setup(props, { emit }) {
    const addCondition = () => {
      props.group.children.push({ type: 'condition', field: '', operator: '=', value: '' })
      emit('update', props.group)
    }
    const addGroup = () => {
      props.group.children.push({ type: 'group', logic: 'AND', children: [] })
      emit('update', props.group)
    }
    const addSubquery = () => {
      props.group.children.push({ type: 'subquery', group: { type: 'group', logic: 'AND', children: [] }, agg: '', field: '' })
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
        props.supportSubquery ? h(ElButton, { type: 'warning', size: 'small', style: 'margin-left:4px', onClick: addSubquery }, () => '添加子查询') : null,
        props.removable ? h(ElButton, { type: 'danger', size: 'small', style: 'margin-left:4px', onClick: handleRemoveSelf }, () => '删除分组') : null
      ]),
      ...props.group.children.map((item, idx) =>
        item.type === 'group'
          ? h(ConditionGroup, {
              group: item,
              fields: props.fields,
              operators: props.operators,
              tableMap: props.tableMap,
              supportAgg: props.supportAgg,
              supportSubquery: props.supportSubquery,
              removable: true,
              onUpdate: val => updateChild(idx, val),
              onRemove: () => removeItem(idx)
            })
          : item.type === 'subquery'
            ? h(SubQueryItem, {
                subquery: item,
                fields: props.fields,
                operators: props.operators,
                tableMap: props.tableMap,
                supportAgg: props.supportAgg,
                supportSubquery: props.supportSubquery,
                onUpdate: val => updateChild(idx, val),
                onRemove: () => removeItem(idx)
              })
            : h(ConditionItem, {
                condition: item,
                fields: props.fields,
                operators: props.operators,
                tableMap: props.tableMap,
                supportAgg: props.supportAgg,
                onUpdate: val => updateChild(idx, val),
                onRemove: () => removeItem(idx)
              })
      )
    ])
  }
}
// 单个条件组件
const ConditionItem = {
  props: ['condition', 'fields', 'operators', 'tableMap', 'supportAgg'],
  emits: ['update', 'remove'],
  setup(props, { emit }) {
    const update = (key, val) => {
      props.condition[key] = val
      emit('update', props.condition)
    }
    // 字段类型、可选值
    const fieldObj = computed(() => props.fields.find(f => f.name === props.condition.field) || {})
    // value类型切换
    const valueType = computed({
      get: () => props.condition.valueType || 'const',
      set: v => { update('valueType', v); if(v==='const') update('value', ''); if(v==='subquery') update('value', { type: 'subquery', group: { type: 'group', logic: 'AND', children: [] }, agg: '', field: '' }) }
    })
    const updateSubquery = (val) => {
      update('value', val)
    }
    return () => {
      // 主输入区
      const mainRow = [
        props.supportAgg ? h(ElSelect, {
          modelValue: props.condition.agg || '',
          placeholder: '聚合',
          style: 'width:80px',
          onChange: val => update('agg', val)
        }, () => aggFuncs.map(fn => h(ElOption, { value: fn, label: fn || '无' }))) : null,
        h(ElSelect, {
          modelValue: props.condition.field,
          placeholder: '选择字段',
          style: 'width:140px',
          onChange: val => update('field', val)
        }, () => props.fields.map(f => h(ElOption, { value: f.name, label: f.label }))),
        h(ElSelect, {
          modelValue: props.condition.operator,
          placeholder: '符号',
          style: 'width:100px',
          onChange: val => update('operator', val)
        }, () => props.operators.map(op => h(ElOption, { value: op.value, label: op.label }))),
        // value类型切换
        h(ElSelect, {
          modelValue: valueType.value,
          style: 'width:90px',
          onChange: val => valueType.value = val
        }, () => [
          h(ElOption, { value: 'const', label: '常量/下拉' }),
          h(ElOption, { value: 'subquery', label: '子查询' })
        ]),
        // IN 多选
        props.condition.operator === 'IN' && fieldObj.value.values ? h(ElSelect, {
          modelValue: props.condition.value,
          multiple: true,
          placeholder: '多选',
          style: 'width:160px',
          onChange: val => update('value', val)
        }, () => fieldObj.value.values.map(v => h(ElOption, { value: v, label: v }))) :
        // 区间
        props.condition.operator === 'BETWEEN' ? [
          h(ElInput, {
            modelValue: Array.isArray(props.condition.value) ? props.condition.value[0] : '',
            placeholder: '最小值',
            style: 'width:70px',
            onInput: val => update('value', [val, Array.isArray(props.condition.value) ? props.condition.value[1] : ''])
          }),
          h('span', ' ~ '),
          h(ElInput, {
            modelValue: Array.isArray(props.condition.value) ? props.condition.value[1] : '',
            placeholder: '最大值',
            style: 'width:70px',
            onInput: val => update('value', [Array.isArray(props.condition.value) ? props.condition.value[0] : '', val])
          })
        ] :
        // LIKE
        props.condition.operator === 'LIKE' ? h(ElInput, {
          modelValue: props.condition.value,
          placeholder: '模糊匹配',
          style: 'width:120px',
          onInput: val => update('value', val)
        }) :
        // 有可选值
        fieldObj.value.values ? h(ElSelect, {
          modelValue: props.condition.value,
          placeholder: '选择值',
          style: 'width:120px',
          onChange: val => update('value', val)
        }, () => fieldObj.value.values.map(v => h(ElOption, { value: v, label: v }))) :
        // 默认输入框
        h(ElInput, {
          modelValue: props.condition.value,
          placeholder: '输入值',
          style: 'width:120px',
          onInput: val => update('value', val)
        }),
        h(ElButton, { type: 'danger', size: 'small', onClick: () => emit('remove') }, () => '删除')
      ];
      // 子查询区分行显示
      const subqueryRow = valueType.value === 'subquery' ? h('div', { style: 'margin:6px 0 0 0; padding:10px 12px 8px 12px; background:#f6f8fa; border:1.5px solid #b3b3b3; border-radius:6px; width:100%;' }, [
        h(SubQueryItem, {
          subquery: props.condition.value,
          fields: props.fields,
          operators: props.operators,
          tableMap: props.tableMap,
          supportAgg: props.supportAgg,
          supportSubquery: false,
          onUpdate: updateSubquery
        })
      ]) : null;
      return h('div', { class: 'condition-item', style: 'margin-bottom:10px;' }, [
        h('div', { style: 'display:flex;align-items:center;gap:8px;flex-wrap:wrap;' }, mainRow),
        subqueryRow
      ])
    }
  }
}
// 子查询组件
const SubQueryItem = {
  props: ['subquery', 'fields', 'operators', 'tableMap', 'supportAgg', 'supportSubquery'],
  emits: ['update', 'remove'],
  setup(props, { emit }) {
    const update = (key, val) => {
      props.subquery[key] = val
      emit('update', props.subquery)
    }
    return () => h('div', { class: 'subquery-item', style: 'margin-bottom:6px;display:flex;align-items:center;gap:6px;border:1px dashed #aaa;padding:8px 8px 8px 16px;background:#f9f9f9;' }, [
      h('span', '子查询: '),
      h(ElSelect, {
        modelValue: props.subquery.agg || '',
        placeholder: '聚合',
        style: 'width:80px',
        onChange: val => update('agg', val)
      }, () => aggFuncs.filter(Boolean).map(fn => h(ElOption, { value: fn, label: fn }))),
      h(ElSelect, {
        modelValue: props.subquery.field,
        placeholder: '字段',
        style: 'width:120px',
        onChange: val => update('field', val)
      }, () => props.fields.map(f => h(ElOption, { value: f.name, label: f.label }))),
      h(ConditionGroup, {
        group: props.subquery.group,
        fields: props.fields,
        operators: props.operators,
        tableMap: props.tableMap,
        supportAgg: props.supportAgg,
        supportSubquery: props.supportSubquery,
        removable: false,
        onUpdate: val => { props.subquery.group = val; emit('update', props.subquery) }
      }),
      h(ElButton, { type: 'danger', size: 'small', onClick: () => emit('remove') }, () => '删除子查询')
    ])
  }
}
// SQL生成
function buildWhereSQL(group) {
  if (!group || !group.children || !group.children.length) return ''
  return group.children.map(item => {
    if (item.type === 'group') {
      return '(' + buildWhereSQL(item) + ')'
    } else if (item.type === 'subquery') {
      const agg = item.agg ? `${item.agg}(` : ''
      const aggEnd = item.agg ? ')' : ''
      return `(
  select ${agg}${item.field}${aggEnd} from ... where ${buildWhereSQL(item.group)}
 )`
    } else {
      let field = item.field
      if (item.agg) field = `${item.agg}(${field})`
      // value为子查询
      if (item.valueType === 'subquery' && item.value && item.value.type === 'subquery') {
        const sub = item.value
        const agg = sub.agg ? `${sub.agg}(` : ''
        const aggEnd = sub.agg ? ')' : ''
        return `${field} ${item.operator} (select ${agg}${sub.field}${aggEnd} from ... where ${buildWhereSQL(sub.group)})`
      }
      if (item.operator === 'IN') {
        return `${field} IN (${(item.value||[]).map(v=>`'${v}'`).join(',')})`
      } else if (item.operator === 'BETWEEN') {
        return `${field} BETWEEN '${item.value?.[0]||''}' AND '${item.value?.[1]||''}'`
      } else if (item.operator === 'LIKE') {
        return `${field} LIKE '%${item.value||''}%'`
      } else {
        return `${field} ${item.operator} '${item.value}'`
      }
    }
  }).join(' ' + group.logic + ' ')
}
function buildFullSQL() {
  // select ... from ... where ... order by ...
  const selectFields = [
    's_acctbal', 's_name', 'n_name', 'p_partkey', 'p_mfgr', 's_address', 's_phone', 's_comment'
  ]
  const fromTables = selectedTables.value.join(', ')
  const where = buildWhereSQL(conditionBuilder.value)
  const orderBy = orderByList.value.filter(ob=>ob.field).map(ob=>`${ob.field} ${ob.order.toUpperCase()}`).join(', ')
  return `select\n  ${selectFields.join(', ')}\nfrom\n  ${fromTables}\nwhere\n  ${where}\n${orderBy ? 'order by\n  ' + orderBy : ''}`
}
</script>

<style scoped>
.query-builder-demo {
  max-width: 900px;
  margin: 40px auto;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.08);
  padding: 32px 32px 24px 32px;
}
.toolbar {
  margin-bottom: 18px;
  display: flex;
  align-items: center;
}
.builder-area {
  margin-bottom: 18px;
}
.sql-preview {
  margin-top: 18px;
}
.order-by-area {
  margin-top: 18px;
}
/* 优化子查询分行样式 */
.condition-item .subquery-item {
  margin-bottom: 0 !important;
  padding: 0 0 0 0 !important;
  background: none !important;
  border: none !important;
}
</style> 