from PIL import Image, ImageEnhance
import os
import random
import math
import threading
from concurrent.futures import ThreadPoolExecutor
import traceback

class ImageProcessor:
    @staticmethod
    def preview_image(image_path, process_type, **kwargs):
        """生成预览图片
        Args:
            image_path: 输入图片路径
            process_type: 处理类型，可选值：'resize', 'compress', 'random', 'exposure', 'filter'
            **kwargs: 处理参数
        Returns:
            PIL.Image对象
        """
        try:
            with Image.open(image_path) as img:
                preview_img = img.copy()
                if process_type == 'resize':
                    width = kwargs.get('width')
                    height = kwargs.get('height')
                    keep_ratio = kwargs.get('keep_ratio', True)
                    return ImageProcessor._preview_resize(preview_img, width, height, keep_ratio)
                elif process_type == 'exposure':
                    brightness_factor = kwargs.get('brightness_factor', 1.0)
                    return ImageProcessor._preview_exposure(preview_img, brightness_factor)
                elif process_type == 'filter':
                    filter_type = kwargs.get('filter_type')
                    return ImageProcessor._preview_filter(preview_img, filter_type)
                return preview_img
        except Exception as e:
            print(f"生成预览图片时出错: {str(e)}")
            raise
    
    @staticmethod
    def _preview_resize(img, width=None, height=None, keep_ratio=True):
        """预览调整尺寸效果"""
        original_width, original_height = img.size
        new_width = width
        new_height = height
        
        if keep_ratio:
            if width and height:
                ratio_w = width / original_width
                ratio_h = height / original_height
                ratio = min(ratio_w, ratio_h)
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)
            elif width:
                ratio = width / original_width
                new_width = width
                new_height = int(original_height * ratio)
            else:
                ratio = height / original_height
                new_height = height
                new_width = int(original_width * ratio)
        
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    @staticmethod
    def _preview_exposure(img, brightness_factor):
        """预览曝光度调整效果"""
        if img.mode in ('RGBA', 'LA'):
            alpha = img.getchannel('A')
            img = img.convert('RGB')
            enhancer = ImageEnhance.Brightness(img)
            adjusted = enhancer.enhance(brightness_factor)
            adjusted = adjusted.convert('RGBA')
            adjusted.putalpha(alpha)
            return adjusted
        else:
            enhancer = ImageEnhance.Brightness(img)
            return enhancer.enhance(brightness_factor)
    
    @staticmethod
    def _preview_filter(img, filter_type):
        """预览滤镜效果"""
        if filter_type == 'grayscale':
            return img.convert('L').convert('RGB')
        elif filter_type == 'blur':
            from PIL import ImageFilter
            return img.filter(ImageFilter.GaussianBlur(radius=2))
        elif filter_type == 'sharpen':
            from PIL import ImageFilter
            return img.filter(ImageFilter.SHARPEN)
        elif filter_type == 'contour':
            from PIL import ImageFilter
            return img.filter(ImageFilter.CONTOUR)
        return img

    @staticmethod
    def resize_image(image_path, output_path, width=None, height=None, keep_ratio=True, callback=None):
        """调整图片尺寸"""
        try:
            # 使用with语句确保图片文件正确关闭
            with Image.open(image_path) as img:
                original_width, original_height = img.size
                new_width = width
                new_height = height
                
                if keep_ratio:
                    if width and height:
                        ratio_w = width / original_width
                        ratio_h = height / original_height
                        ratio = min(ratio_w, ratio_h)
                        new_width = int(original_width * ratio)
                        new_height = int(original_height * ratio)
                    elif width:
                        ratio = width / original_width
                        new_width = width
                        new_height = int(original_height * ratio)
                    else:
                        ratio = height / original_height
                        new_height = height
                        new_width = int(original_width * ratio)
                
                # 优化内存使用：对于大图片，先缩小再处理
                if original_width > 3000 or original_height > 3000:
                    # 先进行粗略缩小以减少内存使用
                    intermediate_size = (min(original_width, 3000), min(original_height, 3000))
                    img.thumbnail(intermediate_size, Image.Resampling.LANCZOS)
                
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                resized_img.save(output_path)
                
                if callback:
                    callback()
        except Exception as e:
            print(f"调整图片尺寸时出错: {str(e)}")
            raise
    
    @staticmethod
    def compress_image(image_path, output_path, quality, callback=None):
        """压缩图片"""
        with Image.open(image_path) as img:
            if img.format == 'PNG' and img.mode in ('RGBA', 'LA'):
                img = img.convert('RGB')
            img.save(output_path, quality=quality, optimize=True)
            
            if callback:
                callback()
    
    @staticmethod
    def random_adjust(image_path, output_path, max_rotation, callback=None):
        """随机微调图片"""
        with Image.open(image_path) as img:
            width, height = img.size
            angle = random.uniform(-max_rotation, max_rotation)
            
            radian = math.radians(abs(angle))
            cos_a = math.cos(radian)
            sin_a = math.sin(radian)
            new_width = int(width * cos_a + height * sin_a)
            new_height = int(height * cos_a + width * sin_a)
            
            scale = max(width / new_width, height / new_height)
            scale *= 1.2
            
            enlarged_size = (int(img.size[0] * scale), int(img.size[1] * scale))
            img = img.resize(enlarged_size, Image.Resampling.LANCZOS)
            img = img.rotate(angle, Image.BICUBIC, expand=False)
            
            left = (img.size[0] - width) // 2
            top = (img.size[1] - height) // 2
            img = img.crop((left, top, left + width, top + height))
            img.save(output_path)
            
            if callback:
                callback()
    
    @staticmethod
    def adjust_exposure(image_path, output_path, brightness_factor, callback=None):
        """调整图片曝光度"""
        try:
            with Image.open(image_path) as img:
                if img.mode in ('RGBA', 'LA'):
                    alpha = img.getchannel('A')
                    img = img.convert('RGB')
                    enhancer = ImageEnhance.Brightness(img)
                    adjusted = enhancer.enhance(brightness_factor)
                    adjusted = adjusted.convert('RGBA')
                    adjusted.putalpha(alpha)
                else:
                    enhancer = ImageEnhance.Brightness(img)
                    adjusted = enhancer.enhance(brightness_factor)
                
                if adjusted.mode == 'RGBA':
                    adjusted.save(output_path, 'PNG')
                else:
                    adjusted.save(output_path, quality=95, optimize=True)
                    
                if callback:
                    callback()
        except Exception as e:
            print(f"调整曝光度时出错: {str(e)}")
            raise
            
    @staticmethod
    def apply_filter(image_path, output_path, filter_type, callback=None):
        """应用滤镜效果
        
        Args:
            image_path: 输入图片路径
            output_path: 输出图片路径
            filter_type: 滤镜类型，可选值：'grayscale', 'sepia', 'negative', 'blur', 'sharpen', 'contour'
            callback: 回调函数
        """
        try:
            with Image.open(image_path) as img:
                # 保存透明通道（如果有）
                has_alpha = img.mode in ('RGBA', 'LA')
                if has_alpha:
                    alpha = img.getchannel('A')
                    img = img.convert('RGB')
                
                # 应用不同的滤镜效果
                if filter_type == 'grayscale':
                    # 灰度
                    filtered = img.convert('L').convert('RGB')
                
                elif filter_type == 'sepia':
                    # 复古棕褐色
                    img = img.convert('RGB')
                    filtered = Image.new('RGB', img.size)
                    for x in range(img.width):
                        for y in range(img.height):
                            r, g, b = img.getpixel((x, y))
                            # 棕褐色算法
                            tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                            tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                            tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                            filtered.putpixel((x, y), (min(tr, 255), min(tg, 255), min(tb, 255)))
                
                elif filter_type == 'negative':
                    # 负片效果
                    img = img.convert('RGB')
                    filtered = Image.new('RGB', img.size)
                    for x in range(img.width):
                        for y in range(img.height):
                            r, g, b = img.getpixel((x, y))
                            filtered.putpixel((x, y), (255-r, 255-g, 255-b))
                
                elif filter_type == 'blur':
                    # 模糊效果
                    from PIL import ImageFilter
                    filtered = img.filter(ImageFilter.GaussianBlur(radius=2))
                
                elif filter_type == 'sharpen':
                    # 锐化效果
                    from PIL import ImageFilter
                    filtered = img.filter(ImageFilter.SHARPEN)
                
                elif filter_type == 'contour':
                    # 轮廓效果
                    from PIL import ImageFilter
                    filtered = img.filter(ImageFilter.CONTOUR)
                
                else:
                    # 默认不做处理
                    filtered = img.copy()
                
                # 恢复透明通道
                if has_alpha:
                    filtered = filtered.convert('RGBA')
                    filtered.putalpha(alpha)
                
                # 保存处理后的图片
                if filtered.mode == 'RGBA':
                    filtered.save(output_path, 'PNG')
                else:
                    filtered.save(output_path, quality=95, optimize=True)
                
                if callback:
                    callback()
        except Exception as e:
            print(f"应用滤镜时出错: {str(e)}")
            raise

    @staticmethod
    def process_images_batch(process_func, image_files, base_folder, output_folder, max_workers=None, progress_callback=None, **kwargs):
        """批量处理图片
        
        Args:
            process_func: 处理函数 (resize_image, compress_image等)
            image_files: 图片文件列表
            base_folder: 基础文件夹路径
            output_folder: 输出文件夹路径
            max_workers: 最大工作线程数，默认为None（使用系统默认值）
            progress_callback: 进度回调函数
            **kwargs: 传递给处理函数的其他参数
        
        Returns:
            成功处理的图片数量
        """
        total_files = len(image_files)
        processed_count = [0]  # Use list to allow modification in closure
        errors = []
        lock = threading.Lock()

        def process_single_image(image_file):
            try:
                input_path = os.path.join(base_folder, image_file)
                output_path = os.path.join(output_folder, image_file)
                
                # 确保输出子目录存在
                output_subdir = os.path.dirname(output_path)
                if output_subdir and not os.path.exists(output_subdir):
                    os.makedirs(output_subdir, exist_ok=True)
                
                def update_progress():
                    with lock:
                        processed_count[0] += 1
                        if progress_callback:
                            progress_callback(processed_count[0], total_files)
                
                # 调用处理函数
                process_func(input_path, output_path, callback=update_progress, **kwargs)
                
                return True
            except Exception as e:
                print(f"处理图片 {image_file} 时出错: {str(e)}")
                traceback.print_exc()
                return False
        
        # 使用线程池执行任务
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_file = {executor.submit(process_single_image, image_file): image_file 
                             for image_file in image_files}
            
            # 收集处理结果
            for future in future_to_file:
                image_file = future_to_file[future]
                try:
                    if not future.result():
                        errors.append(image_file)
                except Exception as e:
                    print(f"处理图片 {image_file} 时发生异常: {str(e)}")
                    errors.append(image_file)
        
        # 返回成功处理的图片数量
        return processed_count[0]


