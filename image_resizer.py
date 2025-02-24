import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageEnhance
import os

class ImageResizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片批量处理工具")
        self.root.geometry("1000x700")  # 增加窗口默认大小
        
        # 设置整体样式
        style = ttk.Style()
        style.configure('TButton', padding=5)
        style.configure('TLabelframe', padding=8)
        style.configure('TLabelframe.Label', font=('Arial', 9, 'bold'))
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(expand=True, fill='both')
        
        # 左侧框架（文件列表区域）
        self.left_frame = ttk.LabelFrame(self.main_frame, text="文件列表", padding="5")
        self.left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # 选择文件夹按钮
        self.select_btn = ttk.Button(self.left_frame, 
                                   text="选择图片文件夹", 
                                   command=self.select_folder)
        self.select_btn.pack(pady=(5, 10), padx=5, fill='x')
        
        # 显示选择的文件夹路径
        self.path_label = ttk.Label(self.left_frame, 
                                  text="未选择文件夹", 
                                  wraplength=350)
        self.path_label.pack(pady=(0, 5), padx=5)
        
        # 创建列表框和滚动条
        self.listbox_frame = ttk.Frame(self.left_frame)
        self.listbox_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.scrollbar = ttk.Scrollbar(self.listbox_frame)
        self.scrollbar.pack(side='right', fill='y')
        
        self.listbox = tk.Listbox(self.listbox_frame, 
                                 yscrollcommand=self.scrollbar.set,
                                 selectmode='single',
                                 font=('Arial', 9),
                                 activestyle='dotbox')
        self.listbox.pack(side='left', fill='both', expand=True)
        self.scrollbar.config(command=self.listbox.yview)
        
        # 添加列表框选择事件绑定
        self.listbox.bind('<<ListboxSelect>>', self.show_preview)
        
        # 删除选中图片按钮
        self.delete_btn = ttk.Button(self.left_frame,
                                   text="删除选中图片",
                                   command=self.delete_selected)
        self.delete_btn.pack(pady=5, padx=5, fill='x')
        
        # 右侧框架（功能区域）
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side='right', fill='both', expand=True)
        
        # 预览区域
        self.preview_frame = ttk.LabelFrame(self.right_frame, text="预览", padding="5")
        self.preview_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.image_label = ttk.Label(self.preview_frame)
        self.image_label.pack(expand=True, pady=5)
        
        self.size_label = ttk.Label(self.preview_frame, text="")
        self.size_label.pack(pady=5)
        
        # 功能区域（使用Notebook来组织不同功能）
        self.notebook = ttk.Notebook(self.right_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # 调整尺寸标签页
        self.resize_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.resize_frame, text="调整尺寸")
        
        # 宽度输入框
        self.width_frame = ttk.Frame(self.resize_frame)
        self.width_frame.pack(fill='x', pady=5)
        ttk.Label(self.width_frame, text="宽度:").pack(side='left')
        self.width_var = tk.StringVar()
        self.width_entry = ttk.Entry(self.width_frame, textvariable=self.width_var, width=10)
        self.width_entry.pack(side='left', padx=5)
        ttk.Label(self.width_frame, text="像素").pack(side='left')
        
        # 高度输入框
        self.height_frame = ttk.Frame(self.resize_frame)
        self.height_frame.pack(fill='x', pady=5)
        ttk.Label(self.height_frame, text="高度:").pack(side='left')
        self.height_var = tk.StringVar()
        self.height_entry = ttk.Entry(self.height_frame, textvariable=self.height_var, width=10)
        self.height_entry.pack(side='left', padx=5)
        ttk.Label(self.height_frame, text="像素").pack(side='left')
        
        # 保持比例选项
        self.keep_ratio_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.resize_frame, 
                       text="保持原始比例",
                       variable=self.keep_ratio_var).pack(pady=5)
        
        ttk.Button(self.resize_frame,
                  text="开始调整尺寸",
                  command=self.process_resize).pack(pady=10)
        
        # 压缩标签页
        self.compress_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.compress_frame, text="压缩")
        
        ttk.Label(self.compress_frame, text="压缩质量:").pack(pady=(0, 5))
        self.quality_var = tk.IntVar(value=85)
        self.quality_label = ttk.Label(self.compress_frame, text="85")
        self.quality_label.pack()
        quality_scale = ttk.Scale(self.compress_frame,
                 from_=1, to=100,
                 orient='horizontal',
                 variable=self.quality_var,
                 command=lambda v: self.quality_label.config(text=str(int(float(v)))))
        quality_scale.pack(fill='x', pady=5)
        
        ttk.Label(self.compress_frame,
                 text="1-60: 低质量，文件最小\n"
                      "61-85: 中等质量，平衡大小\n"
                      "86-100: 高质量，文件较大",
                 justify='left').pack(pady=5)
        
        ttk.Button(self.compress_frame,
                  text="开始压缩",
                  command=self.process_compress).pack(pady=10)
        
        # 随机微调标签页
        self.random_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.random_frame, text="随机微调")
        
        ttk.Label(self.random_frame, text="最大旋转角度:").pack(pady=(0, 5))
        self.rotation_var = tk.IntVar(value=5)
        self.rotation_label = ttk.Label(self.random_frame, text="5°")
        self.rotation_label.pack()
        rotation_scale = ttk.Scale(self.random_frame,
                 from_=1, to=45,
                 orient='horizontal',
                 variable=self.rotation_var,
                 command=lambda v: self.rotation_label.config(text=f"{int(float(v))}°"))
        rotation_scale.pack(fill='x', pady=5)
        
        ttk.Button(self.random_frame,
                  text="开始随机微调",
                  command=self.process_random).pack(pady=10)
        
        # 曝光度调整标签页
        self.exposure_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.exposure_frame, text="曝光度")
        
        ttk.Label(self.exposure_frame, text="曝光度调整:").pack(pady=(0, 5))
        self.exposure_var = tk.DoubleVar(value=1.0)
        self.exposure_label = ttk.Label(self.exposure_frame, text="1.0")
        self.exposure_label.pack()
        exposure_scale = ttk.Scale(self.exposure_frame,
                 from_=0.1, to=2.0,
                 orient='horizontal',
                 variable=self.exposure_var,
                 command=lambda v: self.exposure_label.config(text=f"{float(v):.1f}"))
        exposure_scale.pack(fill='x', pady=5)
        
        ttk.Label(self.exposure_frame,
                 text="0.1-0.9: 降低曝光度\n1.0: 保持原样\n1.1-2.0: 提高曝光度",
                 justify='left').pack(pady=5)
        
        ttk.Button(self.exposure_frame,
                  text="开始调整曝光度",
                  command=self.process_exposure).pack(pady=10)
        
        # 保存当前文件夹路径
        self.current_folder = ""
        
    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.current_folder = folder_path
            self.path_label.config(text=f"已选择文件夹: {folder_path}")
            self.load_images()
    
    def load_images(self):
        # 清空列表框
        self.listbox.delete(0, tk.END)
        self.image_files = []
        
        # 获取所有图片文件
        valid_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
        for file in os.listdir(self.current_folder):
            if file.lower().endswith(valid_extensions):
                self.image_files.append(file)
                self.listbox.insert(tk.END, file)
    
    def show_preview(self, event):
        selection = self.listbox.curselection()
        if selection:
            try:
                image_path = os.path.join(self.current_folder, self.image_files[selection[0]])
                image = Image.open(image_path)
                
                # 获取并显示原始图片尺寸
                original_size = image.size
                self.size_label.config(text=f"图片尺寸: {original_size[0]} x {original_size[1]} 像素")
                
                # 调整图片大小以适应预览窗口
                preview_size = (300, 300)
                image.thumbnail(preview_size, Image.ANTIALIAS)
                
                # 创建PhotoImage对象
                photo = ImageTk.PhotoImage(image)
                
                # 更新预览标签
                self.image_label.config(image=photo)
                self.image_label.image = photo  # 保持引用
            except Exception as e:
                messagebox.showerror("错误", f"无法加载图片: {str(e)}")
                self.size_label.config(text="")  # 清空尺寸信息
    
    def delete_selected(self):
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            self.listbox.delete(index)
            del self.image_files[index]
            # 清除预览和尺寸信息
            self.image_label.config(image='')
            self.size_label.config(text="")
    
    def process_resize(self):
        """处理调整尺寸的功能"""
        if not self.image_files:
            messagebox.showwarning("警告", "请先选择需要处理的图片！")
            return
            
        try:
            width = int(self.width_var.get()) if self.width_var.get() else None
            height = int(self.height_var.get()) if self.height_var.get() else None
            
            if not (width or height):
                messagebox.showwarning("警告", "请至少输入宽度或高度！")
                return
            
            output_folder = os.path.join(self.current_folder, "resized")
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            
            for image_file in self.image_files:
                input_path = os.path.join(self.current_folder, image_file)
                output_path = os.path.join(output_folder, image_file)
                
                with Image.open(input_path) as img:
                    original_width, original_height = img.size
                    new_width = width
                    new_height = height
                    
                    if self.keep_ratio_var.get():
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
                    
                    resized_img = img.resize((new_width, new_height), Image.ANTIALIAS)
                    resized_img.save(output_path)
            
            messagebox.showinfo("完成", f"调整尺寸完成！\n保存在: {output_folder}")
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字！")
        except Exception as e:
            messagebox.showerror("错误", f"处理图片时出错: {str(e)}")
    
    def process_compress(self):
        """处理压缩的功能"""
        if not self.image_files:
            messagebox.showwarning("警告", "请先选择需要处理的图片！")
            return
            
        try:
            quality = self.quality_var.get()
            output_folder = os.path.join(self.current_folder, "compressed")
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            
            for image_file in self.image_files:
                input_path = os.path.join(self.current_folder, image_file)
                output_path = os.path.join(output_folder, image_file)
                
                with Image.open(input_path) as img:
                    if img.format == 'PNG' and img.mode in ('RGBA', 'LA'):
                        img = img.convert('RGB')
                    img.save(output_path, quality=quality, optimize=True)
            
            messagebox.showinfo("完成", f"压缩完成！\n保存在: {output_folder}")
            
        except Exception as e:
            messagebox.showerror("错误", f"处理图片时出错: {str(e)}")
    
    def process_random(self):
        """处理随机微调的功能"""
        if not self.image_files:
            messagebox.showwarning("警告", "请先选择需要处理的图片！")
            return
            
        try:
            max_rotation = self.rotation_var.get()
            output_folder = os.path.join(self.current_folder, "random_adjusted")
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            
            import random
            import math
            
            for image_file in self.image_files:
                input_path = os.path.join(self.current_folder, image_file)
                output_path = os.path.join(output_folder, image_file)
                
                with Image.open(input_path) as img:
                    width, height = img.size
                    angle = random.uniform(-max_rotation, max_rotation)
                    
                    radian = math.radians(abs(angle))
                    cos_a = math.cos(radian)
                    sin_a = math.sin(radian)
                    new_width = int(width * cos_a + height * sin_a)
                    new_height = int(height * cos_a + width * sin_a)
                    
                    scale = max(width / new_width, height / new_height)
                    scale *= 1.1
                    
                    enlarged_size = (int(img.size[0] * scale), int(img.size[1] * scale))
                    img = img.resize(enlarged_size, Image.ANTIALIAS)
                    img = img.rotate(angle, Image.BICUBIC, expand=False)
                    
                    left = (img.size[0] - width) // 2
                    top = (img.size[1] - height) // 2
                    img = img.crop((left, top, left + width, top + height))
                    img.save(output_path)
            
            messagebox.showinfo("完成", f"随机微调完成！\n保存在: {output_folder}")
            
        except Exception as e:
            messagebox.showerror("错误", f"处理图片时出错: {str(e)}")
    
    def process_exposure(self):
        """处理调整曝光度的功能"""
        if not self.image_files:
            messagebox.showwarning("警告", "请先选择需要处理的图片！")
            return
            
        try:
            brightness_factor = self.exposure_var.get()
            
            # 如果曝光度因子为1.0，提示用户无需处理
            if brightness_factor == 1.0:
                messagebox.showinfo("提示", "曝光度设置为1.0，图片将保持原样")
                return
            
            output_folder = os.path.join(self.current_folder, "exposure_adjusted")
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            
            for image_file in self.image_files:
                input_path = os.path.join(self.current_folder, image_file)
                output_path = os.path.join(output_folder, image_file)
                
                with Image.open(input_path) as img:
                    # 如果是PNG格式且有透明通道，需要特殊处理
                    if img.mode in ('RGBA', 'LA'):
                        # 分离alpha通道
                        alpha = img.getchannel('A')
                        # 转换图片模式以调整亮度
                        img = img.convert('RGB')
                        # 调整亮度
                        enhancer = ImageEnhance.Brightness(img)
                        adjusted = enhancer.enhance(brightness_factor)
                        # 恢复alpha通道
                        adjusted = adjusted.convert('RGBA')
                        adjusted.putalpha(alpha)
                    else:
                        # 直接调整亮度
                        enhancer = ImageEnhance.Brightness(img)
                        adjusted = enhancer.enhance(brightness_factor)
                    
                    # 保存调整后的图片
                    if adjusted.mode == 'RGBA':
                        adjusted.save(output_path, 'PNG')
                    else:
                        adjusted.save(output_path, quality=95, optimize=True)
            
            messagebox.showinfo("完成", 
                              f"曝光度调整完成！\n"
                              f"调整系数: {brightness_factor}\n"
                              f"保存在: {output_folder}")
            
        except Exception as e:
            messagebox.showerror("错误", f"处理图片时出错: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageResizerApp(root)
    root.mainloop() 