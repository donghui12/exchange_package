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
from .video_downloader import VideoDownloader
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
        self.video_downloader = VideoDownloader()
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
            
            # 3.5. 下载视频
            self.log("开始下载商品视频...")
            video_results = self._download_videos(product_output_dir)
            result['video_results'] = video_results
            
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
            
            # 5. 创建ZIP压缩包（可选）
            if create_zip:
                self.log("创建ZIP压缩包...")
                zip_path = f"{product_output_dir}.zip"
                if self._create_zip_package(product_output_dir, zip_path):
                    self.log(f"ZIP压缩包创建成功: {os.path.basename(zip_path)}")
                    # 删除原文件夹
                try:
                    shutil.rmtree(product_output_dir)
                    self.log(f"已删除原文件夹: {folder_name}")
                except Exception as del_err:
                    self.log(f"删除文件夹失败: {del_err}")
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
            if filename.endswith('.txt'):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    pdd_files.append(file_path)
        
        # 按文件名排序
        pdd_files.sort()
        return pdd_files
    
    def _create_zip_package(self, source_dir: str, zip_path: str) -> bool:
        """创建ZIP压缩包"""
        try:
            parent_dir = os.path.dirname(source_dir)

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        if file.startswith('.') or file.lower() == 'thumbs.db':
                            continue
                        file_path = os.path.join(root, file)
                        # 让 zip 里包含顶层目录名
                        arc_name = os.path.relpath(file_path, parent_dir)
                        
                        # Windows中文文件名兼容处理
                        try:
                            # 确保路径使用正斜杠（ZIP标准）
                            arc_name = arc_name.replace('\\', '/')
                            
                            # 修正时间戳（避免某些系统拒绝解析）
                            info = zipfile.ZipInfo(arc_name)
                            info.date_time = time.localtime(time.time())[:6]
                            
                            # 设置UTF-8编码标志，支持中文文件名
                            info.flag_bits |= 0x800  # UTF-8 flag
                            
                            with open(file_path, 'rb') as f:
                                zipf.writestr(info, f.read())
                                
                        except Exception as e:
                            print(f"添加文件到ZIP失败: {file_path}, 错误: {e}")
                            # 尝试使用安全的文件名
                            safe_name = self._make_safe_zip_filename(arc_name)
                            info = zipfile.ZipInfo(safe_name)
                            info.date_time = time.localtime(time.time())[:6]
                            with open(file_path, 'rb') as f:
                                zipf.writestr(info, f.read())

            return True
        except Exception as e:
            print(f"创建ZIP压缩包失败: {e}")
            return False
        
    def _make_safe_zip_filename(self, filename: str) -> str:
        """生成ZIP文件安全的文件名"""
        import re
        
        # 移除或替换可能有问题的字符
        safe_name = filename
        
        # 替换Windows路径分隔符
        safe_name = safe_name.replace('\\', '/')
        
        # 移除控制字符
        safe_name = re.sub(r'[\x00-\x1f\x7f]', '', safe_name)
        
        # 如果包含非ASCII字符，尝试转换为安全形式
        try:
            safe_name.encode('ascii')
        except UnicodeEncodeError:
            # 包含非ASCII字符，使用URL编码形式
            import urllib.parse
            parts = safe_name.split('/')
            encoded_parts = []
            for part in parts:
                try:
                    part.encode('ascii')
                    encoded_parts.append(part)
                except UnicodeEncodeError:
                    # 对非ASCII部分进行编码
                    encoded_part = urllib.parse.quote(part.encode('utf-8'))
                    encoded_parts.append(encoded_part)
            safe_name = '/'.join(encoded_parts)
        
        return safe_name
    
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
    
    def _download_videos(self, output_dir: str) -> Dict[str, Any]:
        """
        下载商品视频
        
        Args:
            output_dir: 输出目录
            
        Returns:
            Dict: 视频下载结果
        """
        result = {
            'success': False,
            'total_videos': 0,
            'downloaded_videos': 0,
            'skipped_videos': 0,
            'failed_videos': 0,
            'video_files': [],
            'thumbnail_files': [],
            'errors': []
        }
        
        try:
            # 获取所有视频
            videos = self.parser.get_videos()
            result['total_videos'] = len(videos)
            
            if not videos:
                self.log("未找到视频文件")
                result['success'] = True
                return result
            
            self.log(f"发现 {len(videos)} 个视频文件")
            
            # 创建视频下载目录
            video_dir = os.path.join(output_dir, "产品视频")
            
            # 下载视频
            video_results = self.video_downloader.download_videos_batch(
                videos, video_dir, ""
            )
            
            # 处理下载结果
            for video_result in video_results:
                if video_result['success']:
                    if video_result.get('skipped'):
                        result['skipped_videos'] += 1
                    else:
                        result['downloaded_videos'] += 1
                    result['video_files'].append(video_result['file_path'])
                else:
                    result['failed_videos'] += 1
                    result['errors'].append(video_result['error'])
            
            # 下载视频缩略图
            self.log("开始下载视频缩略图...")
            thumbnail_results = self.video_downloader.download_thumbnails(
                videos, video_dir, ""
            )
            
            # 处理缩略图下载结果
            for thumb_result in thumbnail_results:
                if thumb_result['success']:
                    result['thumbnail_files'].append(thumb_result['file_path'])
            
            self.log(f"视频下载完成: {result['downloaded_videos']}/{result['total_videos']} 成功")
            if result['skipped_videos'] > 0:
                self.log(f"跳过已存在视频: {result['skipped_videos']} 个")
            if result['failed_videos'] > 0:
                self.log(f"下载失败: {result['failed_videos']} 个")
            
            result['success'] = True
            
        except Exception as e:
            error_msg = f"视频下载失败: {str(e)}"
            self.log(error_msg)
            result['errors'].append(error_msg)
        
        return result
    
    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'downloader'):
            self.downloader.close()
        if hasattr(self, 'video_downloader'):
            self.video_downloader.close()