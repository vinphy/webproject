<template>
	<div class="edit-test-case">
		<div class="page-header">
			<el-button type="primary" @click="goBack">
				<!-- <img src="../assets/demo.svg" class="icon" style="width: 16px; height: 16px; margin-right: 8px;" /> -->
				返回列表
			</el-button>
			<h2>{{ editingTestCase.name }}</h2>
			<el-button type="primary" @click="saveTestCase">
				<!-- <img src="../assets/demo.svg" class="icon" style="width: 16px; height: 16px; margin-right: 8px;" /> -->
				保存
			</el-button>
		</div>

		<el-card class="test-case-editor-card">
			<div class="editor-header">
				<h3>测试用例流程</h3>
				<div class="header-actions">
					<el-button type="primary" @click="generateSql">
						<!-- <img src="../assets/demo.svg" class="icon" style="width: 16px; height: 16px; margin-right: 8px;" /> -->
						生成SQL
					</el-button>
					<el-button type="success" @click="executeTest">
						<!-- <img src="../assets/demo.svg" class="icon" style="width: 16px; height: 16px; margin-right: 8px;" /> -->
						执行测试
					</el-button>
				</div>
			</div>
			<div class="editor-content">
				<div class="toolbox">
					<h4>模块库</h4>
					<div class="modules">
						<div 
							v-for="module in modules" 
							:key="module.id"
							class="module-item"
							@dragstart="onDragStart($event, module)"
							draggable="true"
						>
							<el-icon :size="24">{{ module.icon }}</el-icon>
							<span>{{ module.name }}</span>
							<el-tooltip :content="module.tooltip" placement="right">
								<el-icon class="tooltip-icon"><QuestionFilled /></el-icon>
							</el-tooltip>
						</div>
					</div>
				</div>
				<div class="canvas" @drop="onDrop" @dragover.prevent>
					<div class="canvas-header">
						<el-button type="primary" @click="addModule">添加模块</el-button>
						<el-button type="info" @click="clearCanvas">清空画布</el-button>
					</div>
					<div class="canvas-grid">
						<div 
							v-for="(node, index) in editingTestCase.steps" 
							:key="index"
							class="node"
							:class="{'node-configured': node.parameters && node.parameters.length > 0}"
						>
							<div class="node-header">
								<h5>{{ node.name }}</h5>
								<div class="node-actions">
									<el-button size="small" @click="configureNode(index)">
										<!-- <img src="../assets/demo.svg" class="icon" style="width: 16px; height: 16px; margin-right: 8px;" /> -->
										配置
									</el-button>
									<el-button size="small" type="danger" @click="removeModule(index)">
										<!-- <img src="../assets/demo.svg" class="icon" style="width: 16px; height: 16px; margin-right: 8px;" /> -->
										删除
									</el-button>
								</div>
							</div>
							<div class="node-content">
								<p>{{ node.description }}</p>
								<div v-if="node.parameters && node.parameters.length > 0" class="node-params">
									<h6>参数：</h6>
									<ul>
										<li v-for="(param, paramIndex) in node.parameters" :key="paramIndex">
											{{ param.name }}: {{ param.value }}
										</li>
									</ul>
								</div>
							</div>
							<div class="node-connectors">
								<div class="connector top"></div>
								<div class="connector bottom"></div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</el-card>

		<!-- 节点配置对话框 -->
		<el-dialog
			v-model="nodeConfigDialogVisible"
			title="配置模块参数"
			width="700px"
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
				
				<!-- SQL查询模块特殊配置 -->
				<template v-if="currentNode.name === 'SQL查询'">
					<el-form-item label="选择表">
						<el-select v-model="currentNode.table" placeholder="请选择表">
							<el-option 
								v-for="table in databaseTables" 
								:key="table.name" 
								:label="table.name" 
								:value="table.name"
							/>
						</el-select>
					</el-form-item>
					<el-form-item label="选择字段">
						<el-select 
							v-model="currentNode.fields" 
							multiple 
							placeholder="请选择字段"
							filterable
						>
							<el-option 
								v-for="field in getTableFields(currentNode.table)" 
								:key="field" 
								:label="field" 
								:value="field"
							/>
						</el-select>
					</el-form-item>
					<el-form-item label="查询条件">
						<el-button type="primary" @click="addCondition">添加条件</el-button>
						<div v-for="(condition, index) in currentNode.conditions" :key="index" class="condition-item">
							<el-select v-model="condition.field" placeholder="字段" style="width: 120px; margin-right: 10px">
								<el-option 
									v-for="field in getTableFields(currentNode.table)" 
									:key="field" 
									:label="field" 
									:value="field"
								/>
							</el-select>
							<el-select v-model="condition.operator" placeholder="操作符" style="width: 100px; margin-right: 10px">
								<el-option label="=" value="=" />
								<el-option label="!=" value="!=" />
								<el-option label=">" value=">" />
								<el-option label="<" value="<" />
								<el-option label=">=" value=">=" />
								<el-option label="<=" value="<=" />
								<el-option label="LIKE" value="LIKE" />
							</el-select>
							<el-input v-model="condition.value" placeholder="值" style="flex: 1; margin-right: 10px" />
							<el-button type="danger" @click="removeCondition(index)">删除</el-button>
						</div>
					</el-form-item>
					<el-form-item label="排序">
						<el-select v-model="currentNode.orderBy" placeholder="排序字段" style="width: 150px; margin-right: 10px">
							<el-option 
								v-for="field in getTableFields(currentNode.table)" 
								:key="field" 
								:label="field" 
								:value="field"
							/>
						</el-select>
						<el-select v-model="currentNode.orderDirection" placeholder="排序方向" style="width: 100px">
							<el-option label="升序" value="ASC" />
							<el-option label="降序" value="DESC" />
						</el-select>
					</el-form-item>
					<el-form-item label="限制行数">
						<el-input-number v-model="currentNode.limit" :min="1" :max="1000" />
					</el-form-item>
				</template>
				
				<!-- 数据库连接模块特殊配置 -->
				<template v-else-if="currentNode.name === '数据库连接'">
					<el-form-item label="连接字符串">
						<el-input v-model="currentNode.connectionString" placeholder="数据库连接字符串" />
					</el-form-item>
					<el-form-item label="用户名">
						<el-input v-model="currentNode.username" placeholder="数据库用户名" />
					</el-form-item>
					<el-form-item label="密码">
						<el-input v-model="currentNode.password" type="password" placeholder="数据库密码" />
					</el-form-item>
				</template>
				
				<!-- SQL92合规性测试模块特殊配置 -->
				<template v-else-if="currentNode.name === 'SQL92合规性测试'">
					<el-form-item label="测试类型">
						<el-select v-model="currentNode.testType" placeholder="请选择测试类型">
							<el-option label="基本SQL语句" value="basic_sql" />
							<el-option label="数据类型支持" value="data_types" />
							<el-option label="约束支持" value="constraints" />
							<el-option label="连接查询" value="joins" />
							<el-option label="事务支持" value="transactions" />
						</el-select>
					</el-form-item>
					<el-form-item label="测试表名">
						<el-input v-model="currentNode.testTable" placeholder="请输入测试表名" />
					</el-form-item>
					<el-form-item label="测试数据量">
						<el-input-number v-model="currentNode.testDataSize" :min="1" :max="10000" />
					</el-form-item>
				</template>
				
				<!-- 性能测试模块特殊配置 -->
			<template v-else-if="currentNode.name === '性能测试'">
				<el-form-item label="测试类型">
					<el-select v-model="currentNode.performanceTestType" placeholder="请选择测试类型">
						<el-option label="单表查询性能" value="single_table" />
						<el-option label="多表连接性能" value="multi_table" />
						<el-option label="索引性能" value="index" />
						<el-option label="并发性能" value="concurrency" />
						<el-option label="大数据量插入" value="bulk_insert" />
					</el-select>
				</el-form-item>
				<el-form-item label="测试表名">
					<el-input v-model="currentNode.testTable" placeholder="请输入测试表名" />
				</el-form-item>
				<el-form-item label="测试数据量">
					<el-input-number v-model="currentNode.testDataSize" :min="1000" :max="1000000" />
				</el-form-item>
				<el-form-item label="并发用户数" v-if="currentNode.performanceTestType === 'concurrency'">
					<el-input-number v-model="currentNode.concurrency" :min="1" :max="1000" />
				</el-form-item>
				<el-form-item label="测试持续时间(秒)" v-if="currentNode.performanceTestType === 'concurrency'">
					<el-input-number v-model="currentNode.duration" :min="10" :max="3600" />
				</el-form-item>
			</template>
			
			<!-- 创建数据库模块特殊配置 -->
			<template v-else-if="currentNode.name === '创建数据库'">
				<el-form-item label="数据库名" required>
					<el-input v-model="currentNode.databaseName" placeholder="请输入数据库名" />
				</el-form-item>
				<el-form-item label="字符集">
					<el-select v-model="currentNode.charset" placeholder="请选择字符集">
						<el-option label="utf8mb4" value="utf8mb4" />
						<el-option label="utf8" value="utf8" />
						<el-option label="gbk" value="gbk" />
					</el-select>
				</el-form-item>
				<el-form-item label="排序规则">
					<el-select v-model="currentNode.collation" placeholder="请选择排序规则">
						<el-option label="utf8mb4_unicode_ci" value="utf8mb4_unicode_ci" />
						<el-option label="utf8mb4_general_ci" value="utf8mb4_general_ci" />
						<el-option label="utf8_unicode_ci" value="utf8_unicode_ci" />
					</el-select>
				</el-form-item>
			</template>
			
			<!-- 创建表模块特殊配置 -->
			<template v-else-if="currentNode.name === '创建表'">
				<el-form-item label="数据库名" required>
					<el-select v-model="currentNode.databaseName" placeholder="请选择数据库">
						<el-option 
							v-for="db in databaseList" 
							:key="db.name" 
							:label="db.name" 
							:value="db.name"
						/>
					</el-select>
				</el-form-item>
				<el-form-item label="表名" required>
					<el-input v-model="currentNode.tableName" placeholder="请输入表名" />
				</el-form-item>
				<el-form-item label="字段定义" required>
					<el-button type="primary" @click="addColumn">添加字段</el-button>
					<div v-for="(column, index) in currentNode.columns" :key="index" class="column-item">
						<el-input v-model="column.fieldName" placeholder="字段名" style="width: 120px; margin-right: 10px" />
						<el-select v-model="column.dataType" placeholder="数据类型" style="width: 120px; margin-right: 10px">
							<el-option label="INT" value="INT" />
							<el-option label="VARCHAR" value="VARCHAR" />
							<el-option label="TEXT" value="TEXT" />
							<el-option label="DATE" value="DATE" />
							<el-option label="TIME" value="TIME" />
							<el-option label="DATETIME" value="DATETIME" />
							<el-option label="DECIMAL" value="DECIMAL" />
						</el-select>
						<el-checkbox v-model="column.notNull" label="不允许为空" style="margin-right: 10px" />
						<el-checkbox v-model="column.primaryKey" label="主键" style="margin-right: 10px" />
						<el-checkbox v-model="column.autoIncrement" label="自增" style="margin-right: 10px" />
						<el-input v-model="column.comment" placeholder="注释" style="flex: 1; margin-right: 10px" />
						<el-button type="danger" @click="removeColumn(index)">删除</el-button>
					</div>
				</el-form-item>
			</template>
				
				<!-- 其他模块的通用参数配置 -->
				<template v-else>
					<el-form-item label="参数">
						<el-button type="primary" @click="addParameter">添加参数</el-button>
						<div v-for="(param, index) in currentNode.parameters" :key="index" class="parameter-item">
							<el-input v-model="param.name" placeholder="参数名" style="width: 150px; margin-right: 10px" />
							<el-input v-model="param.value" placeholder="参数值" style="flex: 1; margin-right: 10px" />
							<el-button type="danger" @click="removeParameter(index)">删除</el-button>
						</div>
					</el-form-item>
				</template>
			</el-form>
			<template #footer>
				<span class="dialog-footer">
					<el-button @click="nodeConfigDialogVisible = false">取消</el-button>
					<el-button type="primary" @click="saveNodeConfig">确定</el-button>
				</span>
			</template>
		</el-dialog>

		<!-- SQL生成结果对话框 -->
		<el-dialog
			v-model="sqlResultDialogVisible"
			title="生成的SQL语句"
			width="800px"
		>
			<el-input
				v-model="generatedSql"
				type="textarea"
				rows="10"
				readonly
			/>
			<template #footer>
				<span class="dialog-footer">
					<el-button @click="sqlResultDialogVisible = false">关闭</el-button>
					<el-button type="primary" @click="copySql">复制SQL</el-button>
				</span>
			</template>
		</el-dialog>

		<!-- 测试执行结果对话框 -->
		<el-dialog
			v-model="testResultDialogVisible"
			title="测试执行结果"
			width="800px"
		>
			<el-card v-if="testResult.success" type="success" shadow="never">
				<template #header>
					<div class="card-header">
						<!-- <img src="../assets/demo.svg" class="icon" style="width: 16px; height: 16px; margin-right: 8px;" /> -->
						<span>测试执行成功</span>
					</div>
				</template>
				<div class="test-result-content">
					<p>执行时间: {{ testResult.executionTime }}</p>
					<p>影响行数: {{ testResult.affectedRows }}</p>
					<p>执行结果: {{ testResult.message }}</p>
				</div>
			</el-card>
			<el-card v-else type="danger" shadow="never">
				<template #header>
					<div class="card-header">
						<!-- <img src="../assets/demo.svg" class="icon" style="width: 16px; height: 16px; margin-right: 8px;" /> -->
						<span>测试执行失败</span>
					</div>
				</template>
				<div class="test-result-content">
					<p>执行时间: {{ testResult.executionTime }}</p>
					<p>错误信息: {{ testResult.message }}</p>
				</div>
			</el-card>
			<template #footer>
				<span class="dialog-footer">
					<el-button @click="testResultDialogVisible = false">关闭</el-button>
				</span>
			</template>
		</el-dialog>
	</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

