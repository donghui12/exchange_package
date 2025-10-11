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
                        content = f.read()
                    
                    # 尝试解析完整JSON
                    try:
                        self.data = json.loads(content)
                        print(f"使用编码 {encoding} 成功解析完整JSON")
                        break
                    except json.JSONDecodeError as e:
                        print(f"JSON解析错误 (编码:{encoding}): {e}")
                        
                        # 尝试修复不完整的JSON
                        if self._try_fix_incomplete_json(content, encoding):
                            print(f"使用编码 {encoding} 成功解析部分数据")
                            break
                        
                except (UnicodeDecodeError, UnicodeError):
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
    
    def _try_fix_incomplete_json(self, content: str, encoding: str) -> bool:
        """尝试修复不完整的JSON数据"""
        try:
            print(f"尝试修复不完整的JSON (编码: {encoding})")
            
            # 找到最后一个完整的对象或数组
            stack = []
            last_complete_pos = 0
            in_string = False
            escape_next = False
            
            for i, char in enumerate(content):
                if escape_next:
                    escape_next = False
                    continue
                    
                if char == '\\':
                    escape_next = True
                    continue
                    
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                
                if not in_string:
                    if char in '{[':
                        stack.append(char)
                    elif char in '}]':
                        if stack:
                            if (char == '}' and stack[-1] == '{') or (char == ']' and stack[-1] == '['):
                                stack.pop()
                                if not stack:
                                    last_complete_pos = i + 1
            
            if last_complete_pos > 0:
                # 尝试解析到最后完整位置的内容
                partial_content = content[:last_complete_pos]
                try:
                    self.data = json.loads(partial_content)
                    print(f"成功解析部分数据，长度: {last_complete_pos}/{len(content)}")
                    return True
                except json.JSONDecodeError:
                    pass
            
            # 如果找不到完整的JSON，尝试提取基本信息
            return self._extract_basic_info(content)
            
        except Exception as e:
            print(f"修复JSON失败: {e}")
            return False
    
    def _extract_basic_info(self, content: str) -> bool:
        """从不完整的数据中提取基本信息"""
        try:
            print("尝试从不完整数据中提取基本信息")
            
            # 创建一个基本的数据结构
            self.data = {}
            
            # 使用正则表达式提取关键信息
            import re
            
            # 提取商品ID
            goods_id_match = re.search(r'"goods_id":(\d+)', content)
            if goods_id_match:
                goods_id = int(goods_id_match.group(1))
                self.data['goods'] = {'goods_id': goods_id}
                
                # 提取商品名称（可能是乱码）
                goods_name_match = re.search(r'"goods_name":"([^"]*)"', content)
                if goods_name_match:
                    goods_name = goods_name_match.group(1)
                    # 尝试修复编码问题
                    goods_name = self._fix_encoding(goods_name)
                    self.data['goods']['goods_name'] = goods_name
                
                # 提取短名称
                short_name_match = re.search(r'"short_name":"([^"]*)"', content)
                if short_name_match:
                    short_name = short_name_match.group(1)
                    short_name = self._fix_encoding(short_name)
                    self.data['goods']['short_name'] = short_name
                
                # 提取基本数值
                market_price_match = re.search(r'"market_price":(\d+)', content)
                if market_price_match:
                    self.data['goods']['market_price'] = int(market_price_match.group(1))
                
                quantity_match = re.search(r'"quantity":(\d+)', content)
                if quantity_match:
                    self.data['goods']['quantity'] = int(quantity_match.group(1))
                
                # 提取图片信息
                self._extract_images_from_text(content)
                
                # 提取SKU信息
                self._extract_sku_from_text(content)
                
                print(f"提取到商品ID: {goods_id}")
                return True
            
            return False
            
        except Exception as e:
            print(f"提取基本信息失败: {e}")
            return False
    
    def _fix_encoding(self, text: str) -> str:
        """尝试修复编码问题"""
        if not text:
            return text
            
        try:
            # 如果文本包含乱码字符，尝试重新编码
            if any(ord(c) > 127 for c in text):
                # 尝试不同的编码方式
                encodings = ['utf-8', 'gbk', 'gb2312', 'latin1']
                for encoding in encodings:
                    try:
                        # 将字符串编码为bytes再解码
                        fixed_text = text.encode('latin1').decode(encoding)
                        if not any(c in fixed_text for c in '��'):  # 避免明显的乱码
                            return fixed_text
                    except:
                        continue
        except:
            pass
            
        return text
    
    def _extract_images_from_text(self, content: str):
        """从文本中提取图片信息"""
        import re
        
        # 提取gallery中的图片
        gallery_matches = re.findall(r'"url":"([^"]*\.(?:jpg|jpeg|png|gif)[^"]*)"[^}]*"type":(\d+)', content)
        
        if not self.data.get('goods'):
            self.data['goods'] = {}
        
        self.data['goods']['gallery'] = []
        
        for i, (url, img_type) in enumerate(gallery_matches[:20]):  # 限制最多20张图片
            self.data['goods']['gallery'].append({
                'id': i + 1,
                'url': url,
                'type': int(img_type),
                'priority': i
            })
        
        # 提取decoration中的详情图
        decoration_matches = re.findall(r'"img_url":"([^"]*\.(?:jpg|jpeg|png|gif)[^"]*)"', content)
        self.data['goods']['decoration'] = []
        
        for i, img_url in enumerate(decoration_matches[:15]):  # 限制最多15张详情图
            self.data['goods']['decoration'].append({
                'type': 'image',
                'priority': i,
                'contents': [{'img_url': img_url}]
            })
    
    def _extract_sku_from_text(self, content: str):
        """从文本中提取SKU信息"""
        import re
        
        # 提取SKU信息 - 更宽松的匹配策略
        sku_id_matches = re.findall(r'"sku_id":(\d+)', content)
        
        if not self.data.get('sku'):
            self.data['sku'] = []
        
        # 如果找到了SKU ID，尝试提取对应的价格信息
        for i, sku_id in enumerate(sku_id_matches[:15]):  # 限制最多15个SKU
            sku_id = int(sku_id)
            
            # 在SKU ID附近寻找价格信息
            sku_section_pattern = f'"sku_id":{sku_id}[^{{}}]*?(?="sku_id":|$)'
            sku_section_match = re.search(sku_section_pattern, content)
            
            if sku_section_match:
                sku_section = sku_section_match.group(0)
                
                # 提取价格
                group_price_match = re.search(r'"group_price":(\d+)', sku_section)
                normal_price_match = re.search(r'"normal_price":(\d+)', sku_section)
                thumb_url_match = re.search(r'"thumb_url":"([^"]*)"', sku_section)
                
                group_price = int(group_price_match.group(1)) if group_price_match else 0
                normal_price = int(normal_price_match.group(1)) if normal_price_match else 0
                thumb_url = thumb_url_match.group(1) if thumb_url_match else ''
            else:
                # 如果找不到对应的section，使用默认值
                group_price = 1000 + i * 100  # 示例价格
                normal_price = group_price + 200
                thumb_url = ''
            
            self.data['sku'].append({
                'sku_id': sku_id,
                'group_price': group_price,
                'normal_price': normal_price,
                'thumb_url': thumb_url,
                'specs': [{'spec_key': '颜色', 'spec_value': f'规格{i+1}'}],
                'quantity': 100  # 默认库存
            })
    
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
        
        # 不同商品可能使用不同的type值表示主图
        # 常见的主图类型: 1, 13
        main_image_types = [1, 13]
        
        for img in gallery:
            img_type = img.get('type')
            if img_type in main_image_types:
                img_info = {
                    'url': img.get('url', ''),
                    'width': img.get('width', 0),
                    'height': img.get('height', 0),
                    'priority': img.get('priority', 0),
                    'type': img_type
                }
                if img_info['url']:
                    main_images.append(img_info)
        
        # 如果没有找到主图，尝试从其他类型中推断主图
        if not main_images:
            # 分析所有图片类型，选择优先级最低的作为主图
            type_analysis = {}
            for img in gallery:
                img_type = img.get('type')
                priority = img.get('priority', 999)
                if img_type not in type_analysis:
                    type_analysis[img_type] = {'min_priority': priority, 'count': 0}
                else:
                    type_analysis[img_type]['min_priority'] = min(type_analysis[img_type]['min_priority'], priority)
                type_analysis[img_type]['count'] += 1
            
            # 选择最小优先级的类型作为主图类型
            if type_analysis:
                main_type = min(type_analysis.keys(), key=lambda t: type_analysis[t]['min_priority'])
                print(f"自动识别主图类型: type={main_type}")
                
                for img in gallery:
                    if img.get('type') == main_type:
                        img_info = {
                            'url': img.get('url', ''),
                            'width': img.get('width', 0),
                            'height': img.get('height', 0),
                            'priority': img.get('priority', 0),
                            'type': img.get('type')
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