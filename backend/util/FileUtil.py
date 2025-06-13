import os
import json
from typing import Dict, List, Any

class FileUtil:
    @staticmethod
    def ensure_dir(directory: str) -> None:
        """确保目录存在，如果不存在则创建"""
        if not os.path.exists(directory):
            os.makedirs(directory)

    @staticmethod
    def write_file(file_path: str, content: str) -> None:
        """写入文件内容"""
        # 确保目录存在
        directory = os.path.dirname(file_path)
        FileUtil.ensure_dir(directory)
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    def write_module_files(module_name: str, files: List[Dict[str, Any]]) -> Dict[str, str]:
        """写入模块相关文件
        
        Args:
            module_name: 模块名称
            files: 文件列表，每个文件包含 name 和 content
            
        Returns:
            Dict[str, str]: 写入结果，key 为文件路径，value 为状态信息
        """
        results = {}
        # 获取项目根目录的上级目录
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        workspace_dir = os.path.join(os.path.dirname(current_dir), 'workspace')
        base_path = os.path.join(workspace_dir, module_name)
        
        try:
            # 确保 workspace 目录存在
            FileUtil.ensure_dir(workspace_dir)
            
            # 写入每个文件
            for file in files:
                file_path = os.path.join(base_path, file['name'])
                FileUtil.write_file(file_path, file['content'])
                results[file_path] = 'success'
                
            return {
                'status': 'success',
                'message': f'Successfully wrote {len(files)} files for module {module_name}',
                'results': results
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to write files for module {module_name}: {str(e)}',
                'results': results
            } 