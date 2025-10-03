import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk
# --- 新增/替换：导入 ---
import io
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)


class ClipboardHelper:
    def __init__(self, platform):
        self.platform = platform
        self.root = tk.Tk()
        self.root.title(f"Clipboard Helper - {platform}")
        self.root.geometry("900x150+100+50")
        self.root.configure(bg="yellow")

        self.status = tk.StringVar()
        self.setup_ui()

    def setup_ui(self):
        btn_frame = tk.Frame(self.root, bg="yellow")
        btn_frame.pack(pady=10)

        files = {
            "标题": f"title_{self.platform}.txt",
            "正文": f"content_{self.platform}.txt",
            "封面": f"cover_{self.platform}.jpg",
            "音频": f"audio_{self.platform}.wav",
            "视频": f"video_{self.platform}.mp4",
        }

        for label, fname in files.items():
            if label == "标题":
                btn = tk.Button(
                    btn_frame,
                    text=f"复制{label}",
                    command=lambda p=platform: self.copy_title_text(p),
                    width=22, height=2,
                    bg="white", fg="black"
                )
            elif label == "正文":
                btn = tk.Button(
                    btn_frame,
                    text=f"复制{label}",
                    command=lambda p=platform: self.copy_content_text(p),
                    width=22, height=2,
                    bg="white", fg="black"
                )
            else:
                # 封面/音频/视频都走 _open_and_copy_file
                btn = tk.Button(
                    btn_frame,
                    text=f"打开{label}并复制",
                    command=lambda f=fname: self._open_and_copy_file(f),
                    width=22, height=2,
                    bg="white", fg="black"
                )
            btn.pack(side=tk.LEFT, padx=5)


        status_label = tk.Label(
            self.root, textvariable=self.status,
            bg="yellow", fg="black", font=("Arial", 12)
        )
        status_label.pack(fill=tk.X, pady=5)

    def _open_and_copy_file(self, filename):
        file_path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(file_path):
            self.status.set(f"文件不存在: {file_path}")
            print(f"[WARN] 文件不存在: {file_path}")
            return

        print(f"[DEBUG] 目标文件: {file_path}")

        # --- 三重尝试 ---
        commands = [
            f'explorer /select,"{file_path}"',
            f'explorer /n,/select,"{file_path}"',
            f'explorer "{os.path.dirname(file_path)}"'
        ]

        opened = False
        for idx, cmd in enumerate(commands, 1):
            try:
                print(f"[DEBUG] 尝试{idx}: {cmd}")
                subprocess.Popen(cmd, shell=True)
                opened = True
                break
            except Exception as e:
                print(f"[WARN] 尝试{idx}失败: {e}")

        if not opened:
            self.status.set(f"Explorer 打开失败: {file_path}")
            return

        # --- 复制到剪贴板 ---
        self.copy_file_to_clipboard(file_path)
        self.status.set(f"已复制文件: {os.path.basename(file_path)}\n路径: {file_path}")



    # --- 新增：复制文本到剪贴板（标题/正文用）---
    def copy_text_to_clipboard(self, text: str):
        try:
            import win32clipboard as w
            import win32con
            w.OpenClipboard()
            try:
                w.EmptyClipboard()
                w.SetClipboardData(win32con.CF_UNICODETEXT, text)
            finally:
                w.CloseClipboard()
            self.status.set(f"已复制文本（{min(len(text), 50)}字）：{text[:50]}{'…' if len(text) > 50 else ''}")
            print("[DEBUG] 文本已写入剪贴板")
        except Exception as e:
            self.status.set(f"复制文本失败：{e}")
            print(f"[ERROR] 复制文本失败: {e}")

    # --- 新增：复制图片到剪贴板（粘贴图片本体）---
    def copy_image_to_clipboard(self, file_path: str):
        try:
            import win32clipboard as w
            import win32con
            img = Image.open(file_path).convert("RGB")
            with io.BytesIO() as output:
                # BMP 文件包含 14 字节文件头；CF_DIB 需要去掉文件头
                img.save(output, format="BMP")
                bmp_data = output.getvalue()[14:]
            w.OpenClipboard()
            try:
                w.EmptyClipboard()
                w.SetClipboardData(win32con.CF_DIB, bmp_data)
            finally:
                w.CloseClipboard()
            self.status.set(f"已复制图片到剪贴板：{os.path.basename(file_path)}")
            print("[DEBUG] 图片已以 CF_DIB 写入剪贴板")
        except Exception as e:
            self.status.set(f"复制图片失败：{e}")
            print(f"[ERROR] 复制图片失败: {e}")

    # --- 替换：打开并复制（只在是图片时复制图片；音/视频不再写入路径到剪贴板）---
    def _open_and_copy_file(self, filename: str):
        file_path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(file_path):
            self.status.set(f"文件不存在：{file_path}")
            print(f"[WARN] 文件不存在: {file_path}")
            return

        # 打开文件夹并选中目标文件（保持你之前可用的 explorer 打开逻辑）
        try:
            if sys.platform.startswith("win"):
                # 使用 /select,"路径" 方式
                cmd = f'explorer /select,"{file_path}"'
                print(f"[DEBUG] 执行：{cmd}")
                subprocess.Popen(cmd, shell=True)
            elif sys.platform.startswith("darwin"):
                subprocess.Popen(["open", "-R", file_path])
            else:
                subprocess.Popen(["xdg-open", os.path.dirname(file_path)])
        except Exception as e:
            print(f"[WARN] 打开目录失败: {e}")

        # 仅当是图片时，把“图片本体”放进剪贴板；其它类型不写入剪贴板（避免粘贴出路径）
        lower = file_path.lower()
        if lower.endswith((".png", ".jpg", ".jpeg", ".bmp", ".webp")):
            self.copy_image_to_clipboard(file_path)
        else:
            # 音/视频不再覆盖剪贴板，防止 Ctrl+V 出现路径
            self.status.set(f"已打开并选中文件：{os.path.basename(file_path)}（剪贴板未改动）")
            print("[DEBUG] 非图片文件：未写剪贴板（保留用于拖拽上传）")

    # --- 新增：复制标题/正文文本（按钮回调用）---
    def copy_title_text(self, platform: str):
        path = os.path.join(DATA_DIR, f"title_{platform}.txt")
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.copy_text_to_clipboard(f.read().strip())
        except Exception as e:
            self.status.set(f"复制标题失败：{e}")

    def copy_content_text(self, platform: str):
        path = os.path.join(DATA_DIR, f"content_{platform}.txt")
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.copy_text_to_clipboard(f.read().strip())
        except Exception as e:
            self.status.set(f"复制正文失败：{e}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python clipboard_helper.py <platform>")
        sys.exit(1)

    platform = sys.argv[1].lower()
    app = ClipboardHelper(platform)
    app.run()
