import api from './index'

// 获取测试用例列表
export function getTestCaseList(params) {
  return api({
    url: '/api/test-cases/',
    method: 'get',
    params
  })
}

// 获取测试用例详情
export function getTestCaseDetail(caseId) {
  return api({
    url: `/api/test-cases/${caseId}`,
    method: 'get'
  })
}

// 创建测试用例
export function createTestCase(data) {
  return api({
    url: '/api/test-cases/',
    method: 'post',
    data
  })
}

// 更新测试用例
export function updateTestCase(caseId, data) {
  return api({
    url: `/api/test-cases/${caseId}`,
    method: 'put',
    data
  })
}

// 删除测试用例
export function deleteTestCase(caseId) {
  return api({
    url: `/api/test-cases/${caseId}`,
    method: 'delete'
  })
}