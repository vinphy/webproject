<template>
  <div class="module-management">
    <div class="module-container">
      <!-- 左侧模块列表 -->
      <div class="module-list">
        <h3>模块列表</h3>
        <!-- 基础模块 -->
        <div class="module-category">
          <h4>基础模块</h4>
          <div class="module-items">
            <div
              v-for="module in availableModules.basic"
              :key="module.id"
              class="module-item"
              :data-type="module.type"
              draggable="true"
              @dragstart="handleDragStart($event, module)"
            >
              <img :src="module.icon" class="module-icon" alt="模块图标" />
              <span>{{ module.name }}</span>
            </div>
          </div>
        </div>
        <!-- 自定义模块 -->
        <div class="module-category">
          <h4>自定义模块</h4>
          <div class="module-items">
            <div
              v-for="module in availableModules.custom"
              :key="module.id"
              class="module-item"
              :data-type="module.type"
              draggable="true"
              @dragstart="handleDragStart($event, module)"
            >
              <img :src="module.icon" class="module-icon" alt="模块图标" />
              <span>{{ module.name }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧画布区域 -->
      <div 
        class="canvas-container"
        @dragover.prevent
        @drop="handleDrop"
        @contextmenu="handleCanvasContextMenu"
      >
        <div class="canvas" ref="canvasRef">
          <!-- 连线 -->
          <svg class="connections-layer">
            <defs>
              <marker
                id="arrowhead"
                markerWidth="8"
                markerHeight="6"
                refX="7"
                refY="3"
                orient="auto"
              >
                <polygon
                  points="0 0, 8 3, 0 6"
                  fill="#409EFF"
                />
              </marker>
              <marker
                id="arrowhead-temp"
                markerWidth="8"
                markerHeight="6"
                refX="7"
                refY="3"
                orient="auto"
              >
                <polygon
                  points="0 0, 8 3, 0 6"
                  fill="#67C23A"
                />
              </marker>
            </defs>
            <g v-for="conn in connections" :key="conn.id" class="connection-group">
              <path
                :d="getConnectionPath(conn.startPos, conn.endPos)"
                class="connection-path"
                :class="{ 'animated': conn.animated }"
                @click="selectConnection(conn)"
              />
            </g>
            <g v-if="tempLine" class="connection-group">
              <path
                :d="getConnectionPath(tempLine.start, tempLine.end)"
                class="connection-path temp"
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
            @dblclick="handleNodeDblClick(node)"
            @contextmenu="showContextMenu($event, node)"
          >
            <div class="node-header">
              <img :src="node.icon" class="node-icon" alt="节点图标" />
              <span>{{ node.name }}</span>
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
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 参数配置对话框 -->
    <el-dialog
      v-model="configDialogVisible"
      :title="currentNode?.name + ' 参数配置'"
      width="800px"
      destroy-on-close
    >
      <div class="config-content">
        <!-- 表名配置 -->
        <div class="config-section">
          <div class="section-header">
            <div class="table-name-row" style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
              <span class="label" style="min-width: 60px;">数据库：</span>
              <el-select 
                v-model="currentNode.databaseName" 
                :placeholder="currentNode.type === 'create' ? '选择或输入数据库名称' : '选择数据库'"
                :filterable="currentNode.type === 'create'"
                :allow-create="currentNode.type === 'create'"
                :default-first-option="currentNode.type === 'create'"
                style="width: 200px"
                @change="onDatabaseChange"
              >
                <el-option 
                  v-for="db in databaseList" 
                  :key="db" 
                  :label="db" 
                  :value="db" 
                />
              </el-select>
              <span class="label" style="min-width: 60px;">表名：</span>
              <el-select 
                v-model="currentNode.tableName" 
                :placeholder="currentNode.type === 'create' ? '选择或输入表名' : '选择表名'"
                :filterable="currentNode.type === 'create'"
                :allow-create="currentNode.type === 'create'"
                :default-first-option="currentNode.type === 'create'"
                style="width: 200px"
              >
                <el-option 
                  v-for="table in getTablesByDatabase(currentNode.databaseName)" 
                  :key="table" 
                  :label="table" 
                  :value="table" 
                />
              </el-select>
            </div>
          </div>
        </div>

        <!-- 参数配置 -->
        <div class="config-section">
          <div class="section-header">
            <h4>字段配置</h4>
            <el-button type="primary" size="small" @click="addParameter">添加参数</el-button>
          </div>
          <div class="section-content">
            <div class="parameter-header">
              <span class="param-col">列名</span>
              <span class="param-col">值</span>
              <span class="param-col">操作</span>
            </div>
            <div v-for="(param, index) in currentNode.parameters" :key="index" class="parameter-item">
              <el-input v-model="param.name" placeholder="字段名" class="param-col" />
              <el-input v-model="param.value" placeholder="字段值/类型" class="param-col" />
              <div class="param-col">
                <el-button type="danger" size="small" @click="removeParameter(index)">删除</el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 条件配置 -->
        <div class="config-section">
          <div class="section-header">
            <h4>条件语句</h4>
          </div>
          <div class="section-content">
            <el-input
              v-model="currentNode.condition"
              type="textarea"
              :rows="3"
              placeholder="请输入WHERE条件，例如: id = 1 AND status = 'active'"
            />
          </div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="configDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveConfig">确定</el-button>
        </span>
      </template>
    </el-dialog>

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
                      @dblclick="file.type === 'file' ? openFile(file) : null"
                      @click="file.type === 'directory' ? toggleFolder(file) : null"
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
                          @dblclick="child.type === 'file' ? openFile(child) : null"
                          @click="child.type === 'directory' ? toggleFolder(child) : null"
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
                              @dblclick="grandChild.type === 'file' ? openFile(grandChild) : null"
                              @click="grandChild.type === 'directory' ? toggleFolder(grandChild) : null"
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
import { ref, onMounted, onUnmounted, computed } from 'vue'
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
  FolderOpened
} from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage, ElLoading } from 'element-plus'
import WaveIcon from '../assets/波形.svg'

