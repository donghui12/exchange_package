"""
视频下载器模块
用于下载拼多多商品视频
"""

import os
import requests
import time
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed


class VideoDownloader:
    """视频下载器"""
    
    def __init__(self, max_workers: int = 3, timeout: int = 30):
        """
        初始化视频下载器
        
        Args:
            max_workers: 最大并发下载数
            timeout: 下载超时时间（秒）
        """
        self.max_workers = max_workers
        self.timeout = timeout
        self.session = requests.Session()
        
        # 设置User-Agent，模拟浏览器请求
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        
    def _get_file_extension(self, url: str) -> str:
        """从URL获取文件扩展名"""
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        
        if '.mp4' in path:
            return '.mp4'
        elif '.avi' in path:
            return '.avi'
        elif '.mov' in path:
            return '.mov'
        elif '.wmv' in path:
            return '.wmv'
        else:
            return '.mp4'  # 默认使用mp4
    
    def _safe_filename(self, filename: str) -> str:
        """生成安全的文件名"""
        illegal_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\n', '\r', '\t']
        safe_name = filename
        
        for char in illegal_chars:
            safe_name = safe_name.replace(char, '_')
        
        # 限制文件名长度
        if len(safe_name) > 200:
            safe_name = safe_name[:200]
        
        return safe_name
    
    def download_video(self, video_info: Dict[str, Any], download_dir: str, 
                      prefix: str = "") -> Dict[str, Any]:
        """
        下载单个视频
        
        Args:
            video_info: 视频信息字典
            download_dir: 下载目录
            prefix: 文件名前缀
            
        Returns:
            Dict: 下载结果
        """
        url = video_info.get('url', '')
        if not url:
            return {
                'success': False,
                'error': '视频URL为空',
                'video_info': video_info
            }
        
        try:
            # 创建下载目录
            os.makedirs(download_dir, exist_ok=True)
            
            # 生成文件名
            ext = self._get_file_extension(url)
            video_type = video_info.get('video_type', 'video')
            priority = video_info.get('priority', 0)
            
            if prefix:
                filename = f"{prefix}_{video_type}_{priority}{ext}"
            else:
                filename = f"{video_type}_{priority}{ext}"
            
            filename = self._safe_filename(filename)
            file_path = os.path.join(download_dir, filename)
            
            # 如果文件已存在，跳过下载
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                if file_size > 0:
                    return {
                        'success': True,
                        'file_path': file_path,
                        'file_size': file_size,
                        'skipped': True,
                        'video_info': video_info
                    }
            
            # 下载视频
            print(f"正在下载视频: {filename}")
            
            response = self.session.get(url, timeout=self.timeout, stream=True)
            response.raise_for_status()
            
            # 获取文件大小
            content_length = response.headers.get('content-length')
            total_size = int(content_length) if content_length else 0
            
            # 写入文件
            downloaded_size = 0
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # 显示下载进度
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            print(f"\r下载进度: {progress:.1f}%", end='', flush=True)
            
            print()  # 换行
            
            # 验证文件大小
            actual_size = os.path.getsize(file_path)
            if actual_size == 0:
                os.remove(file_path)
                return {
                    'success': False,
                    'error': '下载的文件为空',
                    'video_info': video_info
                }
            
            return {
                'success': True,
                'file_path': file_path,
                'file_size': actual_size,
                'video_info': video_info
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'网络错误: {str(e)}',
                'video_info': video_info
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'下载失败: {str(e)}',
                'video_info': video_info
            }
    
    def download_videos_batch(self, videos: List[Dict[str, Any]], 
                             download_dir: str, prefix: str = "") -> List[Dict[str, Any]]:
        """
        批量下载视频
        
        Args:
            videos: 视频信息列表
            download_dir: 下载目录
            prefix: 文件名前缀
            
        Returns:
            List[Dict]: 下载结果列表
        """
        if not videos:
            return []
        
        print(f"开始批量下载 {len(videos)} 个视频...")
        
        results = []
        
        # 使用线程池并行下载
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交下载任务
            future_to_video = {
                executor.submit(self.download_video, video, download_dir, prefix): video 
                for video in videos
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_video):
                result = future.result()
                results.append(result)
                
                if result['success']:
                    if result.get('skipped'):
                        print(f"✓ 跳过已存在文件: {os.path.basename(result['file_path'])}")
                    else:
                        print(f"✓ 下载完成: {os.path.basename(result['file_path'])} ({result['file_size']} 字节)")
                else:
                    print(f"✗ 下载失败: {result['error']}")
        
        # 统计结果
        success_count = sum(1 for r in results if r['success'])
        print(f"\n下载完成: {success_count}/{len(videos)} 个视频成功下载")
        
        return results
    
    def download_thumbnails(self, videos: List[Dict[str, Any]], 
                           download_dir: str, prefix: str = "") -> List[Dict[str, Any]]:
        """
        下载视频缩略图
        
        Args:
            videos: 视频信息列表
            download_dir: 下载目录
            prefix: 文件名前缀
            
        Returns:
            List[Dict]: 下载结果列表
        """
        thumbnails = []
        
        for video in videos:
            thumbnail_url = video.get('thumbnail', '')
            if thumbnail_url:
                # 创建缩略图信息
                thumbnail_info = {
                    'url': thumbnail_url,
                    'video_type': f"{video.get('video_type', 'video')}_thumbnail",
                    'priority': video.get('priority', 0),
                    'width': video.get('width', 0),
                    'height': video.get('height', 0)
                }
                thumbnails.append(thumbnail_info)
        
        if not thumbnails:
            return []
        
        print(f"开始下载 {len(thumbnails)} 个视频缩略图...")
        
        # 创建缩略图下载目录
        thumbnail_dir = os.path.join(download_dir, "缩略图")
        
        results = []
        for thumbnail in thumbnails:
            try:
                # 生成文件名
                ext = '.jpeg' if 'jpeg' in thumbnail['url'] else '.jpg'
                video_type = thumbnail.get('video_type', 'thumbnail')
                priority = thumbnail.get('priority', 0)
                
                if prefix:
                    filename = f"{prefix}_{video_type}_{priority}{ext}"
                else:
                    filename = f"{video_type}_{priority}{ext}"
                
                filename = self._safe_filename(filename)
                
                # 下载缩略图
                result = self.download_video(thumbnail, thumbnail_dir, "")
                if result['success']:
                    # 重命名文件
                    old_path = result['file_path']
                    new_path = os.path.join(thumbnail_dir, filename)
                    if old_path != new_path:
                        os.rename(old_path, new_path)
                        result['file_path'] = new_path
                
                results.append(result)
                
            except Exception as e:
                results.append({
                    'success': False,
                    'error': f'缩略图下载失败: {str(e)}',
                    'video_info': thumbnail
                })
        
        return results
    
    def close(self):
        """关闭下载器"""
        if hasattr(self, 'session'):
            self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()