<template>
  <div class="permission-page">
    <el-card class="permission-card">
      <div class="header-row">
        <h3>权限管理 (RBAC)</h3>
      </div>

      <div class="body-grid">
        <div class="perm-topbar" style="display:flex;align-items:center;justify-content:space-between;gap:12px">
          <div style="display:flex;align-items:center;gap:12px">
            <el-select v-model="selectedRoleId" placeholder="选择角色" style="min-width:240px" @change="onRoleChange">
              <el-option v-for="r in roles" :key="r.id" :label="r.name" :value="r.id" />
            </el-select>
            <el-button type="primary" size="small" v-if="canManage" @click="createRole">新增角色</el-button>
          </div>
          <div style="display:flex;align-items:center;gap:8px">
            <el-input v-model="newPermCode" placeholder="权限 code (eg: project:view)" clearable style="width:220px" />
            <el-input v-model="newPermName" placeholder="权限名称" clearable style="width:220px" />
            <el-button v-if="canManage" type="primary" size="small" @click="createPermission">新增权限</el-button>
            <el-button type="primary" :disabled="!selectedRoleId" @click="assignPermissions">保存分配</el-button>
            <el-button plain @click="refreshAll">刷新</el-button>
          </div>
        </div>

        <div class="perm-table" style="margin-top:12px">
          <el-table :data="pagedGroups" style="width:100%" size="small" :row-key="(row)=>row.key">
            <el-table-column label="多选" width="120">
              <template #default="{ row }">
                <el-tooltip content="全选/取消本菜单" placement="top">
                  <el-checkbox :indeterminate="!isGroupAllSelected(row) && row.items.some(it => selectedPermissionIds.includes(it.id))" :checked="isGroupAllSelected(row)" @change="() => toggleGroupAll(row)"></el-checkbox>
                </el-tooltip>
              </template>
            </el-table-column>
            <el-table-column prop="label" label="菜单名称" width="240" >
              <template #default="{ row }"><span class="menu-name">{{ row.label }}</span></template>
            </el-table-column>
            <el-table-column label="菜单操作">
              <template #default="{ row }">
                <div style="display:flex;flex-wrap:wrap;gap:8px">
                  <el-checkbox-group v-model="selectedPermissionIds">
                    <el-checkbox v-for="perm in row.items" :key="perm.id" :label="String(perm.id)">{{ perm.name || perm.code }}</el-checkbox>
                  </el-checkbox-group>
                </div>
              </template>
            </el-table-column>
          </el-table>
          <div style="display:flex;justify-content:flex-end;margin-top:12px">
            <el-pagination
              v-model:current-page="currentPage"
              :page-size="pageSize"
              :total="permissionGroups.length"
              layout="prev, pager, next, sizes, jumper"
              :page-sizes="[5,10,20]"
              @size-change="handlePageSizeChange"
              @current-change="handlePageChange"
            />
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { api, getCurrentUser, userRef } from '@/utils/auth'
import { initPermissions, hasPermission } from '@/utils/permission'
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
    // normalize ids to strings for stable comparison with selectedPermissionIds
    permissions.value = (data || []).map(p => {
      try {
        return { ...p, id: p.id !== undefined && p.id !== null ? String(p.id) : String(p) }
      } catch (e) {
        return p
      }
    })
  } catch (e) { ElMessage.error('加载权限失败') }
}

const userPermissions = ref([])

const canManage = computed(() => {
  const u = userRef.value || getCurrentUser()
  try {
    if (!u) return false
    if ((u.role || '') === 'admin') return true
    return hasPermission('auth:manage')
  } catch (e) { return false }
})

const permissionGroups = computed(() => {
  const map = {}
  ;(permissions.value || []).forEach(raw => {
    let p = raw
    if (typeof raw === 'string' || typeof raw === 'number') {
      p = { id: String(raw), code: String(raw), name: String(raw) }
    } else {
      // ensure code/name exist and id is string
      p = {
        ...raw,
        id: raw.id !== undefined && raw.id !== null ? String(raw.id) : String(raw.code ?? JSON.stringify(raw)),
        code: raw.code ?? raw.name ?? String(raw.id ?? ''),
        name: raw.name ?? raw.code ?? String(raw.id ?? '')
      }
    }
    const code = (p.code || '').toString()
    const key = code.split(/[:.]/)[0] || 'other'
    if (!map[key]) map[key] = { key, label: key, items: [] }
    map[key].items.push(p)
  })
  return Object.values(map)
    .map(g => ({ key: g.key, label: g.label || g.key, items: g.items.sort((a,b)=> (a.code||'').localeCompare(b.code||'')) }))
    .sort((a,b)=> a.key.localeCompare(b.key))
})

