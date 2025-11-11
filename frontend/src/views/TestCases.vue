<template>
	<div class="cases-container">
		<div class="page-header">
			<h2>测试用例列表</h2>
			<el-button type="primary" @click="router.push(`/components`)">
				<el-icon><Plus /></el-icon>
				新增用例
			</el-button>
		</div>

		<el-card class="cases-card">
			<div class="search-bar">
				<el-input
					v-model="searchQuery"
					placeholder="搜索用例名称或描述"
					style="width: 300px"
					clearable
					@input="handleSearch"
				>
					<template #prefix>
						<el-icon><Search /></el-icon>
					</template>
				</el-input>

				<el-select v-model="statusFilter" placeholder="状态筛选" style="width: 150px" @change="handleFilter">
					<el-option label="全部" value="" />
					<el-option label="草稿" value="草稿" />
					<el-option label="可执行" value="可执行" />
					<el-option label="禁用" value="禁用" />
				</el-select>

				<div class="spacer"></div>
			</div>

			<el-table
				:data="cases"
				style="width: 100%"
				v-loading="loading"
				row-key="id"
				class="cases-table"
				@row-dblclick="onRowDblClick"
			>
				<!-- ID、名称、描述 -->
				<el-table-column prop="id" label="用例ID" width="120" class-name="col-id" align="left" header-align="left" />
				<el-table-column prop="name" label="用例名称" min-width="160" align="left" header-align="left" show-overflow-tooltip />
				<el-table-column prop="description" label="用例描述" min-width="260" align="left" header-align="left" show-overflow-tooltip />

				<!-- 类型 -->
				<el-table-column prop="type" label="类型" width="120" align="center" header-align="center">
					<template #default="scope">
						<el-tag :type="getTypeTag(scope.row.type)" size="small">{{ scope.row.type || '-' }}</el-tag>
					</template>
				</el-table-column>

				<!-- 状态 -->
				<el-table-column prop="status" label="状态" width="100" align="center" header-align="center">
					<template #default="scope">
						<el-tag :type="getStatusType(scope.row.status)" size="small">{{ scope.row.status }}</el-tag>
					</template>
				</el-table-column>

				<!-- 优先级 -->
				<el-table-column prop="priority" label="优先级" width="100" align="center" header-align="center">
					<template #default="scope">
						<el-tag :type="getPriorityTag(scope.row.priority)" size="small">{{ scope.row.priority }}</el-tag>
					</template>
				</el-table-column>

				<!-- 创建人 -->
				<el-table-column prop="created_by" label="创建人" width="120" align="center" header-align="center" />

				<!-- 更新时间 -->
				<el-table-column prop="updated_at" label="更新时间" width="180" align="center" header-align="center">
					<template #default="scope">
						{{ formatDate(scope.row.updated_at) }}
					</template>
				</el-table-column>

				<!-- 操作 -->
				<el-table-column label="操作" width="200" align="center" header-align="center" fixed="right">
					<template #default="scope">
						<el-button link type="primary" size="small" @click="viewDetail(scope.row)">查看</el-button>
						<el-button link type="primary" size="small" @click="editCase(scope.row)">编辑</el-button>
						<el-button link type="danger" size="small" @click="deleteCase(scope.row)">删除</el-button>
					</template>
				</el-table-column>
			</el-table>

			<!-- 分页 -->
			<div class="pagination">
				<el-pagination
					v-model:current-page="currentPage"
					v-model:page-size="pageSize"
					:page-sizes="[10, 20, 50, 100]"
					:total="total"
					layout="total, sizes, prev, pager, next, jumper"
					@size-change="handleSizeChange"
					@current-change="handleCurrentChange"
				/>
			</div>
		</el-card>
	</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { getTestCaseList, deleteTestCase } from '@/api/testCase'

const router = useRouter()

// 响应式数据
const cases = ref([])
const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 加载测试用例列表
const loadCases = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      size: pageSize.value,
      search: searchQuery.value || undefined,
      status: statusFilter.value || undefined
    }
    
    const response = await getTestCaseList(params)
    if (response.data.status === 'success') {
      cases.value = response.data.data.items
      total.value = response.data.data.total
    } else {
      throw new Error(response.data.message || '获取测试用例列表失败')
    }
  } catch (error) {
    console.error('加载测试用例列表失败:', error)
    ElMessage.error('加载测试用例列表失败')
    // 降级处理：使用模拟数据
    cases.value = [
      { id: 1, name: '用户登录功能测试', description: '测试用户登录功能的正确性', type: '功能测试', status: '可执行', priority: '高', created_by: 'admin', updated_at: new Date().toISOString() },
      { id: 2, name: '数据导出性能测试', description: '测试大数据量导出的性能', type: '性能测试', status: '草稿', priority: '中', created_by: 'tester', updated_at: new Date().toISOString() }
    ]
    total.value = cases.value.length
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
  loadCases()
}

// 筛选处理
const handleFilter = () => {
  currentPage.value = 1
  loadCases()
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  loadCases()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadCases()
}

// 标签类型映射
const getTypeTag = (type) => {
  const typeMap = {
    '功能测试': 'primary',
    '性能测试': 'success', 
    '安全测试': 'warning',
    '兼容性测试': 'info'
  }
  return typeMap[type] || 'default'
}

const getStatusType = (status) => {
  const types = { '草稿': 'info', '可执行': 'success', '禁用': 'danger' }
  return types[status] || 'info'
}

const getPriorityTag = (priority) => {
  const priorityMap = {
    '高': 'danger',
    '中': 'warning',
    '低': 'info'
  }
  return priorityMap[priority] || 'default'
}

// 日期格式化
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 操作函数
const viewDetail = (row) => {
  router.push(`/test-case-detail/${row.id}`)
}

const editCase = (row) => {
  ElMessage.info(`编辑用例: ${row.name}`)
  // 预留编辑功能
}

const deleteCase = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除测试用例 "${row.name}"？`, '提示', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })
    
    const response = await deleteTestCase(row.id)
    if (response.data.status === 'success') {
      ElMessage.success('删除测试用例成功')
      loadCases() // 重新加载列表
    } else {
      throw new Error(response.data.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除测试用例失败:', error)
      ElMessage.error('删除测试用例失败')
    }
  }
}

const onRowDblClick = (row) => {
  viewDetail(row)
}

// 生命周期
onMounted(() => {
  loadCases()
})
</script>

<style scoped>
.cases-container {
	padding: 20px;
}

.page-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20px;
}

.page-header h2 {
	margin: 0;
	color: #303133;
}

.cases-card {
	margin-bottom: 20px;
}

.search-bar {
	display: flex;
	align-items: center;
	gap: 16px;
	margin-bottom: 20px;
}
.search-bar .spacer { flex: 1 1 auto; }

.pagination {
	display: flex;
	justify-content: center;
	margin-top: 20px;
}
</style>