import threading
import time
from datetime import datetime
from typing import Dict, List, Optional
from models.resource_model import ResourceMonitor, ResourceModel

class ResourceService:
    def __init__(self):
        self.resource_monitor = ResourceMonitor()
        self.resource_model = None
        self.update_thread = None
        self.running = False
    
    def start_background_update(self):
        """启动后台更新线程"""
        if self.running:
            return
        
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        print("资源监控后台更新线程已启动")
    
    def stop_background_update(self):
        """停止后台更新线程"""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=5)
        print("资源监控后台更新线程已停止")
    
    def _update_loop(self):
        """后台更新循环"""
        while self.running:
            try:
                self._update_resource_data()
                # time.sleep(60)  # 每分钟更新一次
                time.sleep(3)
            except Exception as e:
                print(f"资源数据更新失败 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {e}")
                time.sleep(10)  # 出错后等待10秒再重试
    
    def _update_resource_data(self):
        """更新资源数据到数据库"""
        if self.resource_model is None:
            self.resource_model = ResourceModel()
        
        # 生成当前资源数据
        current_data = self.resource_monitor.get_current_resources()
        
        # 插入到数据库
        success = self.resource_model.insert_resource_record(
            current_data['cpu_usage'],
            current_data['gpu_usage']
        )
        
        # 每次插入后都检查并清理，保证只保留40条最新记录
        if success:
            self.resource_model.cleanup_old_records(max_records=40)
            # 取消注释，启用更新日志
            print(f"资源数据已更新 - CPU: {current_data['cpu_usage']}%, GPU: {current_data['gpu_usage']}%")
        
        # 清理旧记录（每天清理一次）
        if datetime.now().hour == 0 and datetime.now().minute < 1:
            self.resource_model.cleanup_old_records()
    
    def get_cpu_status(self) -> Dict:
        """获取CPU状态 - 直接从数据库获取最新记录"""
        if self.resource_model is None:
            self.resource_model = ResourceModel()
        
        latest_cpu = self.resource_model.get_latest_cpu_usage()
        
        if latest_cpu:
            return latest_cpu
        else:
            return {
                'cpu_usage': 0,
            }
    
    def get_gpu_history(self) -> List[Dict]:
        """获取GPU历史数据"""
        if self.resource_model is None:
            self.resource_model = ResourceModel()
        latest_gpu = self.resource_model.get_latest_gpu_usage()
        print("-------service gpu history-------", latest_gpu)
        if latest_gpu:
            return latest_gpu
        else:
            return {
                'gpu_usage': 0,
            }

# 创建全局实例
resource_service = ResourceService()