# 拼多多素材包转换工具 (PDD Material Package Converter)

一个用于将拼多多商品导出数据转换为标准素材包格式的桌面应用工具。

## 功能特性

- 🔄 **自动转换**: 将PDD商品JSON数据转换为标准素材包结构
- 📁 **智能分类**: 自动下载并分类存储主图、详情图、SKU图等
- 📊 **Excel生成**: 自动生成包含商品信息的Excel导入模板
- 🎛️ **多种格式**: 支持两种不同的输出格式选择
- 📦 **压缩打包**: 可选择性创建ZIP压缩包
- 🖥️ **友好界面**: 直观的图形用户界面
- ⚙️ **可配置**: 支持自定义转换间隔等参数

## 项目结构

```
exchange_package/
├── src/                           # 源代码目录
│   ├── __init__.py               # 包初始化文件
│   ├── config.py                 # 配置文件模块
│   ├── core/                     # 核心功能模块
│   │   ├── __init__.py          
│   │   ├── converter.py          # 主转换逻辑
│   │   ├── data_parser.py        # 数据解析模块
│   │   ├── downloader.py         # 图片下载模块
│   │   └── excel_generator.py    # Excel生成模块
│   ├── gui/                      # 图形界面模块
│   │   ├── __init__.py
│   │   ├── main_window.py        # 主窗口界面
│   │   ├── widgets.py            # 自定义控件
│   │   └── dialogs.py            # 对话框组件
│   └── utils/                    # 工具函数模块
│       ├── __init__.py
│       ├── file_utils.py         # 文件操作工具
│       ├── image_utils.py        # 图片处理工具
│       └── logger.py             # 日志工具
├── build/                        # 构建配置目录
│   ├── __init__.py
│   ├── material_converter.spec   # PyInstaller配置
│   ├── build.bat                 # Windows构建脚本
│   └── build.sh                  # Linux/Mac构建脚本
├── tests/                        # 测试文件目录
├── docs/                         # 文档目录
├── examples/                     # 示例文件目录
│   ├── pdd_goods_554049016296.txt # 示例PDD数据文件
│   └── 产品素材包模板/            # 素材包模板示例
├── main.py                       # 应用程序入口
├── requirements.txt              # Python依赖列表
├── README.md                     # 项目说明文档
└── LICENSE                       # 许可证文件
```

## 模块说明

### 🔧 核心模块 (src/core/)

#### converter.py - 主转换逻辑
- `MaterialConverter`: 主转换器类
- 协调各个模块完成完整的转换流程
- 处理转换异常和错误恢复

#### data_parser.py - 数据解析模块  
- `PDDDataParser`: PDD数据解析器
- 解析JSON格式的商品数据
- 提取商品基础信息、图片URL、SKU信息等

#### downloader.py - 图片下载模块
- `ImageDownloader`: 图片下载器类
- 支持多线程下载和断点续传
- 自动重试和错误处理机制

#### excel_generator.py - Excel生成模块
- `ExcelGenerator`: Excel文件生成器
- 基于openpyxl库生成标准的导入模板
- 支持自定义表头和数据格式

### 🖥️ 界面模块 (src/gui/)

#### main_window.py - 主窗口界面
- `MaterialConverterApp`: 主应用程序类
- 实现完整的GUI界面布局
- 处理用户交互和事件响应

#### widgets.py - 自定义控件
- `PathSelectWidget`: 路径选择控件
- `ProgressWidget`: 进度显示控件
- `LogWidget`: 日志输出控件

#### dialogs.py - 对话框组件
- `SettingsDialog`: 设置对话框
- `AboutDialog`: 关于对话框
- `ErrorDialog`: 错误提示对话框

### 🛠️ 工具模块 (src/utils/)

#### file_utils.py - 文件操作工具
- 文件/文件夹创建、删除、复制等操作
- ZIP压缩包创建和解压
- 路径处理和验证

#### image_utils.py - 图片处理工具
- 图片格式转换和优化
- 图片尺寸调整和质量压缩
- 图片信息获取和验证

#### logger.py - 日志工具
- 统一的日志记录和输出
- 支持文件日志和界面日志
- 可配置的日志级别和格式

### ⚙️ 配置模块 (src/config.py)

- 应用程序全局配置管理
- 默认参数和常量定义
- 文件命名规则和路径配置

## 数据转换流程

1. **数据解析**: 读取pdd_goods_*.txt文件，解析JSON数据
2. **创建目录**: 根据选择的格式创建对应的文件夹结构
3. **下载图片**: 
   - 主图: 从gallery字段提取type=1的图片
   - 详情图: 从decoration字段提取图片
   - SKU图: 从sku数组提取thumb_url图片
4. **生成Excel**: 创建包含商品信息的导入模板
5. **文件组织**: 按照标准素材包格式整理所有文件
6. **可选压缩**: 根据用户选择创建ZIP压缩包

## 支持的数据格式

### 输入格式
- **PDD数据文件**: JSON格式的.txt文件
- 包含完整的商品信息、图片链接、SKU数据等

### 输出格式

#### 格式1 (传统格式)
```
商品名称_商品ID/
├── 主图/
│   ├── 主图_1.jpg
│   ├── 主图_2.jpg
│   └── ...
├── SKU图/
│   ├── 规格名_1.jpg
│   └── ...
├── 详情图/
│   ├── 详情图_1.jpg
│   └── ...
├── 主图视频/
└── 导入产品模板.xlsx
```

#### 格式2 (产品格式)
```
商品名称_商品ID/
├── 产品主图/
│   ├── 主图_1.jpg
│   └── ...
├── SKU图/
├── 详情图/
├── 产品视频/
└── 导入产品模板.xlsx
```

## 安装和使用

### 环境要求
- Python 3.7+
- Windows/Linux/macOS

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行程序
```bash
python main.py
```

### 构建可执行文件
```bash
# Windows
cd build
build.bat

# Linux/Mac  
cd build
./build.sh
```

## 使用说明

1. **选择数据包文件夹**: 选择包含pdd_goods_*.txt文件的文件夹
2. **选择输出文件夹**: 指定生成素材包的保存位置
3. **设置转换参数**: 
   - 输出间隔时间(秒)
   - 选择导出格式(格式1或格式2)
   - 是否创建ZIP压缩包
4. **开始转换**: 点击"开始转换"按钮执行转换
5. **查看进度**: 在日志区域查看转换进度和结果

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。