// 可用模块列表
const availableModules = ref({
  basic: [
    {
      id: 1,
      name: 'insert',
      icon: WaveIcon,
      type: 'insert',
      category: 'basic',
      inputs: [
        { name: '输入1', connected: false, id: 'input1' }
      ],
      outputs: [
        { name: '输出1', connected: false, id: 'output1' }
      ]
    },
    {
      id: 2,
      name: 'update',
      icon: WaveIcon,
      type: 'update',
      category: 'basic',
      inputs: [
        { name: '数据输入', connected: false, id: 'input1' }
      ],
      outputs: [
        { name: '处理结果', connected: false, id: 'output1' }
      ]
    },
    {
      id: 3,
      name: 'select',
      icon: WaveIcon,
      type: 'select',
      category: 'basic',
      inputs: [
        { name: '信号输入', connected: false, id: 'input1' }
      ],
      outputs: [
        { name: '监控输出', connected: false, id: 'output1' }
      ]
    },
    {
      id: 4,
      name: 'create',
      icon: WaveIcon,
      type: 'create',
      category: 'basic',
      inputs: [
        { name: '数据输入', connected: false, id: 'input1' }
      ],
      outputs: [
        { name: '创建结果', connected: false, id: 'output1' }
      ]
    },
    {
      id: 6,
      name: 'delete',
      icon: WaveIcon,
      type: 'delete',
      category: 'basic',
      inputs: [
        { name: '数据输入', connected: false, id: 'input1' }
      ],
      outputs: [
        { name: '创建结果', connected: false, id: 'output1' }
      ]
    }
  ],
  custom: [
    {
      id: 5,
      name: 'custom',
      icon: WaveIcon,
      type: 'custom',
      category: 'custom',
      inputs: [
        { name: '数据输入', connected: false, id: 'input1' }
      ],
      outputs: [
        { name: '分析结果', connected: false, id: 'output1' }
      ]
    }
  ]
})

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
        } else {
          // 获取所有数据库表对应关系
          databaseTables.value = data.database_tables
          tableCache.value.set('all', data.database_tables)
        }
      }
    }
  } catch (error) {
    console.error('预加载表列表失败:', error)
  }
}

