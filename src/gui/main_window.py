"""
主窗口界面模块
实现应用程序的主要GUI界面
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
import sys
from typing import Dict, Any

# 添加父目录到路径，以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.core.converter import MaterialConverter
from src.config import Config
from src.utils.logger import get_ui_logger
from .widgets import PathSelectWidget, ProgressWidget, LogWidget, SettingsFrame
from .dialogs import SettingsDialog, AboutDialog, ErrorDialog
from .license_dialog import LicenseManagerDialog

class MaterialConverterApp:
    """素材包转换工具主应用程序类"""
    
    def __init__(self):
        """初始化应用程序"""
        self.root = tk.Tk()
        self.root.title(Config.APP_NAME)
        self.root.geometry("800x700")
        self.root.minsize(600, 500)
        
        # 初始化变量
        self.converter = None
        self.conversion_thread = None
        self.is_converting = False
        self.ui_logger = get_ui_logger()
        
        # 创建界面
        self._create_widgets()
        self._setup_logger()
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # 初始化完成
        self.log_widget.append_log("应用程序初始化完成", "INFO")
        self.log_widget.append_log(f"版本: {Config.APP_VERSION}", "INFO")
    
    def _create_widgets(self):
        """创建界面控件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建路径选择区域
        self._create_path_section(main_frame)
        
        # 创建设置区域
        self._create_settings_section(main_frame)
        
        # 创建进度显示区域
        self._create_progress_section(main_frame)
        
        # 创建控制按钮区域
        self._create_control_section(main_frame)
        
        # 创建日志显示区域
        self._create_log_section(main_frame)
        
        # 创建菜单栏
        self._create_menu()
    
    def _create_path_section(self, parent):
        """创建路径选择区域"""
        path_frame = ttk.LabelFrame(parent, text="路径设置", padding=10)
        path_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 数据包文件夹路径
        self.input_path_widget = PathSelectWidget(
            path_frame,
            label_text="数据包文件夹:",
            dialog_title="选择包含PDD数据文件的文件夹",
            select_directory=True,
            on_path_changed=self._on_input_path_changed
        )
        self.input_path_widget.pack(fill=tk.X, pady=(0, 5))
        
        # 输出文件夹路径
        self.output_path_widget = PathSelectWidget(
            path_frame,
            label_text="输出文件夹:",
            dialog_title="选择输出文件夹",
            select_directory=True
        )
        self.output_path_widget.pack(fill=tk.X)
    
    def _create_settings_section(self, parent):
        """创建设置区域"""
        self.settings_frame = SettingsFrame(parent, "转换设置")
        self.settings_frame.pack(fill=tk.X, pady=(0, 10))
    
    def _create_progress_section(self, parent):
        """创建进度显示区域"""
        progress_frame = ttk.LabelFrame(parent, text="转换进度", padding=10)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_widget = ProgressWidget(
            progress_frame,
            show_percentage=True,
            show_text=True
        )
        self.progress_widget.pack(fill=tk.X)
    
    def _create_control_section(self, parent):
        """创建控制按钮区域"""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 开始转换按钮
        self.start_button = ttk.Button(
            control_frame,
            text="开始转换",
            command=self._start_conversion
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 停止转换按钮
        self.stop_button = ttk.Button(
            control_frame,
            text="停止转换",
            command=self._stop_conversion,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 清空日志按钮
        clear_log_button = ttk.Button(
            control_frame,
            text="清空日志",
            command=self._clear_log
        )
        clear_log_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 保存日志按钮
        save_log_button = ttk.Button(
            control_frame,
            text="保存日志",
            command=self._save_log
        )
        save_log_button.pack(side=tk.LEFT)
        
        # 右侧按钮
        settings_button = ttk.Button(
            control_frame,
            text="高级设置",
            command=self._show_settings
        )
        settings_button.pack(side=tk.RIGHT)
    
    def _create_log_section(self, parent):
        """创建日志显示区域"""
        log_frame = ttk.LabelFrame(parent, text="转换日志", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_widget = LogWidget(log_frame, height=12)
        self.log_widget.pack(fill=tk.BOTH, expand=True)
    
    def _create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="打开输入目录...", command=self._open_input_dir)
        file_menu.add_command(label="打开输出目录...", command=self._open_output_dir)
        file_menu.add_separator()
        file_menu.add_command(label="保存日志...", command=self._save_log)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self._on_closing)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="高级设置...", command=self._show_settings)
        tools_menu.add_command(label="清空日志", command=self._clear_log)
        tools_menu.add_separator()
        tools_menu.add_command(label="授权管理...", command=self._show_license_manager)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self._show_help)
        help_menu.add_command(label="关于", command=self._show_about)
    
    def _setup_logger(self):
        """设置日志记录"""
        # 添加UI日志回调
        self.ui_logger.add_callback(self._on_log_message)
    
    def _on_log_message(self, message: str):
        """处理日志消息"""
        if message:  # 非空消息
            # 根据消息内容判断日志级别
            if "错误" in message or "失败" in message or "异常" in message:
                level = "ERROR"
            elif "警告" in message:
                level = "WARNING"
            elif "完成" in message or "成功" in message:
                level = "SUCCESS"
            else:
                level = "INFO"
            
            self.log_widget.append_log(message, level)
        else:  # 空消息表示清空
            self.log_widget.clear_log()
    
    def _on_input_path_changed(self, path: str):
        """输入路径改变时的处理"""
        if path and os.path.exists(path):
            # 验证目录中是否有PDD文件
            pdd_files = [f for f in os.listdir(path) 
                        if f.startswith('pdd_goods_') and f.endswith('.txt')]
            
            if pdd_files:
                self.log_widget.append_log(f"找到 {len(pdd_files)} 个PDD文件", "INFO")
            else:
                self.log_widget.append_log("目录中未找到PDD数据文件", "WARNING")
    
    def _validate_inputs(self) -> bool:
        """验证输入参数"""
        input_path = self.input_path_widget.get_path()
        output_path = self.output_path_widget.get_path()
        
        if not input_path:
            ErrorDialog.show_error(self.root, "输入错误", "请选择数据包文件夹")
            return False
        
        if not os.path.exists(input_path):
            ErrorDialog.show_error(self.root, "输入错误", "数据包文件夹不存在")
            return False
        
        if not output_path:
            ErrorDialog.show_error(self.root, "输入错误", "请选择输出文件夹")
            return False
        
        # 检查PDD文件
        pdd_files = [f for f in os.listdir(input_path) 
                    if f.startswith('pdd_goods_') and f.endswith('.txt')]
        
        if not pdd_files:
            ErrorDialog.show_error(
                self.root, 
                "输入错误", 
                "在选择的目录中未找到PDD数据文件\n\n文件格式应为: *.txt"
            )
            return False
        
        return True
    
    def _start_conversion(self):
        """开始转换"""
        if not self._validate_inputs():
            return
        
        if self.is_converting:
            ErrorDialog.show_warning(self.root, "警告", "转换正在进行中，请等待完成")
            return
        
        # 获取设置
        settings = self.settings_frame.get_settings()
        input_path = self.input_path_widget.get_path()
        output_path = self.output_path_widget.get_path()
        
        # 确认开始转换
        if not ErrorDialog.ask_yes_no(
            self.root, 
            "确认转换", 
            f"即将开始转换\n\n输入目录: {input_path}\n输出目录: {output_path}\n\n是否继续？"
        ):
            return
        
        # 更新界面状态
        self.is_converting = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_widget.reset()
        
        # 创建转换器
        self.converter = MaterialConverter(progress_callback=self._on_progress_update)
        
        # 在新线程中执行转换
        self.conversion_thread = threading.Thread(
            target=self._run_conversion,
            args=(input_path, output_path, settings),
            daemon=True
        )
        self.conversion_thread.start()
        
        self.log_widget.append_log("开始转换...", "INFO")
    
    def _run_conversion(self, input_path: str, output_path: str, settings: Dict[str, Any]):
        """在后台线程中运行转换"""
        try:
            # 执行批量转换
            result = self.converter.convert_batch_files(
                input_dir=input_path,
                output_dir=output_path,
                export_format=settings['format'],
                create_zip=settings['create_zip'],
                interval_seconds=settings['interval']
            )
            
            # 在主线程中更新界面
            self.root.after(0, self._on_conversion_completed, result)
            
        except Exception as e:
            # 在主线程中处理异常
            self.root.after(0, self._on_conversion_error, str(e))
    
    def _on_progress_update(self, message: str):
        """进度更新回调"""
        # 通过UI日志记录器更新日志
        self.ui_logger.log(message)
    
    def _on_conversion_completed(self, result: Dict[str, Any]):
        """转换完成时的处理"""
        self.is_converting = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        if result['success']:
            self.progress_widget.set_progress(100, "转换完成")
            
            success_msg = (
                f"批量转换完成!\n\n"
                f"总文件数: {result['total_files']}\n"
                f"成功: {result['success_count']}\n"
                f"失败: {result['failed_count']}\n"
                f"用时: {result['total_time']:.2f}秒"
            )
            
            ErrorDialog.show_info(self.root, "转换完成", success_msg)
        else:
            self.progress_widget.set_progress(0, "转换失败")
            ErrorDialog.show_error(
                self.root, 
                "转换失败", 
                f"批量转换失败: {result.get('error', '未知错误')}"
            )
    
    def _on_conversion_error(self, error_message: str):
        """转换错误时的处理"""
        self.is_converting = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_widget.set_progress(0, "转换失败")
        
        ErrorDialog.show_error(self.root, "转换异常", f"转换过程中发生异常:\n\n{error_message}")
    
    def _stop_conversion(self):
        """停止转换"""
        if self.is_converting:
            if ErrorDialog.ask_yes_no(self.root, "确认停止", "确定要停止当前的转换操作吗？"):
                self.is_converting = False
                self.start_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.DISABLED)
                self.progress_widget.set_progress(0, "已停止")
                
                self.log_widget.append_log("用户取消了转换操作", "WARNING")
    
    def _clear_log(self):
        """清空日志"""
        self.log_widget.clear_log()
        self.ui_logger.clear()
    
    def _save_log(self):
        """保存日志"""
        self.log_widget.save_log()
    
    def _open_input_dir(self):
        """打开输入目录"""
        path = self.input_path_widget.get_path()
        if path and os.path.exists(path):
            if os.name == 'nt':
                os.startfile(path)
            else:
                os.system(f'open "{path}"')
    
    def _open_output_dir(self):
        """打开输出目录"""
        path = self.output_path_widget.get_path()
        if path and os.path.exists(path):
            if os.name == 'nt':
                os.startfile(path)
            else:
                os.system(f'open "{path}"')
    
    def _show_settings(self):
        """显示高级设置对话框"""
        dialog = SettingsDialog(self.root)
        result = dialog.show()
        
        if result:
            self.log_widget.append_log("高级设置已更新", "INFO")
    
    def _show_license_manager(self):
        """显示授权管理对话框"""
        try:
            dialog = LicenseManagerDialog(self.root)
            dialog.show()
        except Exception as e:
            ErrorDialog.show_error(
                self.root,
                "授权管理",
                f"打开授权管理时发生错误:\n\n{str(e)}"
            )
    
    def _show_help(self):
        """显示帮助信息"""
        help_text = (
            f"{Config.APP_NAME} 使用说明\n\n"
            "1. 选择数据包文件夹: 选择包含*.txt文件的文件夹\n"
            "2. 选择输出文件夹: 指定生成素材包的保存位置\n"
            "3. 设置转换参数: 配置输出间隔、格式和压缩选项\n"
            "4. 点击开始转换: 执行批量转换操作\n\n"
            "支持的格式:\n"
            "• 格式1: 主图/SKU图/详情图/主图视频\n"
            "• 格式2: 产品主图/SKU图/详情图/产品视频\n\n"
            "注意事项:\n"
            "• 确保网络连接正常，以便下载图片\n"
            "• 转换过程中请勿关闭程序\n"
            "• 建议在转换前备份重要数据"
        )
        
        ErrorDialog.show_info(self.root, "使用说明", help_text)
    
    def _show_about(self):
        """显示关于对话框"""
        dialog = AboutDialog(self.root)
        dialog.show()
    
    def _on_closing(self):
        """窗口关闭时的处理"""
        if self.is_converting:
            if not ErrorDialog.ask_yes_no(
                self.root, 
                "确认退出", 
                "转换正在进行中，确定要退出程序吗？\n\n注意: 退出后当前转换将被中断！"
            ):
                return
        
        # 清理资源
        if self.converter:
            self.converter.cleanup()
        
        # 退出程序
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """运行应用程序"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self._on_closing()
        except Exception as e:
            ErrorDialog.show_error(
                self.root, 
                "程序异常", 
                f"程序运行时发生异常:\n\n{str(e)}",
                details=str(e)
            )
            self._on_closing()