import { getTestCaseDetail, updateTestCase, executeTestCase } from '@/api/testCase'

const router = useRouter()
const route = useRoute()

// 响应式数据
const editingTestCase = ref({
	id: null,
	name: '',
	description: '',
	type: '功能测试',
	priority: '中',
	status: '草稿',
	steps: []
})

// 对话框相关
const nodeConfigDialogVisible = ref(false)
const sqlResultDialogVisible = ref(false)
const testResultDialogVisible = ref(false)

// 当前配置的节点
const currentNode = ref({
	name: '',
	description: '',
	parameters: []
})

// 当前编辑的节点索引
const currentNodeIndex = ref(-1)

// 生成的SQL
const generatedSql = ref('')

// 测试执行结果
const testResult = ref({
	success: false,
	executionTime: '',
	affectedRows: 0,
	message: ''
})

// 模拟数据库列表
const databaseList = ref([
	{ name: 'person' },
	{ name: 'test_db' }
])

// 模拟数据库表结构
const databaseTables = ref([
	{ name: 'users', fields: ['id', 'name', 'email', 'age', 'created_at'] },
	{ name: 'orders', fields: ['id', 'user_id', 'product_id', 'amount', 'status', 'created_at'] },
	{ name: 'products', fields: ['id', 'name', 'price', 'stock', 'category'] }
])

