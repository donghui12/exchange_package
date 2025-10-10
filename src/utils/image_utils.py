"""
图片处理工具模块
提供图片处理和验证功能
"""
import os
from typing import Tuple, Optional
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class ImageUtils:
    """图片处理工具类"""
    
    @staticmethod
    def is_valid_image(file_path: str) -> bool:
        """
        检查文件是否为有效图片
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            bool: 是否为有效图片
        """
        if not PIL_AVAILABLE:
            # 如果PIL不可用，只检查文件扩展名
            valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif']
            ext = os.path.splitext(file_path)[1].lower()
            return ext in valid_extensions
        
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_image_info(file_path: str) -> dict:
        """
        获取图片信息
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            dict: 图片信息字典
        """
        info = {
            'width': 0,
            'height': 0,
            'format': '',
            'mode': '',
            'size_bytes': 0,
            'valid': False
        }
        
        try:
            # 获取文件大小
            if os.path.exists(file_path):
                info['size_bytes'] = os.path.getsize(file_path)
            
            if not PIL_AVAILABLE:
                info['valid'] = ImageUtils.is_valid_image(file_path)
                return info
            
            with Image.open(file_path) as img:
                info['width'] = img.width
                info['height'] = img.height
                info['format'] = img.format or ''
                info['mode'] = img.mode or ''
                info['valid'] = True
                
        except Exception:
            info['valid'] = False
        
        return info
    
    @staticmethod
    def resize_image(input_path: str, 
                    output_path: str, 
                    max_width: int = None, 
                    max_height: int = None, 
                    quality: int = 85) -> bool:
        """
        调整图片尺寸
        
        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径
            max_width: 最大宽度
            max_height: 最大高度
            quality: 输出质量(1-100)
            
        Returns:
            bool: 是否成功
        """
        if not PIL_AVAILABLE:
            return False
        
        try:
            with Image.open(input_path) as img:
                original_width, original_height = img.size
                
                # 计算新尺寸
                new_width = original_width
                new_height = original_height
                
                if max_width and new_width > max_width:
                    ratio = max_width / new_width
                    new_width = max_width
                    new_height = int(new_height * ratio)
                
                if max_height and new_height > max_height:
                    ratio = max_height / new_height
                    new_height = max_height
                    new_width = int(new_width * ratio)
                
                # 如果尺寸没有变化，直接复制文件
                if new_width == original_width and new_height == original_height:
                    img.save(output_path, quality=quality, optimize=True)
                else:
                    # 调整尺寸
                    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    resized_img.save(output_path, quality=quality, optimize=True)
                
                return True
                
        except Exception:
            return False
    
    @staticmethod
    def convert_image_format(input_path: str, 
                           output_path: str, 
                           target_format: str = 'JPEG', 
                           quality: int = 85) -> bool:
        """
        转换图片格式
        
        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径
            target_format: 目标格式(JPEG, PNG, WEBP等)
            quality: 输出质量(1-100)
            
        Returns:
            bool: 是否成功
        """
        if not PIL_AVAILABLE:
            return False
        
        try:
            with Image.open(input_path) as img:
                # 如果是JPEG格式且图片有透明通道，转换为RGB
                if target_format.upper() == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
                    # 创建白色背景
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # 保存图片
                save_kwargs = {'format': target_format, 'optimize': True}
                if target_format.upper() in ['JPEG', 'WEBP']:
                    save_kwargs['quality'] = quality
                
                img.save(output_path, **save_kwargs)
                return True
                
        except Exception:
            return False
    
    @staticmethod
    def compress_image(input_path: str, 
                      output_path: str = None, 
                      quality: int = 85, 
                      max_size_kb: int = None) -> bool:
        """
        压缩图片
        
        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径（如果为None则覆盖原文件）
            quality: 压缩质量(1-100)
            max_size_kb: 最大文件大小(KB)
            
        Returns:
            bool: 是否成功
        """
        if not PIL_AVAILABLE:
            return False
        
        if output_path is None:
            output_path = input_path
        
        try:
            with Image.open(input_path) as img:
                # 如果有透明通道且要保存为JPEG，转换为RGB
                if output_path.lower().endswith(('.jpg', '.jpeg')) and img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # 如果指定了最大文件大小，逐步降低质量
                if max_size_kb:
                    temp_quality = quality
                    while temp_quality > 10:
                        temp_path = output_path + '.temp'
                        img.save(temp_path, quality=temp_quality, optimize=True)
                        
                        # 检查文件大小
                        size_kb = os.path.getsize(temp_path) / 1024
                        if size_kb <= max_size_kb:
                            os.rename(temp_path, output_path)
                            return True
                        else:
                            os.remove(temp_path)
                            temp_quality -= 10
                    
                    # 如果无法达到目标大小，使用最低质量
                    img.save(output_path, quality=10, optimize=True)
                else:
                    img.save(output_path, quality=quality, optimize=True)
                
                return True
                
        except Exception:
            return False
    
    @staticmethod
    def create_thumbnail(input_path: str, 
                        output_path: str, 
                        size: Tuple[int, int] = (150, 150), 
                        quality: int = 85) -> bool:
        """
        创建缩略图
        
        Args:
            input_path: 输入图片路径
            output_path: 输出缩略图路径
            size: 缩略图尺寸(宽, 高)
            quality: 输出质量(1-100)
            
        Returns:
            bool: 是否成功
        """
        if not PIL_AVAILABLE:
            return False
        
        try:
            with Image.open(input_path) as img:
                # 创建缩略图（保持长宽比）
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # 如果是JPEG格式且有透明通道，转换为RGB
                if output_path.lower().endswith(('.jpg', '.jpeg')) and img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', size, (255, 255, 255))
                    # 计算居中位置
                    x = (size[0] - img.width) // 2
                    y = (size[1] - img.height) // 2
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, (x, y), mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                img.save(output_path, quality=quality, optimize=True)
                return True
                
        except Exception:
            return False
    
    @staticmethod
    def get_dominant_color(image_path: str) -> Optional[Tuple[int, int, int]]:
        """
        获取图片主要颜色
        
        Args:
            image_path: 图片路径
            
        Returns:
            Tuple[int, int, int]: RGB颜色值，如果失败返回None
        """
        if not PIL_AVAILABLE:
            return None
        
        try:
            with Image.open(image_path) as img:
                # 转换为RGB模式
                img = img.convert('RGB')
                
                # 缩小图片以提高性能
                img.thumbnail((100, 100))
                
                # 获取所有像素
                pixels = list(img.getdata())
                
                # 统计颜色出现频率
                color_count = {}
                for pixel in pixels:
                    if pixel in color_count:
                        color_count[pixel] += 1
                    else:
                        color_count[pixel] = 1
                
                # 找到出现最多的颜色
                dominant_color = max(color_count, key=color_count.get)
                return dominant_color
                
        except Exception:
            return None
    
    @staticmethod
    def add_watermark(input_path: str, 
                     output_path: str, 
                     watermark_text: str, 
                     position: str = 'bottom-right', 
                     opacity: float = 0.7) -> bool:
        """
        添加水印
        
        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径
            watermark_text: 水印文字
            position: 水印位置('top-left', 'top-right', 'bottom-left', 'bottom-right', 'center')
            opacity: 透明度(0.0-1.0)
            
        Returns:
            bool: 是否成功
        """
        if not PIL_AVAILABLE:
            return False
        
        try:
            from PIL import ImageDraw, ImageFont
            
            with Image.open(input_path) as img:
                # 创建透明图层
                watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(watermark)
                
                # 尝试使用默认字体
                try:
                    font_size = max(img.size) // 20  # 根据图片大小调整字体大小
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
                
                # 获取文字大小
                bbox = draw.textbbox((0, 0), watermark_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # 计算位置
                margin = 20
                if position == 'top-left':
                    x, y = margin, margin
                elif position == 'top-right':
                    x, y = img.width - text_width - margin, margin
                elif position == 'bottom-left':
                    x, y = margin, img.height - text_height - margin
                elif position == 'bottom-right':
                    x, y = img.width - text_width - margin, img.height - text_height - margin
                else:  # center
                    x, y = (img.width - text_width) // 2, (img.height - text_height) // 2
                
                # 绘制水印
                alpha = int(255 * opacity)
                draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, alpha))
                
                # 合并图片
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                watermarked = Image.alpha_composite(img, watermark)
                
                # 如果输出格式是JPEG，转换为RGB
                if output_path.lower().endswith(('.jpg', '.jpeg')):
                    background = Image.new('RGB', watermarked.size, (255, 255, 255))
                    background.paste(watermarked, mask=watermarked.split()[-1])
                    watermarked = background
                
                watermarked.save(output_path, quality=95, optimize=True)
                return True
                
        except Exception:
            return False