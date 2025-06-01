import subprocess
import time
import os

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "scripts")

def run_script(script_name, description):
    print(f"\n[STEP] {description}...")
    try:
        result = subprocess.run(
            ["python", os.path.join(SCRIPTS_DIR, script_name)],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} failed")
        print(e.stdout)
        print(e.stderr)

if __name__ == "__main__":
    print("[MAIN] Starting content generation")
    run_script("generate_contents.py zhihu", "Generate content for Zhihu")
    run_script("generate_contents.py xhs", "Generate content for Xiaohongshu")

    time.sleep(2)  # prevent race conditions

    print("[MAIN] Starting publishing process")
    run_script("zhihu_playwright.py", "Publish to Zhihu")
    run_script("xhs_playwright.py", "Publish to Xiaohongshu")

    print("[DONE] All steps completed")