// 模块库
const modules = ref([
	// { id: 1, name: '数据库连接', icon: '../assets/demo.svg', tooltip: '配置数据库连接信息' },
	// { id: 2, name: 'SQL查询', icon: '../assets/demo.svg', tooltip: '自动生成SQL查询语句' },
	// { id: 3, name: '数据验证', icon: '../assets/demo.svg', tooltip: '验证查询结果' },
	// { id: 4, name: '循环注入', icon: '../assets/demo.svg', tooltip: '循环执行SQL注入数据' },
	// { id: 5, name: '压力测试', icon: '../assets/demo.svg', tooltip: '测试数据库性能' },
	// { id: 6, name: 'SQL92合规性测试', icon: '../assets/demo.svg', tooltip: '测试SQL92标准合规性' },
	// { id: 7, name: '性能测试', icon: '../assets/demo.svg', tooltip: '测试数据库性能指标' }
	{ id: 1, name: '数据库连接', tooltip: '配置数据库连接信息' },
	{ id: 2, name: 'SQL查询', tooltip: '自动生成SQL查询语句' },
	{ id: 3, name: '数据验证', tooltip: '验证查询结果' },
	{ id: 4, name: '循环注入', tooltip: '循环执行SQL注入数据' },
	{ id: 5, name: '压力测试', tooltip: '测试数据库性能' },
	{ id: 6, name: 'SQL92合规性测试', tooltip: '测试SQL92标准合规性' },
	{ id: 7, name: '性能测试', tooltip: '测试数据库性能指标' },
	{ id: 8, name: '创建数据库', tooltip: '创建新的数据库' },
	{ id: 9, name: '创建表', tooltip: '创建新的数据表' }
])

