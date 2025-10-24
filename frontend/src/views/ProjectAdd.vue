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
        <span class="section-title">{{ currentStep === 1 ? '项目基础信息' : (currentStep === 2 ? '测试用例选择' : currentStep === 3 ? '项目参数配置' : '项目入库') }}</span>
      </div>

      <div class="form-wrap">
        <div v-if="currentStep === 1">
          <!-- 基础信息表单保持不变 -->
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

        <!-- 步骤2：左右布局 -->
        <div v-else-if="currentStep === 2" class="step2-wrap">
          <el-row :gutter="16">
            <el-col :span="6">
              <div class="step2-left">
                <div class="left-title">选择执行项</div>
                <el-tree
                  ref="step2TreeRef"
                  :data="treeData"
                  show-checkbox
                  node-key="key"
                  :default-checked-keys="defaultCheckedKeys"
                  @check="onTreeCheckChange"
                />
                <div class="left-tip">勾选"测试用例"后，可在右侧选择具体用例</div>
              </div>
            </el-col>
            <el-col :span="18">
              <div class="step2-right" :class="{ disabled: !step2Selections.cases }">
                <div class="right-header">
                  <span class="h-title">测试用例选择</span>
                  <span class="h-sub">共 {{ allTestCases.length }} 条，已选 {{ form.selectedTestCaseIds.length }} 条</span>
                </div>
                <div class="right-body">
                  <div v-if="!step2Selections.cases" class="disabled-overlay">
                    <el-empty description="请先在左侧勾选测试用例" />
                  </div>
                  <el-transfer
                    v-else
                    v-model="form.selectedTestCaseIds"
                    :data="allTestCases"
                    filterable
                    filter-placeholder="搜索测试用例"
                    :titles="['可选测试用例', '已选测试用例']"
                    :props="{ key: 'key', label: 'label' }"
                    :button-texts="['移除', '添加']"
                  >
                    <template #left-footer>
                      <el-button text type="primary" @click="goAddTestCase">
                        <el-icon style="margin-right: 4px;"><Plus /></el-icon>
                        新增用例
                      </el-button>
                    </template>
                  </el-transfer>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 步骤3：项目参数配置 -->
        <div v-else-if="currentStep === 3" class="step3-wrap">
          <el-form ref="paramsFormRef" :model="projectParams" :rules="paramsRules" label-width="140px" size="large">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="测试环境" prop="testEnvironment">
                  <el-select v-model="projectParams.testEnvironment" placeholder="请选择测试环境" style="width: 100%">
                    <el-option label="开发环境" value="dev" />
                    <el-option label="测试环境" value="test" />
                    <el-option label="预生产环境" value="staging" />
                    <el-option label="生产环境" value="prod" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="优先级" prop="priority">
                  <el-select v-model="projectParams.priority" placeholder="请选择优先级" style="width: 100%">
                    <el-option label="低" value="low" />
                    <el-option label="中" value="medium" />
                    <el-option label="高" value="high" />
                    <el-option label="紧急" value="urgent" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="并发用户数" prop="concurrentUsers">
                  <el-input-number v-model="projectParams.concurrentUsers" :min="1" :max="10000" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="测试轮次" prop="testRounds">
                  <el-input-number v-model="projectParams.testRounds" :min="1" :max="10" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="超时时间(分钟)" prop="timeout">
                  <el-input-number v-model="projectParams.timeout" :min="5" :max="1440" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="重试次数" prop="retryCount">
                  <el-input-number v-model="projectParams.retryCount" :min="0" :max="5" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="测试配置">
              <el-checkbox-group v-model="projectParams.testConfigs">
                <el-checkbox label="auto_retry">自动重试失败用例</el-checkbox>
                <el-checkbox label="parallel_execution">并行执行测试</el-checkbox>
                <el-checkbox label="data_cleanup">测试后清理数据</el-checkbox>
                <el-checkbox label="report_generation">自动生成报告</el-checkbox>
                <el-checkbox label="notification">测试完成通知</el-checkbox>
              </el-checkbox-group>
            </el-form-item>

            <el-form-item label="测试数据源">
              <el-radio-group v-model="projectParams.dataSource">
                <el-radio label="mock">模拟数据</el-radio>
                <el-radio label="staging">预生产数据</el-radio>
                <el-radio label="production">生产数据(脱敏)</el-radio>
                <el-radio label="custom">自定义数据</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="通知配置">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="邮件通知" label-width="100px">
                    <el-input v-model="projectParams.emailNotification" placeholder="输入邮箱地址，多个用逗号分隔" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="钉钉通知" label-width="100px">
                    <el-input v-model="projectParams.dingtalkWebhook" placeholder="输入钉钉机器人Webhook地址" />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form-item>

            <el-form-item label="备注">
              <el-input v-model="projectParams.remarks" type="textarea" :rows="3" placeholder="请输入项目参数相关备注" />
            </el-form-item>
          </el-form>
        </div>

        <!-- 步骤4：项目入库确认 -->
        <div v-else-if="currentStep === 4" class="step4-wrap">
          <div class="confirmation-header">
            <el-icon size="24" color="#67C23A"><Check /></el-icon>
            <span class="confirmation-title">请确认项目信息</span>
            <p class="confirmation-subtitle">请仔细核对以下信息，确认无误后提交项目</p>
          </div>

          <div class="confirmation-content">
            <!-- 基础信息确认 -->
            <div class="confirmation-section">
              <div class="section-header">
                <h3 class="section-title">基础信息</h3>
                <el-button text type="primary" @click="editStep(1)">编辑</el-button>
              </div>
              <div class="section-content">
                <el-row :gutter="20">
                  <el-col :span="12">
                    <div class="info-item">
                      <span class="label">项目编号：</span>
                      <span class="value">{{ form.projectCode }}</span>
                    </div>
                  </el-col>
                  <el-col :span="12">
                    <div class="info-item">
                      <span class="label">项目名称：</span>
                      <span class="value">{{ form.projectName }}</span>
                    </div>
                  </el-col>
                </el-row>
                <el-row :gutter="20">
                  <el-col :span="12">
                    <div class="info-item">
                      <span class="label">项目类型：</span>
                      <el-tag type="primary">{{ form.projectType }}</el-tag>
                    </div>
                  </el-col>
                  <el-col :span="12">
                    <div class="info-item">
                      <span class="label">测试负责人：</span>
                      <span class="value">{{ form.testLeader }}</span>
                    </div>
                  </el-col>
                </el-row>
                <el-row :gutter="20">
                  <el-col :span="12">
                    <div class="info-item">
                      <span class="label">开始日期：</span>
                      <span class="value">{{ formatDate(form.startDate) }}</span>
                    </div>
                  </el-col>
                  <el-col :span="12">
                    <div class="info-item">
                      <span class="label">结束日期：</span>
                      <span class="value">{{ formatDate(form.endDate) }}</span>
                    </div>
                  </el-col>
                </el-row>
                <div class="info-item">
                  <span class="label">项目描述：</span>
                  <span class="value">{{ form.projectDesc }}</span>
                </div>
                <div class="info-item">
                  <span class="label">测试成员：</span>
                  <div class="members-preview">
                    <el-avatar v-for="member in form.teamMembers" :key="member.id" :size="32" :src="member.avatar" :title="member.name" />
                  </div>
                </div>
              </div>
            </div>

            <!-- 测试用例选择确认 -->
            <div class="confirmation-section">
              <div class="section-header">
                <h3 class="section-title">测试用例选择</h3>
                <el-button text type="primary" @click="editStep(2)">编辑</el-button>
              </div>
              <div class="section-content">
                <div class="execution-items">
                  <el-tag v-if="step2Selections.vuln" type="success" size="large">漏洞扫描</el-tag>
                  <el-tag v-if="step2Selections.fuzz" type="warning" size="large">模糊测试</el-tag>
                  <el-tag v-if="step2Selections.cases" type="primary" size="large">测试用例</el-tag>
                </div>
                <div v-if="step2Selections.cases && form.selectedTestCaseIds.length > 0" class="test-cases-preview">
                  <div class="test-cases-title">已选择的测试用例 ({{ form.selectedTestCaseIds.length }} 条)：</div>
                  <div class="test-cases-list">
                    <el-tag v-for="caseId in form.selectedTestCaseIds" :key="caseId" class="test-case-tag">
                      {{ getTestCaseName(caseId) }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>

            <!-- 项目参数配置确认 -->
            <div class="confirmation-section">
              <div class="section-header">
                <h3 class="section-title">项目参数配置</h3>
                <el-button text type="primary" @click="editStep(3)">编辑</el-button>
              </div>
              <div class="section-content">
                <el-row :gutter="20">
                  <el-col :span="12">
                    <div class="info-item">
                      <span class="label">测试环境：</span>
                      <el-tag :type="getEnvironmentTagType(projectParams.testEnvironment)">
                        {{ getEnvironmentName(projectParams.testEnvironment) }}
                      </el-tag>
                    </div>
                  </el-col>
                  <el-col :span="12">
                    <div class="info-item">
                      <span class="label">优先级：</span>
                      <el-tag :type="getPriorityTagType(projectParams.priority)">
                        {{ getPriorityName(projectParams.priority) }}
                      </el-tag>
                    </div>
                  </el-col>
                </el-row>
                <el-row :gutter="20">
                  <el-col :span="12">
                    <div class="info-item">
                      <span class="label">并发用户数：</span>
                      <span class="value">{{ projectParams.concurrentUsers }}</span>
                    </div>
                  </el-col>
                  <el-col :span="12">
                    <div class="info-item">
                      <span class="label">测试轮次：</span>
                      <span class="value">{{ projectParams.testRounds }}</span>
                    </div>
                  </el-col>
                </el-row>
                <el-row :gutter="20">
                  <el-col :span="12">
                    <div class="info-item">
                      <span class="label">超时时间：</span>
                      <span class="value">{{ projectParams.timeout }} 分钟</span>
                    </div>
                  </el-col>
                  <el-col :span="12">
                    <div class="info-item">
                      <span class="label">重试次数：</span>
                      <span class="value">{{ projectParams.retryCount }}</span>
                    </div>
                  </el-col>
                </el-row>
                <div class="info-item">
                  <span class="label">测试配置：</span>
                  <div class="config-tags">
                    <el-tag v-for="config in projectParams.testConfigs" :key="config" size="small">
                      {{ getConfigName(config) }}
                    </el-tag>
                  </div>
                </div>
                <div class="info-item">
                  <span class="label">测试数据源：</span>
                  <el-tag type="info">{{ getDataSourceName(projectParams.dataSource) }}</el-tag>
                </div>
                <div v-if="projectParams.remarks" class="info-item">
                  <span class="label">备注：</span>
                  <span class="value">{{ projectParams.remarks }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="footer-actions">
        <el-button :disabled="currentStep === 1" @click="prevStep">上一步</el-button>
        <div class="right">
          <el-button v-if="currentStep < 4" type="primary" @click="nextStep">下一步</el-button>
          <el-button v-else type="success" :loading="submitting" @click="submitProject">提交项目</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, onActivated, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '../utils/auth'
import { Plus, ArrowLeft, Check } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const currentStep = ref(1)
const formRef = ref()
const paramsFormRef = ref()
// 标记表单是否已经在流转过程中被验证过（避免重复触发 validate 导致不必要的阻塞）
const baseValidated = ref(false)
const paramsValidated = ref(false)
const submitting = ref(false)
const didSubmit = ref(false)  // 标记是否刚刚提交成功
const hasLoadedDraft = ref(false)   // 标记是否已加载/重置过（避免重复 load）

// 数据持久化存储键
const STORAGE_KEY = 'project_add_draft'

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
  ],
  selectedTestCaseIds: []
})

