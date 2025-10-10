"""
PDD数据解析模块
用于解析拼多多商品JSON数据文件
"""
import json
import os
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

class PDDDataParser:
    """拼多多数据解析器"""
    
    def __init__(self):
        self.data = None
        self.goods_info = None
        
    def parse_file(self, file_path: str) -> bool:
        """
        解析PDD数据文件
        
        Args:
            file_path: PDD数据文件路径
            
        Returns:
            bool: 解析是否成功
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 尝试多种编码读取文件
            encodings = ['gbk', 'utf-8', 'gb2312', 'latin1']
            self.data = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        self.data = json.load(f)
                    print(f"使用编码 {encoding} 成功解析文件")
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误 (编码:{encoding}): {e}")
                    continue
            
            if self.data is None:
                raise ValueError("无法使用任何编码解析文件")
                
            # 提取商品基础信息
            self.goods_info = self.data.get('goods', {})
            
            if not self.goods_info:
                raise ValueError("文件中未找到商品信息")
                
            return True
            
        except (json.JSONDecodeError, FileNotFoundError, Exception) as e:
            print(f"解析文件失败: {e}")
            return False
    
    def get_goods_basic_info(self) -> Dict[str, Any]:
        """获取商品基础信息"""
        if not self.goods_info:
            return {}
            
        return {
            'goods_id': self.goods_info.get('goods_id', ''),
            'goods_name': self.goods_info.get('goods_name', '').strip(),
            'short_name': self.goods_info.get('short_name', '').strip(),
            'market_price': self.goods_info.get('market_price', 0),
            'cat_id': self.goods_info.get('cat_id', ''),
            'mall_id': self.goods_info.get('mall_id', ''),
            'quantity': self.goods_info.get('quantity', 0),
            'sold_quantity': self.goods_info.get('sold_quantity', 0),
            'customer_num': self.goods_info.get('customer_num', 0)
        }
    
    def get_price_info(self) -> Dict[str, Any]:
        """获取价格信息"""
        if not self.data:
            return {}
            
        price_data = self.data.get('price', {})
        return {
            'min_group_price': price_data.get('min_group_price', 0),
            'max_group_price': price_data.get('max_group_price', 0),
            'min_normal_price': price_data.get('min_normal_price', 0),
            'max_normal_price': price_data.get('max_normal_price', 0),
            'line_price': price_data.get('line_price', 0)
        }
    
    def get_main_images(self) -> List[Dict[str, Any]]:
        """获取主图列表"""
        if not self.goods_info:
            return []
            
        gallery = self.goods_info.get('gallery', [])
        main_images = []
        
        for img in gallery:
            if img.get('type') == 1:  # type=1 表示主图
                img_info = {
                    'url': img.get('url', ''),
                    'width': img.get('width', 0),
                    'height': img.get('height', 0),
                    'priority': img.get('priority', 0)
                }
                if img_info['url']:
                    main_images.append(img_info)
        
        # 按优先级排序
        main_images.sort(key=lambda x: x['priority'])
        return main_images
    
    def get_detail_images(self) -> List[Dict[str, Any]]:
        """获取详情图列表"""
        if not self.goods_info:
            return []
            
        decoration = self.goods_info.get('decoration', [])
        detail_images = []
        
        for item in decoration:
            if item.get('type') == 'image':
                contents = item.get('contents', [])
                for content in contents:
                    img_url = content.get('img_url', '')
                    if img_url:
                        img_info = {
                            'url': img_url,
                            'width': content.get('width', 0),
                            'height': content.get('height', 0),
                            'priority': item.get('priority', 0)
                        }
                        detail_images.append(img_info)
        
        # 按优先级排序
        detail_images.sort(key=lambda x: x['priority'])
        return detail_images
    
    def get_sku_info(self) -> List[Dict[str, Any]]:
        """获取SKU信息"""
        if not self.data:
            return []
            
        sku_list = self.data.get('sku', [])
        sku_info = []
        
        for sku in sku_list:
            specs = sku.get('specs', [])
            spec_text = ''
            if specs:
                spec_values = [spec.get('spec_value', '') for spec in specs]
                spec_text = '_'.join(filter(None, spec_values))
            
            sku_data = {
                'sku_id': sku.get('sku_id', ''),
                'spec': spec_text,
                'price': sku.get('price', 0),
                'normal_price': sku.get('normal_price', 0),
                'group_price': sku.get('group_price', 0),
                'quantity': sku.get('quantity', 0),
                'thumb_url': sku.get('thumb_url', ''),
                'specs': specs
            }
            sku_info.append(sku_data)
            
        return sku_info
    
    def get_sku_images(self) -> List[Dict[str, Any]]:
        """获取SKU图片列表"""
        sku_list = self.get_sku_info()
        sku_images = []
        
        for i, sku in enumerate(sku_list, 1):
            thumb_url = sku.get('thumb_url', '')
            if thumb_url:
                img_info = {
                    'url': thumb_url,
                    'spec': sku.get('spec', f'SKU{i}'),
                    'sku_id': sku.get('sku_id', ''),
                    'index': i
                }
                sku_images.append(img_info)
                
        return sku_images
    
    def get_clean_goods_name(self) -> str:
        """获取清理后的商品名称（用于文件夹命名）"""
        goods_info = self.get_goods_basic_info()
        goods_name = goods_info.get('goods_name', '')
        
        # 清理文件名中的非法字符
        illegal_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        clean_name = goods_name
        for char in illegal_chars:
            clean_name = clean_name.replace(char, '_')
            
        # 限制长度避免路径过长
        if len(clean_name) > 50:
            clean_name = clean_name[:50]
            
        return clean_name.strip()
    
    def get_folder_name(self) -> str:
        """获取商品文件夹名称"""
        goods_info = self.get_goods_basic_info()
        clean_name = self.get_clean_goods_name()
        goods_id = goods_info.get('goods_id', '')
        
        if clean_name and goods_id:
            return f"{clean_name}_{goods_id}"
        elif goods_id:
            return f"商品_{goods_id}"
        else:
            return "未知商品"
    
    def get_image_extension(self, url: str) -> str:
        """从URL获取图片扩展名"""
        try:
            parsed = urlparse(url)
            path = parsed.path.lower()
            
            if path.endswith('.jpg') or path.endswith('.jpeg'):
                return '.jpg'
            elif path.endswith('.png'):
                return '.png'
            elif path.endswith('.webp'):
                return '.webp'
            else:
                return '.jpg'  # 默认使用jpg
                
        except Exception:
            return '.jpg'
    
    def get_summary(self) -> Dict[str, Any]:
        """获取数据汇总信息"""
        goods_info = self.get_goods_basic_info()
        main_images = self.get_main_images()
        detail_images = self.get_detail_images()
        sku_images = self.get_sku_images()
        
        return {
            'goods_name': goods_info.get('goods_name', ''),
            'goods_id': goods_info.get('goods_id', ''),
            'folder_name': self.get_folder_name(),
            'main_images_count': len(main_images),
            'detail_images_count': len(detail_images),
            'sku_images_count': len(sku_images),
            'total_images': len(main_images) + len(detail_images) + len(sku_images)
        }