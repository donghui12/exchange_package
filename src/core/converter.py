"""
主转换器模块
协调各个组件完成完整的转换流程
"""
import os
import time
import shutil
import zipfile
from typing import Callable, Optional, Dict, Any

from .data_parser import PDDDataParser
from .downloader import ImageDownloader
from .excel_generator import ExcelGenerator
from src.config import Config
from ..utils.file_utils import FileUtils

class MaterialConverter:
    """素材包转换器主类"""
    
    def __init__(self, progress_callback: Optional[Callable] = None):
        """
        初始化转换器
        
        Args:
            progress_callback: 进度回调函数
        """
        self.progress_callback = progress_callback
        self.parser = PDDDataParser()
        self.downloader = ImageDownloader(progress_callback=progress_callback)
        self.excel_generator = ExcelGenerator()
        self.file_utils = FileUtils()
        
    def log(self, message: str):
        """记录日志"""
        if self.progress_callback:
            self.progress_callback(message)
        print(message)
    
    def convert_single_file(self, 
                           pdd_file_path: str, 
                           output_dir: str, 
                           export_format: int = 2, 
                           create_zip: bool = False) -> Dict[str, Any]:
        """
        转换单个PDD文件
        
        Args:
            pdd_file_path: PDD数据文件路径
            output_dir: 输出目录
            export_format: 导出格式(1或2)
            create_zip: 是否创建ZIP压缩包
            
        Returns:
            Dict: 转换结果
        """
        result = {
            'success': False,
            'error': None,
            'file_path': pdd_file_path,
            'output_path': '',
            'download_results': {},
            'processing_time': 0
        }
        
        start_time = time.time()
        
        try:
            self.log(f"开始处理文件: {os.path.basename(pdd_file_path)}")
            
            # 1. 解析数据文件
            self.log("正在解析商品数据...")
            if not self.parser.parse_file(pdd_file_path):
                raise Exception("解析PDD数据文件失败")
            
            # 获取商品信息
            summary = self.parser.get_summary()
            self.log(f"商品: {summary['goods_name']}")
            self.log(f"商品ID: {summary['goods_id']}")
            self.log(f"图片总数: {summary['total_images']}")
            
            # 2. 创建输出目录
            folder_name = self.parser.get_folder_name()
            product_output_dir = os.path.join(output_dir, folder_name)
            
            if os.path.exists(product_output_dir):
                self.log(f"输出目录已存在，将被覆盖: {folder_name}")
                shutil.rmtree(product_output_dir)
            
            os.makedirs(product_output_dir, exist_ok=True)
            self.log(f"创建输出目录: {folder_name}")
            
            # 3. 下载图片
            self.log("开始下载商品图片...")
            download_results = self.downloader.download_all_images(
                self.parser, 
                product_output_dir, 
                export_format
            )
            
            result['download_results'] = download_results
            
            # 4. 生成Excel文件
            self.log("生成Excel导入模板...")
            if self.excel_generator.create_product_template(
                self.parser, 
                product_output_dir, 
                download_results
            ):
                self.log("Excel模板生成成功")
            else:
                self.log("Excel模板生成失败")
            
            # 5. 生成汇总报告
            if self.excel_generator.create_summary_sheet(
                self.parser, 
                product_output_dir, 
                download_results
            ):
                self.log("汇总报告生成成功")
            
            # 6. 创建ZIP压缩包（可选）
            if create_zip:
                self.log("创建ZIP压缩包...")
                zip_path = f"{product_output_dir}.zip"
                if self._create_zip_package(product_output_dir, zip_path):
                    self.log(f"ZIP压缩包创建成功: {os.path.basename(zip_path)}")
                    result['zip_path'] = zip_path
                else:
                    self.log("ZIP压缩包创建失败")
            
            # 7. 完成
            result['success'] = True
            result['output_path'] = product_output_dir
            result['processing_time'] = time.time() - start_time
            
            self.log(f"转换完成! 用时: {result['processing_time']:.2f}秒")
            self.log(f"输出路径: {product_output_dir}")
            
        except Exception as e:
            result['error'] = str(e)
            result['processing_time'] = time.time() - start_time
            self.log(f"转换失败: {str(e)}")
        
        return result
    
    def convert_batch_files(self, 
                           input_dir: str, 
                           output_dir: str, 
                           export_format: int = 2, 
                           create_zip: bool = False,
                           interval_seconds: int = 3) -> Dict[str, Any]:
        """
        批量转换PDD文件
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            export_format: 导出格式(1或2)
            create_zip: 是否创建ZIP压缩包
            interval_seconds: 转换间隔时间
            
        Returns:
            Dict: 批量转换结果
        """
        batch_result = {
            'success': True,
            'total_files': 0,
            'success_count': 0,
            'failed_count': 0,
            'results': [],
            'total_time': 0
        }
        
        start_time = time.time()
        
        try:
            # 查找所有PDD文件
            pdd_files = self._find_pdd_files(input_dir)
            batch_result['total_files'] = len(pdd_files)
            
            if not pdd_files:
                self.log("未找到任何PDD数据文件 (*.txt)")
                batch_result['success'] = False
                return batch_result
            
            self.log(f"找到 {len(pdd_files)} 个PDD文件，开始批量转换...")
            
            # 逐个转换文件
            for i, pdd_file in enumerate(pdd_files, 1):
                self.log(f"\n=== 处理第 {i}/{len(pdd_files)} 个文件 ===")
                
                # 转换单个文件
                result = self.convert_single_file(
                    pdd_file, 
                    output_dir, 
                    export_format, 
                    create_zip
                )
                
                batch_result['results'].append(result)
                
                if result['success']:
                    batch_result['success_count'] += 1
                else:
                    batch_result['failed_count'] += 1
                
                # 间隔等待（除了最后一个文件）
                if i < len(pdd_files) and interval_seconds > 0:
                    self.log(f"等待 {interval_seconds} 秒后处理下一个文件...")
                    time.sleep(interval_seconds)
            
            # 计算总时间
            batch_result['total_time'] = time.time() - start_time
            
            # 输出汇总结果
            self.log(f"\n=== 批量转换完成 ===")
            self.log(f"总文件数: {batch_result['total_files']}")
            self.log(f"成功: {batch_result['success_count']}")
            self.log(f"失败: {batch_result['failed_count']}")
            self.log(f"总用时: {batch_result['total_time']:.2f}秒")
            
        except Exception as e:
            batch_result['success'] = False
            batch_result['error'] = str(e)
            self.log(f"批量转换异常: {str(e)}")
        
        return batch_result
    
    def _find_pdd_files(self, directory: str) -> list:
        """查找目录中的PDD文件"""
        pdd_files = []
        
        if not os.path.exists(directory):
            return pdd_files
        
        for filename in os.listdir(directory):
            if filename.startswith('pdd_goods_') and filename.endswith('.txt'):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    pdd_files.append(file_path)
        
        # 按文件名排序
        pdd_files.sort()
        return pdd_files
    
    def _create_zip_package(self, source_dir: str, zip_path: str) -> bool:
        """创建ZIP压缩包"""
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_name = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, arc_name)
            
            return True
            
        except Exception as e:
            self.log(f"创建ZIP压缩包失败: {str(e)}")
            return False
    
    def validate_input_directory(self, directory: str) -> Dict[str, Any]:
        """
        验证输入目录
        
        Args:
            directory: 输入目录路径
            
        Returns:
            Dict: 验证结果
        """
        result = {
            'valid': False,
            'error': None,
            'pdd_files': [],
            'file_count': 0
        }
        
        try:
            if not os.path.exists(directory):
                result['error'] = "目录不存在"
                return result
            
            if not os.path.isdir(directory):
                result['error'] = "路径不是有效目录"
                return result
            
            # 查找PDD文件
            pdd_files = self._find_pdd_files(directory)
            result['pdd_files'] = pdd_files
            result['file_count'] = len(pdd_files)
            
            if not pdd_files:
                result['error'] = "目录中未找到PDD数据文件 (*.txt)"
                return result
            
            result['valid'] = True
            
        except Exception as e:
            result['error'] = f"验证目录时出错: {str(e)}"
        
        return result
    
    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'downloader'):
            self.downloader.close()