// 项目参数配置
const projectParams = reactive({
  testEnvironment: 'test',
  priority: 'medium',
  concurrentUsers: 10,
  testRounds: 1,
  timeout: 30,
  retryCount: 2,
  testConfigs: ['auto_retry', 'report_generation'],
  dataSource: 'mock',
  emailNotification: '',
  dingtalkWebhook: '',
  remarks: ''
})

// 步骤2选择状态
const step2Selections = reactive({ vuln: false, fuzz: false, cases: true })

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

const paramsRules = {
  testEnvironment: [
    { required: true, message: '请选择测试环境', trigger: 'change' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ],
  concurrentUsers: [
    { required: true, message: '请输入并发用户数', trigger: 'blur' }
  ],
  testRounds: [
    { required: true, message: '请输入测试轮次', trigger: 'blur' }
  ],
  timeout: [
    { required: true, message: '请输入超时时间', trigger: 'blur' }
  ],
  retryCount: [
    { required: true, message: '请输入重试次数', trigger: 'blur' }
  ]
}

// 左侧树形复选
const treeData = ref([
  { key: 'vuln', label: '漏洞扫描' },
  { key: 'fuzz', label: '模糊测试' },
  { key: 'cases', label: '测试用例' }
])
const step2TreeRef = ref()
const defaultCheckedKeys = ref(Object.keys(step2Selections).filter(k => step2Selections[k]))
const onTreeCheckChange = () => {
  const keys = step2TreeRef.value?.getCheckedKeys(true) || []
  step2Selections.vuln = keys.includes('vuln')
  step2Selections.fuzz = keys.includes('fuzz')
  step2Selections.cases = keys.includes('cases')
}

// 模拟测试用例数据
const allTestCases = ref([
  { key: 1, label: '登录功能用例 - 正常登录' },
  { key: 2, label: '登录功能用例 - 密码错误' },
  { key: 3, label: '注册功能用例 - 邮箱重复' },
  { key: 4, label: '项目列表 - 搜索过滤' },
  { key: 5, label: '接口稳定性 - 重试与超时' },
  { key: 6, label: '权限控制 - 非法访问拦截' },
  { key: 7, label: '上传下载 - 大文件断点续传' },
  { key: 8, label: '移动端适配 - 横竖屏切换' }
])

// 数据持久化相关函数
const saveDraft = () => {
  const draftData = {
    currentStep: currentStep.value,
    form: { ...form },
    projectParams: { ...projectParams },
    step2Selections: { ...step2Selections }
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(draftData))
}

const loadDraft = () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      const draftData = JSON.parse(saved)
      currentStep.value = draftData.currentStep || 1
      
      // 恢复表单数据
      Object.assign(form, draftData.form || {})
      Object.assign(projectParams, draftData.projectParams || {})
      Object.assign(step2Selections, draftData.step2Selections || {})
      
      // 更新树形选择状态
      defaultCheckedKeys.value = Object.keys(step2Selections).filter(k => step2Selections[k])
      
      ElMessage.info('已恢复草稿数据')
    }
  } catch (error) {
    console.error('加载草稿失败:', error)
  }
}

