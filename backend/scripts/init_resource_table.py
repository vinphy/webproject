from util.db import init_db, Base
from models.resource_model import ResourceMonitorRecord

def init_resource_table():
    """初始化资源监控表"""
    try:
        # 创建所有表
        init_db()
        print("资源监控表初始化成功")
    except Exception as e:
        print(f"资源监控表初始化失败: {e}")

if __name__ == "__main__":
    init_resource_table()