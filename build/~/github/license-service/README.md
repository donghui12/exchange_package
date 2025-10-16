# 通用授权服务 (Universal License Service)

一个通用的软件授权验证服务，支持多应用的授权管理和验证。

## 🎯 功能特性

- 🔐 **多应用支持**: 支持为多个应用提供授权服务
- 🌐 **RESTful API**: 提供标准的HTTP API接口
- 💾 **数据持久化**: 使用SQLite/MySQL数据库存储授权信息
- 🔒 **安全验证**: 支持机器码绑定和授权码验证
- ⏰ **过期管理**: 支持永久授权和时限授权
- 📊 **管理后台**: 提供Web管理界面
- 📝 **详细日志**: 记录所有验证请求和操作
- 🚀 **易部署**: 支持Docker容器化部署

## 🏗️ 技术架构

- **后端框架**: FastAPI (Python)
- **数据库**: SQLite (可扩展为MySQL/PostgreSQL)
- **认证**: JWT Token
- **文档**: 自动生成API文档
- **部署**: Docker + Nginx

## 📁 项目结构

```
license-service/
├── app/                    # 应用核心代码
│   ├── api/               # API路由
│   ├── core/              # 核心配置
│   ├── db/                # 数据库相关
│   ├── models/            # 数据模型
│   ├── schemas/           # Pydantic模式
│   ├── services/          # 业务逻辑
│   └── utils/             # 工具函数
├── tests/                 # 测试代码
├── docker/                # Docker配置
├── docs/                  # 文档
├── requirements.txt       # Python依赖
├── docker-compose.yml     # Docker编排
└── README.md             # 项目说明
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

```bash
cp .env.example .env
# 编辑 .env 文件配置数据库等信息
```

### 3. 初始化数据库

```bash
python -m app.db.init_db
```

### 4. 启动服务

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. 访问API文档

打开浏览器访问: http://localhost:8000/docs

## 📖 API文档

详细的API接口文档请参考: [API.md](docs/API.md)

## 🔧 配置说明

详细的配置说明请参考: [CONFIG.md](docs/CONFIG.md)

## 🐳 Docker部署

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d
```

## 📊 管理后台

访问管理后台: http://localhost:8000/admin

## 🔐 安全说明

- 所有API请求需要有效的API Key
- 机器码使用硬件信息生成，确保设备唯一性
- 授权码使用加密算法生成，防止伪造
- 支持IP白名单限制访问

## 📈 监控和日志

- 所有API请求都会记录详细日志
- 支持Prometheus监控指标
- 可集成ELK日志分析

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

MIT License