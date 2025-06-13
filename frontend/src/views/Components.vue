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
      >
        <div class="canvas">
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
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { 
  Cpu, 
  Connection, 
  DataLine, 
  Monitor,
  Histogram
} from '@element-plus/icons-vue'

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
</style> 