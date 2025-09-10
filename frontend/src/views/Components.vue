<template>
  <div class="module-management">
    <!-- 测试用例输入弹框 -->
    <el-dialog
      v-model="showTestCaseDialog"
      title="创建测试用例"
      width="400px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
    >
      <el-form :model="testCaseForm" :rules="testCaseRules" ref="testCaseFormRef">
        <el-form-item label="测试用例名称" prop="name">
          <el-input 
            v-model="testCaseForm.name" 
            placeholder="请输入测试用例名称"
          />
        </el-form-item>
        <el-form-item label="测试用例描述" prop="description">
          <el-input 
            v-model="testCaseForm.description" 
            placeholder="请输入测试用例描述"
            type="textarea"
            rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showTestCaseDialog = false">取消</el-button>
          <el-button type="primary" @click="handleTestCaseConfirm">
            确认
          </el-button>
        </span>
      </template>
    </el-dialog>


    <div class="module-container">
      <!-- 左侧模块列表 -->
      <div class="module-list">
        <div class="module-list-header">
          <!-- <h3 class="module-title">模块列表</h3> -->
          <el-button 
            type="primary" 
            size="small" 
            @click="showTestCaseDialog = true"
            class="module-manage-btn"
          >
            <el-icon><Setting /></el-icon>
            模块列表
          </el-button>
        </div>
        
        <div class="module-categories">
        <!-- 第一级：大层级 -->
        <div 
          v-for="(categoryData, categoryKey) in availableModules" 
          :key="categoryKey"
          class="module-category"
        >
          <!-- 大层级标题 -->
          <div 
            class="category-header"
            @click="toggleCategory(categoryKey)"
            :class="{ 'expanded': expandedCategories.includes(categoryKey) }"
            :title="categoryData.description"
          >
            <img :src="categoryData.icon" class="category-icon" alt="分类图标" />
            <span class="category-name">{{ categoryData.name }}</span>
            <span class="expand-icon">{{ expandedCategories.includes(categoryKey) ? '▼' : '▶' }}</span>
          </div>
          
          <!-- 第二级：子层级 -->
          <div 
            v-if="expandedCategories.includes(categoryKey)"
            class="sub-categories"
          >
            <div 
              v-for="(subCategoryData, subCategoryKey) in categoryData.children" 
              :key="subCategoryKey"
              class="sub-category"
            >
              <!-- 子层级标题 -->
              <div 
                class="sub-category-header"
                @click="toggleSubCategory(categoryKey, subCategoryKey)"
                :class="{ 'expanded': expandedSubCategories.includes(`${categoryKey}-${subCategoryKey}`) }"
                :title="subCategoryData.description"
              >
                  <div class="sub-category-content">
                <img :src="subCategoryData.icon" class="sub-category-icon" alt="子分类图标" />
                <span class="sub-category-name">{{ subCategoryData.name }}</span>
                <span class="expand-icon">{{ expandedSubCategories.includes(`${categoryKey}-${subCategoryKey}`) ? '▼' : '▶' }}</span>
                  </div>
              </div>
              
              <!-- 第三级：模块列表 -->
              <div 
                v-if="expandedSubCategories.includes(`${categoryKey}-${subCategoryKey}`)"
                class="sub-modules"
              >
                <div 
                  v-for="module in subCategoryData.children" 
                  :key="module.id"
                  class="module-item"
                  :data-subtype="module.subType"
                  draggable="true"
                  @dragstart="handleDragStart($event, module)"
                  :title="module.description"
                >
                    <div class="module-content">
                  <div class="module-info">
                    <span class="module-name">{{ module.name }}</span>
                      </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        </div>
      </div>

      <!-- 右侧绘制区域 -->
      <div class="canvas-area">
        <!-- 标签页组件 -->
        <div class="tabs-container">
          <div class="tabs-header">
            <div 
              v-for="tab in tabs" 
              :key="tab.id"
              class="tab-item"
              :class="{ 'active': tab.active }"
              @click="switchTab(tab.id)"
            >
              <span class="tab-title">{{ tab.title }}</span>
              <span 
                v-if="tabs.length > 1" 
                class="tab-close"
                @click.stop="closeTab(tab.id)"
              >
                ×
              </span>
            </div>
            <div class="tab-add" @click="addNewTab('未命名')">
              +
            </div>
          </div>
        </div>

        <!-- 画布区域 - 为每个标签页创建独立的canvas -->
        <div 
          v-for="tab in tabs" 
          :key="tab.id"
          class="canvas-container"
          :class="{ 'active': tab.active }"
          @dragover.prevent
          @drop="handleDrop"
          @contextmenu="handleCanvasContextMenu"
          @keydown="handleKeyDown"
          @click="handleCanvasClick"
          tabindex="0"
        >
          <div class="canvas" ref="canvasRef" @drop="handleFileDrop" @dragover="handleDragOver" @dragenter="handleDragEnter">
            <!-- 连线层 -->
            <svg class="connections-layer">
              <defs v-if="tab.id === tabs[0].id">
                <marker id="arrowhead-global" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                  <polygon points="0 0, 10 3.5, 0 7" fill="#409EFF" />
                </marker>
              </defs>
              <g class="connection-group">
                <path
                  v-for="connection in connections"
                  :key="connection.id"
                  :d="bezierPath(connection.startPos, connection.endPos)"
                  class="connection-path animated"
                  :marker-end="globalArrowheadUrl"
                />
              </g>
            </svg>
            <!-- 节点 -->
            <div
              v-for="node in placedNodes"
              :key="node.id"
              class="node"
              :data-node-id="node.id"
              :data-type="node.type"
              :style="{
                left: node.x + 'px',
                top: node.y + 'px',
                transform: `scale(${node.scale || 1})`
              }"
              @mousedown="startDrag($event, node)"
              @click="selectNode(node)"
              @dblclick="handleNodeDblClick(node)"
              @contextmenu="showContextMenu($event, node)"
              :class="{ 'selected': selectedNode && selectedNode.id === node.id }"
            >
              <div class="node-header">
                <img :src="node.icon" class="node-icon" alt="节点图标" />
                <span>{{ node.name }}</span>
                <span class="node-type">({{ node.type }})</span>
              </div>
              <div class="node-ports">
                <div class="ports-container">
                  <div 
                    v-for="(input, index) in node.inputs" 
                    :key="'input-' + index"
                    class="port input-port"
                    :class="{ 
                      'connected': input.connected,
                      'connecting': input.connecting,
                      'can-connect': isConnecting && !startPort?.isInput
                    }"
                    :data-port-id="input.id"
                    :style="{ top: `${(index + 1) * 30}px` }"
                    @mousedown.stop="startConnection($event, node, input, true)"
                    @mouseup.stop="handlePortMouseUp($event, node, input, true)"
                  >
                    <div class="port-dot"></div>
                    <div class="port-content">
                      <span class="port-label">{{ input.name }}</span>
                    </div>
                  </div>
                  <div
                    v-for="(output, index) in node.outputs" 
                    :key="'output-' + index"
                    class="port output-port"
                    :class="{ 
                      'connected': output.connected,
                      'connecting': output.connecting,
                      'can-connect': isConnecting && startPort?.isInput
                    }"
                    :data-port-id="output.id"
                    :style="{ top: `${(index + 1) * 30}px` }"
                    @mousedown.stop="startConnection($event, node, output, false)"
                    @mouseup.stop="handlePortMouseUp($event, node, output, false)"
                  >
                    <div class="port-content">
                      <span class="port-label">{{ output.name }}</span>
                    </div>
                    <div class="port-dot"></div>
                  </div>
                </div>
                
                <!-- 参数信息显示在端口区域内 -->
                <div v-if="node.databaseName || node.tableName || (node.parameters && node.parameters.length > 0) || node.condition" class="node-params-display">
                  <div v-if="node.databaseName" class="param-line">
                    <span class="param-label">DB:</span>
                    <span class="param-text">{{ node.databaseName }}</span>
                  </div>
                  <div v-if="node.tableName" class="param-line">
                    <span class="param-label">表:</span>
                    <span class="param-text">{{ node.tableName }}</span>
                  </div>
                  <div v-if="node.parameters && node.parameters.length > 0" class="param-line">
                    <span class="param-label">参数:</span>
                    <span class="param-text">
                      {{ node.parameters.slice(0, 2).map(p => p.name).join(', ') }}{{ node.parameters.length > 2 ? '...' : '' }}
                    </span>
                  </div>
                  <div v-if="node.condition" class="param-line">
                    <span class="param-label">条件:</span>
                    <span class="param-text">
                      {{ node.condition.length > 20 ? node.condition.substring(0, 20) + '...' : node.condition }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 参数配置对话框 -->
    <NodeConfigDialog
      v-model:visible="configDialogVisible"
      :node="currentNode"
      :database-list="databaseList"
      :get-tables-by-database="getTablesByDatabase"
      :get-columns-by-database-table="getColumnsByDatabaseTable"
      @save="handleConfigSave"
    />

    <!-- 代码展示面板 -->
    <div class="code-panel" :class="{ 'code-panel-collapsed': isCodePanelCollapsed }">
      <div class="code-panel-header" @click="toggleCodePanel">
        <span>生成的代码</span>
        <el-icon :class="{ 'is-collapsed': isCodePanelCollapsed }">
          <ArrowRight />
        </el-icon>
      </div>
      <div class="code-panel-content" v-show="!isCodePanelCollapsed">
        <!-- 文件树形结构 -->
        <div v-if="!currentFile" class="file-tree">
          <div class="tree-content">
            <div class="tree-node">
              <div class="tree-item workspace">
                <el-icon><FolderOpened /></el-icon>
                <span>workspace</span>
              </div>
              <div class="tree-children">
                <div v-for="file in fileStructure" :key="file.path" class="tree-node">
                  <div 
                    class="tree-item" 
                    :class="{ 'is-folder': file.type === 'directory' }"
                  >
                    <el-icon 
                      v-if="file.type === 'directory'"
                      class="expand-icon"
                      :class="{ 'is-expanded': expandedFolders.has(file.path) }"
                      @click="toggleFolder(file)"
                    >
                      <ArrowRight />
                    </el-icon>
                    <el-icon v-if="file.type === 'directory'">
                      <Folder v-if="!expandedFolders.has(file.path)" />
                      <FolderOpened v-else />
                    </el-icon>
                    <el-icon v-else>
                      <Document />
                    </el-icon>
                    <span 
                      class="file-name"
                      :class="{ 'draggable-file': file.name.endsWith('_model.json') || file.name.endsWith('_test.json') }"
                      @dblclick="file.type === 'file' ? openFile(file) : null"
                      @click="file.type === 'directory' ? toggleFolder(file) : null"
                      @dragstart="handleFileDragStart($event, file)"
                      draggable="true"
                    >{{ file.name }}</span>
                  </div>
                  <div v-if="file.type === 'directory' && file.children && expandedFolders.has(file.path)" class="tree-children">
                    <div v-for="child in file.children" :key="child.path" class="tree-node">
                      <div 
                        class="tree-item" 
                        :class="{ 'is-folder': child.type === 'directory' }"
                      >
                        <el-icon 
                          v-if="child.type === 'directory'"
                          class="expand-icon"
                          :class="{ 'is-expanded': expandedFolders.has(child.path) }"
                          @click="toggleFolder(child)"
                        >
                          <ArrowRight />
                        </el-icon>
                        <el-icon v-if="child.type === 'directory'">
                          <Folder v-if="!expandedFolders.has(child.path)" />
                          <FolderOpened v-else />
                        </el-icon>
                        <el-icon v-else>
                          <Document />
                        </el-icon>
                        <span 
                          class="file-name"
                          :class="{ 'draggable-file': child.name.endsWith('_model.json') || child.name.endsWith('_test.json')  }"
                          @dblclick="child.type === 'file' ? openFile(child) : null"
                          @click="child.type === 'directory' ? toggleFolder(child) : null"
                          @dragstart="handleFileDragStart($event, child)"
                          draggable="true"
                        >{{ child.name }}</span>
                      </div>
                      <div v-if="child.type === 'directory' && child.children && expandedFolders.has(child.path)" class="tree-children">
                        <div v-for="grandChild in child.children" :key="grandChild.path" class="tree-node">
                          <div 
                            class="tree-item" 
                            :class="{ 'is-folder': grandChild.type === 'directory' }"
                          >
                            <el-icon 
                              v-if="grandChild.type === 'directory'"
                              class="expand-icon"
                              :class="{ 'is-expanded': expandedFolders.has(grandChild.path) }"
                              @click="toggleFolder(grandChild)"
                            >
                              <ArrowRight />
                            </el-icon>
                            <el-icon v-if="grandChild.type === 'directory'">
                              <Folder v-if="!expandedFolders.has(grandChild.path)" />
                              <FolderOpened v-else />
                            </el-icon>
                            <el-icon v-else>
                              <Document />
                            </el-icon>
                            <span 
                              class="file-name"
                              :class="{ 'draggable-file': grandChild.name.endsWith('_model.json') || grandChild.name.endsWith('_test.json')  }"
                              @dblclick="grandChild.type === 'file' ? openFile(grandChild) : null"
                              @click="grandChild.type === 'directory' ? toggleFolder(grandChild) : null"
                              @dragstart="handleFileDragStart($event, grandChild)"
                              draggable="true"
                            >{{ grandChild.name }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 文件内容 -->
        <div v-else class="file-content">
          <div class="file-header">
            <el-button 
              type="text" 
              class="back-button"
              @click="backToTree"
            >
              <el-icon><Back /></el-icon>
              返回
            </el-button>
            <span class="file-name">{{ currentFile.name }}</span>
          </div>
          <div class="file-body">
            <pre><code>{{ currentFile.content }}</code></pre>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 右键菜单 -->
    <div 
      v-show="contextMenuVisible" 
      class="context-menu"
      :style="{ left: contextMenuX + 'px', top: contextMenuY + 'px' }"
    >
      <div class="menu-item" @click="handleGenerateCode">
        <el-icon><Document /></el-icon>
        生成代码
      </div>
      <div class="menu-item" @click="handleDeleteNode">
        <el-icon><Delete /></el-icon>
        删除节点
      </div>
    </div>

    <!-- 画布右键菜单 -->
    <div 
      v-show="showModelMenu" 
      class="context-menu"
      :style="{ left: modelMenuX + 'px', top: modelMenuY + 'px' }"
    >
      <div class="menu-item" @click="handleGenerateModelFile">
        <el-icon><Document /></el-icon>
        生成测试文件
      </div>
    </div>

    <!-- 生成模型文件对话框 -->
    <el-dialog
      v-model="showModelDialog"
      title="生成模型文件"
      width="400px"
    >
      <el-form>
        <el-form-item label="文件名">
          <el-input 
            v-model="modelFileName" 
            placeholder="请输入文件名（不需要.json后缀）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showModelDialog = false">取消</el-button>
          <el-button type="primary" @click="generateModelFile">
            确认
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { 
  Cpu, 
  Connection, 
  DataLine, 
  Monitor,
  Histogram,
  ArrowRight,
  Document,
  Back,
  Folder,
  FolderOpened,
  Delete,
  Setting
} from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage, ElLoading } from 'element-plus'
import NodeConfigDialog from './components/NodeConfigDialog.vue'

//测试用例相关状态
const showTestCaseDialog = ref(true)
const testCaseForm = ref({
  name: '',
  description: ''
})
const testCaseRules = ref({
  name: [
    { required: true, message: '请输入测试用例名称', trigger: 'blur' },
    { max: 50, message: '名称不能超过50个字符', trigger: 'blur' }
  ],
  description: [
    { max: 200, message: '描述不能超过200个字符', trigger: 'blur' }
  ]
})
const testCaseFormRef = ref(null)

// 处理测试用例确认
const handleTestCaseConfirm = async () => {
  if (!testCaseFormRef.value) return
  
  try {
    await testCaseFormRef.value.validate()
    // 验证通过，关闭对话框
    showTestCaseDialog.value = false
    // 将当前活动tab标题更新为测试用例名称
    const currentTab = tabs.value.find(t => t.id === activeTabId.value)
    if (currentTab && testCaseForm.value.name) {
      currentTab.title = testCaseForm.value.name
    }
    ElMessage.success('测试用例创建成功')
  } catch (error) {
    // 验证失败，不关闭对话框
    console.log('测试用例信息验证失败:', error)
  }
}

// 可用模块列表
const availableModules = ref({})

// 展开的分类
const expandedCategories = ref([])
const expandedSubCategories = ref([])

// 切换大层级展开状态
const toggleCategory = (categoryKey) => {
  const index = expandedCategories.value.indexOf(categoryKey)
  if (index > -1) {
    expandedCategories.value.splice(index, 1)
    // 同时收起所有相关的子层级
    expandedSubCategories.value = expandedSubCategories.value.filter(key => !key.startsWith(categoryKey + '-'))
  } else {
    expandedCategories.value.push(categoryKey)
  }
}

// 切换子层级展开状态
const toggleSubCategory = (categoryKey, subCategoryKey) => {
  const key = `${categoryKey}-${subCategoryKey}`
  const index = expandedSubCategories.value.indexOf(key)
  if (index > -1) {
    expandedSubCategories.value.splice(index, 1)
  } else {
    expandedSubCategories.value.push(key)
  }
}


// 加载模型列表
const loadModelModules = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/code/get_model_modules')
    if (response.ok) {
      const data = await response.json()
      if (data.status === 'success') {
        availableModules.value = data.data
        console.log('模型列表加载成功:', data.data)
        // 默认展开第一个大层级
        if (Object.keys(data.data).length > 0) {
          expandedCategories.value = [Object.keys(data.data)[0]]
        }
      }
    }
  } catch (error) {
    console.error('加载模型列表失败:', error)
    // 如果加载失败，使用默认数据
    availableModules.value = {
      database_definition: {
        name: "数据库定义",
        description: "数据库结构定义相关模块",
        icon: "/src/assets/demo.svg",
        children: {
          create: {
            name: "创建操作",
            description: "创建数据库对象",
            icon: "/src/assets/Data.svg",
            children: [
              {
                id: "create_database",
                name: "创建数据库",
                description: "创建新的数据库",
                type: "create",
                subType: "database",
                category: "database_definition",
                inputs: [{ name: "数据库配置", connected: false, id: "input1", type: "config" }],
                outputs: [{ name: "创建结果", connected: false, id: "output1", type: "result" }]
              }
            ]
          }
        }
      },
      database_operation: {
        name: "数据库操作",
        description: "数据增删改查操作模块",
        icon: "/src/assets/Data.svg",
        children: {
          select: {
            name: "查询操作",
            description: "数据查询相关操作",
            icon: "/src/assets/test.svg",
            children: [
              {
                id: "basic_select",
                name: "基本查询",
                description: "基础数据查询操作",
                type: "select",
                subType: "basic",
                category: "database_operation",
                inputs: [{ name: "查询条件", connected: false, id: "input1", type: "condition" }],
                outputs: [{ name: "查询结果", connected: false, id: "output1", type: "data" }]
              }
            ]
          }
        }
      }
    }
    // 默认展开第一个大层级
    if (Object.keys(availableModules.value).length > 0) {
      expandedCategories.value = [Object.keys(availableModules.value)[0]]
    }
  }
}


