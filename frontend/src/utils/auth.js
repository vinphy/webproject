import axios from 'axios'
import { ref } from 'vue'

const TOKEN_KEY = 'access_token'
const USER_KEY = 'current_user'

export const tokenRef = ref(localStorage.getItem(TOKEN_KEY) || '')
export const userRef = ref((() => { try { return JSON.parse(localStorage.getItem(USER_KEY) || 'null') } catch { return null } })())

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
  tokenRef.value = token
}

export function getToken() {
  return tokenRef.value || localStorage.getItem(TOKEN_KEY)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
  tokenRef.value = ''
}

export function setCurrentUser(user) {
  localStorage.setItem(USER_KEY, JSON.stringify(user || null))
  userRef.value = user || null
}

export function getCurrentUser() {
  return userRef.value || (function(){ try { return JSON.parse(localStorage.getItem(USER_KEY) || 'null') } catch { return null } })()
}

export function clearCurrentUser() {
  localStorage.removeItem(USER_KEY)
  userRef.value = null
}

window.addEventListener('storage', (e) => {
  if (e.key === TOKEN_KEY) tokenRef.value = e.newValue || ''
  if (e.key === USER_KEY) {
    try { userRef.value = e.newValue ? JSON.parse(e.newValue) : null } catch { userRef.value = null }
  }
})

export const api = axios.create({ baseURL: 'http://127.0.0.1:8000' })

api.interceptors.request.use(cfg => {
  const token = getToken()
  if (token) {
    cfg.headers = cfg.headers || {}
    cfg.headers.Authorization = `Bearer ${token}`
  }
  return cfg
})

api.interceptors.response.use(
  res => res,
  err => {
    if (err.response && err.response.status === 401) {
      clearToken(); clearCurrentUser();
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
) 