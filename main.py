"""
拼多多素材包转换工具主程序
PDD Material Package Converter Main Program
"""
import sys
import os
import tkinter as tk
from tkinter import messagebox

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gui.main_window import MaterialConverterApp
from src.gui.license_dialog import LicenseDialog
from src.utils.license_manager import LicenseManager

import fcntl  # Linux/macOS 自带，Windows 也可用 pywin32 方案

LOCK_FILE = os.path.join(os.path.expanduser("~"), ".pdd_material_converter.lock")

# Windows 独有
if os.name == "nt":
    import win32event
    import win32api
    import winerror
else:
    import fcntl

class SingleInstance:
    """
    防止重复运行的单例类
    - Windows: 使用命名互斥量
    - Linux/macOS: 使用 fcntl 文件锁
    """
    def __init__(self, lock_name="material_converter.lock"):
        self.lock_name = lock_name
        self.lockfile = None
        self.handle = None

    def acquire(self) -> bool:
        if os.name == "nt":
            mutex_name = f"Global\\{self.lock_name}"
            self.handle = win32event.CreateMutex(None, False, mutex_name)
            last_error = win32api.GetLastError()
            # ERROR_ALREADY_EXISTS 表示已有实例
            return last_error != winerror.ERROR_ALREADY_EXISTS
        else:
            lock_path = os.path.join(tempfile.gettempdir(), self.lock_name)
            self.lockfile = open(lock_path, "w")
            try:
                fcntl.lockf(self.lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return True
            except IOError:
                return False

    def release(self):
        if os.name == "nt":
            if self.handle:
                win32api.CloseHandle(self.handle)
        else:
            if self.lockfile:
                fcntl.lockf(self.lockfile, fcntl.LOCK_UN)
                self.lockfile.close()

def check_license() -> bool:
    """
    检查软件授权
    
    Returns:
        bool: 是否通过授权验证
    """
    try:
        license_manager = LicenseManager()
        is_valid, message, remaining_days = license_manager.check_license()
        
        if is_valid:
            # 检查是否即将过期（7天内）
            if remaining_days <= 0:
                # 已过期
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror(
                    "授权过期", 
                    f"软件授权已过期！\n\n请联系供应商续费"
                )
                root.destroy()
                return False
                
            elif remaining_days <= 7:
                # 即将过期提醒
                root = tk.Tk()
                root.withdraw()
                messagebox.showwarning(
                    "授权即将过期", 
                    f"软件授权即将过期！\n\n剩余天数: {remaining_days} 天\n请及时联系供应商续费"
                )
                root.destroy()
            
            return True
        else:
            return False
            
    except Exception as e:
        # 授权检查异常，显示错误信息
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "授权检查异常", 
            f"检查软件授权时发生错误:\n\n{str(e)}\n\n请联系技术支持"
        )
        root.destroy()
        return False

def show_license_dialog() -> bool:
    """
    显示授权对话框
    
    Returns:
        bool: 是否成功激活
    """
    try:
        # 创建授权对话框
        license_dialog = LicenseDialog()
        result = license_dialog.show()
        
        return result
        
    except Exception as e:
        # 显示授权对话框异常
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "程序异常", 
            f"显示授权界面时发生错误:\n\n{str(e)}\n\n请联系技术支持"
        )
        root.destroy()
        return False

def main():
    """主程序入口"""
        # 防止重复运行
    instance = SingleInstance("pdd_converter_app")
    if not instance.acquire():
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning("提示", "程序已经在运行中！")
        root.destroy()
        return
    try:
        # 首先检查授权
        if not check_license():
            # 授权无效，显示激活对话框
            if not show_license_dialog():
                # 用户取消激活或激活失败
                print("程序已退出：未通过授权验证")
                return
            
            # 激活成功后重新检查授权
            if not check_license():
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror("授权失败", "激活后仍无法通过授权验证，请联系技术支持")
                root.destroy()
                return
        
        # 授权验证通过，启动主程序
        print("授权验证通过，启动主程序...")
        app = MaterialConverterApp()
        app.run()
        
    except KeyboardInterrupt:
        print("程序被用户中断")
    except Exception as e:
        # 捕获未处理的异常
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "程序异常", 
                f"程序启动时发生未预期的错误:\n\n{str(e)}\n\n请联系技术支持"
            )
            root.destroy()
        except:
            print(f"程序异常: {str(e)}")

if __name__ == "__main__":
    main()