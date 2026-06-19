import tkinter as tk
from tkinter import ttk
import json

import platform
import psutil
import cpuinfo
import wmi
import GPUtil

def obtener_cpu():
    info = cpuinfo.get_cpu_info()

    return {
        "Procesador": info.get("brand_raw", "Desconocido"),
        "Nucleos_Fisicos": psutil.cpu_count(logical=False),
        "Hilos": psutil.cpu_count(logical=True)
    }


def obtener_ram():
    memoria = psutil.virtual_memory()

    return {
        "RAM_Total_GB": round(memoria.total / (1024**3), 2),
        "RAM_Usada_GB": round(memoria.used / (1024**3), 2),
        "RAM_Libre_GB": round(memoria.available / (1024**3), 2),
        "Uso_RAM_Porcentaje": memoria.percent
    }


def obtener_discos():
    discos = []

    for particion in psutil.disk_partitions():
        try:
            uso = psutil.disk_usage(particion.mountpoint)

            discos.append({
                "Unidad": particion.device,
                "Sistema_Archivos": particion.fstype,
                "Capacidad_GB": round(uso.total / (1024**3), 2),
                "Usado_GB": round(uso.used / (1024**3), 2),
                "Libre_GB": round(uso.free / (1024**3), 2),
                "Uso_Porcentaje": uso.percent
            })

        except PermissionError:
            continue

    return discos


def obtener_gpu():
    gpus = []

    try:
        for gpu in GPUtil.getGPUs():
            gpus.append({
                "Nombre": gpu.name,
                "VRAM_MB": gpu.memoryTotal,
                "VRAM_Usada_MB": gpu.memoryUsed,
                "VRAM_Libre_MB": gpu.memoryFree,
                "Uso_GPU_Porcentaje": round(gpu.load * 100, 2)
            })

    except Exception as e:
        print(f"Error al detectar GPU: {e}")

    return gpus


def obtener_motherboard():
    try:
        c = wmi.WMI()
        board = c.Win32_BaseBoard()[0]

        return {
            "Fabricante": board.Manufacturer,
            "Modelo": board.Product
        }

    except Exception:
        return {
            "Fabricante": "No disponible",
            "Modelo": "No disponible"
        }


def obtener_sistema():
    return {
        "Sistema_Operativo": platform.system(),
        "Version": platform.version(),
        "Arquitectura": platform.machine(),
        "Nombre_Equipo": platform.node()
    }


def generar_json():
    datos = {
        "sistema": obtener_sistema(),
        "cpu": obtener_cpu(),
        "ram": obtener_ram(),
        "motherboard": obtener_motherboard(),
        "gpu": obtener_gpu(),
        "discos": obtener_discos()
    }

    with open("hardware.json", "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)

    print("\n Archivo hardware.json generado correctamente")


def mostrar_datos():
    print("=" * 60)
    print("ESCANEO DE HARDWARE")
    print("=" * 60)

    print("\n SISTEMA")
    for k, v in obtener_sistema().items():
        print(f"{k}: {v}")

    print("\n CPU")
    for k, v in obtener_cpu().items():
        print(f"{k}: {v}")

    print("\n RAM")
    for k, v in obtener_ram().items():
        print(f"{k}: {v}")

    print("\n TARJETA MADRE")
    for k, v in obtener_motherboard().items():
        print(f"{k}: {v}")

    print("\n GPU")

    gpus = obtener_gpu()

    if gpus:
        for gpu in gpus:
            print("-" * 40)
            for k, v in gpu.items():
                print(f"{k}: {v}")
    else:
        print("No se detectó GPU dedicada.")

    print("\n DISCOS")

    for disco in obtener_discos():
        print("-" * 40)
        for k, v in disco.items():
            print(f"{k}: {v}")


def escanear():
    resultado.delete("1.0", tk.END)

    datos = {
        "Sistema": obtener_sistema(),
        "CPU": obtener_cpu(),
        "RAM": obtener_ram(),
        "Motherboard": obtener_motherboard(),
        "GPU": obtener_gpu(),
        "Discos": obtener_discos()
    }

    with open("hardware.json", "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)

    for categoria, info in datos.items():
        resultado.insert(tk.END, f"\n===== {categoria} =====\n")

        if isinstance(info, dict):
            for k, v in info.items():
                resultado.insert(tk.END, f"{k}: {v}\n")

        elif isinstance(info, list):
            for item in info:
                resultado.insert(tk.END, f"{item}\n")

ventana = tk.Tk()
ventana.title("PC Hardware Scanner")
ventana.geometry("900x600")
ventana.resizable(False, False)

# Barra superior tipo WinRAR
barra = tk.Frame(ventana, bg="#E5E5E5", height=40)
barra.pack(fill="x")

ttk.Button(barra, text="Escanear", command=escanear).pack(
    side="left", padx=5, pady=5
)

ttk.Button(barra, text="Guardar").pack(
    side="left", padx=5, pady=5
)

ttk.Button(barra, text="Acerca de").pack(
    side="left", padx=5, pady=5
)

# Panel lateral
panel = tk.Frame(ventana, width=200, bg="#F0F0F0")
panel.pack(side="left", fill="y")

tk.Label(
    panel,
    text="Componentes",
    bg="#F0F0F0",
    font=("Segoe UI", 10, "bold")
).pack(pady=10)

for item in [
    "Sistema",
    "CPU",
    "RAM",
    "GPU",
    "Motherboard",
    "Discos"
]:
    tk.Button(panel, text=item, width=20).pack(pady=2)

# Área principal
resultado = tk.Text(
    ventana,
    font=("Consolas", 10)
)

resultado.pack(
    side="right",
    fill="both",
    expand=True
)

ventana.mainloop()