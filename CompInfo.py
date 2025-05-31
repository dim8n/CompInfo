import tkinter as tk
from tkinter import ttk
import socket
import os
import shutil
import platform
import subprocess
import getpass
import psutil
from tkinter import font

# --- Windows-специфичные настройки для скрытия окна консоли ---
# Эти атрибуты существуют в subprocess только на Windows
_startupinfo_windows = None
if platform.system() == "Windows":
    try:
        _startupinfo_windows = subprocess.STARTUPINFO()
        _startupinfo_windows.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        _startupinfo_windows.wShowWindow = subprocess.SW_HIDE
    except AttributeError:
        # Fallback на случай, если какие-то из этих атрибутов отсутствуют (очень старые Python, странные сборки)
        _startupinfo_windows = None
#   --- Конец Windows-специфичных настроек ---

def get_computer_name():
    """Возвращает имя компьютера."""
    return platform.node()

def get_system_info():
    """Возвращает информацию об операционной системе (название, релиз, версия сборки)."""
    system_name = platform.system()
    release = platform.release()
    version = platform.version()
    return f"{system_name} {release} ({version})"

def get_processor_info():
    """Возвращает подробную информацию о модели процессора в зависимости от ОС."""
    system = platform.system()
    if system == "Windows":
        try:
            powershell_command = "Get-CimInstance -ClassName Win32_Processor | Select-Object -ExpandProperty Name"
            
            output = subprocess.check_output(
                ["powershell.exe", "-Command", powershell_command],
                text=True,
                errors='ignore', # Игнорируем ошибки кодировки
                startupinfo=_startupinfo_windows # Используем заранее настроенный startupinfo
            ).strip()

            if output:
                return output.splitlines()[0]
            else:
                return "Неизвестный процессор (PowerShell)"
        except Exception as e:
            return f"Ошибка получения процессора (Windows PowerShell): {e}"
    elif system == "Linux":
        try:
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if "model name" in line:
                        return line.split(":")[1].strip()
            return "Неизвестный процессор (Linux)"
        except Exception as e:
            return f"Ошибка получения процессора (Linux): {e}"
    elif system == "Darwin": # macOS
        try:
            os.environ['PATH'] = os.environ['PATH'] + os.pathsep + '/usr/sbin'
            command = ["sysctl", "-n", "machdep.cpu.brand_string"]
            output = subprocess.check_output(command, text=True).strip()
            return output
        except Exception as e:
            return f"Ошибка получения процессора (macOS): {e}"
    else:
        return f"Недоступно в данной ОС ({system})"

def get_ram_info():
    """Возвращает общий объем оперативной памяти в ГБ."""
    total_ram_bytes = psutil.virtual_memory().total
    total_ram_gb = round(total_ram_bytes / (1024**3), 2)
    return f"{total_ram_gb} ГБ"

def get_username():
    """Возвращает имя текущего пользователя."""
    return getpass.getuser()

def get_domain():
    """Возвращает имя домена (только для Windows)."""
    if platform.system() == "Windows":
        try:
            output = subprocess.check_output(
                "net config workstation", 
                shell=True, 
                text=True, 
                startupinfo=_startupinfo_windows # Используем startupinfo
            )
            for line in output.splitlines():
                if "User name" in line:
                    return line.split()[-1]
                elif "Logon domain" in line:
                    return line.split()[-1]
            return "Не определен"
        except subprocess.CalledProcessError:
            return "Ошибка получения домена"
        except Exception:
            return "Непредвиденная ошибка"
    else:
        return "Недоступно в данной ОС"

def get_all_ip_addresses():
    """Возвращает список всех IP-адресов с привязкой к сетевым интерфейсам."""
    ip_addresses = []
    for interface, addresses in psutil.net_if_addrs().items():
        for addr in addresses:
            if addr.family == socket.AF_INET:
                ip_addresses.append(f"{interface}: \t{addr.address}")
    return ip_addresses

def get_specific_disk_info(drives_to_check):
    """Возвращает информацию о свободном и общем месте на указанных дисках."""
    disk_info = {}
    for drive in drives_to_check:
        if os.path.exists(drive):
            try:
                total, used, free = shutil.disk_usage(drive)
                total_gb = total // (2**30)
                free_gb = free // (2**30)
                disk_info[drive] = {"free_gb": free_gb, "total_gb": total_gb}
            except OSError as e:
                disk_info[drive] = {"error": f"Ошибка: {e}"}
            except Exception as e:
                disk_info[drive] = {"error": f"Непредвиденная ошибка: {e}"}
        else:
            disk_info[drive] = {"error": "Диск не найден"}
    return disk_info

def get_network_drives():
    """Возвращает список подключенных сетевых дисков (только для Windows)."""
    if platform.system() == "Windows":
        try:
            output_bytes = subprocess.check_output(
                "net use", 
                shell=True, 
                startupinfo=_startupinfo_windows # Используем startupinfo
            )
            output_text = output_bytes.decode('cp866', errors='ignore')
            lines = output_text.strip().split('\n')
            network_drives = []
            for line in lines[2:]:
                parts = line.split()
                if len(parts) >= 2 and parts[1].endswith(':'):
                    network_drives.append(f"{parts[1]} -> {parts[2]} ({parts[0]})")
            return network_drives
        except subprocess.CalledProcessError as e:
            return [f"Ошибка получения сетевых дисков: {e}"]
        except Exception as e:
            return [f"Непредвиденная ошибка при получении сетевых дисков: {e}"]
    else:
        return ["Функция доступна только в Windows"]

