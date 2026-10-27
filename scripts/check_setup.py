# Check everything the skill needs and print what is missing (Vietnamese, for the end user).
# Usage: python -X utf8 <skill>/scripts/check_setup.py
import importlib.util, os, shutil, subprocess, sys

CONF = os.path.join(os.path.expanduser("~"), ".kenh-khoa-hoc-short")  # user folder: .env + music/
KEY_FILE = os.path.join(CONF, ".env")
MUSIC_DIR = os.path.join(CONF, "music")
missing = []


def ok(name, good, fix):
    print(("  [OK]   " if good else "  [THIẾU] ") + name)
    if not good:
        missing.append((name, fix))


print("Kiểm tra máy cho skill kenh-khoa-hoc-short:")
ok(f"Python {sys.version.split()[0]} (cần >= 3.9)", sys.version_info >= (3, 9), "Cài Python 3.10+ từ python.org")
for tool, fix in [("ffmpeg", "Windows: winget install Gyan.FFmpeg | macOS: brew install ffmpeg | Linux: sudo apt install ffmpeg"),
                  ("ffprobe", "Đi kèm ffmpeg"),
                  ("node", "Cài Node.js 20+ từ nodejs.org (Windows: winget install OpenJS.NodeJS.LTS)"),
                  ("yt-dlp", "python -m pip install yt-dlp  (chỉ cần khi tìm nhạc nền trên YouTube)")]:
    ok(tool, shutil.which(tool) is not None, fix)
if shutil.which("node"):
    v = subprocess.run(["node", "-v"], capture_output=True, text=True).stdout.strip()
    ok(f"Node {v} (cần >= 20.6 để dùng --env-file)", tuple(map(int, v.lstrip("v").split(".")[:2])) >= (20, 6), "Cập nhật Node.js 20+")
for mod, pkg in [("PIL", "pillow"), ("numpy", "numpy"), ("pymupdf", "pymupdf"), ("faster_whisper", "faster-whisper")]:
    ok(f"Python package {pkg}", importlib.util.find_spec(mod) is not None, f"python -m pip install {pkg}")
key = os.path.exists(KEY_FILE) and "ELEVENLABS_API_KEY=" in open(KEY_FILE, encoding="utf-8").read()
ok(f"ElevenLabs key ở {KEY_FILE}", key,
   f"Tạo file {KEY_FILE} (tạo cả thư mục) với 1 dòng: ELEVENLABS_API_KEY=sk_... (lấy key ở elevenlabs.io > Developers > API Keys)")
music = [f for f in os.listdir(MUSIC_DIR) if f.lower().endswith((".mp3", ".wav", ".m4a"))] if os.path.isdir(MUSIC_DIR) else []
print("  [OK]   Nhạc nền: " + (f"của bạn trong {MUSIC_DIR}" if music else "mặc định của skill (first_snow_piano.mp3)"))

if missing:
    print("\nCần bổ sung:")
    for name, fix in missing:
        print(f"  - {name}: {fix}")
    sys.exit(1)
print("\nMáy đã đủ, dùng được ngay.")
