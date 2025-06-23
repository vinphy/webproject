<template>
    <el-form 
      :model="formData" 
      label-width="120px"
      ref="formRef"
      @submit.prevent="submitForm"
    >
      <template v-for="(item, index) in uiSchema" :key="index">
        <!-- 普通输入框 -->
        <el-form-item 
          v-if="item.type === 'input'" 
          :label="item.label" 
          :prop="item.key"
          :rules="item.required ? [{ required: true, message: `${item.label}不能为空` }] : []"
        >
          <el-input v-model="formData[item.key]" :placeholder="`请输入${item.label}`" />
        </el-form-item>
        
        <!-- 表格编辑器 -->
        <el-form-item 
          v-if="item.type === 'table-editor'" 
          :label="item.label" 
          :prop="item.key"
        >
          <TableEditor 
            v-model="formData[item.key]" 
            :columns="item.columns"
          />
        </el-form-item>
      </template>
      
      <el-form-item>
        <el-button type="primary" native-type="submit">提交</el-button>
      </el-form-item>
    </el-form>
  </template>
  
  <script setup>
  import { ref, watch } from 'vue'
  import { ElMessage } from 'element-plus'
  import TableEditor from './TableEditor.vue'
  
  const props = defineProps({
    uiSchema: {
      type: Array,
      required: true
    },
    initialData: {
      type: Object,
      default: () => ({})
    }
  })
  
  const emit = defineEmits(['submit'])
  
  const formRef = ref(null)
  const formData = ref({})
  
  // 初始化表单数据
  function buildFormData(schema, initial) {
    const data = {}
    schema.forEach(item => {
      data[item.key] = initial[item.key] || (item.type === 'table-editor' ? [] : '')
    })
    return data
  }
  
  watch([
    () => props.uiSchema,
    () => props.initialData
  ], ([newSchema, newInitial]) => {
    formData.value = buildFormData(newSchema, newInitial)
    if (formRef.value) {
      formRef.value.clearValidate && formRef.value.clearValidate()
    }
  }, { immediate: true })
  
  // 提交表单
  const submitForm = async () => {
    try {
      await formRef.value.validate()
      emit('submit', formData.value)
    } catch (error) {
      ElMessage.error('请检查表单填写是否正确')
    }
  }
  </script>