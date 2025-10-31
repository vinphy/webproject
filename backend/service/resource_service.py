from typing import Dict, List
from models.resource_model import resource_monitor
import time
import threading

class ResourceService:
    """资源监控服务层"""
    
    def __init__(self):
        self.last_update_time = {}
        self.update_interval = 60  # 60秒更新一次
        self._start_background_update()
    
    def _start_background_update(self):
        """启动后台数据更新线程"""
        def update_resources():
            while True:
                try:
                    # 每分钟更新一次数据
                    resource_monitor.get_current_resources()
                    time.sleep(self.update_interval)
                except Exception as e:
                    print(f"资源数据更新错误: {e}")
                    time.sleep(10)  # 出错后等待10秒重试
        
        # 启动后台线程
        update_thread = threading.Thread(target=update_resources, daemon=True)
        update_thread.start()
    
    def get_resource_status(self) -> Dict:
        """获取资源状态"""
        return resource_monitor.get_current_resources()
    
    def get_cpu_status(self) -> Dict:
        """获取CPU状态"""
        resources = resource_monitor.cup_usage()
        return resources
    
    def get_gpu_status(self) -> Dict:
        """获取GPU状态"""
        resources = resource_monitor.get_current_resources()
        return resources['gpu']
    
    def get_gpu_history(self, limit: int = 30) -> List[Dict]:
        """获取GPU历史数据"""
        return resource_monitor.get_resource_history('gpu', limit)
    
    def get_cpu_history(self, limit: int = 30) -> List[Dict]:
        """获取CPU历史数据"""
        return resource_monitor.get_resource_history('cpu', limit)

# 创建全局服务实例
resource_service = ResourceService()