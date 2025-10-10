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
- 🔐 **授权验证**: 基于电脑码的软件授权系统

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
│   │   ├── dialogs.py            # 对话框组件
│   │   └── license_dialog.py     # 授权验证对话框
│   └── utils/                    # 工具函数模块
│       ├── __init__.py
│       ├── file_utils.py         # 文件操作工具
│       ├── image_utils.py        # 图片处理工具
│       ├── logger.py             # 日志工具
│       └── license_manager.py    # 授权管理模块
├── build/                        # 构建配置目录
│   ├── __init__.py
│   ├── material_converter.spec   # PyInstaller配置
│   ├── build.bat                 # Windows构建脚本
│   └── build.sh                  # Linux/Mac构建脚本
├── tests/                        # 测试文件目录
├── tools/                        # 工具脚本目录
│   └── license_generator.py      # 授权码生成工具
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

#### license_dialog.py - 授权验证对话框
- `LicenseDialog`: 授权激活对话框
- `LicenseManagerDialog`: 授权管理对话框
- 集成电脑码显示和授权码输入功能

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

#### license_manager.py - 授权管理模块
- `LicenseManager`: 授权管理器类
- 基于硬件信息生成电脑码
- 授权码的生成、验证和本地存储
- 支持在线和离线验证模式

### ⚙️ 配置模块 (src/config.py)

- 应用程序全局配置管理
- 默认参数和常量定义
- 文件命名规则和路径配置

## 数据转换流程

1. **数据解析**: 读取*.txt文件，解析JSON数据
2. **创建目录**: 根据选择的格式创建对应的文件夹结构
3. **下载图片**: 
   - 主图: 从gallery字段提取type=1的图片
   - 详情图: 从decoration字段提取图片
   - SKU图: 从sku数组提取thumb_url图片
4. **生成Excel**: 创建包含商品信息的导入模板
5. **文件组织**: 按照标准素材包格式整理所有文件
6. **可选压缩**: 根据用户选择创建ZIP压缩包

## 授权验证系统

应用程序集成了基于接口验证的授权系统，确保软件的合法使用。

### 授权流程

1. **启动验证**: 每次应用程序启动时自动进行在线授权验证
2. **电脑码生成**: 基于硬件信息生成唯一的电脑码
3. **接口验证**: 通过HTTP接口验证授权码与电脑码的匹配关系
4. **本地缓存**: 验证成功后将授权码保存到本地，下次启动时使用
5. **授权管理**: 通过菜单可查看和管理授权信息

### 接口验证特性

- **实时验证**: 每次启动都进行在线验证，确保授权状态最新
- **服务器配置**: 支持自定义验证服务器地址
- **网络容错**: 合理的超时设置和错误处理机制
- **安全传输**: 使用HTTPS确保数据传输安全
- **状态缓存**: 本地保存授权状态，提升用户体验

### 硬件绑定特性

- **主板序列号**: 获取主板唯一标识
- **CPU信息**: 处理器型号和特征
- **MAC地址**: 网卡物理地址
- **硬盘序列号**: 存储设备标识
- **跨平台支持**: 兼容Windows、macOS、Linux

### 服务器配置

在 `src/config/license_config.py` 中配置验证服务器：

```python
class LicenseConfig:
    LICENSE_SERVER_URL = "https://your-license-server.com/api/license"
    REQUEST_TIMEOUT = 10
```

详细的接口规范请参考 [LICENSE_API.md](LICENSE_API.md)

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

### 首次使用

1. **配置服务器**: 
   - 在 `src/config/license_config.py` 中设置验证服务器地址
   - 确保服务器实现了相应的验证接口
   
2. **授权激活**: 
   - 启动时会显示授权对话框
   - 复制显示的电脑码提供给软件供应商
   - 获取授权码后输入激活
   
3. **选择数据包文件夹**: 选择包含*.txt文件的文件夹
4. **选择输出文件夹**: 指定生成素材包的保存位置
5. **设置转换参数**: 
   - 输出间隔时间(秒)
   - 选择导出格式(格式1或格式2)
   - 是否创建ZIP压缩包
6. **开始转换**: 点击"开始转换"按钮执行转换
7. **查看进度**: 在日志区域查看转换进度和结果

### 授权管理

- **在线验证**: 每次启动自动进行接口验证
- **查看授权状态**: 通过"工具" -> "授权管理"菜单查看当前授权信息
- **重新激活**: 如需更换授权或重新激活，可通过授权管理对话框操作
- **网络要求**: 需要网络连接以进行授权验证

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。
