import os
import shutil
from typing import List, Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session
from models import project_model
import json
import uuid


class ResultImageService:
    def __init__(self, base_upload_dir: str = "uploads/results"):
        self.base_upload_dir = base_upload_dir
        # 确保上传目录存在
        os.makedirs(self.base_upload_dir, exist_ok=True)
    
    def save_result_images(self, db: Session, project_id: int, image_files: List[UploadFile]) -> List[str]:
        """保存结果图片并更新项目记录"""
        saved_paths = []
        
        # 获取项目信息
        project = project_model.get_project_by_id(db, project_id)
        if not project:
            raise ValueError('项目不存在')
        
        # 创建项目专属目录
        project_dir = os.path.join(self.base_upload_dir, f"project_{project_id}")
        os.makedirs(project_dir, exist_ok=True)
        
        # 保存每个图片文件
        for image_file in image_files:
            # 生成唯一文件名
            file_extension = os.path.splitext(image_file.filename)[1] if image_file.filename else '.png'
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"
            file_path = os.path.join(project_dir, unique_filename)
            
            # 保存文件
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image_file.file, buffer)
            
            # 记录保存的路径（相对路径，便于前端访问）
            relative_path = f"/api/result-images/{project_id}/{unique_filename}"
            saved_paths.append(relative_path)
        
        # 更新项目的结果图片路径
        existing_images = self.get_project_result_images(db, project_id)
        all_images = existing_images + saved_paths
        
        # 更新数据库
        project_model.update_project_result_images(db, project_id, all_images)
        
        return saved_paths
    
    def get_project_result_images(self, db: Session, project_id: int) -> List[str]:
        """获取项目的结果图片路径"""
        project = project_model.get_project_by_id(db, project_id)
        if not project:
            return []
        
        # 解析结果图片路径
        if project.result_images:
            try:
                return json.loads(project.result_images)
            except json.JSONDecodeError:
                return []
        return []
    
    def delete_result_image(self, db: Session, project_id: int, image_path: str) -> bool:
        """删除指定的结果图片"""
        # 获取当前图片列表
        current_images = self.get_project_result_images(db, project_id)
        
        # 从列表中移除指定图片
        updated_images = [img for img in current_images if img != image_path]
        
        # 更新数据库
        project_model.update_project_result_images(db, project_id, updated_images)
        
        # 删除物理文件
        try:
            # 从路径中提取文件名
            filename = image_path.split('/')[-1]
            file_path = os.path.join(self.base_upload_dir, f"project_{project_id}", filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception:
            pass
        
        return False

# 创建全局实例
result_image_service = ResultImageService()