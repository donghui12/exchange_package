"""
文件操作工具模块
提供文件和目录操作的工具函数
"""
import os
import shutil
import zipfile
import tempfile
from typing import List, Optional
from pathlib import Path

class FileUtils:
    """文件操作工具类"""
    
    @staticmethod
    def ensure_directory(path: str) -> bool:
        """
        确保目录存在，如果不存在则创建
        
        Args:
            path: 目录路径
            
        Returns:
            bool: 操作是否成功
        """
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception:
            return False
    
    @staticmethod
    def clean_filename(filename: str) -> str:
        """
        清理文件名中的非法字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            str: 清理后的文件名
        """
        # Windows文件系统中的非法字符
        illegal_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        
        clean_name = filename
        for char in illegal_chars:
            clean_name = clean_name.replace(char, '_')
        
        # 去除开头结尾的空格和点
        clean_name = clean_name.strip(' .')
        
        # 限制长度
        if len(clean_name) > 200:
            clean_name = clean_name[:200]
        
        return clean_name
    
    @staticmethod
    def get_safe_path(base_dir: str, filename: str) -> str:
        """
        获取安全的文件路径，避免路径遍历攻击
        
        Args:
            base_dir: 基础目录
            filename: 文件名
            
        Returns:
            str: 安全的文件路径
        """
        # 清理文件名
        safe_filename = FileUtils.clean_filename(filename)
        
        # 构建完整路径
        full_path = os.path.join(base_dir, safe_filename)
        
        # 确保路径在基础目录内
        base_dir = os.path.abspath(base_dir)
        full_path = os.path.abspath(full_path)
        
        if not full_path.startswith(base_dir):
            raise ValueError("文件路径不安全")
        
        return full_path
    
    @staticmethod
    def copy_file(src: str, dst: str) -> bool:
        """
        复制文件
        
        Args:
            src: 源文件路径
            dst: 目标文件路径
            
        Returns:
            bool: 复制是否成功
        """
        try:
            # 确保目标目录存在
            dst_dir = os.path.dirname(dst)
            FileUtils.ensure_directory(dst_dir)
            
            shutil.copy2(src, dst)
            return True
        except Exception:
            return False
    
    @staticmethod
    def move_file(src: str, dst: str) -> bool:
        """
        移动文件
        
        Args:
            src: 源文件路径
            dst: 目标文件路径
            
        Returns:
            bool: 移动是否成功
        """
        try:
            # 确保目标目录存在
            dst_dir = os.path.dirname(dst)
            FileUtils.ensure_directory(dst_dir)
            
            shutil.move(src, dst)
            return True
        except Exception:
            return False
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """
        删除文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 删除是否成功
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception:
            return False
    
    @staticmethod
    def delete_directory(dir_path: str) -> bool:
        """
        删除目录及其内容
        
        Args:
            dir_path: 目录路径
            
        Returns:
            bool: 删除是否成功
        """
        try:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """
        获取文件大小（字节）
        
        Args:
            file_path: 文件路径
            
        Returns:
            int: 文件大小，如果文件不存在返回-1
        """
        try:
            return os.path.getsize(file_path)
        except Exception:
            return -1
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        格式化文件大小为可读字符串
        
        Args:
            size_bytes: 文件大小（字节）
            
        Returns:
            str: 格式化的文件大小
        """
        if size_bytes < 0:
            return "未知"
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        size = float(size_bytes)
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        if unit_index == 0:
            return f"{int(size)} {units[unit_index]}"
        else:
            return f"{size:.2f} {units[unit_index]}"
    
    @staticmethod
    def list_files(directory: str, pattern: str = "*", recursive: bool = False) -> List[str]:
        """
        列出目录中的文件
        
        Args:
            directory: 目录路径
            pattern: 文件模式匹配
            recursive: 是否递归搜索
            
        Returns:
            List[str]: 文件路径列表
        """
        try:
            path = Path(directory)
            if not path.exists() or not path.is_dir():
                return []
            
            if recursive:
                files = list(path.rglob(pattern))
            else:
                files = list(path.glob(pattern))
            
            # 只返回文件，不包含目录
            return [str(f) for f in files if f.is_file()]
        except Exception:
            return []
    
    @staticmethod
    def create_zip_archive(source_dir: str, zip_path: str, exclude_patterns: List[str] = None) -> bool:
        """
        创建ZIP压缩包
        
        Args:
            source_dir: 源目录
            zip_path: ZIP文件路径
            exclude_patterns: 排除的文件模式列表
            
        Returns:
            bool: 创建是否成功
        """
        try:
            exclude_patterns = exclude_patterns or []
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        
                        # 检查是否需要排除
                        should_exclude = False
                        for pattern in exclude_patterns:
                            if pattern in file_path:
                                should_exclude = True
                                break
                        
                        if not should_exclude:
                            arc_name = os.path.relpath(file_path, source_dir)
                            zipf.write(file_path, arc_name)
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def extract_zip_archive(zip_path: str, extract_dir: str) -> bool:
        """
        解压ZIP压缩包
        
        Args:
            zip_path: ZIP文件路径
            extract_dir: 解压目录
            
        Returns:
            bool: 解压是否成功
        """
        try:
            FileUtils.ensure_directory(extract_dir)
            
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(extract_dir)
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_temp_directory() -> str:
        """
        获取临时目录路径
        
        Returns:
            str: 临时目录路径
        """
        return tempfile.gettempdir()
    
    @staticmethod
    def create_temp_file(suffix: str = "", prefix: str = "temp_") -> str:
        """
        创建临时文件
        
        Args:
            suffix: 文件后缀
            prefix: 文件前缀
            
        Returns:
            str: 临时文件路径
        """
        fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
        os.close(fd)  # 关闭文件描述符
        return temp_path
    
    @staticmethod
    def is_valid_directory(path: str) -> bool:
        """
        检查路径是否为有效目录
        
        Args:
            path: 目录路径
            
        Returns:
            bool: 是否为有效目录
        """
        return os.path.exists(path) and os.path.isdir(path)
    
    @staticmethod
    def is_valid_file(path: str) -> bool:
        """
        检查路径是否为有效文件
        
        Args:
            path: 文件路径
            
        Returns:
            bool: 是否为有效文件
        """
        return os.path.exists(path) and os.path.isfile(path)
    
    @staticmethod
    def get_directory_size(directory: str) -> int:
        """
        获取目录总大小（字节）
        
        Args:
            directory: 目录路径
            
        Returns:
            int: 目录大小，如果目录不存在返回-1
        """
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
            return total_size
        except Exception:
            return -1