const clearDraft = () => {
  localStorage.removeItem(STORAGE_KEY)
}

// 监听数据变化，自动保存草稿
watch([form, projectParams, step2Selections, currentStep], () => {
  saveDraft()
}, { deep: true })

const goAddTestCase = () => {
  router.push('/testcases/add')
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
    if (valid) baseValidated.value = true
    if (!valid) return
  } else if (currentStep.value === 3) {
    if (!paramsFormRef.value) return
    const valid = await paramsFormRef.value.validate().catch(() => false)
    if (valid) paramsValidated.value = true
    if (!valid) return
  }
  currentStep.value = Math.min(4, currentStep.value + 1)
}

const prevStep = () => {
  currentStep.value = Math.max(1, currentStep.value - 1)
}

const editStep = (step) => {
  currentStep.value = step
}

const submitProject = async () => {
  submitting.value = true
  try {
    // 如果用户在步骤切换时已通过校验，则不必重复 validate（避免恢复草稿或直接路由导致的误报）
    const validBase = baseValidated.value ? true : await formRef.value?.validate().catch(() => false)
    const validParams = paramsValidated.value ? true : await paramsFormRef.value?.validate().catch(() => false)
    if (!validBase || !validParams) {
      ElMessage.error('请完整填写表单后再提交')
      submitting.value = false
      return
    }

    const payload = {
      projectCode: form.projectCode || null,
      projectName: form.projectName,
      projectType: form.projectType || null,
      testLeader: form.testLeader || null,
      startDate: form.startDate || null,
      endDate: form.endDate || null,
      projectDesc: form.projectDesc || null,
      teamMembers: form.teamMembers ? form.teamMembers.map(m => (m && (m.name || m)) ) : [],
      selectedTestCaseIds: form.selectedTestCaseIds || [],
      projectParams: projectParams,
      step2Selections: step2Selections
    }

    const { data } = await api.post('/api/projects', payload)

    if (data && data.id) {
      clearDraft()
      resetFormData()
      didSubmit.value = true
      ElMessage.success('项目创建成功！')
      router.push('/projects')
      return
    }

    // 若后端未返回 id，也视为成功但给予提示
    ElMessage.success('项目已创建（服务器未返回 id）')
    router.push('/projects')
  } catch (error) {
    const msg = error?.response?.data?.detail || error?.message || '项目创建失败，请重试'
    ElMessage.error(msg)
  } finally {
    submitting.value = false
  }
}

