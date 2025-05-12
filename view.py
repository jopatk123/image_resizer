import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import threading
from controller import ImageResizerController

class ImageResizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片批量处理工具")
        self.root.geometry("1000x700")
        self.controller = ImageResizerController()
        
        # 设置进度回调
        self.controller.set_progress_callback(self.update_progress)
        
        # 设置最大工作线程数（可根据系统性能调整）
        self.controller.set_max_workers(4)  # 使用4个线程进行处理
        
        # 设置整体样式
        style = ttk.Style()
        # 设置中文字体和增加行宽
        default_font = ('Microsoft YaHei UI', 10)  # 使用微软雅黑UI字体
        style.configure('TButton', padding=8, font=default_font)
        style.configure('TLabelframe', padding=10)
        style.configure('TLabelframe.Label', font=('Microsoft YaHei UI', 10, 'bold'))
        style.configure('TLabel', font=default_font)
        style.configure('TCheckbutton', font=default_font)
        style.configure('TRadiobutton', font=default_font)
        style.configure('TNotebook.Tab', font=default_font, padding=(10, 5))
        
        # 进度条变量
        self.progress_var = tk.DoubleVar(value=0.0)
        self.is_processing = False
        
        self._init_ui()
    
    def _init_ui(self):
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="15")
        self.main_frame.pack(expand=True, fill='both')
        
        self._init_left_frame()
        self._init_right_frame()
    
    def _init_left_frame(self):
        # 左侧框架（文件列表区域）
        self.left_frame = ttk.LabelFrame(self.main_frame, text="文件列表", padding="10")
        self.left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # 选择文件夹按钮
        self.select_btn = ttk.Button(self.left_frame, 
                                   text="选择图片文件夹", 
                                   command=self.select_folder)
        self.select_btn.pack(pady=(8, 8), padx=10, fill='x')
        
        # 添加包含子文件夹选项
        self.include_subfolders = tk.BooleanVar(value=False)
        self.subfolder_check = ttk.Checkbutton(
            self.left_frame,
            text="包含子文件夹中的图片",
            variable=self.include_subfolders,
            command=self.reload_images
        )
        self.subfolder_check.pack(pady=(0, 5), padx=5, fill='x')
        
        # 显示选择的文件夹路径
        self.path_label = ttk.Label(self.left_frame, 
                                  text="未选择文件夹", 
                                  wraplength=400)
        self.path_label.pack(pady=(0, 5), padx=5)
        
        # 创建列表框和滚动条
        self.listbox_frame = ttk.Frame(self.left_frame)
        self.listbox_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.scrollbar = ttk.Scrollbar(self.listbox_frame)
        self.scrollbar.pack(side='right', fill='y')
        
        self.listbox = tk.Listbox(self.listbox_frame, 
                                 yscrollcommand=self.scrollbar.set,
                                 selectmode='single',
                                 font=('Microsoft YaHei UI', 10),
                                 activestyle='dotbox',
                                 width=40)
        self.listbox.pack(side='left', fill='both', expand=True)
        self.scrollbar.config(command=self.listbox.yview)
        
        # 添加列表框选择事件绑定
        self.listbox.bind('<<ListboxSelect>>', self.show_preview)
        
        # 删除选中图片按钮
        self.delete_btn = ttk.Button(self.left_frame,
                                   text="删除选中图片",
                                   command=self.delete_selected)
        self.delete_btn.pack(pady=8, padx=10, fill='x')
    
    def _init_right_frame(self):
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
        
        # 进度条
        self.progress_frame = ttk.Frame(self.right_frame)
        self.progress_frame.pack(fill='x', pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame, 
            variable=self.progress_var,
            orient='horizontal',
            length=100, 
            mode='determinate')
        self.progress_bar.pack(fill='x', padx=5, pady=5)
        
        self.progress_label = ttk.Label(self.progress_frame, text="就绪")
        self.progress_label.pack(pady=(0, 5))
        
        # 功能区域（使用Notebook来组织不同功能）
        self.notebook = ttk.Notebook(self.right_frame)
        self.notebook.pack(fill='both', expand=True)
        
        self._init_resize_tab()
        self._init_compress_tab()
        self._init_random_tab()
        self._init_exposure_tab()
        self._init_filter_tab()
        self._init_filter_tab()
    
    def _init_resize_tab(self):
        # 调整尺寸标签页
        self.resize_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(self.resize_frame, text="调整尺寸")
        
        # 宽度输入框
        self.width_frame = ttk.Frame(self.resize_frame)
        self.width_frame.pack(fill='x', pady=5)
        ttk.Label(self.width_frame, text="宽度:").pack(side='left')
        self.width_var = tk.StringVar()
        self.width_entry = ttk.Entry(self.width_frame, textvariable=self.width_var, width=15)
        self.width_entry.pack(side='left', padx=5)
        ttk.Label(self.width_frame, text="像素").pack(side='left')
        
        # 高度输入框
        self.height_frame = ttk.Frame(self.resize_frame)
        self.height_frame.pack(fill='x', pady=5)
        ttk.Label(self.height_frame, text="高度:").pack(side='left')
        self.height_var = tk.StringVar()
        self.height_entry = ttk.Entry(self.height_frame, textvariable=self.height_var, width=15)
        self.height_entry.pack(side='left', padx=5)
        ttk.Label(self.height_frame, text="像素").pack(side='left')
        
        # 保持比例选项
        self.keep_ratio_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.resize_frame, 
                       text="保持原始比例",
                       variable=self.keep_ratio_var).pack(pady=5)
        
        ttk.Button(self.resize_frame,
                  text="开始调整尺寸",
                  command=self.process_resize).pack(pady=15, padx=10, fill='x')
    
    def _init_compress_tab(self):
        # 压缩标签页
        self.compress_frame = ttk.Frame(self.notebook, padding="15")
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
                  command=self.process_compress).pack(pady=15, padx=10, fill='x')
    
    def _init_random_tab(self):
        # 随机微调标签页
        self.random_frame = ttk.Frame(self.notebook, padding="15")
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
                  command=self.process_random).pack(pady=15, padx=10, fill='x')
    
    def _init_exposure_tab(self):
        # 曝光度调整标签页
        self.exposure_frame = ttk.Frame(self.notebook, padding="15")
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
                  command=self.process_exposure).pack(pady=15, padx=10, fill='x')
    
    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.controller.select_folder(folder_path)
            self.path_label.config(text=f"已选择文件夹: {folder_path}")
            self.load_images()
    
    def reload_images(self):
        """重新加载图片，当子文件夹选项改变时调用"""
        self.load_images()
    
    def load_images(self):
        # 清空列表框
        self.listbox.delete(0, tk.END)
        
        # 获取所有图片文件
        image_files = self.controller.load_images(self.include_subfolders.get())
        
        # 更新列表框
        for file in image_files:
            self.listbox.insert(tk.END, file)
    
    def show_preview(self, event):
        selection = self.listbox.curselection()
        if selection:
            try:
                image_file = self.controller.image_files[selection[0]]
                image_path = os.path.join(self.controller.current_folder, image_file)
                image = Image.open(image_path)
                
                # 获取并显示原始图片尺寸
                original_size = image.size
                self.size_label.config(text=f"图片尺寸: {original_size[0]} x {original_size[1]} 像素")
                
                # 调整图片大小以适应预览窗口
                preview_size = (300, 300)
                image.thumbnail(preview_size, Image.Resampling.LANCZOS)
                
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
            del self.controller.image_files[index]
            # 清除预览和尺寸信息
            self.image_label.config(image='')
            self.size_label.config(text="")
    
    def update_progress(self, current, total):
        """更新进度条"""
        progress = current / total * 100 if total > 0 else 0
        self.progress_var.set(progress)
        self.progress_label.config(text=f"处理中... {current}/{total} ({progress:.1f}%)")
        self.root.update_idletasks()  # 强制更新UI
    
    def reset_progress(self):
        """重置进度条"""
        self.progress_var.set(0)
        self.progress_label.config(text="就绪")
        self.is_processing = False
    
    def process_in_thread(self, process_func, *args, **kwargs):
        """在线程中处理图片"""
        if self.is_processing:
            messagebox.showwarning("警告", "有处理任务正在进行中，请等待完成")
            return
        
        self.is_processing = True
        self.progress_label.config(text="准备处理...")
        
        def run():
            try:
                success, message = process_func(*args, **kwargs)
                
                # 在主线程中更新UI
                self.root.after(0, lambda: self.show_result(success, message))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"处理过程中出错: {str(e)}"))
            finally:
                self.root.after(0, self.reset_progress)
        
        # 启动处理线程
        threading.Thread(target=run, daemon=True).start()
    
    def show_result(self, success, message):
        """显示处理结果"""
        if success:
            messagebox.showinfo("完成", message)
        else:
            messagebox.showwarning("警告", message)
    
    def process_resize(self):
        try:
            width = int(self.width_var.get()) if self.width_var.get() else None
            height = int(self.height_var.get()) if self.height_var.get() else None
            
            if not (width or height):
                messagebox.showwarning("警告", "请至少输入宽度或高度！")
                return
            
            self.process_in_thread(
                self.controller.process_resize,
                width, height, self.keep_ratio_var.get()
            )
                
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字！")
    
    def process_compress(self):
        self.process_in_thread(
            self.controller.process_compress,
            self.quality_var.get()
        )
    
    def process_random(self):
        self.process_in_thread(
            self.controller.process_random,
            self.rotation_var.get()
        )
    
    def process_exposure(self):
        self.process_in_thread(
            self.controller.process_exposure,
            self.exposure_var.get()
        )
    
    def _init_filter_tab(self):
        # 滤镜效果标签页
        self.filter_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(self.filter_frame, text="滤镜效果")
        
        ttk.Label(self.filter_frame, text="选择滤镜效果:").pack(pady=(0, 5))
        
        # 滤镜选择框架
        self.filter_select_frame = ttk.Frame(self.filter_frame)
        self.filter_select_frame.pack(fill='x', pady=5)
        
        # 滤镜类型选择
        self.filter_var = tk.StringVar(value="grayscale")
        
        # 创建单选按钮
        filters = [
            ("灰度", "grayscale"),
            ("复古棕褐色", "sepia"),
            ("负片", "negative"),
            ("模糊", "blur"),
            ("锐化", "sharpen"),
            ("轮廓", "contour")
        ]
        
        # 使用网格布局放置单选按钮
        for i, (text, value) in enumerate(filters):
            row = i // 2
            col = i % 2
            ttk.Radiobutton(
                self.filter_select_frame,
                text=text,
                value=value,
                variable=self.filter_var
            ).grid(row=row, column=col, sticky='w', padx=5, pady=2)
        
        # 应用滤镜按钮
        ttk.Button(
            self.filter_frame,
            text="应用滤镜",
            command=self.process_filter
        ).pack(pady=15, padx=10, fill='x')
    
    def process_filter(self):
        self.process_in_thread(
            self.controller.process_filter,
            self.filter_var.get()
        )


if __name__ == '__main__':
    root = tk.Tk()
    app = ImageResizerApp(root)
    root.mainloop()