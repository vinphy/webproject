import { api } from '@/utils/auth'

// 获取项目详情
export function getProjectDetail(projectId) {
  return api({
    url: `/api/projects/${projectId}`,
    method: 'get'
  })
}

// 获取项目列表
export function getProjectList(params) {
  return api({
    url: '/api/projects/',
    method: 'get',
    params
  })
}

// 创建项目
export function createProject(data) {
  return api({
    url: '/api/projects/',
    method: 'post',
    data
  })
}