// 已放置的节点
const placedNodes = ref([])
let nodeId = 1

// 连线相关状态
const connections = ref([])
let isConnecting = false
let startPort = null
let tempLine = null

// 拖拽相关状态
let isDragging = false
let currentDragNode = null
let dragOffset = { x: 0, y: 0 }

// 配置对话框相关
const configDialogVisible = ref(false)
const activeTab = ref('ports')
const currentNode = ref(null)

// 代码面板相关
const isCodePanelCollapsed = ref(false)
const generatedFiles = ref([])
const currentFileIndex = ref(0)

// 右键菜单相关
const contextMenuVisible = ref(false)
const contextMenuX = ref(0)
const contextMenuY = ref(0)
const contextMenuNode = ref(null)

// 文件树相关
const fileStructure = ref([])
const currentFile = ref(null)

// 添加数据库列表状态
const databaseList = ref([])
const databaseCache = ref(new Map())

// 添加表列表状态
const tableList = ref([])
const tableCache = ref(new Map())
const databaseTables = ref({})

// 新增：列名缓存
const columnsCache = ref(new Map())

// 添加新的状态变量
const showModelMenu = ref(false)
const modelMenuX = ref(0)
const modelMenuY = ref(0)
const showModelDialog = ref(false)
const modelFileName = ref('')

// 添加展开状态控制
const expandedFolders = ref(new Set())

// 添加文件内容缓存
const fileContentCache = ref(new Map())

// 添加canvas引用
const canvasRef = ref(null)

// 添加选中节点状态
const selectedNode = ref(null)

// 多标签页相关状态
const tabs = ref([
  {
    id: 'main',
    title: '未命名',
    active: true,
    nodes: [],
    connections: [],
    selectedNode: null
  }
])
const activeTabId = ref('main')

// 绝对路径 marker-end 兼容写法
const globalArrowheadUrl = computed(() => `url('${window.location.origin + window.location.pathname}#arrowhead-global')`)

// 预加载数据库列表
const preloadDatabases = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/code/databases')
    if (response.ok) {
      const data = await response.json()
      if (data.status === 'success') {
        databaseList.value = data.databases
        // 缓存数据库列表
        databaseCache.value.set('databases', data.databases)
        console.log('数据库列表加载成功:', data.databases)
      }
    }
  } catch (error) {
    console.error('预加载数据库列表失败:', error)
  }
}

// 预加载表列表
const preloadTables = async (databaseName = null) => {
  try {
    const url = databaseName 
      ? `http://localhost:8000/api/code/tables?database_name=${encodeURIComponent(databaseName)}`
      : 'http://localhost:8000/api/code/tables'
    
    const response = await fetch(url)
    if (response.ok) {
      const data = await response.json()
      if (data.status === 'success') {
        if (databaseName) {
          // 获取指定数据库的表列表
          tableList.value = data.tables
          tableCache.value.set(databaseName, data.tables)
          console.log(`数据库 ${databaseName} 的表列表加载成功:`, data.tables)
        } else {
          // 获取所有数据库表对应关系
          databaseTables.value = data.database_tables
          tableCache.value.set('all', data.database_tables)
          console.log('所有数据库表对应关系加载成功:', data.database_tables)
        }
      }
    }
  } catch (error) {
    console.error('预加载表列表失败:', error)
  }
}

