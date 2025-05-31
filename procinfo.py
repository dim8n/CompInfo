import subprocess
import platform

def get_processor_info():
    system = platform.system()
    if system == "Windows":
        try:
            # Просто проверяем, что powershell.exe запускается
            output = subprocess.check_output(
                ["powershell.exe", "-Command", "Write-Host 'Test from PowerShell'"],
                text=True,
                errors='ignore',
                #creationflags=subprocess.HIDE_WINDOW
            ).strip()
            return f"PowerShell test: {output}"
        except Exception as e:
            return f"PowerShell test error: {e}"
    else:
        return "Other OS"

# Затем в вашем основном коде выведите это значение:
print(get_processor_info())