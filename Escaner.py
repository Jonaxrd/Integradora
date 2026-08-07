import tkinter as tk
from tkinter import ttk
import json
import platform
import psutil
import cpuinfo
import wmi
from upgrade_engine import generar_recomendaciones


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


def obtener_gpu():
    try:
        c = wmi.WMI()
        gpus = []

        for gpu in c.Win32_VideoController():
            vram = "Desconocido"

            try:
                if gpu.AdapterRAM:
                    vram = round(int(gpu.AdapterRAM) / (1024 * 1024), 2)
            except:
                pass

            gpus.append({
                "Nombre": gpu.Name,
                "VRAM_MB": vram,
                "Driver": gpu.DriverVersion
            })

        return gpus

    except Exception as e:
        return [{
            "Error": str(e)
        }]


def obtener_motherboard():
    try:
        c = wmi.WMI()
        board = c.Win32_BaseBoard()[0]
        return {
            "Fabricante": board.Manufacturer,
            "Modelo": board.Product
        }
    except:
        return {"Fabricante": "No disponible", "Modelo": "No disponible"}


def obtener_sistema():
    return {
        "Sistema_Operativo": platform.system(),
        "Version": platform.version(),
        "Arquitectura": platform.machine(),
        "Nombre_Equipo": platform.node()
    }


def obtener_discos():
    discos = []
    for p in psutil.disk_partitions():
        try:
            uso = psutil.disk_usage(p.mountpoint)
            discos.append({
                "Unidad": p.device,
                "Capacidad_GB": round(uso.total / (1024**3), 2),
                "Uso_Porcentaje": uso.percent
            })
        except:
            continue
    return discos

def obtener_temperaturas():
    temperaturas = {
        "CPU_C": "No disponible",
        "GPU_C": "No disponible"
    }

    # Intento 1: psutil
    try:
        sensores = psutil.sensors_temperatures()

        if sensores:
            for nombre, entradas in sensores.items():
                for entrada in entradas:
                    etiqueta = (entrada.label or nombre).lower()

                    if "cpu" in etiqueta or "core" in etiqueta:
                        temperaturas["CPU_C"] = round(entrada.current, 1)

                    if "gpu" in etiqueta:
                        temperaturas["GPU_C"] = round(entrada.current, 1)

    except (AttributeError, Exception):
        pass

    # Intento 2: WMI / ACPI para Windows
    if temperaturas["CPU_C"] == "No disponible":
        try:
            w = wmi.WMI(namespace=r"root\wmi")

            sensores = w.MSAcpi_ThermalZoneTemperature()

            if sensores:
                valor = sensores[0].CurrentTemperature

                # Valor WMI viene en décimas de Kelvin
                celsius = (valor / 10.0) - 273.15

                if 0 < celsius < 150:
                    temperaturas["CPU_C"] = round(celsius, 1)

        except Exception:
            pass

    return temperaturas


def guardar_hardware():
    datos = {
        "Sistema": obtener_sistema(),
        "CPU": obtener_cpu(),
        "RAM": obtener_ram(),
        "Motherboard": obtener_motherboard(),
        "GPU": obtener_gpu(),
        "Discos": obtener_discos(),
        "Temperaturas": obtener_temperaturas()
    }

    with open("hardware.json", "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

    return datos


def ejecutar_engine(presupuesto):

    resultado.insert(
        tk.END,
        "\nAnalizando hardware y presupuesto...\n"
    )

    try:

        datos = generar_recomendaciones(
            presupuesto
        )

        resultado.insert(
            tk.END,
            "\nANÁLISIS COMPLETADO\n"
        )

        resultado.insert(
            tk.END,
            f"\nPresupuesto: ${presupuesto:,} MXN\n"
        )

        perfil = datos["system_profile"]

        resultado.insert(
            tk.END,
            f"Salud estimada: {perfil['health']}%\n"
        )

        resultado.insert(
            tk.END,
            f"Nivel: {perfil['level'].upper()}\n"
        )

        resultado.insert(
            tk.END,
            "\nRECOMENDACIONES\n"
        )

        for r in datos["recommendations"]:

            resultado.insert(
                tk.END,
                f"\n[{r['component']}]\n"
            )

            resultado.insert(
                tk.END,
                f"{r['suggestion']}\n"
            )

            resultado.insert(
                tk.END,
                f"Motivo: {r['reason']}\n"
            )

            resultado.insert(
                tk.END,
                f"Impacto: {r['impact']}\n"
            )

            costo = r["cost"]

            if costo > 0:
                resultado.insert(
                    tk.END,
                    f"Costo estimado: ${costo:,} MXN\n"
                )
            else:
                resultado.insert(
                    tk.END,
                    "Costo estimado: Sin costo\n"
                )

        resultado.insert(
            tk.END,
            "\nresultados.json generado correctamente.\n"
        )

    except Exception as e:

        resultado.insert(
            tk.END,
            f"\nError durante el análisis:\n{e}\n"
        )


def escanear():
    resultado.delete("1.0", tk.END)

    datos = guardar_hardware()

    resultado.insert(tk.END, "\nESCANEO COMPLETADO\n")

    for categoria, info in datos.items():
        resultado.insert(tk.END, f"\n===== {categoria} =====\n")

        if isinstance(info, dict):
            for k, v in info.items():
                resultado.insert(tk.END, f"{k}: {v}\n")

        elif isinstance(info, list):
            for item in info:
                resultado.insert(tk.END, f"{item}\n")

    pedir_presupuesto()


def pedir_presupuesto():
    top = tk.Toplevel(ventana)
    top.title("Presupuesto")
    top.geometry("300x150")

    tk.Label(top, text="Presupuesto (MXN):").pack(pady=10)

    entry = tk.Entry(top)
    entry.pack()

    def confirmar():
        if not entry.get().isdigit():
            return

        presupuesto = int(entry.get())
        top.destroy()

        ejecutar_engine(presupuesto)

    tk.Button(top, text="Continuar", command=confirmar).pack(pady=10)
    




ventana = tk.Tk()
ventana.title("PC Hardware Scanner")
ventana.geometry("900x600")
ventana.resizable(False, False)

barra = tk.Frame(ventana, bg="#E5E5E5", height=40)
barra.pack(fill="x")

ttk.Button(barra, text="Escanear", command=escanear).pack(side="left", padx=5, pady=5)
ttk.Button(barra, text="Guardar").pack(side="left", padx=5, pady=5)
ttk.Button(barra, text="Acerca de").pack(side="left", padx=5, pady=5)

panel = tk.Frame(ventana, width=200, bg="#F0F0F0")
panel.pack(side="left", fill="y")

tk.Label(panel, text="Componentes", bg="#F0F0F0").pack(pady=10)

for item in [
    "Sistema",
    "CPU",
    "RAM",
    "GPU",
    "Motherboard",
    "Discos",
    "Temperaturas"
]:
    tk.Button(panel, text=item, width=20).pack(pady=2)


resultado = tk.Text(ventana, font=("Consolas", 10))
resultado.pack(side="right", fill="both", expand=True)

ventana.mainloop()