// 根据数据库名获取表列表
const getTablesByDatabase = (databaseName) => {
  const tablesObj = databaseTables.value[databaseName] || {}
  //获取所有表名(对象的键)
  const tableNames = Object.keys(tablesObj)
  console.log('根据数据库',databaseName,'获取数据表结果：',tableNames)
  return tableNames
}

// 预加载文件内容
const preloadFileContents = async (files) => {
  for (const file of files) {
    if (file.type === 'file') {
      try {
        const response = await fetch(`http://localhost:8000/api/code/read_file?path=${encodeURIComponent(file.path)}`)
        if (response.ok) {
          const data = await response.json()
          if (data.status === 'success') {
            fileContentCache.value.set(file.path, data.content)
          }
        }
      } catch (error) {
        console.error(`预加载文件失败 ${file.path}:`, error)
      }
    }
    if (file.type === 'directory' && file.children) {
      await preloadFileContents(file.children)
    }
  }
}

// 更新连线位置
const updateConnections = () => {
  const activeCanvas = document.querySelector('.canvas-container.active')
  if (!activeCanvas) return
  
  const canvas = activeCanvas.querySelector('.canvas')
  if (!canvas) return
  
  const rect = canvas.getBoundingClientRect()
  
  connections.value = connections.value.map(conn => {
    const startNode = activeCanvas.querySelector(`[data-node-id="${conn.start.node.id}"]`)
    const endNode = activeCanvas.querySelector(`[data-node-id="${conn.end.node.id}"]`)
    
    if (!startNode || !endNode) return conn
    
    const startPort = startNode.querySelector(`[data-port-id="${conn.start.port.id}"]`)
    const endPort = endNode.querySelector(`[data-port-id="${conn.end.port.id}"]`)
    
    if (!startPort || !endPort) return conn
    
    const startRect = startPort.getBoundingClientRect()
    const endRect = endPort.getBoundingClientRect()
    
    return {
      ...conn,
      startPos: {
        x: startRect.left - rect.left + (conn.start.isInput ? 0 : startRect.width),
        y: startRect.top - rect.top + startRect.height / 2
      },
      endPos: {
        x: endRect.left - rect.left + (conn.end.isInput ? 0 : endRect.width),
        y: endRect.top - rect.top + endRect.height / 2
      }
    }
  })
}

// 开始拖拽节点
const startDrag = (event, node) => {
  if (event.target.closest('.port')) return
  
  isDragging = true
  currentDragNode = node
  dragOffset = {
    x: event.clientX - node.x,
    y: event.clientY - node.y
  }
  
  // 添加事件监听
  document.addEventListener('mousemove', handleDrag)
  document.addEventListener('mouseup', stopDrag)
  
  // 阻止默认行为和事件冒泡
  event.preventDefault()
  event.stopPropagation()
}

// 处理拖拽
const handleDrag = (event) => {
  if (!isDragging || !currentDragNode) return
  
  // 计算新位置
  const newX = event.clientX - dragOffset.x
  const newY = event.clientY - dragOffset.y
  
  // 更新节点位置
  currentDragNode.x = newX
  currentDragNode.y = newY
  
  // 更新连线位置
  updateConnections()
  
  // 阻止默认行为和事件冒泡
  event.preventDefault()
  event.stopPropagation()
}

// 停止拖拽
const stopDrag = (event) => {
  if (!isDragging) return
  
  isDragging = false
  currentDragNode = null
  
  // 移除事件监听
  document.removeEventListener('mousemove', handleDrag)
  document.removeEventListener('mouseup', stopDrag)
  
  // 阻止默认行为和事件冒泡
  event.preventDefault()
  event.stopPropagation()
}

// 添加变量
const updateFrame = ref(null)

// 处理模块拖拽开始
const handleDragStart = (event, module) => {
  event.dataTransfer.setData('moduleId', module.id)
}

// 处理模块放置
const handleDrop = (event) => {
  const moduleId = event.dataTransfer.getData('moduleId')
  
  // 如果没有moduleId，说明不是模块拖拽，直接返回
  if (!moduleId) {
    return
  }
  
  // 阻止事件冒泡，避免触发文件拖拽处理
  event.stopPropagation()
  
  // 在所有分类的三层嵌套结构中查找模块
  let module = null
  let fallbackIcon = ''
  for (const categoryKey in availableModules.value) {
    const category = availableModules.value[categoryKey]
    if (category.children) {
      // 遍历第二级：子层级
      for (const subCategoryKey in category.children) {
        const subCategory = category.children[subCategoryKey]
        if (subCategory.children && Array.isArray(subCategory.children)) {
          // 在第三级：模块列表中查找
          const found = subCategory.children.find(m => m.id === moduleId)
          if (found) {
            module = found
            fallbackIcon = subCategory.icon || category.icon || '/src/assets/logo.svg'
            break
          }
        }
      }
      if (module) break
    }
  }
  
  if (module) {
    // 获取当前活动的canvas容器
    const activeCanvas = event.target.closest('.canvas-container.active') || event.target.closest('.canvas-container')
    if (!activeCanvas) return
    
    const rect = activeCanvas.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top
    
    console.log('拖拽的模块信息:', module)
    console.log('模块图标:', module.icon)
    
    placedNodes.value.push({
      ...module,
      icon: module.icon || fallbackIcon || '/src/assets/logo.svg',
      id: nodeId++,
      originId: module.id,
      x,
      y,
      scale: 1
    })
  }
}

// 开始连线
const startConnection = (event, node, port, isInput) => {
  event.stopPropagation()
  
  if (isInput && port.connected) {
    return
  }
  
  if (!isInput) {
    isConnecting = true
    startPort = { node, port, isInput }
    port.connecting = true
    
    document.addEventListener('mousemove', handleConnectionMove)
    document.addEventListener('mouseup', stopConnection)
    
    const startPos = getPortPosition(node, port, isInput)
    tempLine = {
      start: startPos,
      end: startPos
    }
  }
}

// 处理端口鼠标释放
const handlePortMouseUp = (event, node, port, isInput) => {
  if (!isConnecting) return
  
  // 如果是输入端口，且起始端口是输出端口，则尝试连接
  if (isInput && startPort && !startPort.isInput) {
    const targetPort = { node, port, isInput }
    if (canConnect(startPort, targetPort)) {
      createConnection(startPort, targetPort)
    }
  }
  
  // 清除连接状态
  isConnecting = false
  startPort = null
  tempLine = null
  
  // 清除所有端口的连接状态
  placedNodes.value.forEach(node => {
    node.inputs.forEach(input => input.connecting = false)
    node.outputs.forEach(output => output.connecting = false)
  })
  
  // 移除事件监听
  document.removeEventListener('mousemove', handleConnectionMove)
  document.removeEventListener('mouseup', stopConnection)
}

// 处理连线移动
const handleConnectionMove = (event) => {
  if (!isConnecting) return
  
  const canvas = document.querySelector('.canvas')
  const rect = canvas.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  
  const startPos = getPortPosition(startPort.node, startPort.port, startPort.isInput)
  tempLine = {
    start: startPos,
    end: { x, y }
  }
  
  const targetPort = findPortAtPosition(event.clientX, event.clientY)
  
  placedNodes.value.forEach(node => {
    node.inputs.forEach(input => input.connecting = false)
    node.outputs.forEach(output => output.connecting = false)
  })
  
  if (targetPort && canConnect(startPort, targetPort)) {
    targetPort.port.connecting = true
  }
}

// 获取端口位置
const getPortPosition = (node, port, isInput) => {
  const nodeElement = document.querySelector(`[data-node-id="${node.id}"]`)
  const portElement = nodeElement.querySelector(`[data-port-id="${port.id}"]`)
  const rect = portElement.getBoundingClientRect()
  const canvas = document.querySelector('.canvas')
  const canvasRect = canvas.getBoundingClientRect()
  
  return {
    x: rect.left - canvasRect.left + (isInput ? 0 : rect.width),
    y: rect.top - canvasRect.top + rect.height / 2
  }
}

// 查找端口
const findPortAtPosition = (x, y) => {
  const canvas = document.querySelector('.canvas')
  const rect = canvas.getBoundingClientRect()
  const relativeX = x - rect.left
  const relativeY = y - rect.top
  
  for (const node of placedNodes.value) {
    for (const port of [...node.inputs, ...node.outputs]) {
      const portElement = document.querySelector(`[data-port-id="${port.id}"]`)
      if (!portElement) continue
      
      const portRect = portElement.getBoundingClientRect()
      const portX = portRect.left - rect.left
      const portY = portRect.top - rect.top
      
      if (
        relativeX >= portX &&
        relativeX <= portX + portRect.width &&
        relativeY >= portY &&
        relativeY <= portY + portRect.height
      ) {
        return {
          node,
          port,
          isInput: node.inputs.includes(port)
        }
      }
    }
  }
  
  return null
}

// 检查是否可以连接
const canConnect = (start, end) => {
  if (!start || !end) return false
  if (start.isInput === end.isInput) return false
  if (start.node.id === end.node.id) return false
  
  const inputPort = start.isInput ? start.port : end.port
  if (inputPort.connected) return false
  
  return true
}

// 创建连线
const createConnection = (start, end) => {
  const inputPort = start.isInput ? start.port : end.port
  const outputPort = start.isInput ? end.port : start.port
  
  inputPort.connected = true
  outputPort.connected = true
  
  const startPos = getPortPosition(start.isInput ? end.node : start.node, start.isInput ? end.port : start.port, start.isInput)
  const endPos = getPortPosition(start.isInput ? start.node : end.node, start.isInput ? start.port : end.port, start.isInput)
  
  connections.value.push({
    id: Date.now(),
    start: start.isInput ? end : start,
    end: start.isInput ? start : end,
    startPos,
    endPos,
    animated: true
  })
  
  // 立即更新一次连线位置
  updateConnections()
}

// 获取连线路径
const getConnectionPath = (start, end) => {
  const dx = end.x - start.x
  const dy = end.y - start.y
  
  // 计算控制点
  const controlPoint1 = {
    x: start.x + dx * 0.5,
    y: start.y
  }
  const controlPoint2 = {
    x: end.x - dx * 0.5,
    y: end.y
  }
  
  // 调整终点位置，使箭头刚好碰到端口
  const endX = end.x - (dx > 0 ? 7 : -7)
  
  return `M ${start.x} ${start.y} 
          C ${controlPoint1.x} ${controlPoint1.y},
            ${controlPoint2.x} ${controlPoint2.y},
            ${endX} ${end.y}`
}

// 组件卸载时清理事件监听
onUnmounted(() => {
  document.removeEventListener('mousemove', handleDrag)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('mousemove', handleConnectionMove)
  document.removeEventListener('mouseup', stopConnection)
})

// 双击节点打开配置对话框
const handleNodeDblClick = (node) => {
  openConfigDialog(node)
}

// 打开配置对话框
const openConfigDialog = (node) => {
  currentNode.value = { ...node }
  configDialogVisible.value = true
}

