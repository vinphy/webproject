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
				>
					<template #prefix>
						<el-icon><Search /></el-icon>
					</template>
				</el-input>

				<el-select v-model="statusFilter" placeholder="状态筛选" style="width: 150px">
					<el-option label="全部" value="" />
					<el-option label="草稿" value="草稿" />
					<el-option label="可执行" value="可执行" />
					<el-option label="禁用" value="禁用" />
				</el-select>

				<div class="spacer"></div>
			</div>

			<el-table
				:data="filteredCases"
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
				<el-table-column label="类型" width="120" align="left" header-align="left">
					<template #default="{ row }">
						<el-tag v-if="row.type === '功能'" type="primary" size="small">功能</el-tag>
						<el-tag v-else-if="row.type === '性能'" type="success" size="small">性能</el-tag>
						<el-tag v-else-if="row.type === '安全'" type="warning" size="small">安全</el-tag>
						<el-tag v-else size="small">其他</el-tag>
					</template>
				</el-table-column>

				<!-- 状态、创建时间 -->
				<el-table-column prop="status" label="状态" width="100" align="left" header-align="left">
					<template #default="{ row }">
						<el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
					</template>
				</el-table-column>
				<el-table-column prop="createTime" label="创建时间" width="160" align="left" header-align="left" />
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
	</div>
</template>

<script setup>
import { ref, computed, onMounted, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 数据源：localStorage key: test_cases
const cases = ref([])

const loadCases = () => {
	try {
		const saved = localStorage.getItem('test_cases')
		if (saved && saved !== 'null' && saved !== 'undefined') {
			const parsed = JSON.parse(saved)
			cases.value = Array.isArray(parsed) ? parsed : []
		} else {
			// 首次初始化一些示例数据
			cases.value = [
				{ id: 101, name: '数据库插入语句语法校验', description: '验证插入语句语法，涵盖各种插入规则', type: '功能', status: '可执行', createTime: '2024-01-12 10:00:00' },
				{ id: 102, name: '数据库新增语句语法校验', description: '验证新增语句语法，涵盖各种插入规则', type: '性能', status: '草稿', createTime: '2024-01-13 09:30:00' },
				{ id: 103, name: '数据库查询语句语法校验', description: '验证查询语句语法，涵盖各种插入规则。包含聚合查询、模糊查询、关联查询登', type: '安全', status: '可执行', createTime: '2024-01-14 15:20:00' }
			]
			localStorage.setItem('test_cases', JSON.stringify(cases.value))
		}
		total.value = cases.value.length
	} catch (e) {
		ElMessage.error('加载测试用例数据失败')
	}
}

const saveCases = () => {
	try {
		localStorage.setItem('test_cases', JSON.stringify(cases.value))
	} catch {}
}

const filteredCases = computed(() => {
	let filtered = cases.value
	if (searchQuery.value) {
		const q = searchQuery.value.toLowerCase()
		filtered = filtered.filter(c =>
			(c.name || '').toLowerCase().includes(q) ||
			(c.description || '').toLowerCase().includes(q)
		)
	}
	if (statusFilter.value) {
		filtered = filtered.filter(c => c.status === statusFilter.value)
	}
	return filtered
})

const getStatusType = (status) => {
	const types = { '草稿': 'info', '可执行': 'success', '禁用': 'danger' }
	return types[status] || 'info'
}

const handleSizeChange = (val) => {
	pageSize.value = val
	currentPage.value = 1
}
const handleCurrentChange = (val) => { currentPage.value = val }

const onRowDblClick = (row) => {
	router.push(`/test-case-detail/${row.id}`)
}

const createCase = () => {
	// 预留：跳转到新建用例页或弹出对话框
	ElMessage.info('新建用例功能开发中')
}

onMounted(() => { loadCases() })
onActivated(() => { loadCases() })
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

/* 表格样式与 Projects.vue 对齐：左对齐、统一内边距、字号 */
.cases-table :deep(.el-table__header .el-table__cell),
.cases-table :deep(.el-table__body .el-table__cell) {
	padding: 8px 12px;
	text-align: left;
}

.cases-table :deep(.el-table__header .cell),
.cases-table :deep(.el-table__body .cell) {
	display: block;
	text-align: left;
	padding: 0;
}

.cases-table :deep(.el-table__header .cell) { font-size: 14px; font-weight: 600; }
.cases-table :deep(.el-table__body .cell) { font-size: 12px; line-height: 20px; }

/* ID 列固定不换行，等宽数字 */
.cases-table :deep(.col-id .cell) {
	white-space: nowrap;
	font-variant-numeric: tabular-nums;
	font-weight: 600;
	color: #303133;
	font-size: 14px;
}
/* 移除双数行的蓝色字体样式继承 */
.cases-table :deep(.el-table__row:nth-child(even) .el-table__cell) {
  font-weight: normal;
  color: #606266 !important;
}
</style> 