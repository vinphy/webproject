import { ref } from 'vue'
import { api } from './auth'

export const permissionsRef = ref([])

export async function initPermissions() {
  try {
    const res = await api.get('/api/auth/me/permissions')
    permissionsRef.value = Array.isArray(res.data) ? res.data : []
  } catch (e) {
    permissionsRef.value = []
  }
}

export function hasPermission(code) {
  if (!code) return false
  return permissionsRef.value.includes(code)
}

export default { permissionsRef, initPermissions, hasPermission }
