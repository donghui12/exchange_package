"""
对话框组件模块
提供各种对话框组件
"""
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.config import Config

class SettingsDialog:
    """设置对话框"""
    
    def __init__(self, parent, current_settings: dict = None):
        """
        初始化设置对话框
        
        Args:
            parent: 父窗口
            current_settings: 当前设置
        """
        self.parent = parent
        self.result = None
        self.current_settings = current_settings or {}
        
        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("设置")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self._center_window()
        
        # 创建界面
        self._create_widgets()
        
        # 加载当前设置
        self._load_settings()
    
    def _center_window(self):
        """窗口居中"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (300 // 2)
        self.dialog.geometry(f"400x300+{x}+{y}")
    
    def _create_widgets(self):
        """创建控件"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 下载设置
        download_frame = ttk.LabelFrame(main_frame, text="下载设置", padding=10)
        download_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 最大并发数
        ttk.Label(download_frame, text="最大并发下载数:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.max_workers_var = tk.IntVar(value=5)
        max_workers_spinbox = ttk.Spinbox(
            download_frame,
            from_=1,
            to=20,
            width=10,
            textvariable=self.max_workers_var
        )
        max_workers_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # 下载超时
        ttk.Label(download_frame, text="下载超时时间(秒):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.timeout_var = tk.IntVar(value=30)
        timeout_spinbox = ttk.Spinbox(
            download_frame,
            from_=10,
            to=120,
            width=10,
            textvariable=self.timeout_var
        )
        timeout_spinbox.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # 重试次数
        ttk.Label(download_frame, text="最大重试次数:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.max_retries_var = tk.IntVar(value=3)
        retries_spinbox = ttk.Spinbox(
            download_frame,
            from_=0,
            to=10,
            width=10,
            textvariable=self.max_retries_var
        )
        retries_spinbox.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 按钮
        ttk.Button(
            button_frame,
            text="确定",
            command=self._on_ok,
            width=12
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text="取消",
            command=self._on_cancel,
            width=12
        ).pack(side=tk.RIGHT)
        
        ttk.Button(
            button_frame,
            text="恢复默认",
            command=self._on_reset,
            width=12
        ).pack(side=tk.LEFT)
    
    def _load_settings(self):
        """加载当前设置"""
        self.max_workers_var.set(self.current_settings.get('max_workers', 5))
        self.timeout_var.set(self.current_settings.get('timeout', 30))
        self.max_retries_var.set(self.current_settings.get('max_retries', 3))
    
    def _on_reset(self):
        """恢复默认设置"""
        self.max_workers_var.set(5)
        self.timeout_var.set(30)
        self.max_retries_var.set(3)
    
    def _on_ok(self):
        """确定按钮"""
        self.result = {
            'max_workers': self.max_workers_var.get(),
            'timeout': self.timeout_var.get(),
            'max_retries': self.max_retries_var.get()
        }
        self.dialog.destroy()
    
    def _on_cancel(self):
        """取消按钮"""
        self.result = None
        self.dialog.destroy()
    
    def show(self) -> dict:
        """显示对话框并返回结果"""
        self.parent.wait_window(self.dialog)
        return self.result


class AboutDialog:
    """关于对话框"""
    
    def __init__(self, parent):
        """
        初始化关于对话框
        
        Args:
            parent: 父窗口
        """
        self.parent = parent
        
        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("关于")
        self.dialog.geometry("450x350")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self._center_window()
        
        # 创建界面
        self._create_widgets()
    
    def _center_window(self):
        """窗口居中"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (350 // 2)
        self.dialog.geometry(f"450x350+{x}+{y}")
    
    def _create_widgets(self):
        """创建控件"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 应用图标和标题
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        app_title = ttk.Label(
            title_frame,
            text=Config.APP_NAME,
            font=('Arial', 16, 'bold')
        )
        app_title.pack()
        
        version_label = ttk.Label(
            title_frame,
            text=f"版本 {Config.APP_VERSION}",
            font=('Arial', 10)
        )
        version_label.pack(pady=(5, 0))
        
        # 分隔线
        separator = ttk.Separator(main_frame, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, pady=(0, 15))
        
        # 描述信息
        description = (
            "一个用于将拼多多商品导出数据转换为标准素材包格式的桌面应用工具。\n\n"
            "主要功能:\n"
            "• 自动解析PDD商品JSON数据\n"
            "• 智能下载并分类存储商品图片\n"
            "• 生成Excel导入模板\n"
            "• 支持多种输出格式\n"
            "• 可选ZIP压缩打包\n\n"
            "技术支持: Python + tkinter\n"
            f"作者: {Config.APP_AUTHOR}"
        )
        
        desc_label = ttk.Label(
            main_frame,
            text=description,
            font=('Arial', 9),
            justify=tk.LEFT
        )
        desc_label.pack(fill=tk.X, pady=(0, 20))
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="确定",
            command=self.dialog.destroy,
            width=12
        ).pack(side=tk.RIGHT)
    
    def show(self):
        """显示对话框"""
        self.parent.wait_window(self.dialog)


class ErrorDialog:
    """错误提示对话框"""
    
    @staticmethod
    def show_error(parent, title: str = "错误", message: str = "", details: str = None):
        """
        显示错误对话框
        
        Args:
            parent: 父窗口
            title: 标题
            message: 错误消息
            details: 详细信息
        """
        if details:
            # 创建自定义对话框显示详细信息
            dialog = tk.Toplevel(parent)
            dialog.title(title)
            dialog.geometry("500x400")
            dialog.transient(parent)
            dialog.grab_set()
            
            # 居中显示
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
            y = (dialog.winfo_screenheight() // 2) - (400 // 2)
            dialog.geometry(f"500x400+{x}+{y}")
            
            main_frame = ttk.Frame(dialog, padding=10)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 错误消息
            msg_label = ttk.Label(
                main_frame,
                text=message,
                font=('Arial', 10, 'bold'),
                foreground='red'
            )
            msg_label.pack(anchor=tk.W, pady=(0, 10))
            
            # 详细信息
            ttk.Label(main_frame, text="详细信息:", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
            
            details_text = tk.Text(
                main_frame,
                wrap=tk.WORD,
                font=('Consolas', 9),
                bg='#f8f8f8'
            )
            details_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
            details_text.insert(tk.END, details)
            details_text.config(state=tk.DISABLED)
            
            # 按钮
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X)
            
            ttk.Button(
                button_frame,
                text="确定",
                command=dialog.destroy,
                width=12
            ).pack(side=tk.RIGHT)
            
        else:
            # 使用标准错误对话框
            messagebox.showerror(title, message, parent=parent)
    
    @staticmethod
    def show_warning(parent, title: str = "警告", message: str = ""):
        """
        显示警告对话框
        
        Args:
            parent: 父窗口
            title: 标题
            message: 警告消息
        """
        messagebox.showwarning(title, message, parent=parent)
    
    @staticmethod
    def show_info(parent, title: str = "信息", message: str = ""):
        """
        显示信息对话框
        
        Args:
            parent: 父窗口
            title: 标题
            message: 信息
        """
        messagebox.showinfo(title, message, parent=parent)
    
    @staticmethod
    def ask_yes_no(parent, title: str = "确认", message: str = "") -> bool:
        """
        显示确认对话框
        
        Args:
            parent: 父窗口
            title: 标题
            message: 消息
            
        Returns:
            bool: 用户选择是否为是
        """
        return messagebox.askyesno(title, message, parent=parent)