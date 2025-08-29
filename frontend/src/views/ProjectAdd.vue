<template>
  <div class="project-add-page">
    <el-card class="single-card">
      <div class="steps-header">
        <div class="left">
          <div class="title-row">
            <h2 class="page-title">新增项目</h2>
            <el-tag size="small" type="info">第 {{ currentStep }} / 4 步</el-tag>
          </div>
          <p class="steps-sub">按照步骤填写项目信息</p>
        </div>
        <div class="right">
          <el-button text @click="router.go(-1)">
            <el-icon style="margin-right: 6px;"><ArrowLeft /></el-icon>
            返回
          </el-button>
        </div>
      </div>

      <el-steps :active="currentStep - 1" align-center finish-status="success" class="steps">
        <el-step :icon="currentStep === 1 ? Check : ''" title="基础信息" />
        <el-step title="测试用例选择" />
        <el-step title="项目参数配置" />
        <el-step title="项目入库" />
      </el-steps>

      <div class="section-sep"></div>

      <div class="section-header">
        <span class="section-title">项目基础信息</span>
      </div>

      <div class="form-wrap">
        <div v-if="currentStep === 1">
          <el-form ref="formRef" :model="form" :rules="rules" label-width="128px" size="large">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="项目编号" prop="projectCode">
                  <el-input v-model="form.projectCode" placeholder="请输入项目编号" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="项目名称" prop="projectName">
                  <el-input v-model="form.projectName" placeholder="请输入项目名称" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="项目类型" prop="projectType">
                  <el-select v-model="form.projectType" placeholder="请选择项目类型" style="width: 100%">
                    <el-option label="功能测试" value="功能测试" />
                    <el-option label="性能测试" value="性能测试" />
                    <el-option label="安全测试" value="安全测试" />
                    <el-option label="兼容性测试" value="兼容性测试" />
                    <el-option label="自动化测试" value="自动化测试" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="测试负责人" prop="testLeader">
                  <el-input v-model="form.testLeader" placeholder="请输入负责人姓名" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="开始日期" prop="startDate">
                  <el-date-picker v-model="form.startDate" type="date" placeholder="选择开始日期" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="结束日期" prop="endDate">
                  <el-date-picker v-model="form.endDate" type="date" placeholder="选择结束日期" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="项目描述" prop="projectDesc">
              <el-input v-model="form.projectDesc" type="textarea" :rows="5" placeholder="请输入项目详细描述" />
            </el-form-item>

            <el-form-item label="测试成员">
              <div class="members">
                <div class="member" v-for="(m, idx) in form.teamMembers" :key="m.id">
                  <el-avatar :size="32" :src="m.avatar" />
                  <span class="name">{{ m.name }}</span>
                  <el-button text type="danger" @click="removeMember(idx)">移除</el-button>
                </div>
                <el-button type="primary" link @click="addMember">
                  <el-icon><Plus /></el-icon>
                  添加成员
                </el-button>
              </div>
            </el-form-item>
          </el-form>
        </div>

        <div v-else-if="currentStep === 2" class="placeholder">
          <div class="section-note">测试用例选择（占位）</div>
          <el-empty description="测试用例选择（占位）" />
        </div>

        <div v-else-if="currentStep === 3" class="placeholder">
          <div class="section-note">项目参数配置（占位）</div>
          <el-empty description="项目参数配置（占位）" />
        </div>

        <div v-else-if="currentStep === 4" class="placeholder">
          <div class="section-note">项目入库（占位）</div>
          <el-empty description="项目入库（占位）" />
        </div>
      </div>

      <div class="footer-actions">
        <el-button :disabled="currentStep === 1" @click="prevStep">上一步</el-button>
        <div class="right">
          <el-button v-if="currentStep < 4" type="primary" @click="nextStep">下一步</el-button>
          <el-button v-else type="success" @click="submitProject">提交项目</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, ArrowLeft, Check } from '@element-plus/icons-vue'

