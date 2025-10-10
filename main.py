"""
拼多多素材包转换工具主程序
PDD Material Package Converter Main Program
"""
import sys
import os
import tkinter as tk
import tempfile
from tkinter import messagebox

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gui.main_window import MaterialConverterApp
from src.gui.license_dialog import LicenseDialog
from src.utils.license_manager import LicenseManager

class SingleInstance:
    """
    跨平台纯Python单实例实现（使用锁文件）
    无需 pywin32 / fcntl
    """
    def __init__(self, name="material_converter.lock"):
        self.lockfile = os.path.join(tempfile.gettempdir(), name)
        self.fd = None

    def acquire(self):
        if os.path.exists(self.lockfile):
            try:
                os.remove(self.lockfile)
            except:
                return False
        try:
            self.fd = os.open(self.lockfile, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            return True
        except FileExistsError:
            return False

    def release(self):
        if self.fd:
            os.close(self.fd)
        if os.path.exists(self.lockfile):
            os.remove(self.lockfile)

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