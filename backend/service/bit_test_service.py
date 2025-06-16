import pymysql
from datetime import datetime
import pandas as pd
from docx import Document
from docx.shared import Inches
import io

class BitTestService:
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '123456',
            'database': 'webproject',
            'charset': 'utf8mb4'
        }
        self.connection = None
        self.is_testing = False

    def get_connection(self):
        if not self.connection:
            self.connection = pymysql.connect(**self.db_config)
        return self.connection

    def get_test_list(self, page, size):
        try:
            conn = self.get_connection()
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                # 获取总记录数
                cursor.execute("SELECT COUNT(*) as total FROM pms_sca")
                total = cursor.fetchone()['total']

                # 获取分页数据
                offset = (page - 1) * size
                cursor.execute("""
                    SELECT 
                        item as projectName,
                        project_type as type,
                        status as result,
                        info as description
                    FROM pms_sca
                    ORDER BY id DESC
                    LIMIT %s OFFSET %s
                """, (size, offset))
                
                items = cursor.fetchall()
                
                return {
                    'items': items,
                    'total': total
                }
        except Exception as e:
            print(f"Error in get_test_list: {str(e)}")
            raise e

    def start_test(self):
        if self.is_testing:
            raise Exception("测试已经在进行中")
        self.is_testing = True
        # TODO: 实现实际的测试逻辑

    def stop_test(self):
        if not self.is_testing:
            raise Exception("没有正在进行的测试")
        self.is_testing = False
        # TODO: 实现停止测试的逻辑

    def export_excel(self):
        try:
            conn = self.get_connection()
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        project_name as '项目名称',
                        test_type as '类型',
                        test_result as '结果',
                        description as '描述'
                    FROM pms_sca
                    ORDER BY id DESC
                """)
                
                data = cursor.fetchall()
                df = pd.DataFrame(data)
                
                # 创建Excel文件
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='符合性测试报告')
                
                return output.getvalue()
        except Exception as e:
            print(f"Error in export_excel: {str(e)}")
            raise e

    def export_word(self):
        try:
            conn = self.get_connection()
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        project_name,
                        test_type,
                        test_result,
                        description
                    FROM pms_sca
                    ORDER BY id DESC
                """)
                
                data = cursor.fetchall()
                
                # 创建Word文档
                doc = Document()
                doc.add_heading('符合性测试报告', 0)
                doc.add_paragraph(f'生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
                
                # 添加表格
                table = doc.add_table(rows=1, cols=4)
                table.style = 'Table Grid'
                
                # 添加表头
                header_cells = table.rows[0].cells
                header_cells[0].text = '项目名称'
                header_cells[1].text = '类型'
                header_cells[2].text = '结果'
                header_cells[3].text = '描述'
                
                # 添加数据行
                for row in data:
                    cells = table.add_row().cells
                    cells[0].text = row['project_name']
                    cells[1].text = row['test_type']
                    cells[2].text = row['test_result']
                    cells[3].text = row['description']
                
                # 保存到内存
                output = io.BytesIO()
                doc.save(output)
                output.seek(0)
                
                return output.getvalue()
        except Exception as e:
            print(f"Error in export_word: {str(e)}")
            raise e

    def __del__(self):
        if self.connection:
            self.connection.close() 