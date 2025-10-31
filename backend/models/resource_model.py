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
    
    def cleanup_old_records(self, keep_days: int = 7):
        """清理旧记录，保留指定天数内的数据"""
        try:
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            deleted_count = self.db.query(ResourceMonitorRecord).filter(
                ResourceMonitorRecord.timestamp < cutoff_date
            ).delete()
            self.db.commit()
            print(f"清理了 {deleted_count} 条旧资源记录")
            return deleted_count
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
    
    def generate_cpu_usage(self) -> float:
        """生成模拟的CPU使用率数据"""
        return round(random.uniform(5.0, 85.0), 2)
    
    def generate_gpu_usage(self) -> float:
        """生成模拟的GPU使用率数据"""
        return round(random.uniform(10.0, 95.0), 2)
    
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