// 加载测试用例
const loadTestCase = async () => {
	const testCaseId = route.params.id
	if (!testCaseId) {
		ElMessage.error('测试用例ID不存在')
		router.push('/custom')
		return
	}

	try {
		const response = await getTestCaseDetail(testCaseId)
		if (response.data.status === 'success') {
			editingTestCase.value = {
				...response.data.data,
				steps: response.data.data.steps || []
			}
		} else {
			throw new Error(response.data.message || '获取测试用例失败')
		}
	} catch (error) {
		console.error('加载测试用例失败:', error)
		ElMessage.error('加载测试用例失败')
		router.push('/custom')
	}
}

// 返回列表
const goBack = () => {
	router.push('/custom')
}

// 保存测试用例
const saveTestCase = async () => {
	if (!editingTestCase.value.name) {
		ElMessage.error('请输入测试用例名称')
		return
	}

	try {
		const response = await updateTestCase(editingTestCase.value.id, {
			name: editingTestCase.value.name,
			description: editingTestCase.value.description,
			test_type: editingTestCase.value.type,
			priority: editingTestCase.value.priority,
			status: editingTestCase.value.status,
			steps: editingTestCase.value.steps
		})

		if (response.data.status === 'success') {
			ElMessage.success('测试用例保存成功')
			router.push('/custom')
		} else {
			throw new Error(response.data.message || '保存测试用例失败')
		}
	} catch (error) {
		console.error('保存测试用例失败:', error)
		ElMessage.error('保存测试用例失败')
	}
}

// 拖拽开始
const onDragStart = (event, module) => {
	event.dataTransfer.setData('module', JSON.stringify(module))
}

// 拖拽释放
const onDrop = (event) => {
	event.preventDefault()
	const moduleData = JSON.parse(event.dataTransfer.getData('module'))
	addModule(moduleData)
}

// 添加模块
const addModule = (module = null) => {
	const newModule = module || {
		id: Date.now(),
		name: '新模块',
		description: '模块描述',
		parameters: []
	}

	editingTestCase.value.steps.push({
		name: newModule.name,
		description: newModule.description,
		parameters: []
	})
}