// 处理配置保存
const handleConfigSave = (updatedNode) => {
  // 更新节点配置
  const node = placedNodes.value.find(n => n.id === updatedNode.id)
  if (node) {
    Object.assign(node, updatedNode)
  }
  configDialogVisible.value = false
}

// 添加端口
const addPort = (type) => {
  if (!currentNode.value) return
  
  const newPort = {
    name: '',
    type: 'number',
    connected: false,
    connecting: false
  }
  
  if (type === 'input') {
    currentNode.value.inputs.push(newPort)
  } else {
    currentNode.value.outputs.push(newPort)
  }
}

// 删除端口
const removePort = (type, index) => {
  if (!currentNode.value) return
  
  if (type === 'input') {
    currentNode.value.inputs.splice(index, 1)
  } else {
    currentNode.value.outputs.splice(index, 1)
  }
}

// 添加参数
const addParameter = async () => {
  if (!currentNode.value) return
  if (!currentNode.value.parameters) {
    currentNode.value.parameters = []
  }
  if (currentNode.value.type === 'select') {
    // select类型允许多行，每次push新行
    const param = { name: '', value: '', _columns: [] }
    if (currentNode.value.databaseName && currentNode.value.tableName) {
      param._columns = await getColumnsByDatabaseTable(currentNode.value.databaseName, currentNode.value.tableName)
    }
    currentNode.value.parameters.push(param)
  } else {
    currentNode.value.parameters.push({ name: '', value: '' })
  }
}

// 删除参数
const removeParameter = (index) => {
  if (!currentNode.value) return
  currentNode.value.parameters.splice(index, 1)
}

// 保存配置
const saveConfig = () => {
  if (!currentNode.value) return

  // select类型参数校验
  if (currentNode.value.type === 'select') {
    const names = currentNode.value.parameters.map(p => p.name)
    const hasEmpty = names.some(n => !n)
    const hasDuplicate = names.length !== new Set(names).size
    if (hasEmpty) {
      ElMessage.error('列名不能为空，请选择具体字段')
      return
    }
    if (hasDuplicate) {
      ElMessage.error('不能选择重复的列名')
      return
    }
  }

  // 更新节点配置
  const node = placedNodes.value.find(n => n.id === currentNode.value.id)
  if (node) {
    Object.assign(node, currentNode.value)
  }

  configDialogVisible.value = false
}

// 切换代码面板
const toggleCodePanel = () => {
  isCodePanelCollapsed.value = !isCodePanelCollapsed.value
}

// 显示右键菜单
const showContextMenu = (event, node) => {
  console.log('右键菜单触发，节点数据:', node)
  event.preventDefault()
  event.stopPropagation() // 阻止事件冒泡
  
  // 深拷贝节点数据
  contextMenuNode.value = JSON.parse(JSON.stringify(node))
  contextMenuX.value = event.clientX
  contextMenuY.value = event.clientY
  contextMenuVisible.value = true
}

// 隐藏右键菜单
const hideContextMenu = () => {
  contextMenuVisible.value = false
  // 不要在这里清空节点数据
  // contextMenuNode.value = null
}

// 打开文件
const openFile = async (file) => {
  try {
    // 检查缓存中是否有文件内容
    if (fileContentCache.value.has(file.path)) {
      currentFile.value = {
        ...file,
        content: fileContentCache.value.get(file.path)
      }
      return
    }

    // 如果缓存中没有，则从服务器获取
    const response = await fetch(`http://localhost:8000/api/code/read_file?path=${encodeURIComponent(file.path)}`)
    if (!response.ok) {
      throw new Error('读取文件失败')
    }
    const data = await response.json()
    if (data.status === 'success') {
      // 更新缓存
      fileContentCache.value.set(file.path, data.content)
      currentFile.value = {
        ...file,
        content: data.content
      }
    } else {
      throw new Error(data.message || '读取文件失败')
    }
  } catch (error) {
    console.error('读取文件失败:', error)
    ElMessage.error('读取文件失败：' + error.message)
  }
}

// 返回文件树
const backToTree = () => {
  currentFile.value = null
}

// 切换模块展开/折叠
const toggleModule = (module) => {
  module.expanded = !module.expanded
}

// 切换 src 文件夹展开/折叠
const toggleSrc = (module) => {
  module.srcExpanded = !module.srcExpanded
}

// 获取文件结构
const fetchFileStructure = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/code/get_file_structure')
    if (response.ok) {
      const data = await response.json()
      if (data.status === 'success') {
        fileStructure.value = data.files
        // 预加载文件内容
        await preloadFileContents(data.files)
      }
    }
  } catch (error) {
    console.error('获取文件结构失败:', error)
  }
}

// 初始化
onMounted(async () => {
  await loadModelModules() // 加载模型列表
  await fetchFileStructure()
  await preloadDatabases()
  await preloadTables()
  
  // 确保第一个标签页是活动的
  if (tabs.value.length > 0) {
    tabs.value[0].active = true
    activeTabId.value = tabs.value[0].id
  }
})

// 修改生成代码函数中的错误处理部分
const handleGenerateCode = async () => {
  try {
    // 检查节点数据结构
    console.log('节点完整数据:', JSON.stringify(contextMenuNode.value, null, 2))
    
    // 确保节点名称存在
    const nodeName = contextMenuNode.value.name || 'unnamed_module'
    console.log('节点名称:', nodeName)
  
    const { value: folderName } = await ElMessageBox.prompt('请输入模块文件夹名称', '生成模块', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /^[a-zA-Z][a-zA-Z0-9_]*$/,
      inputErrorMessage: '文件夹名称只能包含字母、数字和下划线，且必须以字母开头',
      inputPlaceholder: '请输入文件夹名称',
      inputValidator: (value) => {
        if (!value) {
          return '文件夹名称不能为空'
        }
        if (value.length > 50) {
          return '文件夹名称不能超过50个字符'
        }
        return true
      }
    })
    if (!folderName) return
    
    // 生成代码文件
    const moduleName = folderName
    console.log('模块名称:', moduleName)
    
    // 准备节点数据 - 包含所有可能的字段
    const nodeData = {
      name: moduleName,
      type: contextMenuNode.value.type,
      tableName: contextMenuNode.value.tableName || '', // 保证有值
      databaseName: contextMenuNode.value.databaseName || '',
      parameters: Array.isArray(contextMenuNode.value.parameters) ? contextMenuNode.value.parameters : [],
      condition: contextMenuNode.value.condition || '',
      icon: contextMenuNode.value.icon || "/src/assets/wave-icon.svg"
    }
    
    // 新增：如果节点有sql字段，则一并传递
    if (contextMenuNode.value.sql) {
      nodeData.sql = contextMenuNode.value.sql
    }
    
    // 新增：包含动态表单的所有字段
    if (contextMenuNode.value.fields) {
      nodeData.fields = contextMenuNode.value.fields
    }
    if (contextMenuNode.value.charset) {
      nodeData.charset = contextMenuNode.value.charset
    }
    if (contextMenuNode.value.collation) {
      nodeData.collation = contextMenuNode.value.collation
    }
    
    // 包含所有其他可能的动态字段
    Object.keys(contextMenuNode.value).forEach(key => {
      if (!['name', 'type', 'tableName', 'databaseName', 'parameters', 'condition', 'icon', 'sql', 'fields', 'charset', 'collation'].includes(key)) {
        nodeData[key] = contextMenuNode.value[key]
      }
    })
    
    // 调试输出
    console.log('最终发送到后端的 nodeData:', JSON.stringify(nodeData, null, 2))
    
    console.log('节点图标信息:', contextMenuNode.value.icon)
    console.log('发送到后端的数据:', JSON.stringify(nodeData, null, 2))
    
    const response = await fetch('http://localhost:8000/api/code/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(nodeData)
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '代码生成失败')
    }
    
    const result = await response.json()
    console.log('代码生成结果:', result)
    
    // 显示成功消息和文件路径
    ElMessage({
      type: 'success',
      message: '代码生成成功',
      duration: 5000
    })
    
    // 显示生成的文件路径
    await ElMessageBox.alert(
      `生成的文件路径：\n\n` +
      `SQL文件：${result.files.sql}\n` +
      `JSON文件：${result.files.json}\n` +
      `可拖拽模型：${result.files.draggable}\n` +
      `C++源文件：${result.files.cpp}\n` +
      `头文件：${result.files.header}`,
      '生成成功',
      {
        confirmButtonText: '确定',
        type: 'success'
      }
    )
    
    // 刷新文件树
    await fetchFileStructure()
    
    // 如果是create类型，刷新数据库列表和表列表
    if (nodeData.type === 'create') {
      await preloadDatabases()
      await preloadTables()
    }
    
    // 自动展开新生成的模块
    const newModulePath = moduleName
    expandedFolders.value.add(newModulePath)
    expandedFolders.value.add(`${newModulePath}/src`)
    
    // 预加载新生成的文件内容
    const newFiles = [
      { path: `${newModulePath}/sql/${moduleName}.sql`, type: 'file' },
      { path: `${newModulePath}/${moduleName}_model.json`, type: 'file' },
      { path: `${newModulePath}/src/${moduleName}.cpp`, type: 'file' },
      { path: `${newModulePath}/src/${moduleName}.h`, type: 'file' }
    ]
    await preloadFileContents(newFiles)
    
    // // 自动打开第一个文件
    // if (newFiles.length > 0) {
    //   await openFile(newFiles[0])
    // }
    
  } catch (error) {
    console.error('代码生成错误:', error)
    ElMessage({
      type: 'error',
      message: error.message || '代码生成失败',
      duration: 5000
    })
  }
}

// 监听点击事件，隐藏右键菜单
onMounted(() => {
  document.addEventListener('click', (event) => {
    // 如果点击的不是右键菜单，则隐藏菜单
    if (!event.target.closest('.context-menu')) {
      hideContextMenu()
      hideModelMenu()
    }
  })
})

onUnmounted(() => {
  document.removeEventListener('click', hideContextMenu)
  document.removeEventListener('click', hideModelMenu)
})

// 添加新的方法
const handleCanvasContextMenu = (event) => {
  // 检查是否点击在节点上
  const target = event.target
  if (target.closest('.node')) {
    return // 如果点击在节点上，不显示菜单
  }
  
  event.preventDefault()
  modelMenuX.value = event.clientX
  modelMenuY.value = event.clientY
  showModelMenu.value = true
}

const hideModelMenu = () => {
  showModelMenu.value = false
}

const handleGenerateModelFile = () => {
  showModelDialog.value = true
  hideModelMenu()
}

