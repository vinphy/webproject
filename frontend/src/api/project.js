import {api} from '@/utils/auth'

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

// 新增：获取项目日志
export function getProjectLogs(projectId, lastPosition = 0) {
  return api({
    url: `/api/projects/${projectId}/logs`,
    method: 'get',
    params: { last_position: lastPosition }
  })
}

// 新增：获取项目监控数据
export function getProjectMonitorData(projectId) {
  return api({
    url: `/api/projects/${projectId}/monitor`,
    method: 'get'
  })
}

// 新增：更新项目监控数据
export function updateProjectMonitorData(projectId, data) {
  return api({
    url: `/api/projects/${projectId}/monitor`,
    method: 'put',
    data: data
  })
}

// 删除项目
export function delProject(projectId) {
  return api({
    url: `/api/projects/${projectId}`,
    method: 'delete'
  })
}

// 执行项目
export function exeProject(projectId) {
  return api({
    url: `/api/projects/${projectId}/execute`,
    method: 'post'
  })
}