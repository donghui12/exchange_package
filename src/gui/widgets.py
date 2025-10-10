"""
自定义控件模块
提供GUI界面所需的自定义控件
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
from typing import Callable, Optional

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.config import Config

class PathSelectWidget(ttk.Frame):
    """路径选择控件"""
    
    def __init__(self, parent, label_text: str = "路径:", 
                 dialog_title: str = "选择路径", 
                 select_directory: bool = True,
                 width: int = 50,
                 on_path_changed: Optional[Callable] = None):
        """
        初始化路径选择控件
        
        Args:
            parent: 父控件
            label_text: 标签文本
            dialog_title: 对话框标题
            select_directory: 是否选择目录（False为选择文件）
            width: 输入框宽度
            on_path_changed: 路径改变时的回调函数
        """
        super().__init__(parent)
        
        self.dialog_title = dialog_title
        self.select_directory = select_directory
        self.on_path_changed = on_path_changed
        
        # 创建控件
        self.label = ttk.Label(self, text=label_text)
        self.label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.path_var = tk.StringVar()
        self.path_var.trace('w', self._on_var_changed)
        
        self.entry = ttk.Entry(self, textvariable=self.path_var, width=width)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.browse_button = ttk.Button(self, text="浏览", command=self._browse_path)
        self.browse_button.pack(side=tk.RIGHT)
    
    def _browse_path(self):
        """浏览路径"""
        if self.select_directory:
            path = filedialog.askdirectory(title=self.dialog_title)
        else:
            path = filedialog.askopenfilename(title=self.dialog_title)
        
        if path:
            self.set_path(path)
    
    def _on_var_changed(self, *args):
        """路径变量改变时的回调"""
        if self.on_path_changed:
            self.on_path_changed(self.get_path())
    
    def get_path(self) -> str:
        """获取当前路径"""
        return self.path_var.get().strip()
    
    def set_path(self, path: str):
        """设置路径"""
        self.path_var.set(path)
    
    def clear_path(self):
        """清空路径"""
        self.path_var.set("")
    
    def is_valid_path(self) -> bool:
        """检查路径是否有效"""
        path = self.get_path()
        if not path:
            return False
        
        if self.select_directory:
            return os.path.exists(path) and os.path.isdir(path)
        else:
            return os.path.exists(path) and os.path.isfile(path)


class ProgressWidget(ttk.Frame):
    """进度显示控件"""
    
    def __init__(self, parent, show_percentage: bool = True, show_text: bool = True):
        """
        初始化进度控件
        
        Args:
            parent: 父控件
            show_percentage: 是否显示百分比
            show_text: 是否显示进度文本
        """
        super().__init__(parent)
        
        self.show_percentage = show_percentage
        self.show_text = show_text
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progressbar = ttk.Progressbar(
            self, 
            variable=self.progress_var, 
            maximum=100, 
            mode='determinate'
        )
        self.progressbar.pack(fill=tk.X, pady=(0, 5))
        
        # 信息框架
        self.info_frame = ttk.Frame(self)
        self.info_frame.pack(fill=tk.X)
        
        # 百分比标签
        if show_percentage:
            self.percentage_var = tk.StringVar(value="0%")
            self.percentage_label = ttk.Label(
                self.info_frame, 
                textvariable=self.percentage_var,
                font=('Arial', 9, 'bold')
            )
            self.percentage_label.pack(side=tk.LEFT)
        
        # 进度文本标签
        if show_text:
            self.text_var = tk.StringVar(value="准备中...")
            self.text_label = ttk.Label(
                self.info_frame, 
                textvariable=self.text_var,
                font=('Arial', 9)
            )
            if show_percentage:
                self.text_label.pack(side=tk.LEFT, padx=(10, 0))
            else:
                self.text_label.pack(side=tk.LEFT)
    
    def set_progress(self, value: float, text: str = None):
        """
        设置进度
        
        Args:
            value: 进度值(0-100)
            text: 进度文本
        """
        value = max(0, min(100, value))
        self.progress_var.set(value)
        
        if self.show_percentage:
            self.percentage_var.set(f"{value:.1f}%")
        
        if text is not None and self.show_text:
            self.text_var.set(text)
    
    def reset(self):
        """重置进度"""
        self.set_progress(0, "准备中...")
    
    def set_indeterminate(self, active: bool = True):
        """设置为不定进度模式"""
        if active:
            self.progressbar.config(mode='indeterminate')
            self.progressbar.start(10)
            if self.show_percentage:
                self.percentage_var.set("...")
        else:
            self.progressbar.stop()
            self.progressbar.config(mode='determinate')


class LogWidget(tk.Frame):
    """日志显示控件"""
    
    def __init__(self, parent, height: int = 15, width: int = 80):
        """
        初始化日志控件
        
        Args:
            parent: 父控件
            height: 显示行数
            width: 显示宽度
        """
        super().__init__(parent)
        
        # 创建滚动条
        self.scrollbar = ttk.Scrollbar(self)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建文本框
        self.text = tk.Text(
            self,
            height=height,
            width=width,
            wrap=tk.WORD,
            yscrollcommand=self.scrollbar.set,
            font=('Consolas', 9),
            bg='#f8f8f8',
            fg='#333333'
        )
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 配置滚动条
        self.scrollbar.config(command=self.text.yview)
        
        # 配置文本标签样式
        self.text.tag_configure('INFO', foreground='#333333')
        self.text.tag_configure('WARNING', foreground='#FF8C00')
        self.text.tag_configure('ERROR', foreground='#DC143C')
        self.text.tag_configure('SUCCESS', foreground='#228B22')
        self.text.tag_configure('DEBUG', foreground='#808080')
        
        # 禁用编辑
        self.text.config(state=tk.DISABLED)
    
    def append_log(self, message: str, level: str = 'INFO'):
        """
        添加日志消息
        
        Args:
            message: 日志消息
            level: 日志级别
        """
        self.text.config(state=tk.NORMAL)
        
        # 添加消息
        if not message.endswith('\n'):
            message += '\n'
        
        self.text.insert(tk.END, message, level.upper())
        
        # 自动滚动到底部
        self.text.see(tk.END)
        
        self.text.config(state=tk.DISABLED)
        
        # 更新界面
        self.update_idletasks()
    
    def clear_log(self):
        """清空日志"""
        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        self.text.config(state=tk.DISABLED)
    
    def get_log_text(self) -> str:
        """获取所有日志文本"""
        return self.text.get(1.0, tk.END)
    
    def save_log(self, file_path: str = None) -> bool:
        """
        保存日志到文件
        
        Args:
            file_path: 文件路径，如果为None则弹出保存对话框
            
        Returns:
            bool: 保存是否成功
        """
        if file_path is None:
            file_path = filedialog.asksaveasfilename(
                title="保存日志文件",
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
            )
        
        if not file_path:
            return False
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.get_log_text())
            return True
        except Exception:
            messagebox.showerror("错误", "保存日志文件失败")
            return False


class SettingsFrame(ttk.LabelFrame):
    """设置面板控件"""
    
    def __init__(self, parent, title: str = "设置"):
        """
        初始化设置面板
        
        Args:
            parent: 父控件
            title: 面板标题
        """
        super().__init__(parent, text=title, padding=10)
        
        # 创建变量
        self.interval_var = tk.IntVar(value=3)
        self.format_var = tk.IntVar(value=2)
        self.zip_var = tk.BooleanVar(value=True)
        
        # 创建控件
        self._create_widgets()
    
    def _create_widgets(self):
        """创建控件"""
        # 输出间隔设置
        interval_frame = ttk.Frame(self)
        interval_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(interval_frame, text="输出间隔时间(秒):").pack(side=tk.LEFT)
        
        interval_spinbox = ttk.Spinbox(
            interval_frame,
            from_=0,
            to=60,
            width=10,
            textvariable=self.interval_var
        )
        interval_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Label(interval_frame, text="(转换完成后等待时间)").pack(side=tk.LEFT, padx=(5, 0))
        
        # 导出格式设置
        format_frame = ttk.LabelFrame(self, text="导出格式", padding=5)
        format_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Radiobutton(
            format_frame,
            text="格式1 (主图/SKU图/详情图/主图视频)",
            variable=self.format_var,
            value=1
        ).pack(anchor=tk.W)
        
        ttk.Radiobutton(
            format_frame,
            text="格式2 (产品主图/SKU图/详情图/产品视频)",
            variable=self.format_var,
            value=2
        ).pack(anchor=tk.W)
        
        # ZIP压缩设置
        zip_frame = ttk.Frame(self)
        zip_frame.pack(fill=tk.X)
        
        zip_checkbox = ttk.Checkbutton(
            zip_frame,
            text="创建zip压缩包",
            variable=self.zip_var
        )
        zip_checkbox.pack(side=tk.LEFT)
        
        ttk.Label(zip_frame, text="(将转换后的素材包打包成zip文件)").pack(side=tk.LEFT, padx=(5, 0))
    
    def get_settings(self) -> dict:
        """获取当前设置"""
        return {
            'interval': self.interval_var.get(),
            'format': self.format_var.get(),
            'create_zip': self.zip_var.get()
        }
    
    def set_settings(self, settings: dict):
        """设置配置"""
        self.interval_var.set(settings.get('interval', 3))
        self.format_var.set(settings.get('format', 2))
        self.zip_var.set(settings.get('create_zip', False))