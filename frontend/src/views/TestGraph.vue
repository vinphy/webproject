<template>
  <div class="test-graph-canvas">
    <div v-for="node in nodes" :key="node.id" class="node" :style="{ left: node.x + 'px', top: node.y + 'px' }">
      <div class="node-header">
        <img :src="node.icon" class="node-icon" alt="节点图标" />
        <span>{{ node.name }}</span>
        <span class="node-type">({{ node.type }})</span>
      </div>
      <!-- 端口等可后续补充 -->
    </div>
    <svg class="connections-layer">
      <g>
        <path v-for="conn in connections" :key="conn.id"
          :d="`M ${conn.startPos.x} ${conn.startPos.y} L ${conn.endPos.x} ${conn.endPos.y}`"
          class="connection-path" />
      </g>
    </svg>
  </div>
</template>

<script setup>
const props = defineProps({
  nodes: { type: Array, default: () => [] },
  connections: { type: Array, default: () => [] }
})
</script>

<style scoped>
.test-graph-canvas {
  position: relative;
  width: 100%;
  height: 100%;
  background: #181c24;
  overflow: auto;
}
.node {
  position: absolute;
  min-width: 120px;
  min-height: 40px;
  background: #232a36;
  border: 1.5px solid #409EFF;
  border-radius: 8px;
  color: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  padding: 8px 16px;
}
.node-header {
  display: flex;
  align-items: center;
  gap: 8px;
}
.node-icon {
  width: 24px;
  height: 24px;
}
.connection-path {
  stroke: #409EFF;
  stroke-width: 2;
  fill: none;
  marker-end: url(#arrowhead);
}
</style> 