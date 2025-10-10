"""
授权验证界面模块
实现软件激活和授权管理的GUI界面
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import os
from typing import Optional

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.utils.license_manager import LicenseManager
from src.config import Config

class LicenseDialog:
    """授权验证对话框"""
    
    def __init__(self, parent=None):
        """
        初始化授权对话框
        
        Args:
            parent: 父窗口
        """
        self.parent = parent
        self.result = False
        self.license_manager = LicenseManager()
        
        # 创建对话框窗口
        self.root = tk.Tk() if parent is None else tk.Toplevel(parent)
        self.root.title(f"{Config.APP_NAME} - 软件激活")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        if parent:
            self.root.transient(parent)
            self.root.grab_set()
        
        # 设置窗口图标和样式
        self._setup_window()
        
        # 创建界面
        self._create_widgets()
        
        # 居中显示
        self._center_window()
        
        # 检查现有授权
        self._check_existing_license()
    
    def _setup_window(self):
        """设置窗口样式"""
        # 禁用关闭按钮（强制用户进行激活）
        self.root.protocol("WM_DELETE_WINDOW", self._on_close_attempt)
        
        # 设置焦点
        self.root.focus_set()
    
    def _center_window(self):
        """窗口居中"""
        self.root.update_idletasks()
        width = 500
        height = 400
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_widgets(self):
        """创建界面控件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题区域
        self._create_title_section(main_frame)
        
        # 电脑码显示区域
        self._create_machine_code_section(main_frame)
        
        # 授权码输入区域
        self._create_license_key_section(main_frame)
        
        # 状态显示区域
        self._create_status_section(main_frame)
        
        # 按钮区域
        self._create_button_section(main_frame)
    
    def _create_title_section(self, parent):
        """创建标题区域"""
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 软件名称
        title_label = ttk.Label(
            title_frame,
            text=Config.APP_NAME,
            font=('Arial', 16, 'bold'),
            foreground='#2E86AB'
        )
        title_label.pack()
        
        # 版本信息
        version_label = ttk.Label(
            title_frame,
            text=f"版本 {Config.APP_VERSION}",
            font=('Arial', 10),
            foreground='#666666'
        )
        version_label.pack(pady=(5, 0))
        
        # 分隔线
        separator = ttk.Separator(title_frame, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, pady=(10, 0))
    
    def _create_machine_code_section(self, parent):
        """创建电脑码显示区域"""
        machine_frame = ttk.LabelFrame(parent, text="电脑码", padding=10)
        machine_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 电脑码显示
        self.machine_code = self.license_manager.get_machine_code()
        
        code_frame = ttk.Frame(machine_frame)
        code_frame.pack(fill=tk.X)
        
        self.machine_code_var = tk.StringVar(value=self.machine_code)
        code_entry = ttk.Entry(
            code_frame,
            textvariable=self.machine_code_var,
            font=('Consolas', 11),
            state='readonly',
            width=50
        )
        code_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # 复制按钮
        copy_button = ttk.Button(
            code_frame,
            text="复制",
            command=self._copy_machine_code,
            width=8
        )
        copy_button.pack(side=tk.RIGHT)
        
        # 说明文本
        help_label = ttk.Label(
            machine_frame,
            text="请将此电脑码提供给软件供应商以获取授权码",
            font=('Arial', 9),
            foreground='#666666'
        )
        help_label.pack(pady=(5, 0), anchor=tk.W)
    
    def _create_license_key_section(self, parent):
        """创建授权码输入区域"""
        license_frame = ttk.LabelFrame(parent, text="授权码", padding=10)
        license_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 授权码输入
        self.license_key_var = tk.StringVar()
        
        key_frame = ttk.Frame(license_frame)
        key_frame.pack(fill=tk.X)
        
        self.license_entry = ttk.Entry(
            key_frame,
            textvariable=self.license_key_var,
            font=('Consolas', 11),
            width=50
        )
        self.license_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # 粘贴按钮
        paste_button = ttk.Button(
            key_frame,
            text="粘贴",
            command=self._paste_license_key,
            width=8
        )
        paste_button.pack(side=tk.RIGHT)
        
        # 绑定回车键
        self.license_entry.bind('<Return>', lambda e: self._activate_license())
        
        # 说明文本
        help_label = ttk.Label(
            license_frame,
            text="请输入从软件供应商处获得的授权码",
            font=('Arial', 9),
            foreground='#666666'
        )
        help_label.pack(pady=(5, 0), anchor=tk.W)
    
    def _create_status_section(self, parent):
        """创建状态显示区域"""
        status_frame = ttk.LabelFrame(parent, text="授权状态", padding=10)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 状态文本
        self.status_var = tk.StringVar(value="未激活")
        self.status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            font=('Arial', 10, 'bold'),
            foreground='#E74C3C'
        )
        self.status_label.pack(anchor=tk.W)
        
        # 详细信息
        self.detail_var = tk.StringVar(value="请输入授权码进行激活")
        self.detail_label = ttk.Label(
            status_frame,
            textvariable=self.detail_var,
            font=('Arial', 9),
            foreground='#666666',
            wraplength=450
        )
        self.detail_label.pack(anchor=tk.W, pady=(5, 0))
    
    def _create_button_section(self, parent):
        """创建按钮区域"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 激活按钮
        self.activate_button = ttk.Button(
            button_frame,
            text="激活软件",
            command=self._activate_license,
            style="Accent.TButton"
        )
        self.activate_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 试用按钮（如果支持）
        trial_button = ttk.Button(
            button_frame,
            text="试用 (3天)",
            command=self._start_trial
        )
        trial_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 退出按钮
        exit_button = ttk.Button(
            button_frame,
            text="退出程序",
            command=self._exit_application
        )
        exit_button.pack(side=tk.RIGHT)
        
        # 刷新按钮
        refresh_button = ttk.Button(
            button_frame,
            text="刷新状态",
            command=self._refresh_status
        )
        refresh_button.pack(side=tk.RIGHT, padx=(0, 10))
    
    def _copy_machine_code(self):
        """复制电脑码到剪贴板"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.machine_code)
            messagebox.showinfo("提示", "电脑码已复制到剪贴板")
        except Exception as e:
            messagebox.showerror("错误", f"复制失败: {str(e)}")
    
    def _paste_license_key(self):
        """从剪贴板粘贴授权码"""
        try:
            clipboard_text = self.root.clipboard_get()
            self.license_key_var.set(clipboard_text.strip())
        except Exception:
            messagebox.showwarning("提示", "剪贴板中没有文本内容")
    
    def _activate_license(self):
        """激活授权"""
        license_key = self.license_key_var.get().strip()
        if not license_key:
            messagebox.showwarning("提示", "请输入授权码")
            self.license_entry.focus()
            return
        
        # 显示激活进度
        self._show_progress("正在验证授权码...")
        
        # 在后台线程中执行激活
        def activate_thread():
            try:
                success, message, expiry_date = self.license_manager.activate_license(license_key)
                
                # 在主线程中更新界面
                self.root.after(0, self._on_activation_complete, success, message, expiry_date)
                
            except Exception as e:
                self.root.after(0, self._on_activation_error, str(e))
        
        threading.Thread(target=activate_thread, daemon=True).start()
    
    def _on_activation_complete(self, success, message, expiry_date):
        """激活完成回调"""
        self._hide_progress()
        
        if success:
            self.status_var.set("已激活")
            self.status_label.config(foreground='#27AE60')
            self.detail_var.set(message)
            
            messagebox.showinfo("激活成功", message)
            
            # 激活成功，关闭对话框
            self.result = True
            self.root.destroy()
            
        else:
            self.status_var.set("激活失败")
            self.status_label.config(foreground='#E74C3C')
            self.detail_var.set(message)
            
            messagebox.showerror("激活失败", message)
    
    def _on_activation_error(self, error_message):
        """激活异常回调"""
        self._hide_progress()
        
        self.status_var.set("激活异常")
        self.status_label.config(foreground='#E74C3C')
        self.detail_var.set(f"激活过程中发生错误: {error_message}")
        
        messagebox.showerror("激活异常", f"激活过程中发生错误:\n\n{error_message}")
    
    def _start_trial(self):
        """开始试用"""
        # 生成3天试用授权
        trial_key = self.license_manager.generate_license_key(self.machine_code, days=3)
        
        success, message, expiry_date = self.license_manager.activate_license(trial_key)
        
        if success:
            self.status_var.set("试用中")
            self.status_label.config(foreground='#F39C12')
            self.detail_var.set(f"试用期至: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}")
            
            messagebox.showinfo("试用激活", "试用期激活成功！\n\n试用期限: 3天\n请及时购买正式授权")
            
            self.result = True
            self.root.destroy()
        else:
            messagebox.showerror("试用失败", f"试用激活失败:\n\n{message}")
    
    def _refresh_status(self):
        """刷新授权状态"""
        self._check_existing_license()
    
    def _check_existing_license(self):
        """检查现有授权"""
        try:
            is_valid, message, expiry_date = self.license_manager.check_license()
            
            if is_valid:
                self.status_var.set("已激活")
                self.status_label.config(foreground='#27AE60')
                
                if expiry_date:
                    from datetime import datetime
                    remaining_days = (expiry_date - datetime.now()).days
                    if remaining_days <= 7:
                        self.detail_var.set(f"授权即将过期 (剩余 {remaining_days} 天)")
                        self.status_label.config(foreground='#F39C12')
                    else:
                        self.detail_var.set(f"授权有效期至: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    self.detail_var.set("永久授权")
                
                # 已有有效授权，可以直接使用
                self.result = True
                
            else:
                self.status_var.set("未激活")
                self.status_label.config(foreground='#E74C3C')
                self.detail_var.set(message)
                
        except Exception as e:
            self.status_var.set("状态未知")
            self.status_label.config(foreground='#E74C3C')
            self.detail_var.set(f"检查授权状态时发生错误: {str(e)}")
    
    def _show_progress(self, message):
        """显示进度提示"""
        self.activate_button.config(state=tk.DISABLED, text=message)
        self.root.update()
    
    def _hide_progress(self):
        """隐藏进度提示"""
        self.activate_button.config(state=tk.NORMAL, text="激活软件")
        self.root.update()
    
    def _on_close_attempt(self):
        """用户尝试关闭窗口时的处理"""
        if messagebox.askyesno("确认", "软件需要激活后才能使用，确定要退出吗？"):
            self._exit_application()
    
    def _exit_application(self):
        """退出应用程序"""
        self.result = False
        self.root.destroy()
        if self.parent is None:
            sys.exit(0)
    
    def show(self) -> bool:
        """
        显示对话框
        
        Returns:
            bool: 是否激活成功
        """
        if self.parent:
            self.parent.wait_window(self.root)
        else:
            self.root.mainloop()
        
        return self.result


class LicenseManagerDialog:
    """授权管理对话框（用于已激活用户查看授权信息）"""
    
    def __init__(self, parent):
        """
        初始化授权管理对话框
        
        Args:
            parent: 父窗口
        """
        self.parent = parent
        self.license_manager = LicenseManager()
        
        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("授权管理")
        self.dialog.geometry("450x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self._center_window()
        
        # 创建界面
        self._create_widgets()
        
        # 加载授权信息
        self._load_license_info()
    
    def _center_window(self):
        """窗口居中"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (300 // 2)
        self.dialog.geometry(f"450x300+{x}+{y}")
    
    def _create_widgets(self):
        """创建界面控件"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame,
            text="授权信息",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # 信息显示区域
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建信息标签
        self._create_info_labels(info_frame)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(
            button_frame,
            text="重新激活",
            command=self._reactivate
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            button_frame,
            text="刷新",
            command=self._refresh
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Button(
            button_frame,
            text="关闭",
            command=self.dialog.destroy
        ).pack(side=tk.RIGHT)
    
    def _create_info_labels(self, parent):
        """创建信息显示标签"""
        # 电脑码
        ttk.Label(parent, text="电脑码:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.machine_code_label = ttk.Label(parent, text="", font=('Consolas', 9))
        self.machine_code_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # 授权状态
        ttk.Label(parent, text="授权状态:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.status_label = ttk.Label(parent, text="", font=('Arial', 9))
        self.status_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # 有效期
        ttk.Label(parent, text="有效期:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=2)
        self.expiry_label = ttk.Label(parent, text="", font=('Arial', 9))
        self.expiry_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # 剩余天数
        ttk.Label(parent, text="剩余天数:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=2)
        self.remaining_label = ttk.Label(parent, text="", font=('Arial', 9))
        self.remaining_label.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=2)
    
    def _load_license_info(self):
        """加载授权信息"""
        # 显示电脑码
        machine_code = self.license_manager.get_machine_code()
        self.machine_code_label.config(text=machine_code)
        
        # 检查授权状态
        is_valid, message, expiry_date = self.license_manager.check_license()
        
        if is_valid:
            self.status_label.config(text="已激活", foreground='#27AE60')
            
            if expiry_date:
                from datetime import datetime
                self.expiry_label.config(text=expiry_date.strftime('%Y-%m-%d %H:%M:%S'))
                
                remaining_days = (expiry_date - datetime.now()).days
                if remaining_days <= 0:
                    self.remaining_label.config(text="已过期", foreground='#E74C3C')
                elif remaining_days <= 7:
                    self.remaining_label.config(text=f"{remaining_days} 天", foreground='#F39C12')
                else:
                    self.remaining_label.config(text=f"{remaining_days} 天", foreground='#27AE60')
            else:
                self.expiry_label.config(text="永久")
                self.remaining_label.config(text="永久", foreground='#27AE60')
        else:
            self.status_label.config(text="未激活", foreground='#E74C3C')
            self.expiry_label.config(text="N/A")
            self.remaining_label.config(text="N/A")
    
    def _reactivate(self):
        """重新激活"""
        self.dialog.destroy()
        
        # 显示激活对话框
        license_dialog = LicenseDialog(self.parent)
        license_dialog.show()
    
    def _refresh(self):
        """刷新信息"""
        self._load_license_info()
    
    def show(self):
        """显示对话框"""
        self.parent.wait_window(self.dialog)