// 删除模块
const removeModule = (index) => {
	editingTestCase.value.steps.splice(index, 1)
}

// 获取表字段
const getTableFields = (tableName) => {
	const table = databaseTables.value.find(t => t.name === tableName)
	return table ? table.fields : []
}

// 添加查询条件
const addCondition = () => {
	if (!currentNode.value.conditions) {
		currentNode.value.conditions = []
	}
	currentNode.value.conditions.push({ field: '', operator: '=', value: '' })
}

// 删除查询条件
const removeCondition = (index) => {
	if (currentNode.value.conditions) {
		currentNode.value.conditions.splice(index, 1)
	}
}

// 配置节点
const configureNode = (index) => {
	currentNodeIndex.value = index
	// 深拷贝，确保修改不影响原始数据
	currentNode.value = JSON.parse(JSON.stringify(editingTestCase.value.steps[index]))
	// 初始化必要的属性
	if (currentNode.value.name === 'SQL查询') {
		if (!currentNode.value.fields) currentNode.value.fields = []
		if (!currentNode.value.conditions) currentNode.value.conditions = []
		if (!currentNode.value.orderDirection) currentNode.value.orderDirection = 'ASC'
	} else if (currentNode.value.name === '创建表') {
		if (!currentNode.value.columns) currentNode.value.columns = []
	}
	nodeConfigDialogVisible.value = true
}

// 添加字段
const addColumn = () => {
	if (!currentNode.value.columns) {
		currentNode.value.columns = []
	}
	currentNode.value.columns.push({
		fieldName: '',
		dataType: 'INT',
		notNull: false,
		primaryKey: false,
		autoIncrement: false,
		comment: ''
	})
}

// 删除字段
const removeColumn = (index) => {
	if (currentNode.value.columns) {
		currentNode.value.columns.splice(index, 1)
	}
}

// 添加参数
const addParameter = () => {
	if (!currentNode.value.parameters) {
		currentNode.value.parameters = []
	}
	currentNode.value.parameters.push({ name: '', value: '' })
}

// 删除参数
const removeParameter = (index) => {
	if (currentNode.value.parameters) {
		currentNode.value.parameters.splice(index, 1)
	}
}

// 保存节点配置
const saveNodeConfig = () => {
	if (currentNodeIndex.value >= 0) {
		editingTestCase.value.steps[currentNodeIndex.value] = { ...currentNode.value }
		nodeConfigDialogVisible.value = false
		ElMessage.success('模块配置保存成功')
	}
}

// 清空画布
const clearCanvas = () => {
	ElMessageBox.confirm('确定要清空画布吗？', '提示', {
		type: 'warning',
		confirmButtonText: '确定',
		cancelButtonText: '取消'
	}).then(() => {
		editingTestCase.value.steps = []
		ElMessage.success('画布已清空')
	}).catch(() => {
		// 取消操作
	})
}

