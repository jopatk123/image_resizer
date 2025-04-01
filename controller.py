import os
from model import ImageProcessor, ImageFileManager

class ImageResizerController:
    def __init__(self):
        self.current_folder = ""
        self.image_files = []
        self.image_processor = ImageProcessor()
        self.file_manager = ImageFileManager()
        self.progress_callback = None
        self.max_workers = None  # 默认使用系统决定的线程数
        self.filter_types = {
            'grayscale': '灰度',
            'sepia': '复古棕褐色',
            'negative': '负片',
            'blur': '模糊',
            'sharpen': '锐化',
            'contour': '轮廓'
        }
    
    def select_folder(self, folder_path):
        """选择文件夹并加载图片"""
        self.current_folder = folder_path
        return self.current_folder
    
    def load_images(self, include_subfolders=False):
        """加载图片文件列表"""
        if not self.current_folder:
            return []
        self.image_files = self.file_manager.get_image_files(
            self.current_folder, include_subfolders)
        return self.image_files
    
    def set_progress_callback(self, callback):
        """设置进度回调函数"""
        self.progress_callback = callback
    
    def set_max_workers(self, max_workers):
        """设置最大工作线程数"""
        self.max_workers = max_workers
    
    def process_resize(self, width=None, height=None, keep_ratio=True):
        """处理调整尺寸的功能"""
        if not self.image_files:
            return False, "请先选择需要处理的图片！"
        
        if not (width or height):
            return False, "请至少输入宽度或高度！"
        
        try:
            output_folder = self.file_manager.ensure_output_folder(
                self.current_folder, "resized")
            
            # 使用多线程批处理
            processed_count = self.image_processor.process_images_batch(
                self.image_processor.resize_image,
                self.image_files,
                self.current_folder,
                output_folder,
                max_workers=self.max_workers,
                progress_callback=self.progress_callback,
                width=width,
                height=height,
                keep_ratio=keep_ratio
            )
            
            if processed_count == 0:
                return False, "处理过程中出现错误，没有图片被成功处理"
            elif processed_count < len(self.image_files):
                return True, f"部分图片处理完成 ({processed_count}/{len(self.image_files)})\n保存在: {output_folder}"
            else:
                return True, f"调整尺寸完成！\n保存在: {output_folder}"
            
        except ValueError:
            return False, "请输入有效的数字！"
        except Exception as e:
            return False, f"处理图片时出错: {str(e)}"
    
    def process_compress(self, quality):
        """处理压缩的功能"""
        if not self.image_files:
            return False, "请先选择需要处理的图片！"
        
        try:
            output_folder = self.file_manager.ensure_output_folder(
                self.current_folder, "compressed")
            
            # 使用多线程批处理
            processed_count = self.image_processor.process_images_batch(
                self.image_processor.compress_image,
                self.image_files,
                self.current_folder,
                output_folder,
                max_workers=self.max_workers,
                progress_callback=self.progress_callback,
                quality=quality
            )
            
            if processed_count == 0:
                return False, "处理过程中出现错误，没有图片被成功处理"
            elif processed_count < len(self.image_files):
                return True, f"部分图片处理完成 ({processed_count}/{len(self.image_files)})\n保存在: {output_folder}"
            else:
                return True, f"压缩完成！\n保存在: {output_folder}"
            
        except Exception as e:
            return False, f"处理图片时出错: {str(e)}"
    
    def process_random(self, max_rotation):
        """处理随机微调的功能"""
        if not self.image_files:
            return False, "请先选择需要处理的图片！"
        
        try:
            output_folder = self.file_manager.ensure_output_folder(
                self.current_folder, "random_adjusted")
            
            # 使用多线程批处理
            processed_count = self.image_processor.process_images_batch(
                self.image_processor.random_adjust,
                self.image_files,
                self.current_folder,
                output_folder,
                max_workers=self.max_workers,
                progress_callback=self.progress_callback,
                max_rotation=max_rotation
            )
            
            if processed_count == 0:
                return False, "处理过程中出现错误，没有图片被成功处理"
            elif processed_count < len(self.image_files):
                return True, f"部分图片处理完成 ({processed_count}/{len(self.image_files)})\n保存在: {output_folder}"
            else:
                return True, f"随机微调完成！\n保存在: {output_folder}"
            
        except Exception as e:
            return False, f"处理图片时出错: {str(e)}"
    
    def process_exposure(self, brightness_factor):
        """处理调整曝光度的功能"""
        if not self.image_files:
            return False, "请先选择需要处理的图片！"
        
        if brightness_factor == 1.0:
            return False, "曝光度设置为1.0，图片将保持原样"
        
        try:
            output_folder = self.file_manager.ensure_output_folder(
                self.current_folder, "exposure_adjusted")
            
            # 使用多线程批处理
            processed_count = self.image_processor.process_images_batch(
                self.image_processor.adjust_exposure,
                self.image_files,
                self.current_folder,
                output_folder,
                max_workers=self.max_workers,
                progress_callback=self.progress_callback,
                brightness_factor=brightness_factor
            )
            
            if processed_count == 0:
                return False, "处理过程中出现错误，没有图片被成功处理"
            elif processed_count < len(self.image_files):
                return True, (f"部分图片处理完成 ({processed_count}/{len(self.image_files)})\n"
                             f"调整系数: {brightness_factor}\n"
                             f"保存在: {output_folder}")
            else:
                return True, (f"曝光度调整完成！\n"
                             f"调整系数: {brightness_factor}\n"
                             f"保存在: {output_folder}")
            
        except Exception as e:
            return False, f"处理图片时出错: {str(e)}"
            
    def process_filter(self, filter_type):
        """处理滤镜效果的功能"""
        if not self.image_files:
            return False, "请先选择需要处理的图片！"
        
        if filter_type not in self.filter_types:
            return False, "无效的滤镜类型"
        
        try:
            output_folder = self.file_manager.ensure_output_folder(
                self.current_folder, f"filter_{filter_type}")
            
            # 使用多线程批处理
            processed_count = self.image_processor.process_images_batch(
                self.image_processor.apply_filter,
                self.image_files,
                self.current_folder,
                output_folder,
                max_workers=self.max_workers,
                progress_callback=self.progress_callback,
                filter_type=filter_type
            )
            
            if processed_count == 0:
                return False, "处理过程中出现错误，没有图片被成功处理"
            elif processed_count < len(self.image_files):
                return True, (f"部分图片处理完成 ({processed_count}/{len(self.image_files)})\n"
                             f"滤镜类型: {self.filter_types[filter_type]}\n"
                             f"保存在: {output_folder}")
            else:
                return True, (f"滤镜效果应用完成！\n"
                             f"滤镜类型: {self.filter_types[filter_type]}\n"
                             f"保存在: {output_folder}")
            
        except Exception as e:
            return False, f"处理图片时出错: {str(e)}"