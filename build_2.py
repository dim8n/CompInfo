# build.py
import subprocess
import os

def build():
    user_dir = os.getenv('USERPROFILE')

    # Запускаем PyInstaller
    subprocess.run([
        "pyinstaller",
        #"--onefile",
        "--noconsole",
        "--strip",
        #f"--upx-dir={user_dir}\\Documents\\develop\\upx",
        #f"--version-file={ver_file}",
        "--icon=compinfo.ico",
        "CompInfo.py"
    ])

if __name__ == "__main__":
    build()