// 生成SQL
const generateSql = () => {
	// 自动生成SQL语句，根据模块配置
	let sql = ''

	editingTestCase.value.steps.forEach((step, index) => {
			switch (step.name) {
				case '数据库连接':
					sql += `-- 数据库连接配置\n`
					if (step.connectionString) {
						sql += `-- 连接字符串: ${step.connectionString}\n`
					}
					if (step.username) {
						sql += `-- 用户名: ${step.username}\n`
					}
					sql += `\n`
					break
				case '创建数据库':
					sql += `-- 创建数据库\n`
					if (step.databaseName) {
						sql += `CREATE DATABASE IF NOT EXISTS \`${step.databaseName}\``
						if (step.charset) {
							sql += ` CHARACTER SET ${step.charset}`
						}
						if (step.collation) {
							sql += ` COLLATE ${step.collation}`
						}
						sql += `;\n\n`
					} else {
						sql += `-- 请输入数据库名\n\n`
					}
					break
				case '创建表':
					sql += `-- 创建表\n`
					if (step.databaseName && step.tableName && step.columns && step.columns.length > 0) {
						sql += `USE \`${step.databaseName}\`;\n`
						sql += `CREATE TABLE \`${step.databaseName}\` .\`${step.tableName}\` (\n`
						const fieldLines = []
						step.columns.forEach(column => {
							if (column.fieldName && column.dataType) {
								let line = `    \`${column.fieldName}\` ${column.dataType}`
								if (column.notNull) line += ' NOT NULL'
								if (column.primaryKey) line += ' PRIMARY KEY'
								if (column.autoIncrement) line += ' AUTO_INCREMENT'
								if (column.comment) line += ` COMMENT '${column.comment}'`
								fieldLines.push(line)
							}
						})
						sql += fieldLines.join(',\n')
						sql += `\n);\n\n`
					} else {
						sql += `-- 请配置数据库名、表名和字段\n\n`
					}
					break
				case 'SQL查询':
					sql += `-- SQL查询\n`
					if (step.table) {
						// 生成SELECT语句
						const fields = step.fields && step.fields.length > 0 ? step.fields.join(', ') : '*'
						sql += `SELECT ${fields} FROM ${step.table}`
						
						// 添加WHERE条件
						if (step.conditions && step.conditions.length > 0) {
							const conditions = step.conditions
								.filter(c => c.field && c.operator && c.value)
								.map(c => {
									let value = c.value
									// 处理字符串值
									if (typeof value === 'string' && !value.match(/^\d+$/)) {
										value = `'${value}'`
									}
									return `${c.field} ${c.operator} ${value}`
								})
							
							if (conditions.length > 0) {
								sql += ` WHERE ${conditions.join(' AND ')}`
							}
						}
						
						// 添加ORDER BY
						if (step.orderBy) {
							sql += ` ORDER BY ${step.orderBy} ${step.orderDirection || 'ASC'}`
						}
						
						// 添加LIMIT
						if (step.limit) {
							sql += ` LIMIT ${step.limit}`
						}
						
						sql += `;\n\n`
					} else {
						sql += `-- 请选择表\n\n`
					}
					break
			case '数据验证':
				sql += `-- 数据验证\n`
				if (step.parameters) {
					step.parameters.forEach(param => {
						sql += `-- ${param.name}: ${param.value}\n`
					})
				}
				sql += `\n`
				break
			case '循环注入':
				sql += `-- 循环注入\n`
				if (step.parameters) {
					const loopParam = step.parameters.find(p => p.name === 'loopCount')
					const injectParam = step.parameters.find(p => p.name === 'injectSql')
					if (loopParam && injectParam) {
						sql += `-- 循环 ${loopParam.value} 次\n`
						sql += `${injectParam.value}\n\n`
					}
				}
				break
			case '压力测试':
				sql += `-- 压力测试\n`
				if (step.parameters) {
					const pressureParam = step.parameters.find(p => p.name === 'concurrency')
					if (pressureParam) {
						sql += `-- 并发数: ${pressureParam.value}\n`
					}
				}
				sql += `\n`
				break
			case 'SQL92合规性测试':
				sql += `-- SQL92合规性测试\n`
				if (step.testType) {
					switch (step.testType) {
						case 'basic_sql':
							sql += `-- 基本SQL语句测试\n`
							sql += `SELECT * FROM ${step.testTable || 'test_table'};\n`
							sql += `INSERT INTO ${step.testTable || 'test_table'} (id, name) VALUES (1, 'test');\n`
							sql += `UPDATE ${step.testTable || 'test_table'} SET name = 'updated' WHERE id = 1;\n`
							sql += `DELETE FROM ${step.testTable || 'test_table'} WHERE id = 1;\n`
							break
						case 'data_types':
							sql += `-- 数据类型支持测试\n`
							sql += `CREATE TABLE ${step.testTable || 'test_types'} (\n`
							sql += `    id INTEGER,\n`
							sql += `    name VARCHAR(50),\n`
							sql += `    amount DECIMAL(10,2),\n`
							sql += `    is_active BOOLEAN,\n`
							sql += `    created_date DATE,\n`
							sql += `    created_time TIME,\n`
							sql += `    created_timestamp TIMESTAMP\n`
							sql += `);\n`
							break
						case 'constraints':
							sql += `-- 约束支持测试\n`
							sql += `CREATE TABLE ${step.testTable || 'test_pk'} (id INTEGER PRIMARY KEY, name VARCHAR(50));\n`
							sql += `CREATE TABLE ${step.testTable || 'test_fk'} (id INTEGER PRIMARY KEY, ref_id INTEGER REFERENCES ${step.testTable || 'test_pk'}(id));\n`
							sql += `CREATE TABLE ${step.testTable || 'test_unique'} (id INTEGER, name VARCHAR(50) UNIQUE);\n`
							sql += `CREATE TABLE ${step.testTable || 'test_check'} (id INTEGER, age INTEGER CHECK (age > 0));\n`
							break
						case 'joins':
							sql += `-- 连接查询测试\n`
							sql += `SELECT * FROM ${step.testTable || 'table1'} INNER JOIN ${step.testTable || 'table2'} ON ${step.testTable || 'table1'}.id = ${step.testTable || 'table2'}.ref_id;\n`
							sql += `SELECT * FROM ${step.testTable || 'table1'} LEFT JOIN ${step.testTable || 'table2'} ON ${step.testTable || 'table1'}.id = ${step.testTable || 'table2'}.ref_id;\n`
							sql += `SELECT * FROM ${step.testTable || 'table1'} RIGHT JOIN ${step.testTable || 'table2'} ON ${step.testTable || 'table1'}.id = ${step.testTable || 'table2'}.ref_id;\n`
							break
						case 'transactions':
							sql += `-- 事务支持测试\n`
							sql += `BEGIN TRANSACTION;\n`
							sql += `INSERT INTO ${step.testTable || 'test_table'} (id, name) VALUES (1, 'test');\n`
							sql += `UPDATE ${step.testTable || 'test_table'} SET name = 'updated' WHERE id = 1;\n`
							sql += `COMMIT;\n`
							sql += `\nBEGIN TRANSACTION;\n`
							sql += `INSERT INTO ${step.testTable || 'test_table'} (id, name) VALUES (2, 'test2');\n`
							sql += `ROLLBACK;\n`
							break
					}
				}
				sql += `\n`
				break
			case '性能测试':
				sql += `-- 性能测试\n`
				if (step.performanceTestType) {
					switch (step.performanceTestType) {
						case 'single_table':
							sql += `-- 单表查询性能测试\n`
							sql += `-- 全表扫描\n`
							sql += `SELECT * FROM ${step.testTable || 'test_table'};\n`
							sql += `-- 带条件查询\n`
							sql += `SELECT * FROM ${step.testTable || 'test_table'} WHERE id = 1;\n`
							sql += `-- 带排序查询\n`
							sql += `SELECT * FROM ${step.testTable || 'test_table'} ORDER BY id;\n`
							sql += `-- 带LIMIT查询\n`
							sql += `SELECT * FROM ${step.testTable || 'test_table'} LIMIT 100;\n`
							break
						case 'multi_table':
							sql += `-- 多表连接性能测试\n`
							sql += `SELECT * FROM ${step.testTable || 'table1'} JOIN ${step.testTable || 'table2'} ON ${step.testTable || 'table1'}.id = ${step.testTable || 'table2'}.ref_id;\n`
							sql += `SELECT * FROM ${step.testTable || 'table1'} JOIN ${step.testTable || 'table2'} ON ${step.testTable || 'table1'}.id = ${step.testTable || 'table2'}.ref_id JOIN ${step.testTable || 'table3'} ON ${step.testTable || 'table2'}.id = ${step.testTable || 'table3'}.ref_id;\n`
							break
						case 'index':
							sql += `-- 索引性能测试\n`
							sql += `-- 创建索引\n`
							sql += `CREATE INDEX idx_id ON ${step.testTable || 'test_table'}(id);\n`
							sql += `-- 带索引列查询\n`
							sql += `SELECT * FROM ${step.testTable || 'test_table'} WHERE id = 1;\n`
							break
						case 'concurrency':
							sql += `-- 并发性能测试\n`
							sql += `-- 并发用户数: ${step.concurrency || 100}\n`
							sql += `-- 测试持续时间: ${step.duration || 300}秒\n`
							sql += `-- 混合操作: 查询、插入、更新、删除\n`
							break
						case 'bulk_insert':
							sql += `-- 大数据量插入性能测试\n`
							sql += `-- 插入 ${step.testDataSize || 10000} 条数据\n`
							sql += `INSERT INTO ${step.testTable || 'test_table'} (id, name) VALUES\n`
							// 生成批量插入语句
							let values = []
							for (let i = 1; i <= Math.min(step.testDataSize || 10000, 1000); i++) {
								values.push(`(${i}, 'test${i}')`)
							}
							sql += values.join(',\n') + ';\n'
							break
					}
				}
				sql += `\n`
				break
			default:
				sql += `-- ${step.name}\n\n`
				break
		}
	})

	generatedSql.value = sql
	sqlResultDialogVisible.value = true
	ElMessage.success('SQL生成成功')
}

