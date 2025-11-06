import os
import time
import json
from typing import List, Dict, Optional
from datetime import datetime

class LogFileService:
    """日志文件服务类"""
    
    def __init__(self, base_log_dir: str = None):
        self.base_log_dir = base_log_dir or os.path.join(os.getcwd(), 'logs', 'projects')
        # 确保日志目录存在
        os.makedirs(self.base_log_dir, exist_ok=True)
    
    def get_project_log_file_path(self, project_id: int, project_name: str, log_file_name: str = None) -> str:
        """获取项目日志文件路径，优先使用数据库中的日志文件名"""
        if log_file_name:
            # 如果提供了日志文件名，直接使用
            return os.path.join(self.base_log_dir, log_file_name)
        else:
            # 否则使用原来的逻辑生成文件名
            safe_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_')
            return os.path.join(self.base_log_dir, f'{safe_name}_{project_id}.log')
    
    def read_project_logs(self, project_id: int, project_name: str, last_position: int = 0, log_file_name: str = None) -> Dict:
        """读取项目日志，支持使用数据库中的日志文件名"""
        log_file_path = self.get_project_log_file_path(project_id, project_name, log_file_name)
        
        if not os.path.exists(log_file_path):
            return {
                'success': True,
                'data': [],
                'message': '日志文件不存在',
                'last_position': 0,
                'file_size': 0
            }
        
        logs = []
        current_position = 0
        file_size = os.path.getsize(log_file_path)
        
        try:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                # 如果文件被截断，重置位置
                if last_position > file_size:
                    last_position = 0
                
                if last_position > 0:
                    f.seek(last_position)
                
                new_logs = f.readlines()
                current_position = f.tell()
                
                # 处理日志行
                for line_num, line in enumerate(new_logs, start=1):
                    line = line.strip()
                    if line:
                        # 添加时间戳和行号
                        timestamp = datetime.now().strftime('%H:%M:%S')
                        formatted_log = f"[{timestamp}] {line}"
                        logs.append(formatted_log)
                        
        except Exception as e:
            return {
                'success': False,
                'data': [],
                'message': f'读取日志文件失败: {str(e)}',
                'last_position': last_position,
                'file_size': file_size
            }
        
        return {
            'success': True,
            'data': logs,
            'message': f'成功读取 {len(logs)} 条新日志',
            'last_position': current_position,
            'file_size': file_size
        }
    
    def get_log_file_info(self, project_id: int, project_name: str) -> Dict:
        """获取日志文件信息"""
        log_file_path = self.get_project_log_file_path(project_id, project_name)
        
        if not os.path.exists(log_file_path):
            return {
                'exists': False,
                'file_size': 0,
                'modified_time': None
            }
        
        return {
            'exists': True,
            'file_size': os.path.getsize(log_file_path),
            'modified_time': datetime.fromtimestamp(os.path.getmtime(log_file_path)).isoformat()
        }

# 创建全局实例
log_file_service = LogFileService()