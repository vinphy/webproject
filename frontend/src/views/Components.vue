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
            <path
              v-for="conn in connections"
              :key="conn.id"
              :d="`M ${conn.startPos.x} ${conn.startPos.y} C ${(conn.startPos.x + conn.endPos.x) / 2} ${conn.startPos.y}, ${(conn.startPos.x + conn.endPos.x) / 2} ${conn.endPos.y}, ${conn.endPos.x} ${conn.endPos.y}`"
              class="connection-path"
            />
            <path
              v-if="tempLine"
              :d="`M ${tempLine.start.x} ${tempLine.start.y} C ${(tempLine.start.x + tempLine.end.x) / 2} ${tempLine.start.y}, ${(tempLine.start.x + tempLine.end.x) / 2} ${tempLine.end.y}, ${tempLine.end.x} ${tempLine.end.y}`"
              class="connection-path temp"
            />
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
              top: node.y + 'px'
            }"
            @mousedown="startDrag($event, node)"
          >
            <div class="node-header">
              <el-icon><component :is="node.icon" /></el-icon>
              <span>{{ node.name }}</span>
            </div>
            <div class="node-ports">
              <div class="input-ports">
                <div 
                  v-for="(input, index) in node.inputs" 
                  :key="'input-' + index"
                  class="port input-port"
                  :class="{ 'connected': input.connected }"
                  :data-port-id="input.id"
                  @mousedown="startConnection($event, node, input, true)"
                >
                  <div class="port-dot"></div>
                  <span>{{ input.name }}</span>
                </div>
              </div>
              <div class="output-ports">
                <div 
                  v-for="(output, index) in node.outputs" 
                  :key="'output-' + index"
                  class="port output-port"
                  :class="{ 'connected': output.connected }"
                  :data-port-id="output.id"
                  @mousedown="startConnection($event, node, output, false)"
                >
                  <span>{{ output.name }}</span>
                  <div class="port-dot"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
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
      y
    })
  }
}

// 开始拖动节点
const startDrag = (event, node) => {
  if (event.target.closest('.port')) return
  
  isDragging = true
  currentDragNode = node
  const rect = event.target.getBoundingClientRect()
  dragOffset = {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top
  }
  
  document.addEventListener('mousemove', handleDrag)
  document.addEventListener('mouseup', stopDrag)
}

// 处理节点拖动
const handleDrag = (event) => {
  if (!isDragging || !currentDragNode) return
  
  const canvas = document.querySelector('.canvas')
  const rect = canvas.getBoundingClientRect()
  
  currentDragNode.x = event.clientX - rect.left - dragOffset.x
  currentDragNode.y = event.clientY - rect.top - dragOffset.y
  
  // 更新连线位置
  updateConnections()
}

// 停止拖动
const stopDrag = () => {
  isDragging = false
  currentDragNode = null
  document.removeEventListener('mousemove', handleDrag)
  document.removeEventListener('mouseup', stopDrag)
}

// 开始连线
const startConnection = (event, node, port, isInput) => {
  event.stopPropagation()
  
  if (isInput && port.connected) return
  
  isConnecting = true
  startPort = { node, port, isInput }
  
  document.addEventListener('mousemove', handleConnectionMove)
  document.addEventListener('mouseup', stopConnection)
}

// 处理连线移动
const handleConnectionMove = (event) => {
  if (!isConnecting) return
  
  const canvas = document.querySelector('.canvas')
  const rect = canvas.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  
  // 更新临时连线
  tempLine = {
    start: getPortPosition(startPort.node, startPort.port, startPort.isInput),
    end: { x, y }
  }
}

// 停止连线
const stopConnection = (event) => {
  if (!isConnecting) return
  
  const targetPort = findPortAtPosition(event.clientX, event.clientY)
  
  if (targetPort && canConnect(startPort, targetPort)) {
    createConnection(startPort, targetPort)
  }
  
  isConnecting = false
  startPort = null
  tempLine = null
  
  document.removeEventListener('mousemove', handleConnectionMove)
  document.removeEventListener('mouseup', stopConnection)
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
  
  connections.value.push({
    id: Date.now(),
    start: start.isInput ? end : start,
    end: start.isInput ? start : end
  })
}

// 更新连线位置
const updateConnections = () => {
  connections.value = connections.value.map(conn => ({
    ...conn,
    startPos: getPortPosition(conn.start.node, conn.start.port, conn.start.isInput),
    endPos: getPortPosition(conn.end.node, conn.end.port, conn.end.isInput)
  }))
}

// 组件卸载时清理事件监听
onUnmounted(() => {
  document.removeEventListener('mousemove', handleDrag)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('mousemove', handleConnectionMove)
  document.removeEventListener('mouseup', stopConnection)
})
</script>

<style scoped>
.module-management {
  height: 100%;
  padding: 20px;
  background: #f5f7fa;
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

.connection-path {
  fill: none;
  stroke: #409EFF;
  stroke-width: 2;
  pointer-events: none;
}

.connection-path.temp {
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
  transition: all 0.3s;
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
  padding: 12px 0;
}

.port {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 8px 0;
  color: #606266;
  font-size: 13px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.3s;
}

.port:hover {
  background: #f5f7fa;
  color: #409EFF;
}

.input-port {
  justify-content: flex-start;
}

.output-port {
  justify-content: flex-end;
}

.port-dot {
  width: 10px;
  height: 10px;
  background: #409EFF;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid #ffffff;
  box-shadow: 0 0 0 1px #409EFF;
}

.port:hover .port-dot {
  transform: scale(1.2);
  background: #67C23A;
  box-shadow: 0 0 0 1px #67C23A;
}

.port.connected .port-dot {
  background: #67C23A;
  box-shadow: 0 0 0 1px #67C23A;
}

.input-port .port-dot {
  margin-right: 8px;
}

.output-port .port-dot {
  margin-left: 8px;
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
</style> 