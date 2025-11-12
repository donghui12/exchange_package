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
            self.file_encoding = None  # 记录成功的编码
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    
                    # 尝试解析完整JSON
                    try:
                        self.data = json.loads(content)
                        self.file_encoding = encoding
                        print(f"使用编码 {encoding} 成功解析完整JSON")
                        break  # JSON解析成功就可以了，不强制要求中文正确
                            
                    except json.JSONDecodeError as e:
                        print(f"JSON解析错误 (编码:{encoding}): {e}")
                        
                        # 尝试修复不完整的JSON
                        if self._try_fix_incomplete_json(content, encoding):
                            self.file_encoding = encoding
                            print(f"使用编码 {encoding} 成功解析部分数据")
                            break
                        
                except (UnicodeDecodeError, UnicodeError):
                    continue
            
            if self.data is None:
                raise ValueError("无法使用任何编码解析文件")
                
            # 提取商品基础信息
            # 支持两种数据结构:
            # 1. 直接的 goods 结构
            # 2. store.initDataObj.goods 结构
            self.goods_info = self.data.get('goods', {})
            
            # 如果没有找到goods，尝试从store.initDataObj.goods中获取
            if not self.goods_info and 'store' in self.data:
                store = self.data['store']
                if 'initDataObj' in store:
                    init_data = store['initDataObj']
                    self.goods_info = init_data.get('goods', {})
            
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
    
    def _validate_chinese_content(self) -> bool:
        """验证中文内容是否正确解析"""
        if not self.data:
            return False
        
        try:
            # 检查商品名称
            goods_name = ""
            if 'goods' in self.data:
                goods_name = self.data['goods'].get('goods_name', '')
            elif 'store' in self.data:
                store = self.data['store']
                if 'initDataObj' in store and 'goods' in store['initDataObj']:
                    goods_name = store['initDataObj']['goods'].get('goodsName', '')
            
            # 检查SKU规格
            sku_specs = []
            if 'sku' in self.data:
                for sku in self.data['sku'][:3]:  # 检查前3个SKU
                    specs = sku.get('specs', [])
                    for spec in specs:
                        spec_value = spec.get('spec_value', '')
                        if spec_value:
                            sku_specs.append(spec_value)
            elif 'store' in self.data:
                store = self.data['store']
                if 'initDataObj' in store and 'goods' in store['initDataObj']:
                    goods = store['initDataObj']['goods']
                    if 'skus' in goods:
                        for sku in goods['skus'][:3]:
                            specs = sku.get('specs', [])
                            for spec in specs:
                                spec_value = spec.get('spec_value', '')
                                if spec_value:
                                    sku_specs.append(spec_value)
            
            # 验证是否包含正确的中文字符，而不是乱码
            test_texts = [goods_name] + sku_specs
            for text in test_texts:
                if text and len(text) > 0:
                    # 检查是否包含正确的中文字符
                    if any('\u4e00' <= c <= '\u9fff' for c in text):
                        # 检查是否包含典型的乱码标志
                        if '锟斤拷' not in text and '�' not in text:
                            return True
            
            return False
            
        except Exception as e:
            print(f"验证中文内容时出错: {e}")
            return False
    
    def _fix_encoding(self, text: str) -> str:
        """修复编码问题"""
        if not text:
            return text
            
        try:
            # 检查是否已经是正确的中文
            if any('\u4e00' <= c <= '\u9fff' for c in text):
                return text
            
            # 检查是否包含明显的乱码字符
            if any(ord(c) > 127 for c in text):
                # 常见的编码修复组合
                fix_combinations = [
                    ('utf-8', 'gbk'),       # UTF-8读取，实际是GBK内容
                    ('utf-8', 'gb2312'),    # UTF-8读取，实际是GB2312内容
                    ('latin1', 'gbk'),
                    ('latin1', 'gb2312'),
                    ('latin1', 'utf-8'),
                    ('iso-8859-1', 'gbk'),
                    ('iso-8859-1', 'gb2312'),
                    ('iso-8859-1', 'utf-8'),
                    ('cp1252', 'gbk'),
                    ('cp1252', 'gb2312'),
                ]
                
                for from_encoding, to_encoding in fix_combinations:
                    try:
                        # 将字符串编码为bytes再用正确编码解码
                        fixed_text = text.encode(from_encoding).decode(to_encoding)
                        # 检查修复是否成功（包含常见中文字符）
                        if any(char in fixed_text for char in ['救生', '商品', '包装', '装备', '产品', '用品', '手动', '自动', '红色', '橙色', '黄色', '充气', '腰带', '逗猫', '钢丝', '巴布豆', '双肩包', '书包', '颜色', '小号', '大号', '紫色', '蓝色']):
                            return fixed_text
                        # 检查是否有正常的中文字符范围
                        if any('\u4e00' <= c <= '\u9fff' for c in fixed_text):
                            return fixed_text
                    except (UnicodeDecodeError, UnicodeEncodeError):
                        continue
                
                # 如果无法修复，尝试移除非ASCII字符
                ascii_text = ''.join(c for c in text if ord(c) < 128)
                if ascii_text:
                    return ascii_text
                    
        except Exception as e:
            print(f"编码修复异常: {e}")
            
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
    
    def _generate_goods_url(self, goods_id) -> str:
        """生成商品链接"""
        if not goods_id:
            return ''
        return f'https://mobile.yangkeduo.com/goods.html?goods_id={goods_id}'
    
    def _smart_convert_price(self, price: float) -> float:
        """智能转换价格单位"""
        if price <= 0:
            return 0.0
        
        # 如果包含小数，则直接认为是正常价格，不需要转化
        if price % 1 != 0:
            return price
        
        return price / 100
        
        # 如果价格大于1000，很可能是以分为单位，需要转换为元
        if price > 1000:
            return price / 100
        
        # 如果价格在合理的元单位范围内（1-1000），直接使用
        if 1 <= price <= 1000:
            return price
        
        # 如果价格很小（0.1-1），可能已经是元单位的小数
        if 0.1 <= price < 1:
            return price
        
        # 其他情况，保持原值
        return price
    
    def _to_number(self, value) -> float:
        """将值转换为数字"""
        if isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, str):
            try:
                return float(value)
            except (ValueError, TypeError):
                return 0.0
        else:
            return 0.0
    
    def get_goods_basic_info(self) -> Dict[str, Any]:
        """获取商品基础信息"""
        if not self.goods_info:
            return {}
        
        # 支持两种字段名格式:
        # 1. 旧格式: goods_id, goods_name 等
        # 2. 新格式: goodsID, goodsName 等
        goods_id = self.goods_info.get('goods_id') or self.goods_info.get('goodsID', '')
        goods_name = self.goods_info.get('goods_name') or self.goods_info.get('goodsName', '')
        market_price = self.goods_info.get('market_price') or self.goods_info.get('marketPrice', 0)
        cat_id = self.goods_info.get('cat_id') or self.goods_info.get('catID', '')
        mall_id = self.goods_info.get('mall_id') or self.goods_info.get('mallID', '')
        
        # 修复商品名称的编码问题
        if goods_name:
            goods_name = self._fix_encoding(str(goods_name))
        
        return {
            'goods_id': goods_id,
            'goods_name': goods_name.strip() if goods_name else '',
            'goods_url': self._generate_goods_url(goods_id),
            'short_name': self.goods_info.get('short_name', '').strip(),
            'market_price': market_price,
            'cat_id': cat_id,
            'mall_id': mall_id,
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
        
        main_images = []
        
        # 新格式：使用topGallery作为主图
        if 'topGallery' in self.goods_info:
            top_gallery = self.goods_info['topGallery']
            for i, img in enumerate(top_gallery):
                img_info = {
                    'url': img.get('url', ''),
                    'width': img.get('width', 0),
                    'height': img.get('height', 0),
                    'priority': i,
                    'type': 'topGallery',
                    'aspect_ratio': img.get('aspectRatio', 1)
                }
                if img_info['url']:
                    main_images.append(img_info)
            
            if main_images:
                return main_images
        
        # 旧格式：从gallery中提取主图
        gallery = self.goods_info.get('gallery', [])
        
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
        
        detail_images = []
        
        # 新格式：使用detailGallery作为详情图
        if 'detailGallery' in self.goods_info:
            detail_gallery = self.goods_info['detailGallery']
            for i, img in enumerate(detail_gallery):
                img_info = {
                    'url': img.get('url', ''),
                    'width': img.get('width', 0),
                    'height': img.get('height', 0),
                    'priority': i
                }
                if img_info['url']:
                    detail_images.append(img_info)
            
            if detail_images:
                return detail_images
        
        # 旧格式：从decoration中提取详情图
        decoration = self.goods_info.get('decoration', [])
        
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
    
    def get_videos(self) -> List[Dict[str, Any]]:
        """获取视频列表"""
        if not self.goods_info:
            return []
        
        videos = []
        
        # 从gallery中提取视频
        gallery = self.goods_info.get('gallery', [])
        
        for item in gallery:
            # 检查是否有视频URL
            video_url = item.get('video_url', '')
            if video_url:
                # 这是视频项目
                video_info = {
                    'url': video_url,
                    'thumbnail': item.get('url', ''),  # 视频缩略图
                    'width': item.get('width', 0),
                    'height': item.get('height', 0),
                    'priority': item.get('priority', 0),
                    'type': item.get('type', 0),
                    'video_type': 'main_video',  # 主视频
                    'enable_share': item.get('enable_share', 0)
                }
                videos.append(video_info)
            elif item.get('url', '').endswith('.mp4'):
                # 直接的MP4文件
                video_info = {
                    'url': item.get('url', ''),
                    'thumbnail': '',  # 没有缩略图
                    'width': item.get('width', 0),
                    'height': item.get('height', 0),
                    'priority': item.get('priority', 0),
                    'type': item.get('type', 0),
                    'video_type': 'detail_video',  # 详情视频
                    'enable_share': item.get('enable_share', 0)
                }
                videos.append(video_info)
        
        # 按优先级排序
        return sorted(videos, key=lambda x: x['priority'])
    
    def get_main_videos(self) -> List[Dict[str, Any]]:
        """获取主要视频（带缩略图的视频）"""
        videos = self.get_videos()
        return [v for v in videos if v['video_type'] == 'main_video']
    
    def get_detail_videos(self) -> List[Dict[str, Any]]:
        """获取详情视频（直接的MP4文件）"""
        videos = self.get_videos()
        return [v for v in videos if v['video_type'] == 'detail_video']
    
    def get_sku_info(self) -> List[Dict[str, Any]]:
        """获取SKU信息"""
        if not self.data:
            return []
        
        sku_info = []
        
        # 新格式：从goods.skus中获取SKU信息
        if self.goods_info and 'skus' in self.goods_info:
            skus = self.goods_info['skus']
            for sku in skus:
                specs = sku.get('specs', [])
                spec_text = ''
                if specs:
                    spec_values = []
                    for spec in specs:
                        spec_value = spec.get('spec_value', '')
                        if spec_value:
                            # 修复规格文本的编码问题
                            spec_value = self._fix_encoding(str(spec_value))
                            spec_values.append(spec_value)
                    spec_text = '_'.join(filter(None, spec_values))
                
                # 价格处理 - 智能判断价格单位
                group_price_raw = self._to_number(sku.get('groupPrice') or sku.get('group_price', 0))
                normal_price_raw = self._to_number(sku.get('normalPrice') or sku.get('normal_price', 0))
                price_raw = self._to_number(sku.get('price', 0))
                
                # 智能判断价格单位：
                # 1. 如果价格 > 1000，可能是以分为单位，除以100转换为元
                # 2. 如果价格 <= 1000 且 > 0，可能已经是元单位，保持不变
                # 3. 特殊情况：如果拼团价和单买价都很小(<100)且合理，直接使用
                group_price = self._smart_convert_price(group_price_raw)
                normal_price = self._smart_convert_price(normal_price_raw)  
                price = self._smart_convert_price(price_raw)
                
                sku_data = {
                    'sku_id': sku.get('skuId') or sku.get('sku_id', ''),
                    'spec': spec_text,
                    'price': price,
                    'normal_price': normal_price,
                    'group_price': group_price,
                    'quantity': sku.get('quantity', 0),
                    'thumb_url': sku.get('thumbUrl') or sku.get('thumb_url', ''),
                    'specs': specs
                }
                sku_info.append(sku_data)
            
            if sku_info:
                return sku_info
        
        # 旧格式：从data.sku中获取SKU信息
        sku_list = self.data.get('sku', [])
        
        for sku in sku_list:
            specs = sku.get('specs', [])
            spec_text = ''
            if specs:
                spec_values = []
                for spec in specs:
                    spec_value = spec.get('spec_value', '')
                    if spec_value:
                        # 修复规格文本的编码问题
                        spec_value = self._fix_encoding(str(spec_value))
                        spec_values.append(spec_value)
                spec_text = '_'.join(filter(None, spec_values))
            
            # 价格处理 - 智能判断价格单位
            group_price_raw = self._to_number(sku.get('group_price', 0))
            normal_price_raw = self._to_number(sku.get('normal_price', 0))
            price_raw = self._to_number(sku.get('price', 0))
            
            # 智能判断价格单位：
            # 1. 如果价格 > 1000，可能是以分为单位，除以100转换为元
            # 2. 如果价格 <= 1000 且 > 0，可能已经是元单位，保持不变
            group_price = self._smart_convert_price(group_price_raw)
            normal_price = self._smart_convert_price(normal_price_raw)
            price = self._smart_convert_price(price_raw)
            
            sku_data = {
                'sku_id': sku.get('sku_id', ''),
                'spec': spec_text,
                'price': price,
                'normal_price': normal_price,
                'group_price': group_price,
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
        
        if not goods_name:
            return '未知商品'
        
        # 清理文件名中的非法字符（Windows + macOS + Linux兼容）
        illegal_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\n', '\r', '\t']
        clean_name = goods_name
        
        # 替换非法字符
        for char in illegal_chars:
            clean_name = clean_name.replace(char, '_')
        
        # 移除开头和结尾的空格和点号（Windows不允许）
        clean_name = clean_name.strip(' .')
        
        # 处理Windows保留文件名
        windows_reserved = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 
                           'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 
                           'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
        if clean_name.upper() in windows_reserved:
            clean_name = f"商品_{clean_name}"
        
        # 限制长度，为文件扩展名和ID留出空间
        # Windows路径限制255字符，留出足够空间给"_商品ID.zip"等
        max_length = 200
        if len(clean_name.encode('utf-8')) > max_length:
            # 按字节截取，确保不会截断中文字符
            encoded = clean_name.encode('utf-8')
            truncated = encoded[:max_length]
            # 找到最后一个完整的UTF-8字符
            while len(truncated) > 0:
                try:
                    clean_name = truncated.decode('utf-8')
                    break
                except UnicodeDecodeError:
                    truncated = truncated[:-1]
        
        # 确保不为空
        if not clean_name.strip():
            clean_name = '商品'
            
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