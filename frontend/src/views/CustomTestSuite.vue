<template>
	<div class="custom-test-suite">
		<div class="page-header">
			<h2>自定义测试用例库</h2>
			<el-button type="primary" @click="showCreateDialog">
				<el-icon><Plus /></el-icon>
				新建测试用例
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

				<el-select v-model="typeFilter" placeholder="类型筛选" style="width: 150px" @change="handleFilter">
					<el-option label="全部" value="" />
					<el-option label="功能测试" value="功能测试" />
					<el-option label="性能测试" value="性能测试" />
					<el-option label="安全测试" value="安全测试" />
					<el-option label="兼容性测试" value="兼容性测试" />
				</el-select>

				<div class="spacer"></div>
			</div>

			<el-table
				:data="testCases"
				style="width: 100%"
				v-loading="loading"
				row-key="id"
				class="cases-table"
				@row-dblclick="onRowDblClick"
			>
				<el-table-column prop="id" label="ID" width="40" class-name="col-id" align="left" header-align="left" />
				<el-table-column prop="name" label="用例名称" min-width="100" align="left" header-align="left" show-overflow-tooltip />
				<el-table-column prop="type" label="类型" width="120" align="center" header-align="center">
					<template #default="scope">
						<el-tag :type="getTypeTag(scope.row.type)" size="small">{{ scope.row.type || '-' }}</el-tag>
					</template>
				</el-table-column>
				<el-table-column prop="status" label="状态" width="100" align="center" header-align="center">
					<template #default="scope">
						<el-tag :type="getStatusType(scope.row.status)" size="small">{{ scope.row.status || '未知' }}</el-tag>
					</template>
				</el-table-column>
				<el-table-column prop="priority" label="优先级" width="100" align="center" header-align="center">
					<template #default="scope">
						<el-tag :type="getPriorityTag(scope.row.priority)" size="small">{{ scope.row.priority || '无' }}</el-tag>
					</template>
				</el-table-column>
				<el-table-column prop="created_by" label="创建人" width="120" align="center" header-align="center" />
				<el-table-column prop="updated_at" label="更新时间" width="180" align="center" header-align="center">
					<template #default="scope">
						{{ formatDate(scope.row.updated_at) }}
					</template>
				</el-table-column>
				<el-table-column prop="description" label="用例描述" min-width="260" align="left" header-align="left" show-overflow-tooltip />
				<el-table-column label="操作" width="200" align="center" header-align="center" fixed="right">
					<template #default="scope">
						<el-button link type="primary" size="small" @click="editTestCase(scope.row)">编辑</el-button>
						<el-button link type="danger" size="small" @click="handleDeleteTestCase(scope.row)">删除</el-button>
					</template>
				</el-table-column>
			</el-table>

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

		<!-- 新建测试用例对话框 -->
		<el-dialog
			v-model="createDialogVisible"
			title="新建测试用例"
			width="600px"
		>
			<el-form :model="newTestCase" label-width="120px">
				<el-form-item label="用例名称">
					<el-input v-model="newTestCase.name" placeholder="请输入测试用例名称" />
				</el-form-item>
				<el-form-item label="用例描述">
					<el-input
						v-model="newTestCase.description"
						type="textarea"
						placeholder="请输入测试用例描述"
						rows="3"
					/>
				</el-form-item>
				<el-form-item label="测试类型">
					<el-select v-model="newTestCase.type" placeholder="请选择测试类型">
						<el-option label="功能测试" value="功能测试" />
						<el-option label="性能测试" value="性能测试" />
						<el-option label="安全测试" value="安全测试" />
						<el-option label="兼容性测试" value="兼容性测试" />
					</el-select>
				</el-form-item>
				<el-form-item label="优先级">
					<el-select v-model="newTestCase.priority" placeholder="请选择优先级">
						<el-option label="高" value="高" />
						<el-option label="中" value="中" />
						<el-option label="低" value="低" />
					</el-select>
				</el-form-item>
			</el-form>
			<template #footer>
				<span class="dialog-footer">
					<el-button @click="createDialogVisible = false">取消</el-button>
					<el-button type="primary" @click="handleCreateTestCase">确定</el-button>
				</span>
			</template>
		</el-dialog>



		<!-- 节点配置对话框 -->
		<el-dialog
			v-model="nodeConfigDialogVisible"
			title="配置模块参数"
			width="500px"
		>
			<el-form :model="currentNode" label-width="100px">
				<el-form-item label="模块名称">
					<el-input v-model="currentNode.name" />
				</el-form-item>
				<el-form-item label="模块描述">
					<el-input
						v-model="currentNode.description"
						type="textarea"
						rows="3"
					/>
				</el-form-item>
				<el-form-item label="参数">
					<el-button type="primary" @click="addParameter">添加参数</el-button>
					<div v-for="(param, index) in currentNode.parameters" :key="index" class="parameter-item">
						<el-input v-model="param.name" placeholder="参数名" style="width: 150px; margin-right: 10px" />
						<el-input v-model="param.value" placeholder="参数值" style="flex: 1; margin-right: 10px" />
						<el-button type="danger" @click="removeParameter(index)">删除</el-button>
					</div>
				</el-form-item>
			</el-form>
			<template #footer>
				<span class="dialog-footer">
					<el-button @click="nodeConfigDialogVisible = false">取消</el-button>
					<el-button type="primary" @click="saveNodeConfig">确定</el-button>
				</span>
			</template>
		</el-dialog>
	</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Setting, Monitor, Refresh, WarningFilled, Check, DataLine } from '@element-plus/icons-vue'
import { getTestCaseList, createTestCase, updateTestCase, deleteTestCase } from '@/api/testCase'

const router = useRouter()