// pagination for groups
const currentPage = ref(1)
const pageSize = ref(10)
const pagedGroups = computed(() => {
  const groups = permissionGroups.value || []
  const start = (currentPage.value - 1) * pageSize.value
  return groups.slice(start, start + pageSize.value)
})

const handlePageSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handlePageChange = (val) => {
  currentPage.value = val
}

const isGroupAllSelected = (group) => {
  if (!group || !group.items) return false
  return group.items.every(it => selectedPermissionIds.value.includes(it.id))
}

const toggleGroupAll = (group) => {
  if (!group || !group.items) return
  const ids = group.items.map(i => i.id)
  if (isGroupAllSelected(group)) {
    selectedPermissionIds.value = selectedPermissionIds.value.filter(id => !ids.includes(id))
  } else {
    const set = new Set(selectedPermissionIds.value || [])
    ids.forEach(id => set.add(id))
    selectedPermissionIds.value = Array.from(set)
  }
}

const loadUsers = async () => {
  try {
    if (canManage.value) {
      const { data } = await api.get('/api/auth/users')
      users.value = data || []
    } else {
      // non-admin: only show own info and own permissions
      const me = await api.get('/api/auth/me')
      users.value = [{ id: me.data.id, username: me.data.username, email: me.data.email, role: me.data.role }]
      try {
        const res = await api.get('/api/auth/me/permissions')
        userPermissions.value = Array.isArray(res.data) ? res.data : []
      } catch (e) { userPermissions.value = [] }
    }
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
    const resp = data || []
    // ensure permissions list available to resolve codes -> ids
    if ((!permissions.value || permissions.value.length === 0)) {
      await loadPermissions()
    }
    const ids = []
    for (const item of resp) {
      if (item == null) continue
      // item may be object {id, code} or a string code
      if (typeof item === 'object') {
        if (item.id !== undefined && item.id !== null) {
          ids.push(String(item.id))
          continue
        }
        if (item.code) {
          const found = (permissions.value || []).find(p => String(p.code) === String(item.code) || String(p.id) === String(item.code))
          if (found) ids.push(String(found.id))
          else ids.push(String(item.code))
          continue
        }
      }
      // fallback: item may be a string code
      const found = (permissions.value || []).find(p => String(p.code) === String(item) || String(p.id) === String(item))
      if (found) ids.push(String(found.id))
      else ids.push(String(item))
    }
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
    // convert selected ids (or codes) to permission codes before sending
    const codes = (selectedPermissionIds.value || []).map(pid => {
      // pid is normalized as string; try to find permission by id first
      const byId = (permissions.value || []).find(x => String(x.id) === String(pid))
      if (byId && byId.code) return byId.code
      // if not found by id, maybe pid itself is a code
      const byCode = (permissions.value || []).find(x => String(x.code) === String(pid))
      if (byCode) return byCode.code
      // fallback: send pid as-is
      return pid
    }).filter(Boolean)
    await api.post(`/api/auth/roles/${selectedRoleId.value}/permissions`, { permissions: codes })
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

const onRoleChange = (val) => {
  if (val) loadRolePermissions(val)
  else selectedPermissionIds.value = []
}

// ---- user/role/perm edit/delete/create helpers ----
const newUser = ref({ username: '', email: '', password: '', role: '' })
const editingUser = ref(null)
const editingRole = ref(null)
const editingPerm = ref(null)

const createUser = async () => {
  if (!newUser.value.username || !newUser.value.email || !newUser.value.password) return ElMessage.warning('请输入用户名/邮箱/密码')
  try {
    await api.post('/api/auth/users', { username: newUser.value.username, email: newUser.value.email, password: newUser.value.password, role: newUser.value.role })
    ElMessage.success('用户创建成功')
    newUser.value = { username: '', email: '', password: '', role: '' }
    await loadUsers()
  } catch (e) { ElMessage.error(e?.response?.data?.detail || '创建用户失败') }
}

const deleteUser = async (u) => {
  if (!u) return
  try {
    await api.delete(`/api/auth/users/${u.id}`)
    ElMessage.success('用户已删除')
    await loadUsers()
  } catch (e) { ElMessage.error(e?.response?.data?.detail || '删除用户失败') }
}

const startEditUser = (u) => {
  editingUser.value = { id: u.id, username: u.username, email: u.email, password: '', role: u.role }
}

const saveUserEdit = async () => {
  if (!editingUser.value || !editingUser.value.id) return
  const id = editingUser.value.id
  const payload = { email: editingUser.value.email }
  if (editingUser.value.password) payload.password = editingUser.value.password
  if (editingUser.value.role !== undefined) payload.role = editingUser.value.role
  try {
    await api.put(`/api/auth/users/${id}`, payload)
    ElMessage.success('用户保存成功')
    editingUser.value = null
    await loadUsers()
  } catch (e) { ElMessage.error(e?.response?.data?.detail || '保存用户失败') }
}

const cancelEditUser = () => { editingUser.value = null }

const deleteRole = async (r) => {
  if (!r) return
  try {
    await api.delete(`/api/auth/roles/${r.id}`)
    ElMessage.success('角色已删除')
    await loadRoles(); await loadPermissions(); await loadUsers()
  } catch (e) { ElMessage.error(e?.response?.data?.detail || '删除角色失败') }
}

const startEditRole = (r) => { editingRole.value = { id: r.id, name: r.name, description: r.description } }

const saveRoleEdit = async () => {
  if (!editingRole.value) return
  try {
    await api.put(`/api/auth/roles/${editingRole.value.id}`, { name: editingRole.value.name, description: editingRole.value.description })
    ElMessage.success('角色保存成功')
    editingRole.value = null
    await loadRoles()
  } catch (e) { ElMessage.error(e?.response?.data?.detail || '保存角色失败') }
}

const cancelEditRole = () => { editingRole.value = null }

const deletePermission = async (p) => {
  if (!p) return
  try {
    await api.delete(`/api/auth/permissions/${p.id}`)
    ElMessage.success('权限已删除')
    await loadPermissions(); if (selectedRoleId.value) await loadRolePermissions(selectedRoleId.value)
  } catch (e) { ElMessage.error(e?.response?.data?.detail || '删除权限失败') }
}

const startEditPerm = (p) => { editingPerm.value = { id: p.id, code: p.code, name: p.name, description: p.description } }

const savePermEdit = async () => {
  if (!editingPerm.value) return
  try {
    await api.put(`/api/auth/permissions/${editingPerm.value.id}`, { code: editingPerm.value.code, name: editingPerm.value.name, description: editingPerm.value.description })
    ElMessage.success('权限保存成功')
    editingPerm.value = null
    await loadPermissions()
  } catch (e) { ElMessage.error(e?.response?.data?.detail || '保存权限失败') }
}

const cancelEditPerm = () => { editingPerm.value = null }

onMounted(async () => {
  try { await initPermissions() } catch (e) {}
  await refreshAll()
})
watch(selectedRoleId, (v) => { if (v) loadRolePermissions(v) })
</script>

<style scoped>
.permission-page { padding: 20px }
.body-grid { padding: 12px; max-width: 1200px; margin: 0 auto }
.permission-card { padding: 18px }
.section-title { font-weight: 700; margin-bottom: 8px; font-size: 14px }
.perm-topbar .el-select .el-input__inner { font-size: 13px; padding: 6px 10px }
.perm-topbar .el-button { padding: 6px 10px }
.perm-table { width: 100% }
.role-item { display: block; padding: 6px }
.role-item-row { display:flex; align-items:center; gap:8px; padding:6px 0 }
.perm-row { display:flex; align-items:center; gap:8px; padding:6px 0 }

/* make table use full width and better spacing */
:deep(.el-table) { width: 100% }
:deep(.el-table__cell) { padding: 10px 12px }
:deep(.el-checkbox) { margin-right: 6px }

/* ensure table header/body cells left aligned */
:deep(.el-table__header .el-table__cell),
:deep(.el-table__body .el-table__cell) {
  text-align: left;
}

/* 覆盖全局表格奇偶行样式，解决对齐和颜色问题 */
:deep(.el-table .el-table__row:nth-child(odd) .el-table__cell) {
  text-align: left !important;
  color: #303133 !important;
  background-color: #f5f7fa !important;
  font-weight: 400 !important;
  font-size: 12px !important;
}

:deep(.el-table .el-table__row:nth-child(even) .el-table__cell) {
  text-align: left !important;
  color: #303133 !important;
  font-weight: 400 !important;
  font-size: 12px !important;
}

/* 修复多选列复选框对齐 */
:deep(.el-table-column--selection) {
  display: flex;
  justify-content: flex-start !important;
  padding-left: 12px !important;
}

/* make menu name font match permission labels (not bold, same size/color) */
.menu-name {
  font-weight: 400;
  font-size: 14px;
  color: #606266;
  display: inline-block;
  width: 100%;
  text-align: left;
}
</style>