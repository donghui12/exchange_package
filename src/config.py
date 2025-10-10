"""
配置文件模块
Configuration module for the material converter
"""

class Config:
    """应用配置类"""
    
    # 应用信息
    APP_NAME = "素材包转换工具"
    APP_VERSION = "1.0.0"
    APP_AUTHOR = "Material Converter Team"
    
    # 默认设置
    DEFAULT_INTERVAL = 3  # 默认转换间隔(秒)
    DEFAULT_FORMAT = 2    # 默认导出格式(格式2)
    DEFAULT_CREATE_ZIP = True  # 默认创建zip压缩包
    
    # 文件夹名称配置
    FOLDER_NAMES = {
        "format1": {
            "main_images": "主图",
            "sku_images": "SKU图", 
            "detail_images": "详情图",
            "videos": "主图视频"
        },
        "format2": {
            "main_images": "产品主图",
            "sku_images": "SKU图",
            "detail_images": "详情图", 
            "videos": "产品视频"
        }
    }
    
    # 文件命名配置
    FILE_NAMING = {
        "main_image_prefix": "主图_",
        "detail_image_prefix": "详情图_",
        "excel_filename": "导入产品模板.xlsx"
    }
    
    # 图片下载配置
    DOWNLOAD_CONFIG = {
        "timeout": 30,          # 下载超时时间(秒)
        "max_retries": 3,       # 最大重试次数
        "chunk_size": 8192,     # 下载块大小
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # 支持的图片格式
    SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.webp']
    
    # Excel模板配置 - 按用户提供的15列格式
    EXCEL_HEADERS = [
        "* 产品标题", "货币类型", "货源链接", "货源平台", "产品主编号", 
        "详情描述", "货源类目", "属性", "SKU规格1", "SKU规格2",
        "平台SKU", "* SKU售价", "SKU库存", "SKU重量(KG)", "SKU尺寸(CM)"
    ]