const generateModelFile = async () => {
  if (!modelFileName.value) {
    ElMessage.warning('请输入文件名')
    return
  }

  try {
    // 准备完整的模型数据，包含所有参数信息
    const modelData = {
      nodes: placedNodes.value.map(node => ({
        id: node.id,
        name: node.name,
        type: node.type,
        icon: node.icon,
        x: node.x,
        y: node.y,
        scale: node.scale || 1,
        inputs: node.inputs || [],
        outputs: node.outputs || [],
        // 包含完整的参数信息
        databaseName: node.databaseName,
        tableName: node.tableName,
        parameters: node.parameters || [],
        condition: node.condition,
        properties: node.properties || {}
      })),
      connections: connections.value.map(conn => ({
        id: conn.id,
        start: {
          node: { id: conn.start.node.id },
          port: { id: conn.start.port.id },
          isInput: conn.start.isInput
        },
        end: {
          node: { id: conn.end.node.id },
          port: { id: conn.end.port.id },
          isInput: conn.end.isInput
        },
        startPos: conn.startPos,
        endPos: conn.endPos
      })),
      // 添加元数据
      metadata: {
        generatedAt: new Date().toISOString(),
        totalNodes: placedNodes.value.length,
        totalConnections: connections.value.length,
        description: `包含 ${placedNodes.value.length} 个节点和 ${connections.value.length} 个连线的模型文件`
      }
    }

    const content = JSON.stringify(modelData, null, 2)
    const filePath = `app/${modelFileName.value}.json`

    // 调用后端 API 保存文件
    const response = await fetch('http://localhost:8000/api/code/write_model_file', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        filename: modelFileName.value,
        content: content
      })
    })

    if (!response.ok) {
      throw new Error('保存文件失败')
    }

    const result = await response.json()
    if (result.status === 'success') {
      // 更新缓存
      fileContentCache.value.set(filePath, content)
      ElMessage.success(`模型文件生成成功，保存在: ${result.file_path}`)
      showModelDialog.value = false
      modelFileName.value = ''
      // 刷新文件树
      await fetchFileStructure()
    } else {
      throw new Error(result.message || '保存文件失败')
    }
  } catch (error) {
    console.error('生成模型文件失败:', error)
    ElMessage.error('生成模型文件失败：' + error.message)
  }
}

// 添加展开/折叠方法
const toggleFolder = (file) => {
  if (expandedFolders.value.has(file.path)) {
    expandedFolders.value.delete(file.path)
  } else {
    expandedFolders.value.add(file.path)
  }
}

// 在 script setup 部分添加排序方法
const sortFiles = (files) => {
  return files.sort((a, b) => {
    // 先按类型排序（文件夹在前）
    if (a.type !== b.type) {
      return a.type === 'directory' ? -1 : 1
    }
    // 同类型按名称排序
    return a.name.localeCompare(b.name)
  })
}

// 修改 generateModule 方法
const generateModule = async () => {
  try {
    // 先弹出输入框让用户输入文件夹名称
    const { value: folderName } = await ElMessageBox.prompt('请输入模块文件夹名称', '生成模块', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /^[a-zA-Z][a-zA-Z0-9_]*$/,
      inputErrorMessage: '文件夹名称只能包含字母、数字和下划线，且必须以字母开头',
      inputPlaceholder: '请输入文件夹名称',
      inputValidator: (value) => {
        if (!value) {
          return '文件夹名称不能为空'
        }
        if (value.length > 50) {
          return '文件夹名称不能超过50个字符'
        }
        return true
      }
    })

    if (!folderName) return

    // 显示加载中
    const loading = ElLoading.service({
      lock: true,
      text: '正在生成模块...',
      background: 'rgba(0, 0, 0, 0.7)'
    })

    // 发送请求生成模块
    const response = await fetch('http://localhost:8000/api/code/generate_module', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        module_name: folderName,
        module_type: selectedModuleType.value
      })
    })

    if (!response.ok) {
      throw new Error('生成模块失败')
    }

    const data = await response.json()
    if (data.status === 'success') {
      ElMessage.success('模块生成成功')
      // 重新获取文件结构
      await fetchFileStructure()
    } else {
      throw new Error(data.message || '生成模块失败')
    }
  } catch (error) {
    console.error('生成模块失败:', error)
    ElMessage.error('生成模块失败：' + error.message)
  } finally {
    // 关闭加载中
    ElLoading.service().close()
  }
}

// 添加新的方法
const onDatabaseChange = async () => {
  console.log('数据库切换:', currentNode.value.databaseName)
  
  // 清空当前表名
  currentNode.value.tableName = ''
  
  // 如果选择了数据库，加载该数据库的表列表
  if (currentNode.value.databaseName) {
    await preloadTables(currentNode.value.databaseName)
    
    // 如果不是create类型，自动选择第一个表
    if (currentNode.value.type !== 'create') {
      const tables = getTablesByDatabase(currentNode.value.databaseName)
      console.log(`数据库 ${currentNode.value.databaseName} 的表列表:`, tables)
      if (tables.length > 0) {
        currentNode.value.tableName = tables[0]
        console.log('自动选择第一个表:', tables[0])
      }
    }
  }
}

// 拖拽文件处理
const handleFileDrop = async (event) => {
  event.preventDefault()
  
  console.log('拖拽文件事件触发')
  
  // 检查是否是模块拖拽，如果是则直接返回
  const moduleId = event.dataTransfer.getData('moduleId')
  if (moduleId) {
    console.log('检测到模块拖拽，跳过文件拖拽处理')
    return
  }
  
  // 检查是否有拖拽的文件数据
  const jsonData = event.dataTransfer.getData('application/json')
  const fileName = event.dataTransfer.getData('text/plain')
  
  if (jsonData && fileName && fileName.endsWith('_model.json')) {
    console.log('从文件树拖拽的模型文件:', fileName)
    
    try {
      // 发送到后端解析
      const response = await fetch('http://localhost:8000/api/code/parse_draggable_model', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ file_content: jsonData })
      })
      
      console.log('后端响应状态:', response.status)
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || '解析模型文件失败')
      }
      
      const result = await response.json()
      console.log('解析结果:', result)
      
      if (result.status === 'success') {
        // 获取拖拽位置
        const activeCanvas = event.target.closest('.canvas-container.active') || event.target.closest('.canvas-container')
        if (!activeCanvas) return
        
        const rect = activeCanvas.getBoundingClientRect()
        const x = event.clientX - rect.left
        const y = event.clientY - rect.top
        
        console.log('拖拽位置:', { x, y })
        
        // 设置节点位置
        result.node_data.x = x
        result.node_data.y = y
        
        // 确保节点有必要的属性
        if (!result.node_data.inputs) {
          result.node_data.inputs = []
        }
        if (!result.node_data.outputs) {
          result.node_data.outputs = []
        }
        if (!result.node_data.parameters) {
          result.node_data.parameters = []
        }
        
        // 添加到绘制面板
        placedNodes.value.push(result.node_data)
        
        console.log('节点已添加到面板，当前节点数量:', placedNodes.value.length)
        
        ElMessage.success(`成功导入模型：${result.description}`)
        return
      }
      
    } catch (error) {
      console.error('拖拽文件处理失败:', error)
      ElMessage.error('拖拽文件处理失败：' + error.message)
      return
    }
  }
  
  // 处理从外部文件系统拖拽的文件
  const files = event.dataTransfer.files
  if (files.length === 0) {
    console.log('没有拖拽文件')
    return
  }
  
  const file = files[0]
  console.log('从外部拖拽文件:', file.name, file.type)
  
  // 检查文件类型
  if (!file.name.endsWith('_model.json')) {
    ElMessage.error('请拖拽有效的模型文件（*_model.json）')
    return
  }
  
  try {
    // 读取文件内容
    const content = await file.text()
    console.log('文件内容:', content.substring(0, 200) + '...')
    
    // 发送到后端解析
    const response = await fetch('http://localhost:8000/api/code/parse_draggable_model', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ file_content: content })
    })
    
    console.log('后端响应状态:', response.status)
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '解析模型文件失败')
    }
    
    const result = await response.json()
    console.log('解析结果:', result)
    
    if (result.status === 'success') {
      // 获取拖拽位置
      const activeCanvas = event.target.closest('.canvas-container.active') || event.target.closest('.canvas-container')
      if (!activeCanvas) return
      
      const rect = activeCanvas.getBoundingClientRect()
      const x = event.clientX - rect.left
      const y = event.clientY - rect.top
      
      console.log('拖拽位置:', { x, y })
      
      // 设置节点位置
      result.node_data.x = x
      result.node_data.y = y
      
      // 确保节点有必要的属性
      if (!result.node_data.inputs) {
        result.node_data.inputs = []
      }
      if (!result.node_data.outputs) {
        result.node_data.outputs = []
      }
      if (!result.node_data.parameters) {
        result.node_data.parameters = []
      }
      
      // 添加到绘制面板
      placedNodes.value.push(result.node_data)
      
      console.log('节点已添加到面板，当前节点数量:', placedNodes.value.length)
      
      ElMessage.success(`成功导入模型：${result.description}`)
    }
    
  } catch (error) {
    console.error('拖拽文件处理失败:', error)
    ElMessage.error('拖拽文件处理失败：' + error.message)
  }
}

// 拖拽事件处理
const handleDragOver = (event) => {
  event.preventDefault()
}

const handleDragEnter = (event) => {
  event.preventDefault()
}

// 文件拖拽开始处理
const handleFileDragStart = async (event, file) => {
  // 只处理_model.json文件
  if (!file.name.endsWith('_model.json') &&  !file.name.endsWith('_test.json') ) {
    event.preventDefault()
    return
  }
  if(file.name.endsWith('_test.json')){
    handleTestJsonDrag(event, file)
    return
  }
  
  console.log('开始拖拽文件:', file.name)
  
  try {
    // 从缓存或服务器获取文件内容
    let content
    if (fileContentCache.value.has(file.path)) {
      content = fileContentCache.value.get(file.path)
    } else {
      const response = await fetch(`http://localhost:8000/api/code/read_file?path=${encodeURIComponent(file.path)}`)
      if (response.ok) {
        const data = await response.json()
        if (data.status === 'success') {
          content = data.content
          fileContentCache.value.set(file.path, content)
        }
      }
    }
    
    if (content) {
      // 设置拖拽数据
      event.dataTransfer.setData('application/json', content)
      event.dataTransfer.setData('text/plain', file.name)
      event.dataTransfer.effectAllowed = 'copy'
      
      console.log('拖拽数据已设置')
    } else {
      console.error('无法获取文件内容')
      event.preventDefault()
    }
  } catch (error) {
    console.error('文件拖拽准备失败:', error)
    event.preventDefault()
  }
}

// 添加新的方法
const handleKeyDown = (event) => {
  // 处理Delete键删除选中的节点
  if (event.key === 'Delete' && selectedNode.value) {
    deleteSelectedNode()
  }
}

const selectNode = (node) => {
  selectedNode.value = node
  console.log('选中节点:', node)
}

const handleDeleteNode = () => {
  if (!contextMenuNode.value) return
  
  // 删除与节点相关的连线
  connections.value = connections.value.filter(conn => 
    conn.start.node.id !== contextMenuNode.value.id && conn.end.node.id !== contextMenuNode.value.id
  )
  
  // 删除节点
  const index = placedNodes.value.findIndex(node => node.id === contextMenuNode.value.id)
  if (index !== -1) {
    placedNodes.value.splice(index, 1)
  }
  
  // 如果删除的是当前选中的节点，清除选中状态
  if (selectedNode.value && selectedNode.value.id === contextMenuNode.value.id) {
    selectedNode.value = null
  }
  
  // 隐藏右键菜单
  hideContextMenu()
  
  ElMessage.success('节点已删除')
}

