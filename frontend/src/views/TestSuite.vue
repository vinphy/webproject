<template>
  <div class="test-suite-container">
    <!-- 左侧菜单栏 -->
    <div class="left-sidebar">
      <div class="sidebar-header">
        <h3>测试用例库</h3>
      </div>
      <div class="menu-container">
        <!-- 递归菜单组件 -->
        <div 
          v-for="item in menuData" 
          :key="item.id"
          class="menu-item-wrapper"
        >
          <div 
            class="menu-item"
            :class="{
              'active': selectedCategory === item.id || 
                       selectedSubCategory === item.id || 
                       selectedItem === item.id,
              'level-1': !item.parent,
              'level-2': item.parent && !item.grandparent,
              'level-3': item.grandparent
            }"
            @click="handleMenuClick(item)"
          >
            <span class="menu-text">{{ item.name }}</span>
            <span 
              class="menu-arrow" 
              v-if="item.children && item.children.length > 0"
              :class="{ 'expanded': isExpanded(item.id) }"
            ></span>
          </div>
          
          <!-- 递归子菜单 -->
          <div 
            v-if="item.children && item.children.length > 0 && isExpanded(item.id)"
            class="sub-menu"
          >
            <div 
              v-for="child in item.children" 
              :key="child.id"
              class="menu-item-wrapper"
            >
              <div 
                class="menu-item"
                :class="{
                  'active': selectedCategory === child.id || 
                           selectedSubCategory === child.id || 
                           selectedItem === child.id,
                  'level-2': true
                }"
                @click="handleMenuClick(child)"
              >
                <span class="menu-text">{{ child.name }}</span>
                <span 
                  class="menu-arrow" 
                  v-if="child.children && child.children.length > 0"
                  :class="{ 'expanded': isExpanded(child.id) }"
                ></span>
              </div>
              
              <!-- 三级菜单 -->
              <div 
                v-if="child.children && child.children.length > 0 && isExpanded(child.id)"
                class="sub-menu"
              >
                <div 
                  v-for="grandchild in child.children" 
                  :key="grandchild.id"
                  class="menu-item-wrapper"
                >
                  <div 
                    class="menu-item"
                    :class="{
                      'active': selectedCategory === grandchild.id || 
                               selectedSubCategory === grandchild.id || 
                               selectedItem === grandchild.id,
                      'level-3': true
                    }"
                    @click="handleMenuClick(grandchild)"
                  >
                    <span class="menu-text">{{ grandchild.name }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 中间内容区 -->
    <div class="main-content">
      <div class="content-header">
        <h2>{{ getCurrentContentTitle() }}</h2>
        <div class="content-actions">
          <el-button type="primary" size="small">运行测试</el-button>
          <el-button size="small">编辑</el-button>
        </div>
      </div>
      
      <!-- 内容显示区域 -->
      <div class="content-body" v-if="currentContent">
        <div class="sql-section">
          <div class="section-header">
            <h4>SQL语句</h4>
          </div>
          <div class="markdown-code-block" data-language="sql">
            <div class="code-header">
              <span class="language-label">SQL</span>
            </div>
            <pre class="markdown-pre"><code class="markdown-code">{{ currentContent.sql }}</code></pre>
          </div>
        </div>
        
        <div class="test-code-section">
          <div class="section-header">
            <h4>测试代码</h4>
          </div>
          <div class="markdown-code-block" data-language="python">
            <div class="code-header">
              <span class="language-label">Python</span>
            </div>
            <pre class="markdown-pre"><code class="markdown-code">{{ currentContent.testCode }}</code></pre>
          </div>
        </div>
        
        <div class="test-result-section">
          <div class="section-header">
            <h4>测试结果</h4>
          </div>
          <div class="test-result-content">
            <p>{{ currentContent.testResult }}</p>
          </div>
        </div>
      </div>
      <div v-else class="no-content">
        <p>请从左侧选择测试用例查看详情</p>
      </div>
    </div>

    <!-- 右侧描述区 -->
    <div class="right-sidebar">
      <div class="description-section">
        <div class="section-header">
          <h4>描述信息</h4>
        </div>
        <div class="description-content" v-if="currentContent">
          <p>{{ currentContent.description }}</p>
          
          <div class="meta-info">
            <div class="meta-item">
              <span class="label">创建时间:</span>
              <span class="value">{{ currentContent.createTime }}</span>
            </div>
            <div class="meta-item">
              <span class="label">最后修改:</span>
              <span class="value">{{ currentContent.updateTime }}</span>
            </div>
            <div class="meta-item">
              <span class="label">作者:</span>
              <span class="value">{{ currentContent.author }}</span>
            </div>
          </div>
        </div>
        <div v-else class="no-content">
          <p>请从左侧选择测试用例查看详情</p>
        </div>
      </div>

      <!-- 相关链接区域 -->
      <div class="related-links">
        <div class="section-header">
          <h4>相关链接</h4>
        </div>
        <div class="links-content">
          <ul>
            <li v-for="link in relatedLinks" :key="link.id">
              <a :href="link.url" target="_blank">{{ link.title }}</a>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// 优化后的菜单数据结构
const menuData = ref([
  {
    id: 'database',
    name: '数据库测试',
    children: [
      {
        id: 'mysql',
        name: 'MySQL测试',
        children: [
          {
            id: 'mysql-connection',
            name: '连接测试',
            sql: 'SELECT 1;',
            testCode: 'import mysql.connector\n\n# 测试数据库连接\ndef test_connection():\n    conn = mysql.connector.connect(\n        host="localhost",\n        user="root",\n        password="password",\n        database="test"\n    )\n    cursor = conn.cursor()\n    cursor.execute("SELECT 1")\n    result = cursor.fetchone()\n    print("连接测试通过" if result[0] == 1 else "连接测试失败")\n    conn.close()',
            testResult: '连接测试通过',
            description: '测试MySQL数据库连接是否正常',
            createTime: '2024-01-15',
            updateTime: '2024-01-15',
            author: '系统管理员'
          },
          {
            id: 'mysql-create-table',
            name: '建表测试',
            sql: 'CREATE TABLE users (\n    id INT PRIMARY KEY AUTO_INCREMENT,\n    username VARCHAR(50) NOT NULL,\n    email VARCHAR(100) UNIQUE,\n    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n);',
            testCode: 'import mysql.connector\n\n# 测试建表功能\ndef test_create_table():\n    conn = mysql.connector.connect(\n        host="localhost",\n        user="root",\n        password="password",\n        database="test"\n    )\n    cursor = conn.cursor()\n    \n    # 执行建表SQL\n    cursor.execute(sql)\n    \n    # 验证表是否存在\n    cursor.execute("SHOW TABLES LIKE \'users\'")\n    result = cursor.fetchone()\n    \n    if result:\n        print("建表测试通过")\n        # 清理测试表\n        cursor.execute("DROP TABLE users")\n    else:\n        print("建表测试失败")\n    \n    conn.close()',
            testResult: '建表测试通过',
            description: '测试MySQL建表功能是否正常',
            createTime: '2024-01-15',
            updateTime: '2024-01-15',
            author: '系统管理员'
          }
        ]
      },
      {
        id: 'postgresql',
        name: 'PostgreSQL测试',
        children: [
          {
            id: 'postgresql-connection',
            name: '连接测试',
            sql: 'SELECT 1;',
            testCode: 'import psycopg2\n\n# 测试PostgreSQL数据库连接\ndef test_connection():\n    conn = psycopg2.connect(\n        host="localhost",\n        user="postgres",\n        password="password",\n        database="test"\n    )\n    cursor = conn.cursor()\n    cursor.execute("SELECT 1")\n    result = cursor.fetchone()\n    print("连接测试通过" if result[0] == 1 else "连接测试失败")\n    conn.close()',
            testResult: '连接测试通过',
            description: '测试PostgreSQL数据库连接是否正常',
            createTime: '2024-01-15',
            updateTime: '2024-01-15',
            author: '系统管理员'
          }
        ]
      }
    ]
  },
  {
    id: 'api',
    name: 'API测试',
    children: [
      {
        id: 'rest',
        name: 'REST API',
        children: [
          {
            id: 'api-get',
            name: 'GET请求测试',
            sql: 'N/A',
            testCode: 'import requests\n\n# 测试GET API\ndef test_get_api():\n    response = requests.get("https://api.example.com/users")\n    if response.status_code == 200:\n        print("GET API测试通过")\n        return response.json()\n    else:\n        print("GET API测试失败")\n        return None',
            testResult: 'GET API测试通过',
            description: '测试REST API的GET请求功能',
            createTime: '2024-01-15',
            updateTime: '2024-01-15',
            author: '系统管理员'
          }
        ]
      }
    ]
  },
  {
    id: 'performance',
    name: '性能测试',
    children: [
      {
        id: 'load',
        name: '负载测试',
        children: [
          {
            id: 'load-test',
            name: '基础负载测试',
            sql: 'N/A',
            testCode: 'import time\nimport threading\n\n# 基础负载测试\ndef load_test():\n    def worker():\n        time.sleep(1)  # 模拟工作负载\n    \n    threads = []\n    start_time = time.time()\n    \n    # 创建10个线程模拟并发\n    for i in range(10):\n        thread = threading.Thread(target=worker)\n        threads.append(thread)\n        thread.start()\n    \n    # 等待所有线程完成\n    for thread in threads:\n        thread.join()\n    \n    end_time = time.time()\n    print(f"负载测试完成，耗时: {end_time - start_time:.2f}秒")',
            testResult: '负载测试完成，耗时: 1.02秒',
            description: '基础并发负载性能测试',
            createTime: '2024-01-15',
            updateTime: '2024-01-15',
            author: '系统管理员'
          }
        ]
      }
    ]
  }
]);

// 相关链接数据
const relatedLinks = ref([
  { id: 1, title: 'MySQL官方文档', url: 'https://dev.mysql.com/doc/' },
  { id: 2, title: 'PostgreSQL官方文档', url: 'https://www.postgresql.org/docs/' },
  { id: 3, title: 'Python数据库连接指南', url: 'https://docs.python.org/3/library/sqlite3.html' }
]);

// 响应式数据
const selectedCategory = ref(null);
const selectedSubCategory = ref(null);
const selectedItem = ref(null);
const currentContent = ref(null);
const expandedItems = ref(new Set()); // 存储展开的菜单项ID

// 计算属性
const getCurrentContentTitle = () => {
  return currentContent.value ? currentContent.value.name : '请选择测试用例';
};

// 方法
const isExpanded = (itemId) => {
  return expandedItems.value.has(itemId);
};

const toggleExpanded = (itemId) => {
  if (expandedItems.value.has(itemId)) {
    expandedItems.value.delete(itemId);
  } else {
    expandedItems.value.add(itemId);
  }
};

const handleMenuClick = (item) => {
  // 如果有子菜单，切换展开状态
  if (item.children && item.children.length > 0) {
    toggleExpanded(item.id);
  } else {
    // 如果是叶子节点，设置当前内容
    selectedCategory.value = findTopLevelParent(item.id);
    selectedSubCategory.value = findParent(item.id);
    selectedItem.value = item.id;
    currentContent.value = item;
  }
};

// 辅助方法：查找顶级父节点
const findTopLevelParent = (itemId) => {
  for (const topItem of menuData.value) {
    if (topItem.id === itemId) return topItem.id;
    if (topItem.children) {
      for (const child of topItem.children) {
        if (child.id === itemId) return topItem.id;
        if (child.children) {
          for (const grandchild of child.children) {
            if (grandchild.id === itemId) return topItem.id;
          }
        }
      }
    }
  }
  return null;
};

// 辅助方法：查找直接父节点
const findParent = (itemId) => {
  for (const topItem of menuData.value) {
    if (topItem.children) {
      for (const child of topItem.children) {
        if (child.id === itemId) return child.id;
        if (child.children) {
          for (const grandchild of child.children) {
            if (grandchild.id === itemId) return child.id;
          }
        }
      }
    }
  }
  return null;
};
</script>

<style scoped>
.test-suite-container {
  display: flex;
  height: 100vh;
  background-color: #f5f7fa;
  margin: 0;
  padding: 0;
}

/* 左侧菜单栏样式 - 优化版本 */
.left-sidebar {
  width: 240px;
  background-color: #f8f9fa;
  border-right: 1px solid #e6e6e6;
  overflow-y: auto;
  margin: 0;
}

.sidebar-header {
  padding: 15px 20px;
  border-bottom: none;
  background-color: #f8f9fa;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.menu-container {
  padding: 10px 0;
}

.menu-item-wrapper {
  position: relative;
}

.menu-item {
  padding: 8px 20px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
  color: #333;
  background-color: transparent;
  position: relative;
}

.menu-item:hover {
  background-color: #f0f0f0;
  border-left-color: #007bff;
}

.menu-item.active {
  background-color: #e3f2fd;
  border-left-color: #007bff;
  color: #007bff;
  font-weight: 500;
}

/* 层级样式 */
.menu-item.level-1 {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.menu-item.level-2 {
  padding-left: 35px;
  font-size: 14px;
  font-weight: 400;
  color: #666;
}

.menu-item.level-3 {
  padding-left: 50px;
  font-size: 13px;
  font-weight: 300;
  color: #888;
}

.menu-text {
  line-height: 1.5;
  color: inherit;
}

/* 优化箭头样式 */
.menu-arrow {
  position: relative;
  width: 16px;
  height: 16px;
  margin-left: 8px;
  transition: all 0.2s ease;
}

.menu-arrow::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 6px;
  height: 6px;
  border: 1px solid #999;
  border-top: none;
  border-right: none;
  transform: translate(-50%, -50%) rotate(-45deg);
  transition: all 0.2s ease;
}

.menu-arrow.expanded::before {
  transform: translate(-50%, -50%) rotate(135deg);
}

.menu-item.active .menu-arrow::before {
  border-color: #007bff;
}

.menu-item:hover .menu-arrow::before {
  border-color: #666;
}

/* 子菜单样式 */
.sub-menu {
  overflow: hidden;
  transition: all 0.3s ease;
}

/* 中间内容区样式 */
.main-content {
  flex: 1;
  background-color: white;
  margin: 0;
  border-radius: 0;
  box-shadow: none;
  overflow-y: auto;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: none;
}

.content-header h2 {
  margin: 0;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
}

.content-body {
  padding: 0 20px 20px;
}

/* 代码块样式 */
.markdown-code-block {
  background-color: #f8f9fa;
  border: 1px solid #e1e4e8;
  border-radius: 6px;
  margin: 16px 0;
  overflow: hidden;
}

.code-header {
  background-color: #f6f8fa;
  border-bottom: 1px solid #e1e4e8;
  padding: 8px 16px;
  font-size: 12px;
  color: #586069;
  font-family: 'SFMono-Regular', 'Consolas', 'Liberation Mono', 'Menlo', monospace;
}

.language-label {
  font-weight: 600;
  text-transform: uppercase;
}

.markdown-pre {
  margin: 0;
  padding: 16px;
  background: transparent;
  border: none;
  font-size: 13px;
  line-height: 1.45;
  overflow-x: auto;
}

.markdown-code {
  color: #24292e;
  background: transparent;
  padding: 0;
  border: none;
  font-family: 'SFMono-Regular', 'Consolas', 'Liberation Mono', 'Menlo', monospace;
  white-space: pre;
}

/* 右侧描述区样式 */
.right-sidebar {
  width: 280px;
  background-color: white;
  margin: 0;
  border-radius: 0;
  box-shadow: none;
  overflow-y: auto;
  border-left: 1px solid #e6e6e6;
}

.description-section, .related-links {
  padding: 15px 20px;
  border-bottom: none;
}

.description-content p {
  line-height: 1.6;
  color: #606266;
  margin-bottom: 12px;
}

.meta-info {
  background-color: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  border: none;
}

.meta-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.meta-item:last-child {
  margin-bottom: 0;
}

.label {
  color: #909399;
  font-weight: 400;
}

.value {
  color: #606266;
  font-weight: 500;
}

.links-content ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.links-content li {
  margin-bottom: 8px;
}

.links-content a {
  color: #007bff;
  text-decoration: none;
  font-size: 14px;
}

.links-content a:hover {
  text-decoration: underline;
}

.no-content {
  text-align: center;
  color: #909399;
  padding: 30px 0;
}

.no-content {
  text-align: center;
  color: #909399;
  padding: 30px 0;
}

.links-content ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.links-content li {
  margin-bottom: 8px;
}

.links-content a {
  color: #007bff;
  text-decoration: none;
  font-size: 14px;
}

.links-content a:hover {
  text-decoration: underline;
}

.no-content {
  text-align: center;
  color: #909399;
  padding: 30px 0;
}
</style>