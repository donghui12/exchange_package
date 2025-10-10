@echo off
echo 开始构建素材包转换工具...
echo Building Material Package Converter...

echo 安装依赖...
pip install -r ../requirements.txt
pip install pyinstaller

echo 构建可执行文件...
pyinstaller material_converter.spec

echo 构建完成！
echo Build completed!
pause