const deleteSelectedNode = () => {
  if (!selectedNode.value) return
  
  // 删除与节点相关的连线
  connections.value = connections.value.filter(conn => 
    conn.start.node.id !== selectedNode.value.id && conn.end.node.id !== selectedNode.value.id
  )
  
  // 删除节点
  const index = placedNodes.value.findIndex(node => node.id === selectedNode.value.id)
  if (index !== -1) {
    placedNodes.value.splice(index, 1)
  }
  
  // 清除选中状态
  selectedNode.value = null
  
  ElMessage.success('节点已删除')
}

const handleCanvasClick = (event) => {
  // 如果点击的是画布空白区域，取消选中
  if (event.target.classList.contains('canvas-container') || event.target.classList.contains('canvas')) {
    selectedNode.value = null
  }
}

// 删除重复的onDatabaseChange函数，保留第1536行的函数

// 标签页管理函数
const getCurrentTab = () => {
  return tabs.value.find(tab => tab.id === activeTabId.value)
}

const addNewTab = (title, modelData = null) => {
  const newTabId = `tab_${Date.now()}`
  const newTab = {
    id: newTabId,
    title: '未命名',
    active: false,
    nodes: modelData ? modelData.nodes || [] : [],
    connections: modelData ? modelData.connections || [] : [],
    selectedNode: null
  }
  
  tabs.value.push(newTab)
  switchTab(newTabId)
  
  return newTabId
}

const switchTab = (tabId) => {
  // 保存当前标签页的数据
  const currentTab = getCurrentTab()
  if (currentTab) {
    currentTab.nodes = [...placedNodes.value]
    currentTab.connections = [...connections.value]
    currentTab.selectedNode = selectedNode.value
  }
  
  // 切换到新标签页
  activeTabId.value = tabId
  const targetTab = tabs.value.find(tab => tab.id === tabId)
  
  if (targetTab) {
    // 更新所有标签页的active状态
    tabs.value.forEach(tab => tab.active = tab.id === tabId)
    
    // 加载目标标签页的数据
    placedNodes.value = [...targetTab.nodes]
    connections.value = [...targetTab.connections]
    selectedNode.value = targetTab.selectedNode
    
    // 更新连线位置
    nextTick(() => {
      updateConnections()
    })
  }
}

const closeTab = (tabId) => {
  const index = tabs.value.findIndex(tab => tab.id === tabId)
  if (index === -1) return
  
  // 如果关闭的是当前标签页，切换到其他标签页
  if (tabId === activeTabId.value) {
    const nextTab = tabs.value[index + 1] || tabs.value[index - 1]
    if (nextTab) {
      switchTab(nextTab.id)
    }
  }
  
  // 移除标签页
  tabs.value.splice(index, 1)
  
  // 如果没有标签页了，创建一个新的
  if (tabs.value.length === 0) {
    addNewTab('新绘制界面')
  }
}

// 封装 _test.json 拖拽处理
const handleTestJsonDrag = async (event, file) => {
  try {
    let content
    if (fileContentCache.value.has(file.path)) {
      content = fileContentCache.value.get(file.path)
    } else {
      const response = await fetch(`http://localhost:8000/api/code/read_file?path=${encodeURIComponent(file.path)}`)
      if (response.ok) {
        const data = await response.json()
        if (data.status === 'success') {
          content = data.content
          fileContentCache.value.set(file.path, content)
        }
      }
    }
    if (content) {
      // 调用后端解析接口
      const response = await fetch('http://localhost:8000/api/code/parse_draggable_test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file_content: content })
      })
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || '解析 test.json 文件失败')
      }
      const result = await response.json()
      if (result.status === 'success') {
        // 新开一个tab或页面，传递 nodes/connections
        openTestGraphTab(result.nodes, result.connections, file.name)
      }
    } else {
      event.preventDefault()
    }
  } catch (error) {
    console.error('_test.json文件拖拽准备失败：', error)
    event.preventDefault()
  }
}

// 新开tab并绘制test.json
const openTestGraphTab = (nodes, connections, fileName) => {
  const newTabId = `tab_${Date.now()}`
  tabs.value.push({
    id: newTabId,
    title: fileName.replace('.json', ''),
    active: true,
    nodes,
    connections,
    selectedNode: null
  })
  tabs.value.forEach(tab => tab.active = false)
  tabs.value[tabs.value.length - 1].active = true
  switchTab(newTabId)
}

// 贝塞尔曲线路径生成函数
const bezierPath = (start, end) => {
  if (!start || !end) return ''
  const offset = Math.max(Math.abs(end.x - start.x) / 2, 40)
  return `M ${start.x} ${start.y} C ${start.x + offset} ${start.y}, ${end.x - offset} ${end.y}, ${end.x} ${end.y}`
}

// 新增：通过数据库和表名获取列名
const getColumnsByDatabaseTable = async (databaseName, tableName) => {
  if (!databaseName || !tableName) return [];
  const key = `${databaseName}::${tableName}`;
  if (columnsCache.value.has(key)) {
    return columnsCache.value.get(key);
  }
  try {
    const url = `http://localhost:8000/api/code/columns?database_name=${encodeURIComponent(databaseName)}&table_name=${encodeURIComponent(tableName)}`;
    const response = await fetch(url);
    if (response.ok) {
      const data = await response.json();
      if (data.status === 'success') {
        columnsCache.value.set(key, data.columns);
        return data.columns;
      }
    }
  } catch (error) {
    console.error('获取列名失败:', error);
  }
  return [];
};
</script>

<style scoped>
.module-management {
  display: flex;
  height: 100vh;
  background: #f5f7fa;
}

.module-container {
  display: flex;
  width: 100%;
  height: 100%;
}

.module-list {
  width: 200px;
  background: #ffffff;
  border-right: 1px solid #e4e7ed;
  padding: 0;
  overflow-y: auto;
  flex-shrink: 0;
  max-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 模块列表头部 */
.module-list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafafa;
  position: sticky;
  top: 0;
  z-index: 10;
}

.module-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.module-manage-btn {
  font-size: 24px;
  padding: 20px 12px;
  height: 28px;
}

/* 自定义滚动条样式 */
.module-list::-webkit-scrollbar {
  width: 6px;
}

.module-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.module-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.module-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.module-categories {
  flex: 1;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  }
  
/* 第一级：大层级样式 */
  .module-category {
    border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #ffffff;
    overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.module-category:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
  }
  
/*一集标题*/
  .category-header {
    display: flex;
    align-items: center;
  gap: 10px;
  padding: 14px 16px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
  border-bottom: 1px solid #e4e7ed;
  min-height: 22px;
  }

  .category-header:hover {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  }

  .category-header.expanded {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border-bottom: 1px solid #409eff;
  }
  
  .category-icon {
    width: 18px;
    height: 18px;
    object-fit: contain;
    flex-shrink: 0;
  }
  
  .category-name {
    font-size: 14px;
    font-weight: 600;
    color: #303133;
    flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  }
  
.expand-icon {
  font-size: 12px;
  color: #409eff;
  font-weight: bold;
  transition: transform 0.3s ease;
  flex-shrink: 0;
}

/* 第二级：子层级样式 */
.sub-categories {
  background: #fafafa;
  border-top: 1px solid #e4e7ed;
}

.sub-category {
  border-bottom: 1px solid #f0f0f0;
  position: relative;
}

.sub-category:last-child {
  border-bottom: none;
}

