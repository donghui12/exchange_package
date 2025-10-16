# Windows 构建问题解决方案

## 常见错误和解决方法

### 1. "python不是内部或外部命令"

**原因**: Python未安装或未添加到PATH环境变量

**解决方案**:
1. 下载并安装Python: https://python.org/downloads/
2. 安装时**勾选"Add Python to PATH"**选项
3. 或手动添加Python到PATH:
   - 找到Python安装目录 (通常是 `C:\Users\用户名\AppData\Local\Programs\Python\Python3x\`)
   - 添加到系统PATH环境变量
4. 重启命令提示符

### 2. "pip不是内部或外部命令"

**解决方案**:
- 使用 `python -m pip` 替代 `pip`
- 或重新安装Python确保pip被正确安装

### 3. "pyinstaller不是内部或外部命令"

**解决方案**:
1. 确保pip正常工作
2. 运行: `pip install pyinstaller` 或 `python -m pip install pyinstaller`
3. 如果仍然无法使用pyinstaller命令，使用: `python -m PyInstaller`

### 4. "找不到requirements.txt"

**解决方案**:
- 确保在 `build` 目录中运行批处理文件
- 检查项目结构是否正确

### 5. 中文字符显示问题

**解决方案**:
- 已在新的批处理文件中添加 `chcp 65001` 解决

## 使用步骤

### 方法1: 诊断环境
```cmd
cd build
debug_env.bat
```
这会检查您的Python环境是否正确配置。

### 方法2: 构建程序
```cmd
cd build
build.bat
```
使用增强版的构建脚本，包含详细的错误检查。

## 手动构建步骤

如果批处理文件仍有问题，可以手动执行：

```cmd
# 1. 进入build目录
cd build

# 2. 检查Python
python --version

# 3. 安装依赖
python -m pip install -r ../requirements.txt
python -m pip install pyinstaller

# 4. 构建
python -m PyInstaller material_converter.spec
```

## 输出文件

构建成功后，可执行文件位于:
- Windows: `build\dist\秒转助手.exe`
- macOS: `build/dist/秒转助手`
- Linux: `build/dist/秒转助手`

## 故障排除

如果遇到问题:
1. 运行 `debug_env.bat` 检查环境
2. 确保所有依赖都已安装
3. 检查Python版本 (建议Python 3.7+)
4. 确保有足够的磁盘空间 (至少500MB)