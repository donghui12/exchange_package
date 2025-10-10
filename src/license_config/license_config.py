"""
授权配置文件
"""

class LicenseConfig:
    """授权配置类"""
    
    # 验证服务器配置
    LICENSE_SERVER_URL = "http://42.192.40.156:18080/v1/shopee"
    
    # 超时设置（秒）
    REQUEST_TIMEOUT = 10
    
    # 应用信息
    APP_NAME = "素材包转换工具"
    APP_VERSION = "1.0.0"
    
    # 用户代理
    USER_AGENT = f"{APP_NAME}/{APP_VERSION}"
    
    @classmethod
    def get_verify_url(cls) -> str:
        """获取验证接口URL"""
        return f"{cls.LICENSE_SERVER_URL}/verify"
    
    @classmethod
    def get_request_headers(cls) -> dict:
        """获取请求头"""
        return {
            'Content-Type': 'application/json',
            'User-Agent': cls.USER_AGENT
        }