<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span style="font-weight:600">RBAC 权限管理</span>
          <el-button size="small" @click="initLoad" :loading="pageLoading">刷新</el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <!-- 用户 -->
        <el-tab-pane label="用户" name="users">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <el-input v-model="userQuery" placeholder="搜索用户名/邮箱" clearable style="width:260px" @keyup.enter.native="loadUsers" />
            <div>
              <el-button type="primary" @click="openCreateUser">新建用户</el-button>
            </div>
          </div>

          <el-table :data="filteredUsers" size="small" stripe :loading="tableLoading">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="username" label="用户名" />
            <el-table-column prop="email" label="邮箱" />
            <el-table-column prop="role" label="角色" width="200">
              <template #default="{ row }">
                <el-select v-model="userRole[row.id]" placeholder="选择角色" size="small" style="width:160px" @change="(val)=>assignRole(row.id,val)">
                  <el-option v-for="r in roles" :key="r.id" :label="r.name" :value="r.name" />
                </el-select>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 角色 -->
        <el-tab-pane label="角色" name="roles">
          <div style="display:flex; gap:16px;">
            <!-- 角色列表 -->
            <el-card shadow="never" style="flex: 0 0 360px;">
              <template #header>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                  <span>角色列表</span>
                  <el-button size="small" type="primary" @click="openCreateRole">新建角色</el-button>
                </div>
              </template>
              <el-table :data="roles" size="small" highlight-current-row @current-change="onSelectRole" :loading="tableLoading">
                <el-table-column prop="name" label="角色名" />
                <el-table-column prop="description" label="描述" />
              </el-table>
            </el-card>

            <!-- 角色权限分配 -->
            <el-card shadow="never" style="flex:1; min-height: 340px;">
              <template #header>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                  <span>为角色分配权限</span>
                  <div v-if="activeRole">
                    <el-tag type="info">当前角色：{{ activeRole.name }}</el-tag>
                  </div>
                </div>
              </template>
              <div v-if="activeRole" style="display:flex; gap:12px; align-items:flex-start;">
                <el-transfer
                  v-model="selectedPermIds"
                  :data="permissionTransferData"
                  :props="{ key: 'id', label: 'label' }"
                  filterable
                  filter-placeholder="搜索权限"
                  :titles="['未分配', '已分配']"
                  style="flex:1"
                />
                <div style="width:160px; text-align:right;">
                  <el-button type="primary" :disabled="!activeRole" @click="saveRolePermissions" :loading="permSaving">保存</el-button>
                </div>
              </div>
              <el-empty v-else description="请从左侧选择一个角色" />
            </el-card>
          </div>
        </el-tab-pane>

        <!-- 权限 -->
        <el-tab-pane label="权限" name="permissions">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <span style="font-weight:600">权限列表</span>
            <el-button type="primary" @click="openCreatePermission">新建权限</el-button>
          </div>
          <el-table :data="permissions" size="small" stripe :loading="tableLoading">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="code" label="编码" />
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="description" label="描述" />
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 新建用户 -->
    <el-dialog v-model="createVisible" title="新建用户" width="500px">
      <el-form :model="createForm" label-width="90px">
        <el-form-item label="用户名"><el-input v-model="createForm.username" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="createForm.email" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="createForm.password" type="password" /></el-form-item>
        <el-form-item label="角色">
          <el-select v-model="createForm.role" placeholder="可选" clearable filterable>
            <el-option v-for="r in roles" :key="r.id" :label="r.name" :value="r.name" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible=false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="createUser">保存</el-button>
      </template>
    </el-dialog>

    <!-- 新建角色 -->
    <el-dialog v-model="createRoleVisible" title="新建角色" width="520px">
      <el-form :model="roleDialogForm" label-width="90px">
        <el-form-item label="角色名" required>
          <el-input v-model="roleDialogForm.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="roleDialogForm.description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createRoleVisible=false">取消</el-button>
        <el-button type="primary" :loading="roleCreating" @click="submitCreateRole">创建</el-button>
      </template>
    </el-dialog>

    <!-- 新建权限 -->
    <el-dialog v-model="createPermVisible" title="新建权限" width="600px">
      <el-form :model="permDialogForm" label-width="100px">
        <el-form-item label="权限编码" required>
          <el-input v-model="permDialogForm.code" placeholder="如 user.manage" />
        </el-form-item>
        <el-form-item label="名称" required>
          <el-input v-model="permDialogForm.name" placeholder="显示名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="permDialogForm.description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createPermVisible=false">取消</el-button>
        <el-button type="primary" :loading="permCreating" @click="submitCreatePermission">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '../utils/auth'

const activeTab = ref('users')
const pageLoading = ref(false)
const tableLoading = ref(false)

