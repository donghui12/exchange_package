"""
Excel文件生成模块
生成商品导入模板Excel文件
"""
import os
from datetime import datetime
from typing import Dict, List, Any
try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
except ImportError:
    print("警告: openpyxl 未安装，Excel生成功能将不可用")
    Workbook = None

from src.config import Config

class ExcelGenerator:
    """Excel文件生成器"""
    
    def __init__(self):
        """初始化生成器"""
        if Workbook is None:
            raise ImportError("openpyxl 未安装，无法使用Excel生成功能")
    
    def create_product_template(self, parser, output_dir: str, download_results: Dict = None) -> bool:
        """
        创建商品导入模板Excel文件
        
        Args:
            parser: 数据解析器实例
            output_dir: 输出目录
            download_results: 下载结果统计
            
        Returns:
            bool: 生成是否成功
        """
        try:
            # 创建工作簿
            wb = Workbook()
            ws = wb.active
            ws.title = "商品信息"
            
            # 获取商品数据
            goods_info = parser.get_goods_basic_info()
            price_info = parser.get_price_info()
            sku_list = parser.get_sku_info()
            
            # 设置表头
            headers = Config.EXCEL_HEADERS
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = Border(
                    left=Side(style="thin"),
                    right=Side(style="thin"),
                    top=Side(style="thin"),
                    bottom=Side(style="thin")
                )
            
            # 填充商品基础信息
            row = 2
            
            # 主商品信息行
            ws.cell(row=row, column=1, value=goods_info.get('goods_id', ''))
            ws.cell(row=row, column=2, value=goods_info.get('goods_name', ''))
            ws.cell(row=row, column=3, value=price_info.get('min_group_price', 0) / 100)  # 转换为元
            ws.cell(row=row, column=4, value=price_info.get('line_price', 0) / 100)  # 转换为元
            ws.cell(row=row, column=5, value="主商品")
            
            # 图片数量统计
            if download_results:
                ws.cell(row=row, column=6, value=download_results.get('main_images', {}).get('success', 0))
                ws.cell(row=row, column=7, value=download_results.get('detail_images', {}).get('success', 0))
                ws.cell(row=row, column=8, value=download_results.get('sku_images', {}).get('success', 0))
            else:
                main_images = parser.get_main_images()
                detail_images = parser.get_detail_images()
                sku_images = parser.get_sku_images()
                ws.cell(row=row, column=6, value=len(main_images))
                ws.cell(row=row, column=7, value=len(detail_images))
                ws.cell(row=row, column=8, value=len(sku_images))
            
            ws.cell(row=row, column=9, value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            row += 1
            
            # SKU信息行
            for sku in sku_list:
                ws.cell(row=row, column=1, value=sku.get('sku_id', ''))
                ws.cell(row=row, column=2, value=goods_info.get('goods_name', ''))
                ws.cell(row=row, column=3, value=sku.get('group_price', 0) / 100)  # 转换为元
                ws.cell(row=row, column=4, value=sku.get('normal_price', 0) / 100)  # 转换为元
                
                # 生成规格描述
                specs = sku.get('specs', [])
                spec_desc = []
                for spec in specs:
                    key = spec.get('spec_key', '')
                    value = spec.get('spec_value', '')
                    if key and value:
                        spec_desc.append(f"{key}:{value}")
                
                ws.cell(row=row, column=5, value="; ".join(spec_desc) if spec_desc else "默认规格")
                ws.cell(row=row, column=6, value=0)  # SKU没有单独的主图
                ws.cell(row=row, column=7, value=0)  # SKU没有单独的详情图
                ws.cell(row=row, column=8, value=1 if sku.get('thumb_url') else 0)  # SKU图
                ws.cell(row=row, column=9, value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                
                row += 1
            
            # 设置列宽
            column_widths = [15, 30, 12, 12, 25, 12, 12, 12, 20]
            for i, width in enumerate(column_widths, 1):
                ws.column_dimensions[get_column_letter(i)].width = width
            
            # 设置数据行样式
            for row_num in range(2, row):
                for col_num in range(1, len(headers) + 1):
                    cell = ws.cell(row=row_num, column=col_num)
                    cell.alignment = Alignment(horizontal="left", vertical="center")
                    cell.border = Border(
                        left=Side(style="thin"),
                        right=Side(style="thin"),
                        top=Side(style="thin"),
                        bottom=Side(style="thin")
                    )
                    
                    # 价格列右对齐
                    if col_num in [3, 4]:
                        cell.alignment = Alignment(horizontal="right", vertical="center")
                        cell.number_format = '0.00'
            
            # 保存文件
            file_path = os.path.join(output_dir, Config.FILE_NAMING['excel_filename'])
            wb.save(file_path)
            
            return True
            
        except Exception as e:
            print(f"生成Excel文件失败: {e}")
            return False
    
    def create_summary_sheet(self, parser, output_dir: str, download_results: Dict = None) -> bool:
        """
        创建汇总信息表
        
        Args:
            parser: 数据解析器实例
            output_dir: 输出目录
            download_results: 下载结果统计
            
        Returns:
            bool: 生成是否成功
        """
        try:
            file_path = os.path.join(output_dir, "转换汇总报告.xlsx")
            
            wb = Workbook()
            ws = wb.active
            ws.title = "转换汇总"
            
            # 基础信息
            summary = parser.get_summary()
            goods_info = parser.get_goods_basic_info()
            price_info = parser.get_price_info()
            
            # 设置报告内容
            report_data = [
                ["转换汇总报告", ""],
                ["", ""],
                ["商品信息", ""],
                ["商品ID", goods_info.get('goods_id', '')],
                ["商品名称", goods_info.get('goods_name', '')],
                ["文件夹名称", summary.get('folder_name', '')],
                ["商品价格", f"{price_info.get('min_group_price', 0) / 100:.2f} 元"],
                ["市场价格", f"{price_info.get('line_price', 0) / 100:.2f} 元"],
                ["", ""],
                ["图片统计", ""],
                ["主图数量", summary.get('main_images_count', 0)],
                ["详情图数量", summary.get('detail_images_count', 0)],
                ["SKU图数量", summary.get('sku_images_count', 0)],
                ["图片总数", summary.get('total_images', 0)],
                ["", ""],
            ]
            
            # 添加下载结果
            if download_results:
                report_data.extend([
                    ["下载结果", ""],
                    ["主图下载成功", download_results.get('main_images', {}).get('success', 0)],
                    ["主图下载失败", download_results.get('main_images', {}).get('failed', 0)],
                    ["详情图下载成功", download_results.get('detail_images', {}).get('success', 0)],
                    ["详情图下载失败", download_results.get('detail_images', {}).get('failed', 0)],
                    ["SKU图下载成功", download_results.get('sku_images', {}).get('success', 0)],
                    ["SKU图下载失败", download_results.get('sku_images', {}).get('failed', 0)],
                    ["总下载成功", download_results.get('total_success', 0)],
                    ["总下载失败", download_results.get('total_failed', 0)],
                    ["", ""],
                ])
            
            # 添加时间信息
            report_data.extend([
                ["生成时间", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                ["生成工具", f"{Config.APP_NAME} v{Config.APP_VERSION}"],
            ])
            
            # 填充数据
            for row_idx, (key, value) in enumerate(report_data, 1):
                ws.cell(row=row_idx, column=1, value=key)
                ws.cell(row=row_idx, column=2, value=value)
                
                # 设置样式
                if key and not value:  # 标题行
                    cell = ws.cell(row=row_idx, column=1)
                    cell.font = Font(bold=True, size=12)
                    cell.fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
            
            # 设置列宽
            ws.column_dimensions['A'].width = 20
            ws.column_dimensions['B'].width = 30
            
            # 保存文件
            wb.save(file_path)
            
            return True
            
        except Exception as e:
            print(f"生成汇总报告失败: {e}")
            return False