// 复制SQL
const copySql = () => {
	navigator.clipboard.writeText(generatedSql.value)
	ElMessage.success('SQL已复制到剪贴板')
}

// 执行测试
const executeTest = async () => {
	try {
		const response = await executeTestCase(editingTestCase.value.id, {
			sql: generatedSql.value || ''
		})

		if (response.data.status === 'success') {
			testResult.value = {
				success: true,
				executionTime: response.data.data.executionTime || '',
				affectedRows: response.data.data.affectedRows || 0,
				message: response.data.data.message || '测试执行成功'
			}
		} else {
			testResult.value = {
				success: false,
				executionTime: '',
				affectedRows: 0,
				message: response.data.message || '测试执行失败'
			}
		}
		testResultDialogVisible.value = true
	} catch (error) {
		console.error('执行测试失败:', error)
		testResult.value = {
			success: false,
			executionTime: '',
			affectedRows: 0,
			message: error.message || '测试执行失败'
		}
		testResultDialogVisible.value = true
	}
}

// 生命周期
onMounted(() => {
	loadTestCase()
})
</script>

<style scoped>
.edit-test-case {
	padding: 20px;
}

.page-header {
	display: flex;
	align-items: center;
	gap: 20px;
	margin-bottom: 20px;
}

.page-header h2 {
	margin: 0;
	color: #303133;
	flex: 1;
}