class ImageFileManager:
    def __init__(self):
        self.history = []  # 处理历史记录
    
    @staticmethod
    def get_image_files(folder_path, include_subfolders=False):
        """获取文件夹中的所有图片文件"""
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
        image_files = []
        
        if include_subfolders:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith(image_extensions):
                        # 获取相对路径
                        rel_path = os.path.relpath(os.path.join(root, file), folder_path)
                        image_files.append(rel_path)
        else:
            for file in os.listdir(folder_path):
                if file.lower().endswith(image_extensions):
                    image_files.append(file)
        
        return sorted(image_files)
    
    def ensure_output_folder(self, base_folder, suffix, params=None):
        """确保输出文件夹存在，并根据处理参数生成文件夹名"""
        # 根据处理参数生成文件夹名
        folder_name = f"output_{suffix}"
        if params:
            param_str = "_".join(f"{k}_{v}" for k, v in params.items())
            folder_name = f"{folder_name}_{param_str}"
        
        output_folder = os.path.join(base_folder, folder_name)
        os.makedirs(output_folder, exist_ok=True)
        
        # 记录处理历史
        history_entry = {
            'timestamp': os.path.getctime(output_folder),
            'operation': suffix,
            'params': params,
            'output_folder': output_folder
        }
        self.history.append(history_entry)
        
        return output_folder
    
    def get_history(self):
        """获取处理历史记录"""
        return sorted(self.history, key=lambda x: x['timestamp'], reverse=True)
    
    def get_last_operation(self):
        """获取最后一次操作的信息"""
        return self.history[-1] if self.history else None