// 响应式数据
const testCases = ref([])
const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const typeFilter = ref('')

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 对话框相关
const createDialogVisible = ref(false)
const nodeConfigDialogVisible = ref(false)

// 新建测试用例数据
const newTestCase = ref({
	name: '',
	description: '',
	type: '功能测试',
	priority: '中'
})

// 模块库
const modules = ref([
	{ id: 1, name: '数据库连接', icon: DataLine },
	{ id: 2, name: 'SQL查询', icon: Monitor },
	{ id: 3, name: '数据验证', icon: Check },
	{ id: 4, name: '循环注入', icon: Refresh },
	{ id: 5, name: '压力测试', icon: WarningFilled }
])

// 加载测试用例列表
const loadTestCases = async () => {
	loading.value = true
	try {
		const params = {
			page: currentPage.value,
			size: pageSize.value,
			search: searchQuery.value || undefined,
			type: typeFilter.value || undefined,
			status: statusFilter.value || undefined
		}
		
		const response = await getTestCaseList(params)
		if (response.data.status === 'success') {
			testCases.value = response.data.data.items
			total.value = response.data.data.total
		} else {
			throw new Error(response.data.message || '获取测试用例列表失败')
		}
	} catch (error) {
		console.error('加载测试用例列表失败:', error)
		ElMessage.error('加载测试用例列表失败')
		// 降级处理：使用模拟数据
		testCases.value = [
			{ id: 1, name: '用户登录功能测试', description: '测试用户登录功能的正确性', type: '功能测试', status: '可执行', priority: '高', created_by: 'admin', updated_at: new Date().toISOString() },
			{ id: 2, name: '数据导出性能测试', description: '测试大数据量导出的性能', type: '性能测试', status: '草稿', priority: '中', created_by: 'tester', updated_at: new Date().toISOString() }
		]
		total.value = testCases.value.length
	} finally {
		loading.value = false
	}
}

// 搜索处理
const handleSearch = () => {
	currentPage.value = 1
	loadTestCases()
}

// 筛选处理
const handleFilter = () => {
	currentPage.value = 1
	loadTestCases()
}

// 分页处理
const handleSizeChange = (val) => {
	pageSize.value = val
	currentPage.value = 1
	loadTestCases()
}

const handleCurrentChange = (val) => {
	currentPage.value = val
	loadTestCases()
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

// 显示创建对话框
const showCreateDialog = () => {
	newTestCase.value = {
		name: '',
		description: '',
		type: '功能测试',
		priority: '中'
	}
	createDialogVisible.value = true
}

// 创建测试用例
const handleCreateTestCase = async () => {
	if (!newTestCase.value.name) {
		ElMessage.error('请输入测试用例名称')
		return
	}

	try {
		const response = await createTestCase({
			name: newTestCase.value.name,
			description: newTestCase.value.description,
			test_type: newTestCase.value.type,
			priority: newTestCase.value.priority,
			steps: []
		})

		if (response.data.status === 'success') {
			ElMessage.success('测试用例创建成功')
			createDialogVisible.value = false
			loadTestCases()
		} else {
			throw new Error(response.data.message || '创建测试用例失败')
		}
	} catch (error) {
		console.error('创建测试用例失败:', error)
		ElMessage.error('创建测试用例失败')
	}
}

// 编辑测试用例
const editTestCase = (row) => {
	router.push(`/custom/edit/${row.id}`)
}

// 删除测试用例
const handleDeleteTestCase = async (row) => {
	try {
		await ElMessageBox.confirm(`确认删除测试用例 "${row.name}"？`, '提示', {
			type: 'warning',
			confirmButtonText: '删除',
			cancelButtonText: '取消'
		})
		
		const response = await deleteTestCase(row.id)
		if (response.data.status === 'success') {
			ElMessage.success('删除测试用例成功')
			loadTestCases()
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



// 生命周期
onMounted(() => {
	loadTestCases()
})
</script>

<style scoped>
.custom-test-suite {
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

.test-case-editor {
	height: 60vh;
	display: flex;
	flex-direction: column;
}

.editor-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20px;
	padding-bottom: 10px;
	border-bottom: 1px solid #e4e7ed;
}

.editor-content {
	display: flex;
	flex: 1;
	gap: 20px;
	overflow: hidden;
}

.toolbox {
	width: 200px;
	background-color: #f5f7fa;
	padding: 16px;
	border-radius: 4px;
	overflow-y: auto;
}

.toolbox h4 {
	margin-top: 0;
	margin-bottom: 16px;
	color: #303133;
}

.modules {
	display: flex;
	flex-direction: column;
	gap: 10px;
}

.module-item {
	display: flex;
	align-items: center;
	gap: 10px;
	padding: 10px;
	background-color: #fff;
	border: 1px solid #e4e7ed;
	border-radius: 4px;
	cursor: move;
	transition: all 0.3s;
}

.module-item:hover {
	border-color: #409eff;
	box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.canvas {
	flex: 1;
	background-color: #fafafa;
	border: 1px dashed #d9d9d9;
	border-radius: 4px;
	padding: 20px;
	overflow-y: auto;
	position: relative;
}

.canvas-grid {
	margin-top: 20px;
	display: flex;
	flex-direction: column;
	gap: 20px;
}

.node {
	background-color: #fff;
	border: 1px solid #e4e7ed;
	border-radius: 4px;
	padding: 16px;
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.node-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 10px;
}

.node-header h5 {
	margin: 0;
	color: #303133;
}

.node-content {
	color: #606266;
}

.parameter-item {
	display: flex;
	align-items: center;
	margin-top: 10px;
}

.dialog-footer {
	display: flex;
	justify-content: flex-end;
	gap: 10px;
}
</style>