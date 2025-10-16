@echo off
chcp 65001 >nul
echo 开始构建素材包转换工具...
echo Building Material Package Converter...
echo.

echo 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python命令，请确保Python已安装并添加到PATH
    echo Error: Python command not found, please ensure Python is installed and added to PATH
    pause
    exit /b 1
)

echo 检查pip命令...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到pip命令，尝试使用python -m pip
    echo Error: pip command not found, trying python -m pip
    set PIP_CMD=python -m pip
) else (
    set PIP_CMD=pip
)

echo 当前Python版本:
python --version
echo 当前pip版本:
%PIP_CMD% --version
echo.

echo 安装依赖...
echo Installing dependencies...
%PIP_CMD% install -r ../requirements.txt
if %errorlevel% neq 0 (
    echo 错误: 依赖安装失败
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo 安装PyInstaller...
echo Installing PyInstaller...
%PIP_CMD% install pyinstaller
if %errorlevel% neq 0 (
    echo 错误: PyInstaller安装失败
    echo Error: Failed to install PyInstaller
    pause
    exit /b 1
)

echo 检查PyInstaller是否可用...
pyinstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: PyInstaller命令未找到，尝试使用python -m PyInstaller
    echo Error: PyInstaller command not found, trying python -m PyInstaller
    set PYINSTALLER_CMD=python -m PyInstaller
) else (
    set PYINSTALLER_CMD=pyinstaller
)

echo 构建可执行文件...
echo Building executable...
%PYINSTALLER_CMD% material_converter.spec
if %errorlevel% neq 0 (
    echo 错误: 构建失败
    echo Error: Build failed
    pause
    exit /b 1
)

echo.
echo 构建完成！
echo Build completed!
echo 可执行文件位置: dist\秒转助手.exe
echo Executable location: dist\秒转助手.exe
pause