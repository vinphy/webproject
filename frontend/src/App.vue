<template>
  <div class="app">
    <el-container>
      <el-header>
        <h1>Vue + Python Demo</h1>
      </el-header>
      <el-main>
        <router-view></router-view>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
// 组件逻辑
</script>

<style>
.app {
  font-family: Arial, sans-serif;
}

.el-header {
  background-color: #409EFF;
  color: white;
  text-align: center;
  line-height: 60px;
}

.el-main {
  padding: 20px;
}
</style> 