.sub-category-header {
  padding: 0;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.sub-category-header:hover {
  background: #f0f9ff;
}

.sub-category-header.expanded {
  background: #f0f9ff;
  border-bottom: 1px solid #e4e7ed;
}

/*二级标题*/
.sub-category-content {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px 10px 28px;
  position: relative;
  min-height: 18px;
  }
  
.sub-category-content::before {
  content: '';
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 6px;
  height: 6px;
  background: #409eff;
  border-radius: 50%;
  box-shadow: 0 0 0 1px #e3f2fd;
}

.sub-category-icon {
    width: 14px;
    height: 14px;
  object-fit: contain;
  flex-shrink: 0;
  }
  
.sub-category-name {
    font-size: 12px;
  font-weight: 500;
  color: #606266;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 第三级：模块列表样式 */
.sub-modules {
  background: #ffffff;
  padding: 6px 18px 8px 0px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.module-item {
  display: flex;
  align-items: center;
  padding: 6px 10px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background: #ffffff;
  cursor: grab;
  transition: all 0.3s ease;
  user-select: none;
  min-height: 28px;
  position: relative;
  margin-left: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.module-item:hover {
  border-color: #409eff;
  background: #f0f9ff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
}

.module-item:active {
  cursor: grabbing;
  transform: translateY(0);
}

.module-content {
  display: flex;
  align-items: center;
  width: 100%;
}

.module-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  padding-right: 40px;
}

.module-name {
  font-size: 11px;
  font-weight: 500;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.3;
}

/* 为不同类型的模块添加左侧颜色标识 */
.module-item[data-type="insert"] {
  border-left: 3px solid #409eff;
}

.module-item[data-type="update"] {
  border-left: 3px solid #67c23a;
}

.module-item[data-type="select"] {
  border-left: 3px solid #e6a23c;
}

.module-item[data-type="delete"] {
  border-left: 3px solid #f56c6c;
}

.module-item[data-type="create"] {
  border-left: 3px solid #722ed1;
}

.module-item[data-type="custom"] {
  border-left: 3px solid #909399;
}

/* 子类型标识 - 调整位置和大小 */
.module-item[data-subtype="base"]::after {
  content: "基础";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 8px;
  color: #67c23a;
  background: #f0f9ff;
  padding: 1px 4px;
  border-radius: 8px;
  border: 1px solid #e1f5fe;
  line-height: 1.2;
}

.module-item[data-subtype="where"]::after {
  content: "条件";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 8px;
  color: #e6a23c;
  background: #fdf6ec;
  padding: 1px 4px;
  border-radius: 8px;
  border: 1px solid #fce4d6;
  line-height: 1.2;
}

.module-item[data-subtype="batch"]::after {
  content: "批量";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 8px;
  color: #409eff;
  background: #ecf5ff;
  padding: 1px 4px;
  border-radius: 8px;
  border: 1px solid #d9ecff;
  line-height: 1.2;
}

.module-item[data-subtype="join"]::after {
  content: "关联";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 8px;
  color: #67c23a;
  background: #f0f9ff;
  padding: 1px 4px;
  border-radius: 8px;
  border: 1px solid #e1f5fe;
  line-height: 1.2;
}

.module-item[data-subtype="aggregate"]::after {
  content: "聚合";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 8px;
  color: #722ed1;
  background: #f9f0ff;
  padding: 1px 4px;
  border-radius: 8px;
  border: 1px solid #efdbff;
  line-height: 1.2;
}

.module-item[data-subtype="table"]::after {
  content: "表";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 8px;
  color: #f56c6c;
  background: #fef0f0;
  padding: 1px 4px;
  border-radius: 8px;
  border: 1px solid #fde2e2;
  line-height: 1.2;
}

.module-item[data-subtype="database"]::after {
  content: "库";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 8px;
  color: #e6a23c;
  background: #fdf6ec;
  padding: 1px 4px;
  border-radius: 8px;
  border: 1px solid #fce4d6;
  line-height: 1.2;
}

/* 其他子类型标识保持相同样式 */
.module-item[data-subtype="data_process"]::after {
  content: "处理";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 8px;
  color: #909399;
  background: #f4f4f5;
  padding: 1px 4px;
  border-radius: 8px;
  border: 1px solid #e9e9eb;
  line-height: 1.2;
}

.module-item[data-subtype="data_analysis"]::after {
  content: "分析";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 8px;
  color: #67c23a;
  background: #f0f9ff;
  padding: 1px 4px;
  border-radius: 8px;
  border: 1px solid #e1f5fe;
  line-height: 1.2;
}

.module-item[data-subtype="data_transform"]::after {
  content: "转换";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 8px;
  color: #409eff;
  background: #ecf5ff;
  padding: 1px 4px;
  border-radius: 8px;
  border: 1px solid #d9ecff;
  line-height: 1.2;
}

.module-item[data-subtype="upsert"]::after {
  content: "插入或更新";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 8px;
  color: #409eff;
  background: #ecf5ff;
  padding: 1px 4px;
  border-radius: 8px;
  border: 1px solid #d9ecff;
  line-height: 1.2;
}

/* 其他样式保持不变... */
.canvas-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  overflow: hidden;
  min-width: 0;
  }

.tabs-container {
  background: #fafafa;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
  border-radius: 8px 8px 0 0;
}

.canvas-container {
  flex: 1;
  background: #ffffff;
  border-radius: 0 0 8px 8px;
  overflow: hidden;
  box-shadow: none;
  display: block;
  position: relative;
}

.canvas-container:not(.active) {
  display: none;
}

.canvas {
  width: 100%;
  height: 100%;
  position: relative;
  min-height: 500px;
  background: #f5f7fa;
  background-size: 20px 20px;
}

/* 其他样式保持不变... */
.connections-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.connection-group {
  transform-origin: center;
  will-change: transform;
}

.connection-path {
  fill: none;
  stroke: #409EFF;
  stroke-width: 2;
  pointer-events: none;
  transition: none;
  marker-end: url(#arrowhead-global);
  will-change: d;
}

.connection-path.temp {
  stroke-dasharray: 5;
  animation: dash 1s linear infinite;
  stroke: #67C23A;
  stroke-width: 2;
  marker-end: url(#arrowhead-temp);
}

.connection-path.animated {
  stroke-dasharray: 5;
  animation: dash 1s linear infinite;
  stroke: #409EFF;
  stroke-width: 2;
  fill: none;
}

@keyframes dash {
  to {
    stroke-dashoffset: -10;
  }
}

.node {
  position: absolute;
  width: 150px;
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 12px;
  cursor: move;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  transition: none;
  user-select: none;
  touch-action: none;
}

.node:hover {
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.1);
  border-color: #409EFF;
}

.node-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding-bottom: 6px;
  border-bottom: 1px solid #e4e7ed;
  color: #303133;
  font-weight: 500;
  font-size: 13px;
  line-height: 1.2;
  min-height: 24px;
  text-align: center;
}

.node-ports {
  position: relative;
  min-height: 50px;
  margin: 0 -12px;
  border-bottom: none;
}

.ports-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.port {
  position: absolute;
  display: flex;
  align-items: center;
  color: #606266;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
  user-select: none;
  z-index: 1;
}

.input-port {
  left: -4px;
  top: 60%;
  transform: translateY(-50%);
  justify-content: flex-end;
}

.output-port {
  right: -4px;
  top: 60%;
  transform: translateY(-50%);
  justify-content: flex-start;
}

.port-content {
  position: relative;
  background: transparent;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.3s;
  display: flex;
  align-items: center;
}

.port-label {
  white-space: nowrap;
  font-size: 12px;
  color: white;
  transition: all 0.3s;
  padding: 4px 8px;
  border-radius: 4px;
  opacity: 0;
  position: absolute;
  background: rgba(0, 0, 0, 0.75);
  pointer-events: none;
  z-index: 10;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transform: translateY(-50%);
  top: 50%;
}

.port:hover .port-label {
  opacity: 1;
}

.input-port .port-label {
  right: 100%;
  margin-right: 8px;
}

.output-port .port-label {
  left: 100%;
  margin-left: 8px;
}

.port-dot {
  width: 8px;
  height: 8px;
  background: #409EFF;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #ffffff;
  box-shadow: 0 0 0 1px #409EFF;
  position: relative;
  z-index: 2;
  flex-shrink: 0;
}

.port:hover .port-dot {
  transform: scale(1.2);
  background: #67C23A;
  box-shadow: 0 0 0 1px #67C23A;
}

.port.connecting .port-label {
  color: #67C23A;
  background: rgba(103, 194, 58, 0.1);
}

.port.can-connect .port-label {
  color: #67C23A;
  background: rgba(103, 194, 58, 0.1);
}

.config-content {
  padding: 20px;
}

.ports-section,
.properties-section {
  margin-bottom: 20px;
}

.port-item,
.property-item {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  align-items: center;
}

.port-item .el-input,
.port-item .el-select,
.property-item .el-input,
.property-item .el-select {
  width: 200px;
}

h3 {
  margin-bottom: 15px;
  color: #606266;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.code-panel {
  position: fixed;
  right: 0;
  top: 0;
  bottom: 0;
  width: 400px;
  background: #ffffff;
  color: #333;
  transition: transform 0.3s ease;
  z-index: 1000;
  border-left: 1px solid #e4e7ed;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
}

.code-panel-collapsed {
  transform: translateX(380px);
}

.code-panel-header {
  height: 40px;
  padding: 0 15px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f5f7fa;
  cursor: pointer;
  border-bottom: 1px solid #e4e7ed;
}

.code-panel-header .el-icon {
  transition: transform 0.3s ease;
  color: #909399;
}

.code-panel-header .el-icon.is-collapsed {
  transform: rotate(180deg);
}

.code-tabs {
  display: flex;
  background: #f5f7fa;
  padding: 0 10px;
  border-bottom: 1px solid #e4e7ed;
}

.code-tab {
  padding: 8px 15px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  color: #606266;
}

.code-tab.active {
  border-bottom-color: #409EFF;
  color: #409EFF;
}

.code-content {
  padding: 15px;
  height: calc(100% - 90px);
  overflow: auto;
  background: #ffffff;
}

.code-content pre {
  margin: 0;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  line-height: 1.5;
  color: #333;
}

.context-menu {
  position: fixed;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,.1);
  padding: 5px 0;
  z-index: 3000;
}

.menu-item {
  padding: 8px 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
}

.menu-item:hover {
  background: #f5f7fa;
  color: #409eff;
}

.file-tree {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #ffffff;
}

.tree-content {
  flex: 1;
  overflow: auto;
  padding: 10px 0;
}

.tree-node {
  display: flex;
  flex-direction: column;
}

.tree-children {
  padding-left: 20px;
}

.tree-item {
  display: flex;
  align-items: center;
  padding: 4px 8px;
  cursor: pointer;
  user-select: none;
  gap: 4px;
  color: #606266;
  font-size: 14px;
}

.tree-item:hover {
  background-color: #f5f7fa;
}

.tree-item.is-folder {
  font-weight: 500;
  font-size: 15px;
  color: #303133;
}

.file-name {
  font-size: 14px;
  line-height: 1.5;
}

.expand-icon {
  font-size: 12px;
  color: #909399;
  transition: transform 0.3s ease;
}

.sub-categories {
  background: #fff;
}

.sub-category {
  border-bottom: 1px solid #f0f0f0;
}

.sub-category:last-child {
  border-bottom: none;
}

.expand-icon.is-expanded {
  transform: rotate(90deg);
}

.sub-category-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px 10px 24px;
  background: #fafafa;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  border: 1px solid #e4e7ed;
}

.file-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #ffffff;
}

.file-header {
  padding: 10px 15px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  gap: 10px;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #409EFF;
}

.back-button:hover {
  color: #66b1ff;
}

.file-body {
  flex: 1;
  overflow: auto;
  padding: 15px;
}

.file-body pre {
  margin: 0;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  line-height: 1.5;
  color: #333;
}

.module-icon {
  width: 16px;
  height: 16px;
  margin-right: 8px;
  object-fit: contain; 
}

.node-icon {
  width: 16px;
  height: 16px;
  margin-right: 4px;
  object-fit: contain;
  display: inline-block;
  vertical-align: middle;
}

.config-section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-header h4 {
  margin: 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
  position: relative;
  padding-left: 12px;
}

.section-header h4::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 16px;
  background: #409EFF;
  border-radius: 2px;
}

.table-name-row .label {
  font-size: 16px;
  color: #303133;
  font-weight: 600;
  white-space: nowrap;
}

.parameter-header {
  display: flex;
  padding: 8px 0;
  border-bottom: 1px solid #e4e7ed;
  margin-bottom: 10px;
}

.parameter-header span {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.parameter-item {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  align-items: center;
}

.param-col {
  flex: 1;
  min-width: 0;
}

.param-col:last-child {
  flex: 0 0 80px;
  text-align: center;
}

.section-content {
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

/* 节点参数信息显示样式 */
.node-params-display {
  position: absolute;
  left: 10px;
  right: 0;
  top: 0;
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.9);
  font-size: 9px;
  line-height: 1.2;
  border-radius: 8px 8px 0 0;
}

.param-line {
  display: flex;
  align-items: center;
  margin-bottom: 1px;
  color: #606266;
}

.param-line:last-child {
  margin-bottom: 0;
}

.param-label {
  font-weight: 600;
  color: #909399;
  min-width: 25px;
  margin-right: 3px;
  font-size: 9px;
}

.param-text {
  color: #409EFF;
  font-weight: 500;
  word-break: break-all;
  flex: 1;
  font-size: 9px;
}

/* 节点样式 */

/* 可拖拽文件样式 */
.draggable-file {
  cursor: grab;
  color: #409EFF;
  font-weight: 500;
}

.draggable-file:hover {
  color: #66b1ff;
  text-decoration: underline;
}

.draggable-file:active {
  cursor: grabbing;
}

/* 选中节点样式 */
.node.selected {
  box-shadow: 0 0 0 2px #409EFF;
  border-color: #409EFF;
}

.node:hover {
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.1);
  border-color: #409EFF;
}

.node-type {
  font-size: 12px;
  color: #909399;
  margin-left: 3px;
}

.tabs-container {
  background: #fafafa;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
  border-radius: 8px 8px 0 0;
}

.tabs-header {
  display: flex;
  align-items: center;
  padding: 0 0px;
  background: transparent;
  border-radius: 8px 8px 0 0;
}

.tab-item {
  padding: 12px 20px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  color: #606266;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
  background: transparent;
  border-radius: 4px 4px 0 0;
  margin-right: 2px;
}

.tab-item.active {
  border-bottom-color: #409EFF;
  color: #409EFF;
  background: #fff;
  box-shadow: 0 -2px 8px rgba(64, 158, 255, 0.1);
}

.tab-item:hover {
  background: #f0f9ff;
  color: #409EFF;
}