// 辅助函数
const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN')
}

const getTestCaseName = (caseId) => {
  const testCase = allTestCases.value.find(c => c.key === caseId)
  return testCase ? testCase.label : `用例 ${caseId}`
}

const getEnvironmentName = (env) => {
  const envMap = {
    dev: '开发环境',
    test: '测试环境',
    staging: '预生产环境',
    prod: '生产环境'
  }
  return envMap[env] || env
}

const getEnvironmentTagType = (env) => {
  const typeMap = {
    dev: 'info',
    test: 'primary',
    staging: 'warning',
    prod: 'danger'
  }
  return typeMap[env] || 'info'
}

const getPriorityName = (priority) => {
  const priorityMap = {
    low: '低',
    medium: '中',
    high: '高',
    urgent: '紧急'
  }
  return priorityMap[priority] || priority
}

const getPriorityTagType = (priority) => {
  const typeMap = {
    low: 'info',
    medium: 'primary',
    high: 'warning',
    urgent: 'danger'
  }
  return typeMap[priority] || 'primary'
}

const getConfigName = (config) => {
  const configMap = {
    auto_retry: '自动重试',
    parallel_execution: '并行执行',
    data_cleanup: '数据清理',
    report_generation: '报告生成',
    notification: '完成通知'
  }
  return configMap[config] || config
}

