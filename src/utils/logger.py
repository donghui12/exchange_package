"""
日志工具模块
提供统一的日志记录功能
"""
import os
import logging
import threading
from datetime import datetime
from typing import Callable, Optional, List
from logging.handlers import RotatingFileHandler

class Logger:
    """日志记录器类"""
    
    def __init__(self, name: str = "MaterialConverter", log_dir: str = None):
        """
        初始化日志记录器
        
        Args:
            name: 日志记录器名称
            log_dir: 日志文件目录
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            self._setup_handlers(log_dir)
        
        self._callbacks = []
        self._lock = threading.Lock()
    
    def _setup_handlers(self, log_dir: str = None):
        """设置日志处理器"""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器
        if log_dir:
            try:
                os.makedirs(log_dir, exist_ok=True)
                log_file = os.path.join(log_dir, f"{self.name}.log")
                
                file_handler = RotatingFileHandler(
                    log_file,
                    maxBytes=10*1024*1024,  # 10MB
                    backupCount=5,
                    encoding='utf-8'
                )
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
                
            except Exception as e:
                self.logger.warning(f"无法创建文件日志处理器: {e}")
    
    def add_callback(self, callback: Callable[[str, str], None]):
        """
        添加日志回调函数
        
        Args:
            callback: 回调函数，参数为(level, message)
        """
        with self._lock:
            self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[str, str], None]):
        """
        移除日志回调函数
        
        Args:
            callback: 要移除的回调函数
        """
        with self._lock:
            if callback in self._callbacks:
                self._callbacks.remove(callback)
    
    def _notify_callbacks(self, level: str, message: str):
        """通知所有回调函数"""
        with self._lock:
            for callback in self._callbacks:
                try:
                    callback(level, message)
                except Exception:
                    pass  # 忽略回调函数中的异常
    
    def debug(self, message: str):
        """记录调试信息"""
        self.logger.debug(message)
        self._notify_callbacks('DEBUG', message)
    
    def info(self, message: str):
        """记录一般信息"""
        self.logger.info(message)
        self._notify_callbacks('INFO', message)
    
    def warning(self, message: str):
        """记录警告信息"""
        self.logger.warning(message)
        self._notify_callbacks('WARNING', message)
    
    def error(self, message: str):
        """记录错误信息"""
        self.logger.error(message)
        self._notify_callbacks('ERROR', message)
    
    def critical(self, message: str):
        """记录严重错误信息"""
        self.logger.critical(message)
        self._notify_callbacks('CRITICAL', message)
    
    def exception(self, message: str):
        """记录异常信息（包含堆栈跟踪）"""
        self.logger.exception(message)
        self._notify_callbacks('ERROR', message)


class ProgressLogger:
    """进度日志记录器"""
    
    def __init__(self, logger: Logger = None):
        """
        初始化进度日志记录器
        
        Args:
            logger: 基础日志记录器
        """
        self.logger = logger or Logger()
        self._progress_callbacks = []
        self._lock = threading.Lock()
    
    def add_progress_callback(self, callback: Callable[[int, str], None]):
        """
        添加进度回调函数
        
        Args:
            callback: 回调函数，参数为(progress_percent, message)
        """
        with self._lock:
            self._progress_callbacks.append(callback)
    
    def remove_progress_callback(self, callback: Callable[[int, str], None]):
        """
        移除进度回调函数
        
        Args:
            callback: 要移除的回调函数
        """
        with self._lock:
            if callback in self._progress_callbacks:
                self._progress_callbacks.remove(callback)
    
    def log_progress(self, progress: int, message: str, level: str = 'INFO'):
        """
        记录进度信息
        
        Args:
            progress: 进度百分比(0-100)
            message: 进度消息
            level: 日志级别
        """
        progress = max(0, min(100, progress))  # 确保进度在0-100之间
        
        log_message = f"[{progress}%] {message}"
        
        # 记录到日志
        if level.upper() == 'DEBUG':
            self.logger.debug(log_message)
        elif level.upper() == 'INFO':
            self.logger.info(log_message)
        elif level.upper() == 'WARNING':
            self.logger.warning(log_message)
        elif level.upper() == 'ERROR':
            self.logger.error(log_message)
        else:
            self.logger.info(log_message)
        
        # 通知进度回调
        with self._lock:
            for callback in self._progress_callbacks:
                try:
                    callback(progress, message)
                except Exception:
                    pass


class UILogger:
    """UI日志记录器，专门用于GUI界面的日志显示"""
    
    def __init__(self, max_lines: int = 1000):
        """
        初始化UI日志记录器
        
        Args:
            max_lines: 最大保存的日志行数
        """
        self.max_lines = max_lines
        self._log_lines = []
        self._callbacks = []
        self._lock = threading.Lock()
    
    def add_callback(self, callback: Callable[[str], None]):
        """
        添加UI更新回调函数
        
        Args:
            callback: 回调函数，参数为新的日志消息
        """
        with self._lock:
            self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[str], None]):
        """
        移除UI更新回调函数
        
        Args:
            callback: 要移除的回调函数
        """
        with self._lock:
            if callback in self._callbacks:
                self._callbacks.remove(callback)
    
    def log(self, message: str, timestamp: bool = True):
        """
        添加日志消息
        
        Args:
            message: 日志消息
            timestamp: 是否添加时间戳
        """
        if timestamp:
            timestamp_str = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp_str}] {message}"
        else:
            formatted_message = message
        
        with self._lock:
            self._log_lines.append(formatted_message)
            
            # 限制日志行数
            if len(self._log_lines) > self.max_lines:
                self._log_lines = self._log_lines[-self.max_lines:]
            
            # 通知UI更新
            for callback in self._callbacks:
                try:
                    callback(formatted_message)
                except Exception:
                    pass
    
    def get_all_logs(self) -> List[str]:
        """
        获取所有日志行
        
        Returns:
            List[str]: 所有日志行
        """
        with self._lock:
            return self._log_lines.copy()
    
    def clear(self):
        """清空日志"""
        with self._lock:
            self._log_lines.clear()
            
            # 通知UI清空
            for callback in self._callbacks:
                try:
                    callback("")  # 空消息表示清空
                except Exception:
                    pass
    
    def get_log_text(self, separator: str = "\n") -> str:
        """
        获取所有日志的文本形式
        
        Args:
            separator: 行分隔符
            
        Returns:
            str: 日志文本
        """
        with self._lock:
            return separator.join(self._log_lines)
    
    def save_to_file(self, file_path: str) -> bool:
        """
        保存日志到文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 保存是否成功
        """
        try:
            with self._lock:
                log_text = self.get_log_text()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(log_text)
            
            return True
        except Exception:
            return False


# 全局日志实例
_global_logger = None
_global_ui_logger = None

def get_logger(name: str = "MaterialConverter", log_dir: str = None) -> Logger:
    """
    获取全局日志记录器实例
    
    Args:
        name: 日志记录器名称
        log_dir: 日志文件目录
        
    Returns:
        Logger: 日志记录器实例
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = Logger(name, log_dir)
    return _global_logger

def get_ui_logger(max_lines: int = 1000) -> UILogger:
    """
    获取全局UI日志记录器实例
    
    Args:
        max_lines: 最大保存的日志行数
        
    Returns:
        UILogger: UI日志记录器实例
    """
    global _global_ui_logger
    if _global_ui_logger is None:
        _global_ui_logger = UILogger(max_lines)
    return _global_ui_logger