.tab-title {
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tab-close {
  cursor: pointer;
  font-size: 16px;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s;
  color: #909399;
}

.tab-close:hover {
  background: #f56c6c;
  color: white;
}

.tab-add {
  cursor: pointer;
  font-size: 18px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  color: #909399;
  transition: all 0.3s;
  margin-left: 10px;
  background: transparent;
}

.tab-add:hover {
  background: #409EFF;
  color: white;
}

.module-categories {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.module-category {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 8px;
  background: #ffffff;
  transition: all 0.3s ease;
}

.module-category:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.category-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-bottom: 1px solid #e4e7ed;
  cursor: pointer;
  user-select: none;
  transition: all 0.3s ease;
  border-radius: 4px;
}

.category-header:hover {
  background-color: #f5f7fa;
}

.category-icon {
  width: 18px;
  height: 18px;
  object-fit: contain;
  flex-shrink: 0;
}

.category-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.category-count {
  font-size: 12px;
  color: #909399;
  margin-left: 4px;
  flex-shrink: 0;
}

.category-arrow {
  transition: transform 0.3s ease;
  cursor: pointer;
  font-size: 10px;
  color: #909399;
  width: 14px;
  height: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.category-arrow.expanded {
  transform: rotate(90deg);
}


.module-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background: #fff;
  cursor: grab;
  transition: all 0.3s ease;
  user-select: none;
  min-height: 28px;
  position: relative;
  width: 100%;
  box-sizing: border-box;
}

.module-item:hover {
  border-color: #409eff;
  background: #f0f9ff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
}

.module-item:active {
  cursor: grabbing;
  transform: translateY(0);
}

/* 为不同类型的模块添加左侧颜色标识 */
.module-item[data-type="insert"] {
  border-left: 3px solid #409eff;
}

.module-item[data-type="update"] {
  border-left: 3px solid #67c23a;
}

.module-item[data-type="select"] {
  border-left: 3px solid #e6a23c;
}

.module-item[data-type="delete"] {
  border-left: 3px solid #f56c6c;
}

.module-item[data-type="create"] {
  border-left: 3px solid #722ed1;
}

.module-item[data-type="custom"] {
  border-left: 3px solid #909399;
}

/* 子类型标识 */
.module-item[data-subtype="base"]::after {
  content: "基础";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #67c23a;
  background: #f0f0f0;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="where"]::after {
  content: "条件";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #e6a23c;
  background: #fdf6ec;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="batch"]::after {
  content: "批量";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #409eff;
  background: #ecf5ff;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="join"]::after {
  content: "关联";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #67c23a;
  background: #f0f9ff;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="aggregate"]::after {
  content: "聚合";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #722ed1;
  background: #f9f0ff;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="table"]::after {
  content: "表";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #f56c6c;
  background: #fef0f0;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="database"]::after {
  content: "库";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #e6a23c;
  background: #fdf6ec;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="data_process"]::after {
  content: "处理";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #909399;
  background: #f4f4f5;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="data_analysis"]::after {
  content: "分析";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #67c23a;
  background: #f0f9ff;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="data_transform"]::after {
  content: "转换";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #409eff;
  background: #ecf5ff;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="upsert"]::after {
  content: "插入或更新";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #409eff;
  background: #ecf5ff;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-icon {
  width: 16px;
  height: 16px;
  object-fit: contain;
  flex-shrink: 0;
}

.module-info {
  display: flex;
  flex-direction: column;
  gap: 1px;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  padding-right: 50px; /* 为子类型标签留出空间 */
}

.module-name {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.2;
}

.module-desc {
  font-size: 11px;
  color: #909399;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.2;
}



.sub-category-header:hover {
  background: #f0f9ff;
}

.sub-category-header.expanded {
  border-bottom: 1px solid #e4e7ed;
}

.sub-category-icon {
  width: 16px;
  height: 16px;
  object-fit: contain;
  flex-shrink: 0;
}

.sub-category-name {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  flex: 1;
}

.sub-modules {
  /* padding: 6px 2px 6px 2px; */
  gap: 3px;
  border: 1px solid #e4e7ed;
  border-radius: 3px;
}

.module-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background: #fff;
  cursor: grab;
  transition: all 0.3s ease;
  user-select: none;
  min-height: 28px;
  position: relative;
}

.module-item:hover {
  border-color: #409eff;
  background: #f0f9ff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.module-item:active {
  cursor: grabbing;
  transform: translateY(0);
}

/* 为不同类型的模块添加左侧颜色标识 */
.module-item[data-type="insert"] {
  border-left: 3px solid #409eff;
}

.module-item[data-type="update"] {
  border-left: 3px solid #67c23a;
}

.module-item[data-type="select"] {
  border-left: 3px solid #e6a23c;
}

.module-item[data-type="delete"] {
  border-left: 3px solid #f56c6c;
}

.module-item[data-type="create"] {
  border-left: 3px solid #722ed1;
}

.module-item[data-type="custom"] {
  border-left: 3px solid #909399;
}

/* 子类型标识 */
.module-item[data-subtype="base"]::after {
  content: "基础";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #67c23a;
  background: #f0f0f0;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="where"]::after {
  content: "条件";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #e6a23c;
  background: #fdf6ec;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="batch"]::after {
  content: "批量";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #409eff;
  background: #ecf5ff;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="join"]::after {
  content: "关联";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #67c23a;
  background: #f0f9ff;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="aggregate"]::after {
  content: "聚合";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #722ed1;
  background: #f9f0ff;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="table"]::after {
  content: "表";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #f56c6c;
  background: #fef0f0;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="database"]::after {
  content: "库";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #e6a23c;
  background: #fdf6ec;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="data_process"]::after {
  content: "处理";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #909399;
  background: #f4f4f5;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="data_analysis"]::after {
  content: "分析";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #67c23a;
  background: #f0f9ff;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="data_transform"]::after {
  content: "转换";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #409eff;
  background: #ecf5ff;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="upsert"]::after {
  content: "插入或更新";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #409eff;
  background: #ecf5ff;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-icon {
  width: 16px;
  height: 16px;
  object-fit: contain;
  flex-shrink: 0;
}

.module-info {
  display: flex;
  flex-direction: column;
  gap: 1px;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  padding-right: 50px; /* 为子类型标签留出空间 */
}

.module-name {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.2;
}

.module-desc {
  font-size: 11px;
  color: #909399;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.2;
}



.sub-category-header:hover {
  background: #f0f9ff;
}

.sub-category-header.expanded {
  border-bottom: 1px solid #e4e7ed;
}

.sub-category-icon {
  width: 16px;
  height: 16px;
  object-fit: contain;
  flex-shrink: 0;
}

.sub-category-name {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  flex: 1;
}

.sub-modules {
  /* padding: 6px 2px 6px 2px; */
  gap: 3px;
  border: 1px solid #e4e7ed;
  border-radius: 3px;
}

.module-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background: #fff;
  cursor: grab;
  transition: all 0.3s ease;
  user-select: none;
  min-height: 28px;
  position: relative;
}

.module-item:hover {
  border-color: #409eff;
  background: #f0f9ff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.module-item:active {
  cursor: grabbing;
  transform: translateY(0);
}

.module-icon {
  width: 16px;
  height: 16px;
  object-fit: contain;
  flex-shrink: 0;
}

.module-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  padding-right: 50px; /* 为子类型标签留出空间 */
}

.module-name {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 自定义tooltip样式 */
.module-item[title]:hover::before,
.category-header[title]:hover::before,
.sub-category-header[title]:hover::before {
  content: attr(title);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: #303133;
  color: white;
  padding: 6px 10px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  z-index: 1000;
  margin-bottom: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  pointer-events: none;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.module-item[title]:hover::after,
.category-header[title]:hover::after,
.sub-category-header[title]:hover::after {
  content: '';
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 5px solid transparent;
  border-top-color: #303133;
  margin-bottom: 1px;
  pointer-events: none;
}

/* 子类型标识 */
.module-item[data-subtype="basic"]::after {
  content: "基础";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #67c23a;
  background: #f0f0f0;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="where"]::after {
  content: "条件";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #e6a23c;
  background: #fdf6ec;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="batch"]::after {
  content: "批量";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #409eff;
  background: #ecf5ff;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="join"]::after {
  content: "关联";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #67c23a;
  background: #f0f9ff;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="group"]::after {
  content: "分组";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #722ed1;
  background: #f9f0ff;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="complex"]::after {
  content: "复合";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #f56c6c;
  background: #fef0f0;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="upsert"]::after {
  content: "插入或更新";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #409eff;
  background: #ecf5ff;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="database"]::after {
  content: "数据库";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #e6a23c;
  background: #fdf6ec;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="table"]::after {
  content: "表";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #f56c6c;
  background: #fef0f0;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="index"]::after {
  content: "索引";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #67c23a;
  background: #f0f9ff;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="column"]::after {
  content: "列";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #909399;
  background: #f4f4f5;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="begin"]::after {
  content: "开始";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #67c23a;
  background: #f0f9ff;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="commit"]::after {
  content: "提交";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #409eff;
  background: #ecf5ff;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="rollback"]::after {
  content: "回滚";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #f56c6c;
  background: #fef0f0;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="grant"]::after {
  content: "授予";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #67c23a;
  background: #f0f9ff;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="revoke"]::after {
  content: "撤销";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #f56c6c;
  background: #fef0f0;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="statistical"]::after {
  content: "统计";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #722ed1;
  background: #f9f0ff;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="trend"]::after {
  content: "趋势";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #e6a23c;
  background: #fdf6ec;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="format"]::after {
  content: "格式";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #409eff;
  background: #ecf5ff;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="cleaning"]::after {
  content: "清洗";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #67c23a;
  background: #f0f9ff;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="script"]::after {
  content: "脚本";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #909399;
  background: #f4f4f5;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="function"]::after {
  content: "函数";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #722ed1;
  background: #f9f0ff;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="aggregate"]::after {
  content: "聚合";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #722ed1;
  background: #f9f0ff;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="transform"]::after {
  content: "转换";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #409eff;
  background: #ecf5ff;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="advanced_statistical"]::after {
  content: "高级统计";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #722ed1;
  background: #f9f0ff;
  padding: 1px 4px;
  border-radius: 2px;
}

.module-item[data-subtype="advanced"]::after {
  content: "高级";
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 10px;
  color: #909399;
  background: #f4f4f5;
  padding: 1px 4px;
  border-radius: 2px;
}


  
  .module-title {
    font-size: 14px;
    margin-bottom: 12px;
  }
  
  .category-header {
    padding: 10px;
  }
  
  
  .category-desc {
    font-size: 10px;
    max-width: 80px;
  }
  /* 二级标题间距 */
  .sub-category-header {
    padding: 1px;
  }
  
  .sub-category-name {
    font-size: 12px;
  }
  
  .sub-category-desc {
    font-size: 9px;
    max-width: 70px;
  }
  
  
  .module-item {
    padding: 2px 6px 2px 43px;
    gap: 2px;
    min-height: 28px;
  }
  
  .module-icon {
    width: 14px;
    height: 14px;
  }
  
  .module-name {
    font-size: 12px;
  }
  
  .module-desc {
    font-size: 10px;
  }
  
  /* 调整子类型标签在小屏幕下的大小 */
  .module-item[data-subtype]::after {
    font-size: 8px;
    padding: 1px 2px;
    top: 1px;
    right: 2px;
  }
  
  .module-info {
    padding-right: 35px;
  }
</style> 