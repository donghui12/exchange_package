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
            
            # 填充商品基础信息（按15列格式）
            row = 2
            
            # 获取基础数据
            goods_name = goods_info.get('goods_name', '')
            goods_id = goods_info.get('goods_id', '')
            
            # 主商品信息行（第一个SKU或主商品）
            first_sku = sku_list[0] if sku_list else {}
            
            # 填充15列数据
            ws.cell(row=row, column=1, value=goods_name)  # * 产品标题
            ws.cell(row=row, column=2, value="CNY")  # 货币类型
            ws.cell(row=row, column=3, value=f"https://mobile.yangkeduo.com/goods.html?goods_id={goods_id}")  # 货源链接
            ws.cell(row=row, column=4, value="拼多多")  # 货源平台
            ws.cell(row=row, column=5, value=goods_id)  # 产品主编号
            ws.cell(row=row, column=6, value="")  # 详情描述（待填写）
            ws.cell(row=row, column=7, value="")  # 货源类目（待填写）
            ws.cell(row=row, column=8, value="")  # 属性（待填写）
            
            # SKU规格处理
            if first_sku:
                specs = first_sku.get('specs', [])
                if len(specs) >= 1:
                    ws.cell(row=row, column=9, value=specs[0].get('spec_value', ''))  # SKU规格1
                if len(specs) >= 2:
                    ws.cell(row=row, column=10, value=specs[1].get('spec_value', ''))  # SKU规格2
                
                # 生成平台SKU
                spec_values = [spec.get('spec_value', '') for spec in specs if spec.get('spec_value')]
                platform_sku = "-".join(spec_values) if spec_values else "默认"
                ws.cell(row=row, column=11, value=platform_sku)  # 平台SKU
                
                ws.cell(row=row, column=12, value=first_sku.get('group_price', 0) / 100)  # * SKU售价
            else:
                ws.cell(row=row, column=9, value="")  # SKU规格1
                ws.cell(row=row, column=10, value="")  # SKU规格2
                ws.cell(row=row, column=11, value="默认")  # 平台SKU
                ws.cell(row=row, column=12, value=price_info.get('min_group_price', 0) / 100)  # * SKU售价
            
            ws.cell(row=row, column=13, value=999)  # SKU库存（默认值）
            ws.cell(row=row, column=14, value=0.5)  # SKU重量(KG)（默认值）
            ws.cell(row=row, column=15, value="")  # SKU尺寸(CM)（待填写）
            
            row += 1
            
            # 其他SKU信息行
            for sku in sku_list[1:]:  # 跳过第一个SKU
                ws.cell(row=row, column=1, value=goods_name)  # * 产品标题
                ws.cell(row=row, column=2, value="CNY")  # 货币类型
                ws.cell(row=row, column=3, value="")  # 货源链接（空）
                ws.cell(row=row, column=4, value="")  # 货源平台（空）
                ws.cell(row=row, column=5, value="")  # 产品主编号（空）
                ws.cell(row=row, column=6, value="")  # 详情描述（空）
                ws.cell(row=row, column=7, value="")  # 货源类目（空）
                ws.cell(row=row, column=8, value="")  # 属性（空）
                
                # SKU规格处理
                specs = sku.get('specs', [])
                if len(specs) >= 1:
                    ws.cell(row=row, column=9, value=specs[0].get('spec_value', ''))  # SKU规格1
                if len(specs) >= 2:
                    ws.cell(row=row, column=10, value=specs[1].get('spec_value', ''))  # SKU规格2
                
                # 生成平台SKU
                spec_values = [spec.get('spec_value', '') for spec in specs if spec.get('spec_value')]
                platform_sku = "-".join(spec_values) if spec_values else "默认"
                ws.cell(row=row, column=11, value=platform_sku)  # 平台SKU
                
                ws.cell(row=row, column=12, value=sku.get('group_price', 0) / 100)  # * SKU售价
                ws.cell(row=row, column=13, value=999)  # SKU库存（默认值）
                ws.cell(row=row, column=14, value=0.5)  # SKU重量(KG)（默认值）
                ws.cell(row=row, column=15, value="")  # SKU尺寸(CM)（待填写）
                
                row += 1
            
            # 设置列宽（15列）
            column_widths = [20, 10, 30, 10, 15, 25, 15, 25, 12, 12, 15, 12, 10, 12, 15]
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
                    if col_num in [12]:  # * SKU售价列
                        cell.alignment = Alignment(horizontal="right", vertical="center")
                        cell.number_format = '0.00'
                    # 重量列右对齐
                    elif col_num in [14]:  # SKU重量(KG)列
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