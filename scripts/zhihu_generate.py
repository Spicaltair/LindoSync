import subprocess
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))   # 项目根目录
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")        # 脚本目录

if __name__ == "__main__":
    script_path = os.path.join(SCRIPTS_DIR, "generate_contents.py")
    subprocess.check_call(["python", script_path, "zhihu"])

