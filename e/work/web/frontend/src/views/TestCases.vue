// ... existing code ...
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { getTestCaseList, deleteTestCase } from '@/api/testCase'

const router = useRouter()

// 响应式数据
const cases = ref([])
const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 加载测试用例列表
const loadCases = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      size: pageSize.value,
      search: searchQuery.value || undefined,
      status: statusFilter.value || undefined
    }
    
    const response = await getTestCaseList(params)
    if (response.data.status === 'success') {
      cases.value = response.data.data.items
      total.value = response.data.data.total
    } else {
      throw new Error(response.data.message || '获取测试用例列表失败')
    }
  } catch (error) {
    console.error('加载测试用例列表失败:', error)
    ElMessage.error('加载测试用例列表失败')
    // 降级处理：使用模拟数据
    cases.value = [
      { id: 1, name: '用户登录功能测试', description: '测试用户登录功能的正确性', type: '功能测试', status: '可执行', priority: '高', created_by: 'admin', updated_at: new Date().toISOString() },
      { id: 2, name: '数据导出性能测试', description: '测试大数据量导出的性能', type: '性能测试', status: '草稿', priority: '中', created_by: 'tester', updated_at: new Date().toISOString() }
    ]
    total.value = cases.value.length
  } finally {
    loading.value = false
  }
}

// ... existing code ...
</script>