const getDataSourceName = (source) => {
  const sourceMap = {
    mock: '模拟数据',
    staging: '预生产数据',
    production: '生产数据(脱敏)',
    custom: '自定义数据'
  }
  return sourceMap[source] || source
}

// 生命周期
const handleFreshReset = () => {
  clearDraft()
  resetFormData()
  hasLoadedDraft.value = true
}

// 1) 组件 setup 阶段立即处理 fresh，避免先渲染到第4步
if (String(route.query.fresh || '') === '1') {
  handleFreshReset()
}

// 2) mounted 时如果没有 fresh 才加载草稿
onMounted(() => {
  if (!hasLoadedDraft.value) {
    loadDraft()
    hasLoadedDraft.value = true
  }
})

// 3) 组件被 keep-alive 激活时，如带 fresh 再次强制重置
onActivated(() => {
  if (String(route.query.fresh || '') === '1') {
    handleFreshReset()
  }
})

// 4) 监听路由参数变化，用户切换到 fresh=1 时立刻重置
watch(() => route.query.fresh, (val) => {
  if (String(val || '') === '1') {
    handleFreshReset()
  }
})

// 卸载时仅在未提交时保存草稿
onUnmounted(() => {
  if (!didSubmit.value) {
    saveDraft()
  }
})

const resetFormData = () => {
  formRef.value?.resetFields?.()
  paramsFormRef.value?.resetFields?.()
}
</script>

