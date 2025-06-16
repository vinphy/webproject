<template>
  <div class="module-management">
    <div class="module-container">
      <!-- 左侧模块列表 -->
      <div class="module-list">
        <h3>可用模块</h3>
        <div class="module-items">
          <div
            v-for="module in availableModules"
            :key="module.id"
            class="module-item"
            :data-type="module.type"
            draggable="true"
            @dragstart="handleDragStart($event, module)"
          >
            <el-icon><component :is="module.icon" /></el-icon>
            <span>{{ module.name }}</span>
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
              <el-icon><component :is="node.icon" /></el-icon>
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
      <el-tabs v-model="activeTab">
        <el-tab-pane label="端口配置" name="ports">
          <div class="config-content">
            <div class="ports-section">
              <h3>输入端口</h3>
              <div v-for="(input, index) in currentNode?.inputs" :key="'input-' + index" class="port-item">
                <el-input v-model="input.name" placeholder="端口名称" />
                <el-select v-model="input.type" placeholder="数据类型">
                  <el-option label="数值" value="number" />
                  <el-option label="字符串" value="string" />
                  <el-option label="布尔值" value="boolean" />
                  <el-option label="数组" value="array" />
                  <el-option label="对象" value="object" />
                </el-select>
                <el-button type="danger" @click="removePort('input', index)">删除</el-button>
  </div>
              <el-button type="primary" @click="addPort('input')">添加输入端口</el-button>
            </div>
            
            <div class="ports-section">
              <h3>输出端口</h3>
              <div v-for="(output, index) in currentNode?.outputs" :key="'output-' + index" class="port-item">
                <el-input v-model="output.name" placeholder="端口名称" />
                <el-select v-model="output.type" placeholder="数据类型">
                  <el-option label="数值" value="number" />
                  <el-option label="字符串" value="string" />
                  <el-option label="布尔值" value="boolean" />
                  <el-option label="数组" value="array" />
                  <el-option label="对象" value="object" />
                </el-select>
                <el-button type="danger" @click="removePort('output', index)">删除</el-button>
              </div>
              <el-button type="primary" @click="addPort('output')">添加输出端口</el-button>
            </div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="属性配置" name="properties">
          <div class="config-content">
            <div class="properties-section">
              <div v-for="(prop, key) in currentNode?.properties" :key="key" class="property-item">
                <el-input v-model="prop.name" placeholder="属性名称" />
                <el-select v-model="prop.type" placeholder="数据类型">
                  <el-option label="数值" value="number" />
                  <el-option label="字符串" value="string" />
                  <el-option label="布尔值" value="boolean" />
                  <el-option label="数组" value="array" />
                  <el-option label="对象" value="object" />
                </el-select>
                <el-input v-model="prop.value" placeholder="默认值" />
                <el-button type="danger" @click="removeProperty(key)">删除</el-button>
              </div>
              <el-button type="primary" @click="addProperty">添加属性</el-button>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="configDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveConfig">保存</el-button>
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
        生成模型文件
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

// 可用模块列表
const availableModules = ref([
  {
    id: 1,
    name: 'insert模块',
    icon: 'Cpu',
    type: 'cpu',
    inputs: [
      { name: '输入1', connected: false, id: 'input1' },
      { name: '输入2', connected: false, id: 'input2' }
    ],
    outputs: [
      { name: '输出1', connected: false, id: 'output1' },
      { name: '输出2', connected: false, id: 'output2' }
    ]
  },
  {
    id: 2,
    name: 'update模块',
    icon: 'DataLine',
    type: 'data',
    inputs: [
      { name: '数据输入', connected: false, id: 'input1' }
    ],
    outputs: [
      { name: '处理结果', connected: false, id: 'output1' }
    ]
  },
  {
    id: 3,
    name: '数据处理',
    icon: 'Monitor',
    type: 'monitor',
    inputs: [
      { name: '信号输入', connected: false, id: 'input1' }
    ],
    outputs: [
      { name: '监控输出', connected: false, id: 'output1' }
    ]
  },
  {
    id: 4,
    name: '分析模块',
    icon: 'Histogram',
    type: 'analysis',
    inputs: [
      { name: '数据输入', connected: false, id: 'input1' }
    ],
    outputs: [
      { name: '分析结果', connected: false, id: 'output1' }
    ]
  }
])

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
  const module = availableModules.value.find(m => m.id === moduleId)
  
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
  currentNode.value = JSON.parse(JSON.stringify(node)) // 深拷贝
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

