import tkinter as tk
from tkinter import ttk
import socket
import os
import shutil
import platform
import subprocess
import getpass
import psutil  # Добавляем импорт psutil
from tkinter import font

def get_computer_name():
    return platform.node()

def get_all_ip_addresses():
    ip_addresses = []
    for interface, addresses in psutil.net_if_addrs().items():
        for addr in addresses:
            if addr.family == socket.AF_INET:
                ip_addresses.append(f"{interface}: {addr.address}")
    return ip_addresses

def get_username():
    return getpass.getuser()

def get_domain():
    if platform.system() == "Windows":
        try:
            output = subprocess.check_output("net config workstation", shell=True, text=True)
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

def get_specific_disk_info(drives_to_check):
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
    if platform.system() == "Windows":
        try:
            output_bytes = subprocess.check_output("net use", shell=True)
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
    computer_name_var.set(f"Имя компьютера: {get_computer_name()}")
    ip_addresses = "\n".join(get_all_ip_addresses())
    ip_address_var.set(ip_addresses if ip_addresses else "Нет IP-адресов")
    username_var.set(f"Пользователь: {get_username()}")
    domain_var.set(f"Домен: {get_domain()}")

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

root = tk.Tk()
root.title("Информация о системе")

bold_small_font = font.Font(weight="bold", size=10)  # Создаем жирный шрифт размером 10
style = ttk.Style()
style.configure("TLabelframe.Label", font=bold_small_font)

# Фрейм для информации о системе (имя компьютера, пользователь, домен)
system_info_frame = ttk.LabelFrame(root, text="Информация о системе", style="TLabelframe")
system_info_frame.pack(pady=5, padx=10, fill="x")

computer_name_var = tk.StringVar()
computer_name_label = ttk.Label(system_info_frame, textvariable=computer_name_var, anchor="w")
computer_name_label.pack(pady=2, padx=5, fill="x")

username_var = tk.StringVar()
username_label = ttk.Label(system_info_frame, textvariable=username_var, anchor="w")
username_label.pack(pady=2, padx=5, fill="x")

domain_var = tk.StringVar()
domain_label = ttk.Label(system_info_frame, textvariable=domain_var, anchor="w")
domain_label.pack(pady=2, padx=5, fill="x")

# Фрейм для информации о сети
network_info_frame = ttk.LabelFrame(root, text="Сеть", style="TLabelframe")
network_info_frame.pack(pady=5, padx=10, fill="x")

ip_address_var = tk.StringVar()
ip_address_label = ttk.Label(network_info_frame, textvariable=ip_address_var, anchor="w")
ip_address_label.pack(pady=2, padx=5, fill="x")

# Фрейм для информации о дисках C: и D:
disks_frame = ttk.LabelFrame(root, text="Локальные диски (C:, D:)", style="TLabelframe")
disks_frame.pack(pady=5, padx=10, fill="x")

# Информация и прогрессбар для диска C:
c_disk_frame = ttk.Frame(disks_frame)
c_disk_frame.pack(pady=2, padx=5, fill="x")
c_disk_label_var = tk.StringVar(value="C:")
c_disk_label = ttk.Label(c_disk_frame, textvariable=c_disk_label_var, anchor="w")
c_disk_label.pack(side="left", fill="x", expand=True)
c_disk_progress = ttk.Progressbar(c_disk_frame, orient="horizontal", length=200, mode="determinate")
c_disk_progress.pack(side="right", padx=5)

# Информация и прогрессбар для диска D:
d_disk_frame = ttk.Frame(disks_frame)
d_disk_frame.pack(pady=2, padx=5, fill="x")
d_disk_label_var = tk.StringVar(value="D:")
d_disk_label = ttk.Label(d_disk_frame, textvariable=d_disk_label_var, anchor="w")
d_disk_label.pack(side="left", fill="x", expand=True)
d_disk_progress = ttk.Progressbar(d_disk_frame, orient="horizontal", length=200, mode="determinate")
d_disk_progress.pack(side="right", padx=5)

# Фрейм для информации о сетевых дисках
network_drives_frame = ttk.LabelFrame(root, text="Сетевые диски", style="TLabelframe")
network_drives_frame.pack(pady=5, padx=10, fill="x")

network_drives_var = tk.StringVar(value="Нет подключенных сетевых дисков")
network_drives_label = ttk.Label(network_drives_frame, textvariable=network_drives_var, justify='left')
network_drives_label.pack(pady=2, padx=5, fill="x")

update_info() # Первоначальное обновление информации

root.mainloop()