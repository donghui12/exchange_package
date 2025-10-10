# 部署配置指南

## 🎯 接口授权系统部署

### 1. 服务器配置

修改 `src/config/license_config.py` 中的服务器地址：

```python
class LicenseConfig:
    # 🔧 修改为您的实际验证服务器地址
    LICENSE_SERVER_URL = "https://your-license-server.com/api/license"
    
    # ⏱️ 请求超时时间（秒）
    REQUEST_TIMEOUT = 10
    
    # 📱 应用信息
    APP_NAME = "素材包转换工具"
    APP_VERSION = "1.0.0"
```

### 2. 验证接口实现

服务器需要实现验证接口：

**接口地址**: `POST {LICENSE_SERVER_URL}/verify`

**请求格式**: 详见 [LICENSE_API.md](LICENSE_API.md)

### 3. 重新构建应用

修改配置后需要重新构建：

```bash
cd build
pyinstaller material_converter.spec
```

### 4. 测试验证

1. **获取电脑码**: 启动应用程序获取电脑码
2. **配置授权码**: 在您的服务器系统中配置对应的授权码
3. **测试激活**: 在应用中输入授权码进行测试

## 🔧 配置示例

### 开发环境配置

```python
# 开发环境 - 使用本地测试服务器
LICENSE_SERVER_URL = "http://42.192.40.156:8000/v1/shopee"
REQUEST_TIMEOUT = 30  # 开发环境延长超时
```

### 生产环境配置

```python
# 生产环境 - 使用正式服务器
LICENSE_SERVER_URL = "https://license.yourcompany.com/api/v1/license"
REQUEST_TIMEOUT = 10  # 生产环境标准超时
```

## 🚀 快速部署

### 1. 最小化修改部署

只需修改一个文件即可完成部署：

```bash
# 1. 编辑配置文件
vim src/config/license_config.py

# 2. 重新构建
cd build && pyinstaller material_converter.spec

# 3. 分发可执行文件
cp dist/素材包转换工具 /path/to/distribution/
```

### 2. 验证部署结果

```bash
# 运行应用程序，检查：
# 1. 是否显示正确的服务器地址
# 2. 网络连接是否正常
# 3. 授权验证是否工作
./素材包转换工具
```

## ⚠️ 注意事项

1. **HTTPS**: 生产环境必须使用HTTPS确保安全
2. **网络**: 确保客户端能够访问验证服务器
3. **防火墙**: 配置必要的网络访问权限
4. **日志**: 在服务器端记录验证请求日志
5. **监控**: 监控接口的可用性和响应时间

## 🛠️ 故障排除

### 常见问题

1. **网络连接失败**
   - 检查服务器地址配置
   - 验证网络连接
   - 检查防火墙设置

2. **验证接口错误**
   - 确认接口格式正确
   - 检查服务器日志
   - 验证授权码格式

3. **超时问题**
   - 增加 `REQUEST_TIMEOUT` 值
   - 优化服务器响应速度
   - 检查网络延迟

### 调试方法

1. **查看详细错误**: 应用程序会显示具体的错误信息
2. **服务器日志**: 检查验证服务器的访问日志
3. **网络测试**: 使用curl测试接口连通性

```bash
curl -X POST https://your-server.com/api/license/verify \
  -H "Content-Type: application/json" \
  -d '{"license_key":"test","machine_code":"test","action":"verify"}'
```