// 添加属性
const addProperty = () => {
  if (!currentNode.value) return
  
  const key = 'prop_' + Date.now()
  currentNode.value.properties[key] = {
    name: '',
    type: 'string',
    value: ''
  }
}

// 删除属性
const removeProperty = (key) => {
  if (!currentNode.value) return
  delete currentNode.value.properties[key]
}

// 保存配置
const saveConfig = () => {
  if (!currentNode.value) return
  
  // 更新节点配置
  const node = placedNodes.value.find(n => n.id === currentNode.value.id)
  if (node) {
    Object.assign(node, currentNode.value)
    // 更新连线
    updateConnections()
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
    if (!response.ok) {
      throw new Error('获取文件结构失败')
    }
    const data = await response.json()
    if (data.status === 'success') {
      // 对文件结构进行排序
      const sortDirectory = (dir) => {
        if (dir.children) {
          dir.children = sortFiles(dir.children)
          dir.children.forEach(child => {
            if (child.type === 'directory') {
              sortDirectory(child)
            }
          })
        }
        return dir
      }
      
      fileStructure.value = sortFiles(data.files).map(sortDirectory)
      // 异步预加载文件内容
      preloadFileContents(fileStructure.value)
    } else {
      throw new Error(data.message || '获取文件结构失败')
    }
  } catch (error) {
    console.error('获取文件结构失败:', error)
    ElMessage.error('获取文件结构失败：' + error.message)
  }
}

// 在组件挂载时获取文件结构
onMounted(() => {
  fetchFileStructure()
})

// 修改生成代码函数中的错误处理部分
const handleGenerateCode = async () => {
  console.log('开始生成代码，当前节点:', contextMenuNode.value)
  
  if (!contextMenuNode.value) {
    console.error('节点数据为空')
    ElMessage.error('未选择节点')
    return
  }

  // 检查节点数据结构
  console.log('节点完整数据:', JSON.stringify(contextMenuNode.value, null, 2))
  
  try {
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
    
    // 确保输入输出端口存在，并提供默认值
    const nodeData = contextMenuNode.value
    console.log('节点数据:', nodeData)
    
    // 检查并初始化输入输出端口
    if (!nodeData.inputs) {
      console.log('初始化输入端口')
      nodeData.inputs = []
    }
    if (!nodeData.outputs) {
      console.log('初始化输出端口')
      nodeData.outputs = []
    }
    if (!nodeData.properties) {
      console.log('初始化属性')
      nodeData.properties = {}
    }
    
    const inputs = Array.isArray(nodeData.inputs) ? nodeData.inputs : []
    const outputs = Array.isArray(nodeData.outputs) ? nodeData.outputs : []
    const properties = nodeData.properties || {}
    
    console.log('处理后的端口数据:', { inputs, outputs, properties })
    
    // 如果没有输入输出端口，添加默认端口
    if (inputs.length === 0) {
      console.log('添加默认输入端口')
      inputs.push({ name: 'input1', type: 'number' })
      inputs.push({ name: 'input2', type: 'number' })
    }
    if (outputs.length === 0) {
      console.log('添加默认输出端口')
      outputs.push({ name: 'result', type: 'number' })
    }
    
    // 生成 main.c
    const mainContent = `#include <stdio.h>

// 输入端口
${inputs.map(input => `double ${input.name || 'input_' + Math.random().toString(36).substr(2, 5)};`).join('\n')}

// 输出端口
${outputs.map(output => `double ${output.name || 'output_' + Math.random().toString(36).substr(2, 5)};`).join('\n')}

// 属性
${Object.entries(properties).map(([key, prop]) => 
`${prop.type || 'double'} ${prop.name || 'prop_' + key} = ${prop.value || '0'};`
).join('\n')}

int main() {
  // 读取输入
  ${inputs.map(input => 
    `printf("请输入 ${input.name || 'input_' + Math.random().toString(36).substr(2, 5)}: ");\n    scanf("%lf", &${input.name || 'input_' + Math.random().toString(36).substr(2, 5)});`
  ).join('\n    ')}
  
  // 执行加法运算
  ${outputs[0]?.name || 'result'} = ${inputs.map(input => input.name || 'input_' + Math.random().toString(36).substr(2, 5)).join(' + ')};
  
  // 输出结果
  printf("计算结果: %lf\\n", ${outputs[0]?.name || 'result'});
  
  return 0;
}`
    
    // 生成 README.md
    const readmeContent = `# ${nodeName} 组件

## 功能说明
这是一个简单的加法运算组件。

## 输入端口
${inputs.map(input => `- ${input.name || 'input_' + Math.random().toString(36).substr(2, 5)}: ${input.type || 'number'}`).join('\n')}

## 输出端口
${outputs.map(output => `- ${output.name || 'output_' + Math.random().toString(36).substr(2, 5)}: ${output.type || 'number'}`).join('\n')}

## 属性
${Object.entries(properties).map(([key, prop]) => 
`- ${prop.name || 'prop_' + key}: ${prop.type || 'number'} = ${prop.value || '0'}`
).join('\n')}

## 编译运行
\`\`\`bash
gcc src/main.c -o ${moduleName}
./${moduleName}
\`\`\``
    
    console.log('生成的文件内容:', { mainContent, readmeContent })
    
    // 准备文件数据
    const files = [
      {
        name: 'src/main.c',
        content: mainContent
      },
      {
        name: 'README.md',
        content: readmeContent
      }
    ]
    
    try {
      // 调用后端 API 写入文件
      const response = await fetch('http://localhost:8000/api/code/write_module_files', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          module_name: moduleName,
          files: files
        })
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      console.log('文件写入结果:', result)
      
      if (result.status === 'success') {
        // 重新获取文件结构
        await fetchFileStructure()
        
        // 重置当前文件
        currentFile.value = null
        isCodePanelCollapsed.value = false
        
        ElMessage.success('代码生成成功，文件已保存到本地')
      } else {
        throw new Error(result.message || '文件写入失败')
      }
    } catch (error) {
      console.error('文件写入失败:', error)
      ElMessage.error('文件写入失败：' + error.message)
    }

  } catch (error) {
    console.error('代码生成错误:', error)
    ElMessage.error('代码生成失败：' + (error.message || '未知错误'))
  }
  
  hideContextMenu()
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
  width: 200px;
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

