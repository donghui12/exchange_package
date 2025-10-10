"""
授权验证模块
实现卡密和电脑码的生成与验证功能
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

class LicenseManager:
    """授权管理器"""
    
    def __init__(self):
        """初始化授权管理器"""
        self.license_file = "license.dat"
        self.server_url = "https://api.example.com/license"  # 可配置的验证服务器
        
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
            hardware_info = f"{motherboard_id}|{cpu_info}|{mac_address}|{disk_serial}"
            
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
            "app_name": "素材包转换工具",
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
    
    def verify_license_key(self, license_key: str, machine_code: str) -> Tuple[bool, str, Optional[datetime]]:
        """
        验证授权码
        
        Args:
            license_key: 授权码
            machine_code: 电脑码
            
        Returns:
            Tuple[bool, str, Optional[datetime]]: (是否有效, 错误信息, 过期时间)
        """
        try:
            # 移除格式化字符
            clean_key = license_key.replace('-', '').replace(' ', '')
            
            # Base64解码
            try:
                mixed_data = base64.b64decode(clean_key.encode('utf-8'))
            except:
                return False, "授权码格式错误", None
            
            # 解密
            secret_key = "MaterialConverter2024"
            try:
                license_bytes = self._xor_encrypt(mixed_data, secret_key.encode())
                license_json = license_bytes.decode('utf-8')
                license_data = json.loads(license_json)
            except:
                return False, "授权码无效", None
            
            # 验证电脑码
            if license_data.get("machine_code") != machine_code:
                return False, "授权码与当前电脑不匹配", None
            
            # 验证应用名称
            if license_data.get("app_name") != "素材包转换工具":
                return False, "授权码不适用于此应用", None
            
            # 验证过期时间
            expiry_str = license_data.get("expiry_date")
            if not expiry_str:
                return False, "授权码缺少有效期信息", None
            
            try:
                expiry_date = datetime.fromisoformat(expiry_str)
            except:
                return False, "授权码有效期格式错误", None
            
            if datetime.now() > expiry_date:
                return False, f"授权码已过期（过期时间：{expiry_date.strftime('%Y-%m-%d %H:%M:%S')}）", expiry_date
            
            return True, "授权验证成功", expiry_date
            
        except Exception as e:
            return False, f"验证过程中发生错误：{str(e)}", None
    
    def _xor_encrypt(self, data: bytes, key: bytes) -> bytes:
        """XOR加密/解密"""
        key_len = len(key)
        return bytes([data[i] ^ key[i % key_len] for i in range(len(data))])
    
    def save_license(self, license_key: str) -> bool:
        """
        保存授权信息到本地文件
        
        Args:
            license_key: 授权码
            
        Returns:
            bool: 保存是否成功
        """
        try:
            license_data = {
                "license_key": license_key,
                "machine_code": self.get_machine_code(),
                "activation_date": datetime.now().isoformat()
            }
            
            # 简单混淆
            data_json = json.dumps(license_data)
            encrypted_data = base64.b64encode(data_json.encode()).decode()
            
            with open(self.license_file, 'w') as f:
                f.write(encrypted_data)
            
            return True
        except:
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
    
    def check_license(self) -> Tuple[bool, str, Optional[datetime]]:
        """
        检查当前授权状态
        
        Returns:
            Tuple[bool, str, Optional[datetime]]: (是否有效, 状态信息, 过期时间)
        """
        # 加载本地授权
        license_key = self.load_license()
        if not license_key:
            return False, "未找到授权信息，请激活软件", None
        
        # 获取电脑码
        machine_code = self.get_machine_code()
        
        # 验证授权
        return self.verify_license_key(license_key, machine_code)
    
    def activate_license(self, license_key: str) -> Tuple[bool, str, Optional[datetime]]:
        """
        激活授权
        
        Args:
            license_key: 授权码
            
        Returns:
            Tuple[bool, str, Optional[datetime]]: (是否成功, 结果信息, 过期时间)
        """
        machine_code = self.get_machine_code()
        
        # 验证授权码
        is_valid, message, expiry_date = self.verify_license_key(license_key, machine_code)
        
        if is_valid:
            # 保存授权信息
            if self.save_license(license_key):
                return True, f"激活成功！授权有效期至：{expiry_date.strftime('%Y-%m-%d %H:%M:%S')}", expiry_date
            else:
                return False, "激活成功但保存授权信息失败", expiry_date
        else:
            return False, message, expiry_date
    
    def online_verify(self, license_key: str, machine_code: str) -> Tuple[bool, str]:
        """
        在线验证授权（可选功能）
        
        Args:
            license_key: 授权码
            machine_code: 电脑码
            
        Returns:
            Tuple[bool, str]: (是否有效, 消息)
        """
        if not requests:
            return True, "网络验证模块未安装，使用离线验证"
            
        try:
            payload = {
                "license_key": license_key,
                "machine_code": machine_code,
                "app_name": "素材包转换工具",
                "version": "1.0.0"
            }
            
            response = requests.post(
                f"{self.server_url}/verify",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("valid", False), result.get("message", "验证失败")
            else:
                return False, "服务器验证失败"
                
        except Exception:
            # 网络错误时，允许离线验证
            return True, "网络连接失败，使用离线验证"