// 根据数据库名获取表列表
const getTablesByDatabase = (databaseName) => {
  return databaseTables.value[databaseName] || []
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
  const canvas = document.querySelector('.canvas')
  const rect = canvas.getBoundingClientRect()
  
  connections.value = connections.value.map(conn => {
    const startNode = document.querySelector(`[data-node-id="${conn.start.node.id}"]`)
    const endNode = document.querySelector(`[data-node-id="${conn.end.node.id}"]`)
    
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
  const moduleId = parseInt(event.dataTransfer.getData('moduleId'))
  // 在basic和custom分类中查找模块
  const module = availableModules.value.basic.find(m => m.id === moduleId) || 
                availableModules.value.custom.find(m => m.id === moduleId)
  
  if (module) {
    const rect = event.target.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top
    
    placedNodes.value.push({
      ...module,
      id: nodeId++,
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
  
  // 确保parameters数组存在且至少有一个元素
  if (!currentNode.value.parameters) {
    currentNode.value.parameters = [{
      name: '',
      value: ''
    }]
  }
  
  // 如果不是create类型，设置默认的数据库和表名
  if (node.type !== 'create') {
    // 如果没有设置数据库名，选择第一个数据库
    if (!currentNode.value.databaseName && databaseList.value.length > 0) {
      currentNode.value.databaseName = databaseList.value[0]
    }
    
    // 如果有数据库名，设置默认表名
    if (currentNode.value.databaseName) {
      const tables = getTablesByDatabase(currentNode.value.databaseName)
      if (tables.length > 0 && !currentNode.value.tableName) {
        currentNode.value.tableName = tables[0]
      }
    }
  }
  
  configDialogVisible.value = true
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
const addParameter = () => {
  if (!currentNode.value) return
  
  if (!currentNode.value.parameters) {
    currentNode.value.parameters = []
  }
  
  currentNode.value.parameters.push({
    name: '',
    value: ''
  })
}

// 删除参数
const removeParameter = (index) => {
  if (!currentNode.value) return
  currentNode.value.parameters.splice(index, 1)
}

// 保存配置
const saveConfig = () => {
  if (!currentNode.value) return
  
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
  await fetchFileStructure()
  await preloadDatabases()
  await preloadTables()
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
    
    // 准备节点数据
    const nodeData = {
      name: moduleName,
      type: contextMenuNode.value.type,
      tableName: contextMenuNode.value.tableName,
      databaseName:contextMenuNode.value.databaseName,
      parameters: contextMenuNode.value.parameters || [],
      condition: contextMenuNode.value.condition
    }
    
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
      `XML文件：${result.files.xml}\n` +
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
      { path: `${newModulePath}/${moduleName}.xml`, type: 'file' },
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
    // 准备模型数据
    const modelData = {
      nodes: placedNodes.value.map(node => ({
        id: node.id,
        name: node.name,
        type: node.type,
        x: node.x,
        y: node.y,
        inputs: node.inputs || [],
        outputs: node.outputs || [],
        properties: node.properties || {}
      })),
      connections: connections.value.map(conn => ({
        id: conn.id,
        source: conn.source,
        target: conn.target,
        sourceHandle: conn.sourceHandle,
        targetHandle: conn.targetHandle
      }))
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
  // 清空当前表名
  currentNode.value.tableName = ''
  
  // 如果选择了数据库，加载该数据库的表列表
  if (currentNode.value.databaseName) {
    await preloadTables(currentNode.value.databaseName)
    
    // 如果不是create类型，自动选择第一个表
    if (currentNode.value.type !== 'create') {
      const tables = getTablesByDatabase(currentNode.value.databaseName)
      if (tables.length > 0) {
        currentNode.value.tableName = tables[0]
      }
    }
  }
}
</script>

<style scoped>
.module-management {
  height: 100%;
  padding: 20px;
  background: #f5f7fa;
  user-select: none; /* 禁止文字选择 */
}

.module-container {
  display: flex;
  gap: 20px;
  height: 100%;
}

.module-list {
  width: 130px;
  background: #ffffff;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.module-list h3 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.module-category {
  margin-bottom: 20px;
}

.module-category h4 {
  margin: 0 0 10px 0;
  color: #606266;
  font-size: 14px;
  font-weight: 500;
}

.module-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.module-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
  cursor: move;
  color: #606266;
  transition: all 0.3s;
  border: 1px solid #e4e7ed;
}

/* 为不同类型的模块添加不同的颜色 */
.module-item[data-type="insert"] {
  border-left: 3px solid #409EFF;
}

.module-item[data-type="update"] {
  border-left: 3px solid #67C23A;
}

.module-item[data-type="select"] {
  border-left: 3px solid #E6A23C;
}

.module-item[data-type="create"] {
  border-left: 3px solid #F56C6C;
}
.module-item[data-type="delete"] {
  border-left: 3px solid #722ED1;
}

.module-item[data-type="custom"] {
  border-left: 3px solid #909399;
}



/* 节点类型对应的颜色 */
.node[data-type="insert"] {
  border-left: 3px solid #409EFF;
}

.node[data-type="update"] {
  border-left: 3px solid #67C23A;
}

.node[data-type="select"] {
  border-left: 3px solid #E6A23C;
}

.node[data-type="create"] {
  border-left: 3px solid #F56C6C;
}
.node[data-type="delete"] {
  border-left: 3px solid #722ED1;
}

.node[data-type="custom"] {
  border-left: 3px solid #909399;
}

.module-item:hover {
  background: #ecf5ff;
  color: #409EFF;
  border-color: #409EFF;
}

.canvas-container {
  flex: 1;
  background: #ffffff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.canvas {
  width: 100%;
  height: 100%;
  position: relative;
  min-height: 500px;
  background: #f5f7fa;
  background-image: 
    linear-gradient(rgba(0, 0, 0, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 0, 0, 0.05) 1px, transparent 1px);
  background-size: 20px 20px;
}

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
  marker-end: url(#arrowhead);
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
}

@keyframes dash {
  to {
    stroke-dashoffset: -10;
  }
}

.node {
  position: absolute;
  width: 220px;
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
  gap: 8px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
  color: #303133;
  font-weight: 500;
  text-align: center;
}

.node-ports {
  position: relative;
  min-height: 120px;
  margin: 0 -12px;
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
  transition: transform 0.3s;
  cursor: pointer;
  margin-right: 4px;
  font-size: 14px;
}

.expand-icon.is-expanded {
  transform: rotate(90deg);
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
  margin-right: 8px;
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
</style> 