def update_info():
    """Обновляет информацию в метках интерфейса."""
    computer_name_var.set(f"Имя компьютера: \t{get_computer_name()}")
    system_info_var.set(f"ОС: \t\t\t{get_system_info()}")
    processor_var.set(f"Процессор: \t\t{get_processor_info()}")
    ram_var.set(f"ОЗУ: \t\t\t{get_ram_info()}")
    username_var.set(f"Пользователь: \t\t{get_username()}")
    domain_var.set(f"Домен: \t\t\t{get_domain()}")

    ip_addresses = "\n".join(get_all_ip_addresses())
    ip_address_var.set(ip_addresses if ip_addresses else "Нет IP-адресов")

    disk_info = get_specific_disk_info(["C:", "D:"])

    for drive, info in disk_info.items():
        if drive == "C:":
            if "error" in info:
                c_disk_label_var.set(f"C: - {info['error']}")
                c_disk_progress['value'] = 0
            else:
                c_disk_label_var.set(f"C: - Свободно: {info['free_gb']} ГБ / Всего: {info['total_gb']} ГБ")
                c_disk_progress['maximum'] = info['total_gb']
                c_disk_progress['value'] = info['total_gb'] - info['free_gb']
        elif drive == "D:":
            if "error" in info:
                d_disk_label_var.set(f"D: - {info['error']}")
                d_disk_progress['value'] = 0
            else:
                d_disk_label_var.set(f"D: - Свободно: {info['free_gb']} ГБ / Всего: {info['total_gb']} ГБ")
                d_disk_progress['maximum'] = info['total_gb']
                d_disk_progress['value'] = info['total_gb'] - info['free_gb']

    network_drives_list = get_network_drives()
    network_drives_text = "\n".join(network_drives_list)
    network_drives_var.set(network_drives_text if network_drives_list else "Нет подключенных сетевых дисков")

    root.after(5000, update_info)

# --- Инициализация Tkinter ---
root = tk.Tk()
root.title("Информация о системе")

# --- Настройка стилей ---
bold_small_font = font.Font(weight="bold", size=10)
style = ttk.Style()
style.configure("TLabelframe.Label", font=bold_small_font)

# --- Фрейм: Информация о системе ---
system_info_frame = ttk.LabelFrame(root, text="Информация о системе", style="TLabelframe")
system_info_frame.pack(pady=5, padx=10, fill="x")

computer_name_var = tk.StringVar()
computer_name_label = ttk.Label(system_info_frame, textvariable=computer_name_var, anchor="w", font=("Lucida Console", 9))
computer_name_label.pack(pady=2, padx=5, fill="x")

system_info_var = tk.StringVar()
system_info_label = ttk.Label(system_info_frame, textvariable=system_info_var, anchor="w", font=("Lucida Console", 9))
system_info_label.pack(pady=2, padx=5, fill="x")

processor_var = tk.StringVar()
processor_label = ttk.Label(system_info_frame, textvariable=processor_var, anchor="w", font=("Lucida Console", 9))
processor_label.pack(pady=2, padx=5, fill="x")

ram_var = tk.StringVar()
ram_label = ttk.Label(system_info_frame, textvariable=ram_var, anchor="w", font=("Lucida Console", 9))
ram_label.pack(pady=2, padx=5, fill="x")

username_var = tk.StringVar()
username_label = ttk.Label(system_info_frame, textvariable=username_var, anchor="w", font=("Lucida Console", 9))
username_label.pack(pady=2, padx=5, fill="x")

domain_var = tk.StringVar()
domain_label = ttk.Label(system_info_frame, textvariable=domain_var, anchor="w", font=("Lucida Console", 9))
domain_label.pack(pady=2, padx=5, fill="x")

# --- Фрейм: Сеть ---
network_info_frame = ttk.LabelFrame(root, text="Сеть", style="TLabelframe")
network_info_frame.pack(pady=5, padx=10, fill="x")

ip_address_var = tk.StringVar()
ip_address_label = ttk.Label(network_info_frame, textvariable=ip_address_var, anchor="w", font=("Lucida Console", 9))
ip_address_label.pack(pady=2, padx=5, fill="x")

# --- Фрейм: Локальные диски (C:, D:) ---
disks_frame = ttk.LabelFrame(root, text="Локальные диски (C:, D:)", style="TLabelframe")
disks_frame.pack(pady=5, padx=10, fill="x")

c_disk_frame = ttk.Frame(disks_frame)
c_disk_frame.pack(pady=2, padx=5, fill="x")
c_disk_label_var = tk.StringVar(value="C:")
c_disk_label = ttk.Label(c_disk_frame, textvariable=c_disk_label_var, anchor="w")
c_disk_label.pack(side="left", fill="x", expand=True)
c_disk_progress = ttk.Progressbar(c_disk_frame, orient="horizontal", length=200, mode="determinate")
c_disk_progress.pack(side="right", padx=5)

d_disk_frame = ttk.Frame(disks_frame)
d_disk_frame.pack(pady=2, padx=5, fill="x")
d_disk_label_var = tk.StringVar(value="D:")
d_disk_label = ttk.Label(d_disk_frame, textvariable=d_disk_label_var, anchor="w")
d_disk_label.pack(side="left", fill="x", expand=True)
d_disk_progress = ttk.Progressbar(d_disk_frame, orient="horizontal", length=200, mode="determinate")
d_disk_progress.pack(side="right", padx=5)

# --- Фрейм: Сетевые диски ---
network_drives_frame = ttk.LabelFrame(root, text="Сетевые диски", style="TLabelframe")
network_drives_frame.pack(pady=5, padx=10, fill="x")

network_drives_var = tk.StringVar(value="Нет подключенных сетевых дисков")
network_drives_label = ttk.Label(network_drives_frame, textvariable=network_drives_var, justify='left', font=("Lucida Console", 9))
network_drives_label.pack(pady=2, padx=5, fill="x")

# --- Первоначальное обновление и запуск главного цикла ---
update_info()
root.mainloop()