.test-case-editor-card {
	margin-bottom: 20px;
}

.editor-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20px;
	padding-bottom: 10px;
	border-bottom: 1px solid #e4e7ed;
}

.editor-header h3 {
	margin: 0;
	color: #303133;
}

.header-actions {
	display: flex;
	gap: 10px;
}

.editor-content {
	display: flex;
	gap: 20px;
	overflow: hidden;
	min-height: 600px;
}

.toolbox {
	width: 220px;
	background-color: #f5f7fa;
	padding: 16px;
	border-radius: 4px;
	overflow-y: auto;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.toolbox h4 {
	margin-top: 0;
	margin-bottom: 16px;
	color: #303133;
	font-size: 14px;
	font-weight: 600;
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
	padding: 12px;
	background-color: #fff;
	border: 1px solid #e4e7ed;
	border-radius: 4px;
	cursor: move;
	transition: all 0.3s;
	position: relative;
}

.module-item:hover {
	border-color: #409eff;
	box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
	transform: translateY(-2px);
}

.tooltip-icon {
	margin-left: auto;
	color: #909399;
	font-size: 14px;
}

.canvas {
	flex: 1;
	background-color: #fafafa;
	border: 1px dashed #d9d9d9;
	border-radius: 4px;
	padding: 20px;
	overflow: auto;
	position: relative;
	background-image: linear-gradient(#e8e8e8 1px, transparent 1px),
	                  linear-gradient(90deg, #e8e8e8 1px, transparent 1px);
	background-size: 20px 20px;
}

.canvas-header {
	display: flex;
	gap: 10px;
	margin-bottom: 20px;
}

.canvas-grid {
	display: flex;
	flex-direction: column;
	gap: 40px;
	position: relative;
}

/* 连接线 */
.canvas-grid::before {
	content: '';
	position: absolute;
	top: 60px;
	left: 50%;
	width: 2px;
	height: calc(100% - 120px);
	background-color: #d9d9d9;
	z-index: 0;
}

.node {
	background-color: #fff;
	border: 2px solid #e4e7ed;
	border-radius: 8px;
	padding: 20px;
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	position: relative;
	z-index: 1;
	transition: all 0.3s;
	width: 400px;
	align-self: center;
}

.node:hover {
	border-color: #409eff;
	box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.node-configured {
	border-color: #67c23a;
	box-shadow: 0 0 0 2px rgba(103, 194, 58, 0.2);
}

.node-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 15px;
	padding-bottom: 10px;
	border-bottom: 1px solid #f0f0f0;
}

.node-header h5 {
	margin: 0;
	color: #303133;
	font-size: 16px;
	font-weight: 600;
}

.node-actions {
	display: flex;
	gap: 8px;
}

.node-content {
	color: #606266;
	font-size: 14px;
}

.node-params {
	margin-top: 15px;
	padding-top: 15px;
	border-top: 1px solid #f0f0f0;
}

.node-params h6 {
	margin: 0 0 10px 0;
	color: #303133;
	font-size: 14px;
	font-weight: 600;
}

.node-params ul {
	margin: 0;
	padding-left: 20px;
}

.node-params li {
	margin-bottom: 5px;
	font-size: 13px;
}

/* 连接器 */
.node-connectors {
	position: absolute;
	left: 50%;
	transform: translateX(-50%);
	width: 2px;
	height: 20px;
	background-color: #d9d9d9;
}

.node-connectors .connector {
	position: absolute;
	left: 50%;
	transform: translateX(-50%);
	width: 10px;
	height: 10px;
	border-radius: 50%;
	background-color: #409eff;
	border: 2px solid #fff;
	box-shadow: 0 0 0 1px #409eff;
}

.node-connectors .connector.top {
	top: -5px;
}

.node-connectors .connector.bottom {
	bottom: -5px;
}

.parameter-item {
	display: flex;
	align-items: center;
	margin-top: 10px;
}

.condition-item {
		display: flex;
		align-items: center;
		margin-top: 10px;
		padding: 10px;
		background-color: #f9f9f9;
		border-radius: 4px;
	}

	.column-item {
		display: flex;
		align-items: center;
		margin-top: 10px;
		padding: 10px;
		background-color: #f9f9f9;
		border-radius: 4px;
	}

.dialog-footer {
	display: flex;
	justify-content: flex-end;
	gap: 10px;
}

.card-header {
	display: flex;
	align-items: center;
	gap: 10px;
}

.test-result-content {
	margin-top: 10px;
}

.test-result-content p {
	margin: 5px 0;
}

/* 响应式设计 */
@media screen and (max-width: 768px) {
	.editor-content {
		flex-direction: column;
	}
	
	.toolbox {
		width: 100%;
		max-height: 200px;
	}
	
	.node {
		width: 100%;
	}
}
</style>