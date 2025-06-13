import os
import json
from typing import Dict, List, Any
import logging
import traceback

# 配置日志
logger = logging.getLogger(__name__)

class FileUtil:
    @staticmethod
    def ensure_dir(directory: str) -> None:
        """确保目录存在，如果不存在则创建"""
        try:
            if not os.path.exists(directory):
                logger.debug(f"创建目录: {directory}")
                os.makedirs(directory)
        except Exception as e:
            logger.error(f"创建目录失败: {directory}")
            logger.error(traceback.format_exc())
            raise

    @staticmethod
    def write_file(file_path: str, content: str) -> None:
        """写入文件内容"""
        try:
            # 确保目录存在
            directory = os.path.dirname(file_path)
            FileUtil.ensure_dir(directory)
            
            # 写入文件
            logger.debug(f"写入文件: {file_path}")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            logger.error(f"写入文件失败: {file_path}")
            logger.error(traceback.format_exc())
            raise

    @staticmethod
    def get_workspace_path() -> str:
        """获取 workspace 目录的路径"""
        try:
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            workspace_path = os.path.join(os.path.dirname(current_dir), 'workspace')
            logger.debug(f"Workspace 路径: {workspace_path}")
            return workspace_path
        except Exception as e:
            logger.error("获取 workspace 路径失败")
            logger.error(traceback.format_exc())
            raise

    @staticmethod
    def get_module_structure(module_name: str) -> Dict[str, Any]:
        """获取模块的文件结构
        
        Args:
            module_name: 模块名称
            
        Returns:
            Dict[str, Any]: 模块的文件结构
        """
        try:
            workspace_path = FileUtil.get_workspace_path()
            module_path = os.path.join(workspace_path, module_name)
            logger.debug(f"获取模块结构: {module_path}")
            
            if not os.path.exists(module_path):
                logger.warning(f"模块目录不存在: {module_path}")
                return None
            
            structure = {
                'name': module_name,
                'expanded': True,
                'srcExpanded': True,
                'files': []
            }
            
            # 遍历模块目录
            for root, dirs, files in os.walk(module_path):
                for file in files:
                    # 获取相对路径
                    rel_path = os.path.relpath(os.path.join(root, file), module_path)
                    # 读取文件内容
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            content = f.read()
                    except Exception as e:
                        logger.warning(f"读取文件失败: {os.path.join(root, file)}")
                        content = ''
                    
                    structure['files'].append({
                        'name': rel_path,
                        'content': content
                    })
                
            return structure
        except Exception as e:
            logger.error(f"获取模块结构失败: {module_name}")
            logger.error(traceback.format_exc())
            raise

    @staticmethod
    def get_all_modules() -> List[Dict[str, Any]]:
        """获取所有模块的文件结构
        
        Returns:
            List[Dict[str, Any]]: 所有模块的文件结构列表
        """
        try:
            workspace_path = FileUtil.get_workspace_path()
            logger.debug(f"获取所有模块，workspace 路径: {workspace_path}")
            
            if not os.path.exists(workspace_path):
                logger.warning(f"Workspace 目录不存在: {workspace_path}")
                return []
            
            modules = []
            for item in os.listdir(workspace_path):
                item_path = os.path.join(workspace_path, item)
                if os.path.isdir(item_path):
                    module_structure = FileUtil.get_module_structure(item)
                    if module_structure:
                        modules.append(module_structure)
            
            return modules
        except Exception as e:
            logger.error("获取所有模块失败")
            logger.error(traceback.format_exc())
            raise

    @staticmethod
    def write_module_files(module_name: str, files: List[Dict[str, Any]]) -> Dict[str, str]:
        """写入模块相关文件
        
        Args:
            module_name: 模块名称
            files: 文件列表，每个文件包含 name 和 content
            
        Returns:
            Dict[str, str]: 写入结果，key 为文件路径，value 为状态信息
        """
        try:
            results = {}
            workspace_path = FileUtil.get_workspace_path()
            base_path = os.path.join(workspace_path, module_name)
            logger.debug(f"写入模块文件，模块路径: {base_path}")
            
            # 确保 workspace 目录存在
            FileUtil.ensure_dir(workspace_path)
            
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
            logger.error(f"写入模块文件失败: {module_name}")
            logger.error(traceback.format_exc())
            return {
                'status': 'error',
                'message': f'Failed to write files for module {module_name}: {str(e)}',
                'results': {}
            } 