import tkinter as tk
from tkinter import filedialog, ttk, messagebox, scrolledtext
# gui_launcher.py 里
import subprocess, sys, os

# 设置基础路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
os.makedirs(DATA_DIR, exist_ok=True)

class SyneticApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Synetic 内容发布平台")
        self.root.geometry("1000x700")
        self.platform_tabs = {} 
        self.setup_ui()

    def setup_ui(self):
        # 上半区：上传文件区域
        upload_frame = tk.LabelFrame(self.root, text="上传原始素材", padx=10, pady=10)
        upload_frame.pack(fill="x", padx=10, pady=10)

        tk.Button(upload_frame, text="上传文本", command=self.upload_text).pack(side="left", padx=10)
        tk.Button(upload_frame, text="上传音频", command=self.upload_audio).pack(side="left", padx=10)
        tk.Button(upload_frame, text="上传视频", command=self.upload_video).pack(side="left", padx=10)
        tk.Button(upload_frame, text="上传图片", command=self.upload_picture).pack(side="left", padx=10)

        # 原始文本展示
        self.origin_text_box = tk.Text(upload_frame, height=10, width=120)
        self.origin_text_box.pack(pady=10)
        self.load_origin_text()

        # 下半区：平台标签页
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.platforms = ["xhs", "zhihu"]
        self.text_boxes = {}

        for platform in self.platforms:
            self.create_platform_tab(platform)

    def create_platform_tab(self, platform):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=platform)

        # 创建上部按钮框架
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=5, padx=5)

        # 创建两个按钮
        generate_button = ttk.Button(button_frame, text="生成内容", command=lambda p=platform: self.generate_content(p))
        post_button = ttk.Button(button_frame, text="发布内容", command=lambda p=platform: self.post_content(p))
        generate_button.pack(side=tk.LEFT, padx=5)
        post_button.pack(side=tk.LEFT, padx=5)

        # 创建中部内容展示框架
        content_frame = ttk.Frame(frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        # 添加文本区（滚动区域）
        content_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD)
        content_text.pack(fill=tk.BOTH, expand=True)

        # 存储引用
        self.platform_tabs[platform] = {
            'frame': frame,
            'text_widget': content_text
        }

    def upload_text(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
                self.origin_text_box.delete("1.0", tk.END)
                self.origin_text_box.insert(tk.END, text)

            with open(os.path.join(DATA_DIR, "origin.txt"), "w", encoding="utf-8") as f:
                f.write(text)

    def upload_audio(self):
        filedialog.askopenfilename(filetypes=[("Audio files", "*.mp3;*.wav")])
        messagebox.showinfo("提示", "音频上传功能待开发")

    def upload_video(self):
        filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.mov")])
        messagebox.showinfo("提示", "视频上传功能待开发")

    def upload_picture(self):
        filedialog.askopenfilename(filetypes=[("Picture files", "*.png;*.jpg")])
        messagebox.showinfo("提示", "视频上传功能待开发")

    def load_origin_text(self):
        origin_path = os.path.join(DATA_DIR, "origin.txt")
        if os.path.exists(origin_path):
            with open(origin_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.origin_text_box.delete("1.0", tk.END)
                self.origin_text_box.insert(tk.END, content)

    def generate_content(self, platform):
        script_path = os.path.join(SCRIPTS_DIR, f"{platform}_generate.py")
        
        try:
            print(f"调试：运行脚本 {script_path}")
            output = subprocess.check_output(["python", script_path], stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="ignore")
            print(f"调试：生成脚本输出: {output}")
            gen_file = os.path.join(DATA_DIR, f"content_{platform}.txt")
            
            if os.path.exists(gen_file):
                with open(gen_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    text_widget = self.platform_tabs[platform]['text_widget']
                    text_widget.delete("1.0", tk.END)
                    text_widget.insert(tk.END, content)
            else:
                messagebox.showerror("错误", f"未生成 content_{platform}.txt")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("执行失败", e.output)



    def post_content(self, platform):
        script = f"{platform}_post.py"   # 使用一个启动发布脚本，可以调节该程序脚本选择调用什么程序发布，增加灵活性。
        script_path = os.path.join(SCRIPTS_DIR, script)

        try:
            # 非阻塞启动新进程（Windows 上新开控制台）
            creationflags = 0
            if os.name == "nt":
                creationflags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
            subprocess.Popen([sys.executable, script_path],
                            creationflags=creationflags)
            messagebox.showinfo("提示", f"已打开 {platform} 发布窗口。发布完成后请手动关闭浏览器。")
        except Exception as e:
            messagebox.showerror("发布失败", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = SyneticApp(root)
    root.mainloop()