// 用户
const users = ref([])
const userQuery = ref('')
const userRole = reactive({})
const filteredUsers = computed(() => {
  const q = userQuery.value.trim().toLowerCase()
  if (!q) return users.value
  return users.value.filter(u => `${u.username} ${u.email}`.toLowerCase().includes(q))
})

// 角色
const roles = ref([])
const roleForm = reactive({ name: '', description: '' })
const roleCreating = ref(false)
const activeRole = ref(null)
const selectedPermIds = ref([])
const permSaving = ref(false)

const createRoleVisible = ref(false)
const roleDialogForm = reactive({ name: '', description: '' })

// 权限
const permissions = ref([])
const permForm = reactive({ code: '', name: '', description: '' })
const permCreating = ref(false)
const permissionTransferData = computed(() => permissions.value.map(p => ({ id: p.id, label: `${p.code} - ${p.name}` })))

const createPermVisible = ref(false)
const permDialogForm = reactive({ code: '', name: '', description: '' })

// 创建用户对话框
const createVisible = ref(false)
const saving = ref(false)
const createForm = reactive({ username: '', email: '', password: '', role: '' })

// APIs
const loadUsers = async () => {
  tableLoading.value = true
  try {
    const res = await api.get('/api/auth/users')
    users.value = res.data
    users.value.forEach(u => userRole[u.id] = u.role || '')
  } finally {
    tableLoading.value = false
  }
}
const loadRoles = async () => {
  const res = await api.get('/api/auth/roles')
  roles.value = res.data
}
const loadPermissions = async () => {
  const res = await api.get('/api/auth/permissions')
  permissions.value = res.data
}
const loadRolePermissions = async (roleId) => {
  const res = await api.get(`/api/auth/roles/${roleId}/permissions`)
  selectedPermIds.value = res.data.map(i => i.id)
}

// Actions
const initLoad = async () => {
  pageLoading.value = true
  try {
    await Promise.all([loadUsers(), loadRoles(), loadPermissions()])
  } finally {
    pageLoading.value = false
  }
}

const openCreateUser = () => { createVisible.value = true }

const createUser = async () => {
  if (!createForm.username || !createForm.email || !createForm.password) {
    ElMessage.warning('请完整填写用户信息')
    return
  }
  saving.value = true
  try {
    await api.post('/api/auth/users', createForm)
    createVisible.value = false
    createForm.username = ''
    createForm.email = ''
    createForm.password = ''
    createForm.role = ''
    await loadUsers()
    ElMessage.success('创建成功')
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '创建失败')
  } finally {
    saving.value = false
  }
}

const assignRole = async (userId, roleName) => {
  try {
    await api.put(`/api/auth/users/${userId}/role`, { role: roleName })
    ElMessage.success('已更新用户角色')
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '更新失败')
  }
}

const openCreateRole = () => {
  roleDialogForm.name = ''
  roleDialogForm.description = ''
  createRoleVisible.value = true
}

const submitCreateRole = async () => {
  if (!roleDialogForm.name) {
    ElMessage.warning('请填写角色名')
    return
  }
  roleCreating.value = true
  try {
    await api.post('/api/auth/roles', { name: roleDialogForm.name, description: roleDialogForm.description })
    createRoleVisible.value = false
    await loadRoles()
    ElMessage.success('已创建角色')
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '创建角色失败')
  } finally {
    roleCreating.value = false
  }
}

const openCreatePermission = () => {
  permDialogForm.code = ''
  permDialogForm.name = ''
  permDialogForm.description = ''
  createPermVisible.value = true
}

const submitCreatePermission = async () => {
  if (!permDialogForm.code || !permDialogForm.name) {
    ElMessage.warning('请填写编码和名称')
    return
  }
  permCreating.value = true
  try {
    await api.post('/api/auth/permissions', permDialogForm)
    createPermVisible.value = false
    await loadPermissions()
    if (activeRole.value) await loadRolePermissions(activeRole.value.id)
    ElMessage.success('已创建权限')
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '创建权限失败')
  } finally {
    permCreating.value = false
  }
}

const onSelectRole = async (row) => {
  activeRole.value = row
  await loadRolePermissions(row.id)
}

const createPermission = async () => {
  if (!permForm.code || !permForm.name) return
  permCreating.value = true
  try {
    await api.post('/api/auth/permissions', permForm)
    permForm.code = ''
    permForm.name = ''
    permForm.description = ''
    await loadPermissions()
    if (activeRole.value) await loadRolePermissions(activeRole.value.id)
    ElMessage.success('已创建权限')
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '创建权限失败')
  } finally {
    permCreating.value = false
  }
}

const saveRolePermissions = async () => {
  if (!activeRole.value) return
  permSaving.value = true
  try {
    await api.post(`/api/auth/roles/${activeRole.value.id}/permissions`, { permissions: selectedPermIds.value })
    ElMessage.success('已保存角色权限')
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '保存失败')
  } finally {
    permSaving.value = false
  }
}

onMounted(initLoad)
</script> 