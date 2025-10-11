# 授权验证接口说明

## 接口地址配置

在 `src/config/license_config.py` 中配置验证服务器地址：

```python
class LicenseConfig:
    # 修改为您的实际验证服务器地址
    LICENSE_SERVER_URL = "https://your-license-server.com/api/license"
```

## 验证接口规范

### 请求

**URL:** `POST {LICENSE_SERVER_URL}/verify`

**Headers:**
```json
{
    "Content-Type": "application/json",
    "User-Agent": "秒转助手/1.0.0"
}
```

**请求体:**
```json
{
    "license_key": "用户输入的授权码",
    "machine_code": "基于硬件生成的电脑码",
    "app_name": "秒转助手",
    "app_version": "1.0.0",
    "action": "verify"
}
```

### 响应

**成功响应 (HTTP 200):**
```json
{
    "success": true,
    "message": "授权验证成功",
    "expiry_date": "2024-12-31T23:59:59",  // 可选，授权过期时间
    "license_type": "standard",            // 可选，授权类型
    "user_info": {                         // 可选，用户信息
        "company": "公司名称",
        "contact": "联系方式"
    }
}
```

**失败响应 (HTTP 200):**
```json
{
    "success": false,
    "message": "授权码无效或已过期",
    "error_code": "INVALID_LICENSE"        // 可选，错误代码
}
```

**服务器错误 (HTTP 4xx/5xx):**
```json
{
    "error": "服务器内部错误",
    "message": "详细错误信息"
}
```

## 电脑码生成规则

电脑码基于以下硬件信息生成：
- 主板序列号
- CPU信息
- MAC地址
- 硬盘序列号

格式：`XXXX-XXXX-XXXX-XXXX-XXXX-XXXX-XXXX-XXXX`

## 客户端行为

1. **启动检查**: 每次应用启动时自动验证授权
2. **本地缓存**: 成功验证后将授权码保存到本地
3. **错误处理**: 网络异常或服务器错误时提示用户
4. **过期提醒**: 授权即将过期时（7天内）显示提醒

## 超时设置

- 默认超时时间：10秒
- 可在配置文件中修改 `REQUEST_TIMEOUT` 参数

## 安全建议

1. 使用HTTPS确保传输安全
2. 服务端验证请求来源和频率
3. 实现授权码的黑名单机制
4. 记录验证日志用于审计