const router = useRouter()
const currentStep = ref(1)
const formRef = ref()

const form = reactive({
  projectCode: '',
  projectName: '',
  projectType: '',
  testLeader: '',
  startDate: '',
  endDate: '',
  projectDesc: '',
  teamMembers: [
    { id: 1, name: '李测试', avatar: 'https://picsum.photos/id/1012/60/60' },
    { id: 2, name: '王工程师', avatar: 'https://picsum.photos/id/1027/60/60' }
  ]
})

const rules = {
  projectCode: [
    { required: true, message: '请输入项目编号', trigger: 'blur' },
    { min: 2, max: 32, message: '长度 2-32 个字符', trigger: 'blur' }
  ],
  projectName: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 2, max: 64, message: '长度 2-64 个字符', trigger: 'blur' }
  ],
  projectType: [
    { required: true, message: '请选择项目类型', trigger: 'change' }
  ],
  testLeader: [
    { required: true, message: '请输入测试负责人', trigger: 'blur' }
  ],
  startDate: [
    { required: true, message: '请选择开始日期', trigger: 'change' }
  ],
  endDate: [
    { required: true, message: '请选择结束日期', trigger: 'change' }
  ],
  projectDesc: [
    { required: true, message: '请输入项目描述', trigger: 'blur' },
    { min: 10, message: '不少于 10 个字符', trigger: 'blur' }
  ]
}

const addMember = () => {
  const nextId = form.teamMembers.length ? Math.max(...form.teamMembers.map(m => m.id)) + 1 : 1
  form.teamMembers.push({ id: nextId, name: '新成员', avatar: `https://picsum.photos/id/${1000 + nextId}/60/60` })
}

const removeMember = (idx) => {
  form.teamMembers.splice(idx, 1)
}

const nextStep = async () => {
  if (currentStep.value === 1) {
    if (!formRef.value) return
    const valid = await formRef.value.validate().catch(() => false)
    if (!valid) return
  }
  currentStep.value = Math.min(4, currentStep.value + 1)
}

const prevStep = () => {
  currentStep.value = Math.max(1, currentStep.value - 1)
}

const submitProject = () => {
  ElMessage.success('项目提交成功')
  router.push('/projects')
}
</script>

<style scoped>
.project-add-page { padding: 20px; }

.single-card :deep(.el-card__body) { padding: 16px; }

.steps-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 8px;
}
.title-row { display: flex; align-items: center; gap: 10px; }
.page-title { margin: 0; font-size: 18px; font-weight: 700; color: #2b3a4b; }
.steps-sub { margin: 6px 0 0 0; color: #8a97a8; font-size: 12px; }

.steps { margin: 0; }
:deep(.el-step__title) { font-size: 14px; }
:deep(.el-steps .el-step:nth-child(1) .el-step__title) { color: #409EFF; }
:deep(.el-steps .el-step .el-step__icon) { border-radius: 50%; width: 28px; height: 28px; font-size: 14px; }
:deep(.el-steps .is-process .el-step__icon) { background-color: #409EFF; border-color: #409EFF; color: #fff; }

.section-sep { height: 1px; background: #edf1f7; margin: 12px 0; }
.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.section-title { font-size: 16px; font-weight: 600; color: #2c3e50; }
.section-note { color: #8592a6; margin-bottom: 8px; }

.form-wrap { padding-top: 4px; }

.placeholder { padding: 24px 0 8px; }

.footer-actions { display: flex; align-items: center; justify-content: space-between; margin-top: 16px; padding-top: 10px; border-top: 1px solid #edf1f7; }

.members { display: flex; gap: 12px; flex-wrap: wrap; }
.member { display: inline-flex; align-items: center; gap: 8px; padding: 6px 10px; border: 1px solid #ebeef5; background: #fff; border-radius: 6px; }
.member .name { color: #303133; }
</style>
  