<style scoped>
.project-add-page { padding: 20px; }

.single-card :deep(.el-card__body) { padding: 16px; }

.steps-header { display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 8px; }
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

/* 步骤二布局与样式 */
.step2-wrap { padding-top: 4px; }
.step2-left { background: #fafbff; border: 1px solid #eef2fb; border-radius: 8px; padding: 12px; }
.step2-left .left-title { font-weight: 700; color: #2c3e50; margin-bottom: 8px; font-size: 16px; }
.step2-left :deep(.el-tree-node__label) { font-size: 14px; }
.left-tip { color: #98a2b3; font-size: 12px; margin-top: 10px; }

.step2-right { background: #fff; border: 1px solid #ebeef5; border-radius: 8px; padding: 12px; min-height: 380px; display: flex; flex-direction: column; }
.step2-right.disabled { opacity: 0.6; pointer-events: none; user-select: none; }
.right-header { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 10px; }
.right-header .h-title { font-weight: 600; color: #2c3e50; font-size: 15px; }
.right-header .h-sub { color: #98a2b3; font-size: 12px; }
.right-body { flex: 1; display: flex; align-items: center; justify-content: center; }
.cases-transfer { width: 640px; max-width: 90%; }
.cases-transfer :deep(.el-transfer__buttons) { padding: 0 8px; }
.cases-transfer :deep(.el-transfer-panel__header) { font-weight: 600; }

/* 步骤三样式 */
.step3-wrap { padding-top: 4px; }

/* 步骤四确认页面样式 */
.step4-wrap { padding-top: 4px; }

.confirmation-header {
  text-align: center;
  margin-bottom: 24px;
  padding: 20px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 12px;
  border: 1px solid #bae6fd;
}

.confirmation-title {
  font-size: 20px;
  font-weight: 700;
  color: #0369a1;
  margin-left: 8px;
}

.confirmation-subtitle {
  margin: 8px 0 0 0;
  color: #0c4a6e;
  font-size: 14px;
}

.confirmation-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.confirmation-section {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.confirmation-section .section-header {
  background: #f9fafb;
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
  margin: 0;
}

.confirmation-section .section-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #374151;
}

.section-content {
  padding: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  min-height: 24px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-item .label {
  font-weight: 600;
  color: #6b7280;
  min-width: 100px;
  margin-right: 8px;
}

.info-item .value {
  color: #111827;
  flex: 1;
}

.members-preview {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.execution-items {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.test-cases-preview {
  margin-top: 12px;
}

.test-cases-title {
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
}

.test-cases-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.test-case-tag {
  margin: 2px;
}

.config-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.placeholder { padding: 24px 0 8px; }

.footer-actions { display: flex; align-items: center; justify-content: space-between; margin-top: 16px; padding-top: 10px; border-top: 1px solid #edf1f7; }

.members { display: flex; gap: 12px; flex-wrap: wrap; }
.member { display: inline-flex; align-items: center; gap: 8px; padding: 6px 10px; border: 1px solid #ebeef5; background: #fff; border-radius: 6px; }
.member .name { color: #303133; }
</style>
  