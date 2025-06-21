<template>
  <div class="config-section">
    <div class="section-header">
      <h4>删除操作配置</h4>
    </div>
    <div class="section-content">
      <div class="info-message">
        <el-alert
          title="删除操作说明"
          type="warning"
          :closable="false"
          show-icon
        >
          <template #default>
            <p>删除操作将根据条件语句删除匹配的数据记录。</p>
            <p>请确保在条件语句中设置正确的WHERE条件，避免误删数据。</p>
            <p>建议在删除前先使用SELECT语句验证要删除的数据。</p>
          </template>
        </el-alert>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  node: {
    type: Object,
    required: true
  }
})
</script>

<style scoped>
.info-message {
  margin-bottom: 15px;
}

.info-message p {
  margin: 5px 0;
  font-size: 14px;
  color: #606266;
}
</style> 