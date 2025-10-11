"""
授权验证模块
实现基于接口验证的授权管理功能
"""
import hashlib
import platform
import uuid
import psutil
import json
import base64
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
try:
    import requests
except ImportError:
    requests = None  # 可选依赖

# 导入配置
try:
    from ..license_config.license_config import LicenseConfig
except ImportError:
    # 如果配置文件不存在，使用默认配置
    class LicenseConfig:
        LICENSE_SERVER_URL = "http://42.192.40.156:18080/v1/shopee"
        REQUEST_TIMEOUT = 10
        APP_NAME = "秒转助手"
        APP_VERSION = "1.0.0"
        
        @classmethod
        def get_verify_url(cls):
            return f"{cls.LICENSE_SERVER_URL}/verify"
        
        @classmethod
        def get_request_headers(cls):
            return {
                'Content-Type': 'application/json',
                'User-Agent': f"{cls.APP_NAME}/{cls.APP_VERSION}"
            }

class LicenseManager:
    """授权管理器"""
    
    def __init__(self, server_url: str = None):
        """初始化授权管理器"""
        self.license_file = "license.dat"
        # 使用配置中的服务器地址，或自定义地址
        self.server_url = server_url or LicenseConfig.LICENSE_SERVER_URL
        self.timeout = LicenseConfig.REQUEST_TIMEOUT
        
    def get_machine_code(self) -> str:
        """
        生成唯一的电脑码
        基于硬件信息生成唯一标识
        
        Returns:
            str: 电脑码
        """
        try:
            # 获取主板序列号
            motherboard_id = self._get_motherboard_id()
            
            # 获取CPU信息
            cpu_info = platform.processor()
            
            # 获取MAC地址
            mac_address = self._get_mac_address()
            
            # 获取硬盘序列号
            disk_serial = self._get_disk_serial()
            
            # 组合硬件信息
            hardware_info = f"{cpu_info}"
            
            # 生成MD5哈希
            machine_code = hashlib.md5(hardware_info.encode()).hexdigest().upper()
            
            # 格式化为更易读的格式
            formatted_code = '-'.join([machine_code[i:i+4] for i in range(0, len(machine_code), 4)])
            
            return formatted_code
            
        except Exception:
            # 如果硬件信息获取失败，使用系统信息生成备用码
            fallback_info = f"{platform.system()}|{platform.node()}|{platform.platform()}"
            fallback_code = hashlib.md5(fallback_info.encode()).hexdigest().upper()
            return '-'.join([fallback_code[i:i+4] for i in range(0, len(fallback_code), 4)])
    
    def _get_motherboard_id(self) -> str:
        """获取主板ID"""
        try:
            if platform.system() == "Windows":
                import subprocess
                result = subprocess.run(
                    ['wmic', 'baseboard', 'get', 'serialnumber'],
                    capture_output=True, text=True
                )
                lines = result.stdout.strip().split('\n')
                return lines[1].strip() if len(lines) > 1 else "UNKNOWN"
            elif platform.system() == "Darwin":  # macOS
                result = os.popen("system_profiler SPHardwareDataType | grep 'Serial Number'").read()
                return result.split(':')[-1].strip() if ':' in result else "UNKNOWN"
            else:  # Linux
                result = os.popen("sudo dmidecode -s baseboard-serial-number").read()
                return result.strip() or "UNKNOWN"
        except:
            return "UNKNOWN"
    
    def _get_mac_address(self) -> str:
        """获取MAC地址"""
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                           for elements in range(0, 2*6, 2)][::-1])
            return mac.upper()
        except:
            return "UNKNOWN"
    
    def _get_disk_serial(self) -> str:
        """获取硬盘序列号"""
        try:
            if platform.system() == "Windows":
                import subprocess
                result = subprocess.run(
                    ['wmic', 'diskdrive', 'get', 'serialnumber'],
                    capture_output=True, text=True
                )
                lines = result.stdout.strip().split('\n')
                return lines[1].strip() if len(lines) > 1 else "UNKNOWN"
            else:
                # 对于非Windows系统，使用分区信息作为替代
                partitions = psutil.disk_partitions()
                if partitions:
                    return str(hash(partitions[0].device))
                return "UNKNOWN"
        except:
            return "UNKNOWN"
    
    def generate_license_key(self, machine_code: str, days: int = 365) -> str:
        """
        生成授权码（服务端功能，这里用于演示）
        
        Args:
            machine_code: 电脑码
            days: 有效天数
            
        Returns:
            str: 授权码
        """
        expiry_date = datetime.now() + timedelta(days=days)
        
        license_data = {
            "machine_code": machine_code,
            "expiry_date": expiry_date.isoformat(),
            "app_name": "秒转助手",
            "version": "1.0.0"
        }
        
        # 将授权数据转换为JSON并编码
        license_json = json.dumps(license_data, separators=(',', ':'))
        license_bytes = license_json.encode('utf-8')
        
        # 简单的混淆处理（实际应用中应使用更安全的加密）
        secret_key = "MaterialConverter2024"
        mixed_data = self._xor_encrypt(license_bytes, secret_key.encode())
        
        # Base64编码
        license_key = base64.b64encode(mixed_data).decode('utf-8')
        
        # 格式化为更易读的格式
        return '-'.join([license_key[i:i+6] for i in range(0, len(license_key), 6)])
    
    def verify_license_online(self, license_key: str, machine_code: str) -> Tuple[bool, str, int]:
        """
        在线验证授权码
        
        Args:
            license_key: 授权码
            machine_code: 电脑码
            
        Returns:
            Tuple[bool, str, Optional[datetime]]: (是否有效, 状态信息, 过期时间)
        """
        if not requests:
            return False, "网络请求模块未安装，请安装 requests 库", None
            
        try:
            payload = {
                "active_code": license_key,
                "machine_code": machine_code,
            }
            print("url:", LicenseConfig.get_verify_url())

            print("payload:", payload)
            
            response = requests.get(LicenseConfig.get_verify_url(),params=payload)
            print("response:", response.status_code)
            
            result = response.json()
            print("this is resp", result)
            
            if result.get("code", 0) == 200:
                # 解析过期时间
                expiry_day = result.get("data", {}).get("expiry_date")
                
                return True, result.get("message", "授权验证成功"), expiry_day
            else:
                return False, result.get("message", "授权验证失败"), 0
                
        except requests.exceptions.Timeout:
            return False, "验证请求超时，请检查网络连接", 0
        except requests.exceptions.ConnectionError:
            return False, "无法连接到验证服务器，请检查网络连接", 0
        except requests.exceptions.RequestException as e:
            return False, f"网络请求失败: {str(e)}", 0
        except Exception as e:
            return False, f"验证过程中发生错误: {str(e)}", 0
    
    def _xor_encrypt(self, data: bytes, key: bytes) -> bytes:
        """XOR加密/解密"""
        key_len = len(key)
        return bytes([data[i] ^ key[i % key_len] for i in range(len(data))])
    
    def save_license(self, license_key: str) -> bool:
        """
        保存授权码到本地文件
        
        Args:
            license_key: 授权码
            
        Returns:
            bool: 保存是否成功
        """
        try:
            license_data = {
                "license_key": license_key,
                "machine_code": self.get_machine_code(),
                "save_date": datetime.now().isoformat()
            }
            
            # 简单编码存储
            data_json = json.dumps(license_data)
            encoded_data = base64.b64encode(data_json.encode()).decode()
            
            with open(self.license_file, 'w') as f:
                f.write(encoded_data)
            
            return True
        except Exception as e:
            print(f"保存授权码失败: {e}")
            return False
    
    def load_license(self) -> Optional[str]:
        """
        从本地文件加载授权信息
        
        Returns:
            Optional[str]: 授权码，如果不存在返回None
        """
        try:
            if not os.path.exists(self.license_file):
                return None
            
            with open(self.license_file, 'r') as f:
                encrypted_data = f.read().strip()
            
            # 解密
            data_json = base64.b64decode(encrypted_data.encode()).decode()
            license_data = json.loads(data_json)
            
            return license_data.get("license_key")
        except:
            return None
    
    def check_license(self) -> Tuple[bool, str, int]:
        """
        检查当前授权状态
        
        Returns:
            Tuple[bool, str, Optional[datetime]]: (是否有效, 状态信息, 过期时间)
        """
        # 尝试加载本地保存的授权码
        license_key = self.load_license()
        if not license_key:
            return False, "未找到授权信息，请输入授权码激活", None
        
        # 获取电脑码
        machine_code = self.get_machine_code()
        
        # 在线验证授权
        return self.verify_license_online(license_key, machine_code)
    
    def activate_license(self, license_key: str) -> Tuple[bool, str, Optional[datetime]]:
        """
        激活授权
        
        Args:
            license_key: 授权码
            
        Returns:
            Tuple[bool, str, Optional[datetime]]: (是否成功, 结果信息, 过期时间)
        """
        machine_code = self.get_machine_code()
        
        # 在线验证授权码
        is_valid, message, remaining_days = self.verify_license_online(license_key, machine_code)
        today = datetime.now().date()  # 只要日期，不包含时间
        expiry_date = today + timedelta(days=remaining_days)
        if is_valid:
            # 保存授权信息到本地
            if self.save_license(license_key):
                return True, message, expiry_date
            else:
                return True, f"{message}（注意：本地保存失败，下次启动需重新输入授权码）", expiry_date
        else:
            return False, message, expiry_date
    
    def set_server_url(self, url: str):
        """
        设置验证服务器地址
        
        Args:
            url: 服务器地址
        """
        self.server_url = url
    
    def get_server_url(self) -> str:
        """
        获取当前配置的服务器地址
        
        Returns:
            str: 服务器地址
        """
        return self.server_url