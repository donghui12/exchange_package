"""
拼多多素材包转换工具主程序
PDD Material Package Converter Main Program
"""
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui.main_window import MaterialConverterApp

def main():
    """主程序入口"""
    app = MaterialConverterApp()
    app.run()

if __name__ == "__main__":
    main()