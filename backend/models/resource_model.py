from sqlalchemy import Column, Integer, Float, DateTime, Index, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
import random
from typing import List, Dict, Optional
from util.db import SessionLocal, Base

# 资源监控记录表
class ResourceMonitorRecord(Base):
    __tablename__ = 'resource_monitor_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cpu_usage = Column(Float, nullable=False, comment='CPU使用率百分比')
    gpu_usage = Column(Float, nullable=False, comment='GPU使用率百分比')
    timestamp = Column(DateTime, nullable=False, default=datetime.now, comment='记录时间戳')
    
    # 创建索引以提高查询性能
    __table_args__ = (
        Index('idx_timestamp', 'timestamp'),
    )

# 资源模型类 - 负责数据库操作
class ResourceModel:
    def __init__(self):
        # 使用SessionLocal创建新的数据库会话
        self.db = SessionLocal()
    
    def __del__(self):
        # 确保会话被正确关闭
        if hasattr(self, 'db'):
            self.db.close()
    
    def insert_resource_record(self, cpu_usage: float, gpu_usage: float) -> bool:
        """插入资源监控记录"""
        try:
            record = ResourceMonitorRecord(
                cpu_usage=cpu_usage,
                gpu_usage=gpu_usage,
                timestamp=datetime.now()
            )
            self.db.add(record)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"插入资源记录失败: {e}")
            return False
    
    def get_latest_cpu_usage(self) -> Optional[Dict]:
        """获取最新的CPU使用率数据"""
        try:
            record = self.db.query(ResourceMonitorRecord).order_by(
                ResourceMonitorRecord.timestamp.desc()
            ).first()
            
            if record:
                return {
                    'cpu_usage': record.cpu_usage,
                }
            return None
        except Exception as e:
            print(f"查询最新CPU使用率失败: {e}")
            return None
    
    def get_recent_resource_records(self, limit: int = 30) -> List[Dict]:
        """获取最近的资源监控记录"""
        try:
            records = self.db.query(ResourceMonitorRecord).order_by(
                ResourceMonitorRecord.timestamp.desc()
            ).limit(limit).all()
            
            result = []
            for record in reversed(records):  # 按时间顺序返回
                result.append({
                    'cpu_usage': record.cpu_usage,
                    'gpu_usage': record.gpu_usage,
                    'timestamp': record.timestamp.isoformat()
                })
            return result
        except Exception as e:
            print(f"查询资源记录失败: {e}")
            return []

    def cleanup_old_records(self, max_records: int = 39):
        """清理旧记录，保证只保留指定数量的最新记录"""
        try:
            # 获取总记录数
            total_count = self.db.query(ResourceMonitorRecord).count()
            
            if total_count > max_records:
                # 计算需要删除的记录数
                records_to_delete = total_count - max_records
                
                # 获取需要删除的最旧记录的ID
                oldest_records = self.db.query(ResourceMonitorRecord.id).order_by(
                    ResourceMonitorRecord.timestamp.asc()
                ).limit(records_to_delete).all()
                
                # 删除旧记录
                if oldest_records:
                    oldest_ids = [record[0] for record in oldest_records]
                    deleted_count = self.db.query(ResourceMonitorRecord).filter(
                        ResourceMonitorRecord.id.in_(oldest_ids)
                    ).delete(synchronize_session=False)
                    
                    self.db.commit()
                    # print(f"清理了 {deleted_count} 条旧资源记录，当前保留 {max_records} 条最新记录")
                    return deleted_count
            
            return 0
        except Exception as e:
            self.db.rollback()
            print(f"清理旧记录失败: {e}")
            return 0

# 内存数据模型类 - 用于模拟数据生成
class ResourceMonitor:
    def __init__(self):
        self.cpu_history = []  # 存储CPU使用率历史数据
        self.gpu_history = []  # 存储GPU使用率历史数据
        self.max_history_length = 30  # 最大历史记录数
        self.last_gpu_usage = 25.0  # 初始化GPU使用率，避免突变

    def generate_cpu_usage(self) -> float:
        """生成模拟的CPU使用率数据"""
        return round(random.uniform(5.0, 85.0), 2)
    
    def generate_gpu_usage(self) -> float:
        """生成模拟的GPU使用率数据 - 平滑变化避免突变"""
        # 基于上次使用率进行平滑变化，避免突然跳到25%
        change = random.uniform(-15.0, 15.0)
        new_usage = self.last_gpu_usage + change
        
        # 限制在合理范围内
        new_usage = max(5.0, min(95.0, new_usage))
        
        # 更新上次使用率
        self.last_gpu_usage = new_usage
        
        return round(new_usage, 2)
    
    def get_current_resources(self) -> Dict:
        """获取当前资源使用情况并更新历史数据"""
        cpu_usage = self.generate_cpu_usage()
        gpu_usage = self.generate_gpu_usage()
        
        # 更新CPU历史数据
        self.cpu_history.append(cpu_usage)
        if len(self.cpu_history) > self.max_history_length:
            self.cpu_history.pop(0)
        
        # 更新GPU历史数据
        self.gpu_history.append(gpu_usage)
        if len(self.gpu_history) > self.max_history_length:
            self.gpu_history.pop(0)
        
        return {
            'cpu_usage': cpu_usage,
            'gpu_usage': gpu_usage,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_resource_history(self, limit: int = 30) -> Dict:
        """获取资源历史数据"""
        cpu_history = self.cpu_history[-limit:] if len(self.cpu_history) > limit else self.cpu_history
        gpu_history = self.gpu_history[-limit:] if len(self.gpu_history) > limit else self.gpu_history
        
        return {
            'cpu_history': cpu_history,
            'gpu_history': gpu_history
        }

# 创建全局实例
resource_monitor = ResourceMonitor()