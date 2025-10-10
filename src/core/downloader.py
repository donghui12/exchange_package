"""
图片下载模块
支持多线程下载和重试机制
"""
import os
import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Callable, Optional
from urllib.parse import urlparse

from src.config import Config

class ImageDownloader:
    """图片下载器"""
    
    def __init__(self, max_workers: int = 5, progress_callback: Optional[Callable] = None):
        """
        初始化下载器
        
        Args:
            max_workers: 最大并发数
            progress_callback: 进度回调函数
        """
        self.max_workers = max_workers
        self.progress_callback = progress_callback
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': Config.DOWNLOAD_CONFIG['user_agent']
        })
        self._lock = threading.Lock()
        
    def download_single_image(self, url: str, save_path: str, filename: str = None) -> bool:
        """
        下载单张图片
        
        Args:
            url: 图片URL
            save_path: 保存路径
            filename: 文件名（可选）
            
        Returns:
            bool: 下载是否成功
        """
        try:
            # 确保保存目录存在
            os.makedirs(save_path, exist_ok=True)
            
            # 生成文件名
            if not filename:
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                if not filename or '.' not in filename:
                    filename = f"image_{int(time.time())}.jpg"
            
            file_path = os.path.join(save_path, filename)
            
            # 如果文件已存在且大小合理，跳过下载
            if os.path.exists(file_path) and os.path.getsize(file_path) > 1024:
                if self.progress_callback:
                    self.progress_callback(f"跳过已存在的文件: {filename}")
                return True
            
            # 下载图片
            response = self.session.get(
                url,
                timeout=Config.DOWNLOAD_CONFIG['timeout'],
                stream=True
            )
            response.raise_for_status()
            
            # 保存文件
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=Config.DOWNLOAD_CONFIG['chunk_size']):
                    if chunk:
                        f.write(chunk)
            
            # 验证文件大小
            if os.path.getsize(file_path) < 1024:
                os.remove(file_path)
                raise Exception("下载的文件太小，可能损坏")
            
            if self.progress_callback:
                self.progress_callback(f"下载完成: {filename}")
            
            return True
            
        except Exception as e:
            if self.progress_callback:
                self.progress_callback(f"下载失败 {filename}: {str(e)}")
            return False
    
    def download_with_retry(self, url: str, save_path: str, filename: str, max_retries: int = None) -> bool:
        """
        带重试的下载
        
        Args:
            url: 图片URL
            save_path: 保存路径
            filename: 文件名
            max_retries: 最大重试次数
            
        Returns:
            bool: 下载是否成功
        """
        if max_retries is None:
            max_retries = Config.DOWNLOAD_CONFIG['max_retries']
        
        for attempt in range(max_retries + 1):
            if attempt > 0:
                wait_time = 2 ** attempt  # 指数退避
                if self.progress_callback:
                    self.progress_callback(f"等待 {wait_time} 秒后重试下载: {filename}")
                time.sleep(wait_time)
            
            if self.download_single_image(url, save_path, filename):
                return True
                
            if self.progress_callback and attempt < max_retries:
                self.progress_callback(f"第 {attempt + 1} 次下载失败，准备重试: {filename}")
        
        return False
    
    def download_main_images(self, images: List[Dict], save_path: str) -> Dict[str, any]:
        """
        下载主图
        
        Args:
            images: 主图信息列表
            save_path: 保存路径
            
        Returns:
            Dict: 下载结果统计
        """
        results = {'success': 0, 'failed': 0, 'total': len(images)}
        
        if self.progress_callback:
            self.progress_callback(f"开始下载 {len(images)} 张主图...")
        
        def download_task(img_info, index):
            url = img_info.get('url', '')
            filename = f"{Config.FILE_NAMING['main_image_prefix']}{index}.jpg"
            
            success = self.download_with_retry(url, save_path, filename)
            with self._lock:
                if success:
                    results['success'] += 1
                else:
                    results['failed'] += 1
            return success
        
        # 并发下载
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(download_task, img, i + 1) 
                for i, img in enumerate(images)
            ]
            
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    if self.progress_callback:
                        self.progress_callback(f"下载任务异常: {str(e)}")
        
        if self.progress_callback:
            self.progress_callback(f"主图下载完成: 成功 {results['success']}, 失败 {results['failed']}")
        
        return results
    
    def download_detail_images(self, images: List[Dict], save_path: str) -> Dict[str, any]:
        """
        下载详情图
        
        Args:
            images: 详情图信息列表
            save_path: 保存路径
            
        Returns:
            Dict: 下载结果统计
        """
        results = {'success': 0, 'failed': 0, 'total': len(images)}
        
        if self.progress_callback:
            self.progress_callback(f"开始下载 {len(images)} 张详情图...")
        
        def download_task(img_info, index):
            url = img_info.get('url', '')
            filename = f"{Config.FILE_NAMING['detail_image_prefix']}{index}.jpg"
            
            success = self.download_with_retry(url, save_path, filename)
            with self._lock:
                if success:
                    results['success'] += 1
                else:
                    results['failed'] += 1
            return success
        
        # 并发下载
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(download_task, img, i + 1) 
                for i, img in enumerate(images)
            ]
            
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    if self.progress_callback:
                        self.progress_callback(f"下载任务异常: {str(e)}")
        
        if self.progress_callback:
            self.progress_callback(f"详情图下载完成: 成功 {results['success']}, 失败 {results['failed']}")
        
        return results
    
    def download_sku_images(self, images: List[Dict], save_path: str) -> Dict[str, any]:
        """
        下载SKU图
        
        Args:
            images: SKU图信息列表
            save_path: 保存路径
            
        Returns:
            Dict: 下载结果统计
        """
        results = {'success': 0, 'failed': 0, 'total': len(images)}
        
        if self.progress_callback:
            self.progress_callback(f"开始下载 {len(images)} 张SKU图...")
        
        def download_task(img_info):
            url = img_info.get('url', '')
            spec = img_info.get('spec', f"SKU{img_info.get('index', 1)}")
            index = img_info.get('index', 1)
            
            # 清理规格名称用于文件名
            clean_spec = spec.replace('/', '_').replace('\\', '_')
            filename = f"{clean_spec}_{index}.jpg"
            
            success = self.download_with_retry(url, save_path, filename)
            with self._lock:
                if success:
                    results['success'] += 1
                else:
                    results['failed'] += 1
            return success
        
        # 并发下载
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(download_task, img) for img in images]
            
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    if self.progress_callback:
                        self.progress_callback(f"下载任务异常: {str(e)}")
        
        if self.progress_callback:
            self.progress_callback(f"SKU图下载完成: 成功 {results['success']}, 失败 {results['failed']}")
        
        return results
    
    def download_all_images(self, parser, output_dir: str, export_format: int = 2) -> Dict[str, any]:
        """
        下载所有图片
        
        Args:
            parser: 数据解析器实例
            output_dir: 输出目录
            export_format: 导出格式(1或2)
            
        Returns:
            Dict: 下载结果统计
        """
        folder_config = Config.FOLDER_NAMES[f'format{export_format}']
        
        # 获取图片数据
        main_images = parser.get_main_images()
        detail_images = parser.get_detail_images()
        sku_images = parser.get_sku_images()
        
        # 创建文件夹路径
        main_images_dir = os.path.join(output_dir, folder_config['main_images'])
        detail_images_dir = os.path.join(output_dir, folder_config['detail_images'])
        sku_images_dir = os.path.join(output_dir, folder_config['sku_images'])
        videos_dir = os.path.join(output_dir, folder_config['videos'])
        
        # 创建目录
        for directory in [main_images_dir, detail_images_dir, sku_images_dir, videos_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # 下载图片
        main_results = self.download_main_images(main_images, main_images_dir)
        detail_results = self.download_detail_images(detail_images, detail_images_dir)
        sku_results = self.download_sku_images(sku_images, sku_images_dir)
        
        # 汇总结果
        total_results = {
            'main_images': main_results,
            'detail_images': detail_results,
            'sku_images': sku_results,
            'total_success': main_results['success'] + detail_results['success'] + sku_results['success'],
            'total_failed': main_results['failed'] + detail_results['failed'] + sku_results['failed'],
            'total_images': main_results['total'] + detail_results['total'] + sku_results['total']
        }
        
        if self.progress_callback:
            self.progress_callback(
                f"所有图片下载完成! 总计: {total_results['total_images']}, "
                f"成功: {total_results['total_success']}, "
                f"失败: {total_results['total_failed']}"
            )
        
        return total_results
    
    def close(self):
        """关闭下载器"""
        if hasattr(self, 'session'):
            self.session.close()