.module-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
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
  gap: 8px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
  color: #303133;
  font-weight: 500;
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
  left: 0;
  transform: translateX(-15%);
  justify-content: flex-end;
}

.output-port {
  right: 0;
  transform: translateX(15%);
  justify-content: flex-start;
}

.port-content {
  background: transparent;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.3s;
}

.port:hover .port-content {
  background: transparent;
}

.port-label {
  white-space: nowrap;
  font-size: 12px;
  color: #909399;
  transition: all 0.3s;
  padding: 2px 4px;
  border-radius: 2px;
}

.port:hover .port-label {
  color: #409EFF;
  background: rgba(64, 158, 255, 0.1);
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

.input-port .port-dot {
  margin-right: -4px;
}

.output-port .port-dot {
  margin-left: -4px;
}

.port:hover .port-dot {
  transform: scale(1.2);
  background: #67C23A;
  box-shadow: 0 0 0 1px #67C23A;
}

.port.connecting .port-dot {
  background: #67C23A;
  box-shadow: 0 0 0 2px #67C23A;
}

.port.can-connect .port-dot {
  background: #67C23A;
  box-shadow: 0 0 0 2px #67C23A;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(103, 194, 58, 0.4);
  }
  70% {
    box-shadow: 0 0 0 6px rgba(103, 194, 58, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(103, 194, 58, 0);
  }
}

/* 为不同类型的模块添加不同的颜色 */
.module-item[data-type="cpu"] {
  border-left: 3px solid #409EFF;
}

.module-item[data-type="data"] {
  border-left: 3px solid #67C23A;
}

.module-item[data-type="monitor"] {
  border-left: 3px solid #E6A23C;
}

.module-item[data-type="analysis"] {
  border-left: 3px solid #F56C6C;
}

/* 节点类型对应的颜色 */
.node[data-type="cpu"] {
  border-left: 3px solid #409EFF;
}

.node[data-type="data"] {
  border-left: 3px solid #67C23A;
}

.node[data-type="monitor"] {
  border-left: 3px solid #E6A23C;
}

.node[data-type="analysis"] {
  border-left: 3px solid #F56C6C;
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
</style> 