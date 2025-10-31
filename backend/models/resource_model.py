from typing import List, Dict, Optional
import datetime
import random

class ResourceMonitor:
    """资源监控数据模型"""
    
    def __init__(self):
        self.cpu_history = []
        self.gpu_history = []
        self.max_history_size = 30  # 保留30次历史数据
    
    def generate_cpu_usage(self) -> float:
        """生成CPU使用率数据（0-100%）"""
        # 模拟真实CPU使用率波动
        base_usage = 30.0  # 基础使用率
        fluctuation = random.uniform(-15, 25)  # 波动范围
        usage = max(0, min(100, base_usage + fluctuation))
        return round(usage, 2)
    
    def cup_usage(self) -> float:
        cpu_usage = self.generate_cpu_usage()
        return {
            'success': True,
            'data':{'cpu_usage': cpu_usage}
        }
    
    def generate_gpu_usage(self) -> float:
        """生成GPU使用率数据（0-100%）"""
        # 模拟GPU使用率，通常比CPU波动更大
        base_usage = 25.0  # 基础使用率
        fluctuation = random.uniform(-20, 35)  # 更大的波动范围
        usage = max(0, min(100, base_usage + fluctuation))
        return round(usage, 2)
    
    def get_current_resources(self) -> Dict:
        """获取当前资源使用情况"""
        current_time = datetime.datetime.now()
        
        # 生成当前数据
        cpu_usage = self.generate_cpu_usage()
        # print(f"CPU使用率: {cpu_usage}%")
        gpu_usage = self.generate_gpu_usage()
        
        # 更新历史数据
        cpu_data = {
            'timestamp': current_time.isoformat(),
            'usage': cpu_usage
        }
        
        gpu_data = {
            'timestamp': current_time.isoformat(), 
            'usage': gpu_usage
        }
        
        # 添加到历史记录
        self.cpu_history.append(cpu_data)
        self.gpu_history.append(gpu_data)
        
        # 限制历史记录大小
        if len(self.cpu_history) > self.max_history_size:
            self.cpu_history = self.cpu_history[-self.max_history_size:]
        if len(self.gpu_history) > self.max_history_size:
            self.gpu_history = self.gpu_history[-self.max_history_size:]
        
        return {
            'cpu': {
                'current': cpu_usage,
                'history': self.cpu_history,
                'timestamp': current_time.isoformat()
            },
            'gpu': {
                'current': gpu_usage,
                'history': self.gpu_history,
                'timestamp': current_time.isoformat()
            }
        }
    
    def get_resource_history(self, resource_type: str, limit: int = 30) -> List[Dict]:
        """获取指定资源的历史数据"""
        if resource_type.lower() == 'cpu':
            history = self.cpu_history
        elif resource_type.lower() == 'gpu':
            history = self.gpu_history
        else:
            return []
        
        return history[-limit:] if limit > 0 else history

# 创建全局资源监控实例
resource_monitor = ResourceMonitor()