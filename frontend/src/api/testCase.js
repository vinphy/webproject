import {api} from '@/utils/auth'

// 获取测试用例列表
export function getTestCaseList(params) {
  return api({
    url: '/api/test-cases/',
    method: 'get',
    params
  })
}

// 获取测试用例详情
export function getTestCaseDetail(testCaseId) {
  return api({
    url: `/api/test-cases/${testCaseId}`,
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
export function updateTestCase(testCaseId, data) {
  return api({
    url: `/api/test-cases/${testCaseId}`,
    method: 'put',
    data
  })
}

// 删除测试用例
export function deleteTestCase(testCaseId) {
  return api({
    url: `/api/test-cases/${testCaseId}`,
    method: 'delete'
  })
}

// 批量执行测试用例
export function batchExecuteTestCases(testCaseIds) {
  return api({
    url: '/api/test-cases/batch-execute',
    method: 'post',
    data: {
      test_case_ids: testCaseIds
    }
  })
}