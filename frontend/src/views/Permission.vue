<template>
  <div class="permission-page">
    <el-card class="permission-card">
      <div class="header-row">
        <h3>权限管理 (RBAC)</h3>
      </div>

      <div class="body-grid">
        <div class="col roles">
          <div class="section-title">角色</div>
          <el-input v-model="newRoleName" placeholder="新增角色名" clearable @keyup.enter="createRole" />
          <el-button type="primary" size="small" @click="createRole" style="margin-top:8px">新增角色</el-button>

          <el-list style="margin-top:12px">
            <el-radio-group v-model="selectedRoleId">
              <el-radio v-for="r in roles" :key="r.id" :label="r.id" class="role-item">
                {{ r.name }}
              </el-radio>
            </el-radio-group>
          </el-list>
        </div>

        <div class="col perms">
          <div class="section-title">权限 / 分配</div>
          <div class="perm-actions">
            <el-input v-model="newPermCode" placeholder="权限 code (eg: projects.create)" clearable style="width:48%" />
            <el-input v-model="newPermName" placeholder="权限名称" clearable style="width:48%; margin-left:8px" />
            <el-button type="primary" size="small" @click="createPermission" style="margin-top:8px">新增权限</el-button>
          </div>

          <div class="perm-list" style="margin-top:12px">
            <el-checkbox-group v-model="selectedPermissionIds">
              <el-checkbox v-for="p in permissions" :label="p.id" :key="p.id">{{ p.name }} ({{ p.code }})</el-checkbox>
            </el-checkbox-group>
          </div>

          <div style="margin-top:12px">
            <el-button type="primary" :disabled="!selectedRoleId" @click="assignPermissions">保存分配</el-button>
            <el-button plain @click="refreshAll">刷新</el-button>
          </div>
        </div>

        <div class="col users">
          <div class="section-title">用户</div>
          <div style="margin-bottom:8px">可为用户指派角色</div>
          <el-select v-model="selectedUserId" placeholder="选择用户" filterable clearable style="width:100%">
            <el-option v-for="u in users" :key="u.id" :label="u.username" :value="u.id" />
          </el-select>
          <el-select v-model="selectedUserRole" placeholder="选择角色" style="width:100%; margin-top:8px">
            <el-option v-for="r in roles" :key="r.id" :label="r.name" :value="r.name" />
          </el-select>
          <el-button type="primary" size="small" style="margin-top:8px" @click="assignRoleToUser" :disabled="!selectedUserId || !selectedUserRole">指派角色</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { api } from '@/utils/auth'
import { ElMessage } from 'element-plus'

const roles = ref([])
const permissions = ref([])
const users = ref([])

const selectedRoleId = ref(null)
const selectedPermissionIds = ref([])

const newRoleName = ref('')
const newPermCode = ref('')
const newPermName = ref('')

const selectedUserId = ref(null)
const selectedUserRole = ref(null)

const loadRoles = async () => {
  try {
    const { data } = await api.get('/api/auth/roles')
    roles.value = data || []
  } catch (e) { ElMessage.error('加载角色失败') }
}

const loadPermissions = async () => {
  try {
    const { data } = await api.get('/api/auth/permissions')
    permissions.value = data || []
  } catch (e) { ElMessage.error('加载权限失败') }
}

const loadUsers = async () => {
  try {
    const { data } = await api.get('/api/auth/users')
    users.value = data || []
  } catch (e) { /* users may be admin-only */ }
}

const refreshAll = async () => {
  await Promise.all([loadRoles(), loadPermissions(), loadUsers()])
  if (selectedRoleId.value) await loadRolePermissions(selectedRoleId.value)
}

const loadRolePermissions = async (roleId) => {
  if (!roleId) return
  try {
    const { data } = await api.get(`/api/auth/roles/${roleId}/permissions`)
    const ids = (data || []).map(p => p.id)
    selectedPermissionIds.value = ids
  } catch (e) { ElMessage.error('加载角色权限失败') }
}

const createRole = async () => {
  if (!newRoleName.value) return ElMessage.warning('请输入角色名')
  try {
    await api.post('/api/auth/roles', { name: newRoleName.value })
    ElMessage.success('角色创建成功')
    newRoleName.value = ''
    await loadRoles()
  } catch (e) { ElMessage.error(e?.response?.data?.detail || '创建角色失败') }
}

const createPermission = async () => {
  if (!newPermCode.value || !newPermName.value) return ElMessage.warning('请输入权限 code 与名称')
  try {
    await api.post('/api/auth/permissions', { code: newPermCode.value, name: newPermName.value })
    ElMessage.success('权限创建成功')
    newPermCode.value = ''
    newPermName.value = ''
    await loadPermissions()
  } catch (e) { ElMessage.error(e?.response?.data?.detail || '创建权限失败') }
}

const assignPermissions = async () => {
  if (!selectedRoleId.value) return ElMessage.warning('请选择角色')
  try {
    await api.post(`/api/auth/roles/${selectedRoleId.value}/permissions`, { permissions: selectedPermissionIds.value })
    ElMessage.success('分配成功')
  } catch (e) { ElMessage.error(e?.response?.data?.detail || '分配失败') }
}

const assignRoleToUser = async () => {
  if (!selectedUserId.value || !selectedUserRole.value) return
  try {
    await api.put(`/api/auth/users/${selectedUserId.value}/role`, { role: selectedUserRole.value })
    ElMessage.success('指派成功')
    await loadUsers()
  } catch (e) { ElMessage.error(e?.response?.data?.detail || '指派失败') }
}

onMounted(async () => { await refreshAll() })
watch(selectedRoleId, (v) => { if (v) loadRolePermissions(v) })
</script>

<style scoped>
.permission-page { padding: 20px }
.body-grid { display: grid; grid-template-columns: 240px 1fr 280px; gap: 16px }
.section-title { font-weight: 700; margin-bottom: 8px }
.role-item { display: block; padding: 6px }
</style>
