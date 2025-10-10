"""
授权码生成工具
用于生成测试授权码
"""
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.license_manager import LicenseManager

def main():
    """主程序"""
    print("=== 素材包转换工具 - 授权码生成器 ===\n")
    
    license_manager = LicenseManager()
    
    # 获取输入参数
    print("请输入要生成授权码的电脑码:")
    machine_code = input().strip()
    
    if not machine_code:
        print("错误: 电脑码不能为空")
        return
    
    print("\n请输入授权天数 (默认365天):")
    days_input = input().strip()
    
    try:
        days = int(days_input) if days_input else 365
    except ValueError:
        print("错误: 授权天数必须是数字")
        return
    
    if days <= 0:
        print("错误: 授权天数必须大于0")
        return
    
    # 生成授权码
    print(f"\n正在为电脑码 {machine_code} 生成 {days} 天的授权码...")
    
    try:
        license_key = license_manager.generate_license_key(machine_code, days)
        
        print(f"\n=== 授权码生成成功 ===")
        print(f"电脑码: {machine_code}")
        print(f"有效期: {days} 天")
        print(f"授权码: {license_key}")
        print(f"\n请将此授权码提供给用户进行激活")
        
        # 验证生成的授权码
        print(f"\n=== 验证授权码 ===")
        is_valid, message, expiry_date = license_manager.verify_license_key(license_key, machine_code)
        
        if is_valid:
            print(f"✓ 授权码验证成功")
            if expiry_date:
                print(f"✓ 过期时间: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"✗ 授权码验证失败: {message}")
        
    except Exception as e:
        print(f"错误: 生成授权码时发生异常: {str(e)}")

if __name__ == "__main__":
    main()