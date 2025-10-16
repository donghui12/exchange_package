@echo off
chcp 65001 >nul
echo Windows环境诊断工具
echo Windows Environment Diagnostic Tool
echo ====================================
echo.

echo 1. 检查Python安装状态...
echo Checking Python installation...
where python
if %errorlevel% neq 0 (
    echo   ❌ Python未找到在PATH中
    echo   ❌ Python not found in PATH
) else (
    echo   ✓ Python已找到
    echo   ✓ Python found
    python --version
)
echo.

echo 2. 检查pip安装状态...
echo Checking pip installation...
where pip
if %errorlevel% neq 0 (
    echo   ❌ pip未找到在PATH中
    echo   ❌ pip not found in PATH
    echo   尝试使用python -m pip...
    echo   Trying python -m pip...
    python -m pip --version
    if %errorlevel% neq 0 (
        echo   ❌ python -m pip也失败
        echo   ❌ python -m pip also failed
    ) else (
        echo   ✓ python -m pip可用
        echo   ✓ python -m pip available
    )
) else (
    echo   ✓ pip已找到
    echo   ✓ pip found
    pip --version
)
echo.

echo 3. 检查当前目录...
echo Checking current directory...
echo 当前目录: %CD%
echo Current directory: %CD%
dir ..\requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo   ❌ 未找到requirements.txt文件
    echo   ❌ requirements.txt not found
    echo   请确保在build目录中运行此脚本
    echo   Please ensure you run this script in the build directory
) else (
    echo   ✓ requirements.txt已找到
    echo   ✓ requirements.txt found
)
echo.

echo 4. 检查Python模块...
echo Checking Python modules...
python -c "import sys; print('Python可执行路径:', sys.executable)"
python -c "import tkinter; print('✓ tkinter可用')" 2>nul || echo "❌ tkinter不可用"
python -c "import requests; print('✓ requests可用')" 2>nul || echo "❌ requests不可用"
python -c "import openpyxl; print('✓ openpyxl可用')" 2>nul || echo "❌ openpyxl不可用"
python -c "import PIL; print('✓ Pillow可用')" 2>nul || echo "❌ Pillow不可用"
python -c "import psutil; print('✓ psutil可用')" 2>nul || echo "❌ psutil不可用"
echo.

echo 5. 系统信息...
echo System information...
echo Windows版本: 
ver
echo Python路径: 
python -c "import sys; print('\n'.join(sys.path))"
echo.

echo 诊断完成！
echo Diagnostic completed!
echo.
echo 如果看到错误，请：
echo If you see errors, please:
echo 1. 安装Python (https://python.org)
echo 2. 确保Python添加到PATH环境变量
echo 3. 重启命令提示符
echo 4. 在build目录中运行脚本
pause