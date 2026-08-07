import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import threading
import json
import platform
import os


import psutil
import cpuinfo
import wmi

from upgrade_engine import generar_recomendaciones

APP_NAME = "SCOPE Hardware Scanner"
APP_VERSION = "v2.0"

COLOR_BG = "#050505"
COLOR_PANEL = "#0D0D0D"
COLOR_CARD = "#131313"
COLOR_CARD_2 = "#181818"

COLOR_PRIMARY = "#2563EB"
COLOR_PRIMARY_LIGHT = "#3B82F6"

COLOR_TEXT = "#FFFFFF"
COLOR_TEXT_SECONDARY = "#A7B0C0"

COLOR_SUCCESS = "#22C55E"
COLOR_WARNING = "#F59E0B"
COLOR_DANGER = "#EF4444"

PWA_URL = "https://jonaxrd.github.io/Integradora/pwa.html"

datos_hardware = {}
datos_resultados = {}
presupuesto_actual = 0


def obtener_sistema():

    return {
        "Sistema_Operativo": platform.system(),
        "Version": platform.version(),
        "Arquitectura": platform.machine(),
        "Nombre_Equipo": platform.node()
    }


def obtener_cpu():

    info = cpuinfo.get_cpu_info()

    frecuencia = psutil.cpu_freq()

    frecuencia_actual = "No disponible"

    if frecuencia:
        frecuencia_actual = round(
            frecuencia.current / 1000,
            2
        )

    return {
        "Procesador": info.get(
            "brand_raw",
            platform.processor() or "Desconocido"
        ),
        "Nucleos_Fisicos": psutil.cpu_count(
            logical=False
        ),
        "Hilos": psutil.cpu_count(
            logical=True
        ),
        "Frecuencia_GHz": frecuencia_actual,
        "Uso_CPU_Porcentaje": psutil.cpu_percent(
            interval=0.8
        )
    }


def obtener_ram():

    memoria = psutil.virtual_memory()

    return {
        "RAM_Total_GB": round(
            memoria.total / (1024 ** 3),
            2
        ),
        "RAM_Usada_GB": round(
            memoria.used / (1024 ** 3),
            2
        ),
        "RAM_Libre_GB": round(
            memoria.available / (1024 ** 3),
            2
        ),
        "Uso_RAM_Porcentaje": memoria.percent
    }


def obtener_gpu():

    gpus = []

    try:

        conexion = wmi.WMI()

        for gpu in conexion.Win32_VideoController():

            vram = "No disponible"

            try:

                if gpu.AdapterRAM:

                    vram = round(
                        int(gpu.AdapterRAM) /
                        (1024 ** 2),
                        2
                    )

            except Exception:
                pass

            gpus.append({
                "Nombre": gpu.Name,
                "VRAM_MB": vram,
                "Driver": gpu.DriverVersion
            })

    except Exception as e:

        gpus.append({
            "Nombre": "No disponible",
            "VRAM_MB": "No disponible",
            "Driver": "No disponible",
            "Error": str(e)
        })

    return gpus


def obtener_motherboard():

    try:

        conexion = wmi.WMI()

        boards = conexion.Win32_BaseBoard()

        if not boards:

            return {
                "Fabricante": "No disponible",
                "Modelo": "No disponible"
            }

        board = boards[0]

        return {
            "Fabricante": (
                board.Manufacturer
                or "No disponible"
            ),
            "Modelo": (
                board.Product
                or "No disponible"
            )
        }

    except Exception:

        return {
            "Fabricante": "No disponible",
            "Modelo": "No disponible"
        }


def obtener_discos():

    discos = []

    unidades_procesadas = set()

    for particion in psutil.disk_partitions():

        try:

            if particion.device in unidades_procesadas:
                continue

            unidades_procesadas.add(
                particion.device
            )

            uso = psutil.disk_usage(
                particion.mountpoint
            )

            discos.append({
                "Unidad": particion.device,
                "Sistema_Archivos": particion.fstype,
                "Capacidad_GB": round(
                    uso.total / (1024 ** 3),
                    2
                ),
                "Usado_GB": round(
                    uso.used / (1024 ** 3),
                    2
                ),
                "Libre_GB": round(
                    uso.free / (1024 ** 3),
                    2
                ),
                "Uso_Porcentaje": uso.percent
            })

        except (
            PermissionError,
            OSError
        ):
            continue

    return discos


def obtener_temperaturas():

    temperaturas = {
        "CPU_C": "No disponible",
        "GPU_C": "No disponible"
    }

    try:

        sensores = psutil.sensors_temperatures()

        if sensores:

            for nombre, entradas in sensores.items():

                for entrada in entradas:

                    etiqueta = (
                        entrada.label
                        or nombre
                    ).lower()

                    if (
                        "cpu" in etiqueta
                        or "core" in etiqueta
                        or "package" in etiqueta
                    ):

                        temperaturas["CPU_C"] = round(
                            entrada.current,
                            1
                        )

                    if "gpu" in etiqueta:

                        temperaturas["GPU_C"] = round(
                            entrada.current,
                            1
                        )

    except Exception:
        pass

    if temperaturas["CPU_C"] == "No disponible":

        try:

            conexion = wmi.WMI(
                namespace=r"root\wmi"
            )

            sensores = (
                conexion
                .MSAcpi_ThermalZoneTemperature()
            )

            temperaturas_validas = []

            for sensor in sensores:

                valor = sensor.CurrentTemperature

                celsius = (
                    valor / 10.0
                ) - 273.15

                if 0 < celsius < 120:

                    temperaturas_validas.append(
                        celsius
                    )

            if temperaturas_validas:

                temperaturas["CPU_C"] = round(
                    max(temperaturas_validas),
                    1
                )

        except Exception:
            pass

    return temperaturas


def guardar_hardware(datos):

    ruta = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        "hardware.json"
    )

    with open(
        ruta,
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            datos,
            archivo,
            indent=4,
            ensure_ascii=False
        )

    return ruta


def actualizar_estado(
    texto,
    color=COLOR_TEXT_SECONDARY
):

    estado_label.config(
        text=texto,
        fg=color
    )


def actualizar_progreso(valor):

    progreso["value"] = valor


def actualizar_card(label, valor):

    label.config(
        text=valor
    )


def abrir_pwa():

    try:

        webbrowser.open(PWA_URL)

        actualizar_estado(
            "PWA abierta en el navegador.",
            COLOR_SUCCESS
        )

    except Exception as e:

        messagebox.showerror(
            "Error",
            f"No fue posible abrir la PWA.\n\n{e}"
        )


def iniciar_escaneo():

    boton_escanear.config(
        state="disabled"
    )

    progreso["value"] = 0

    salud_numero.config(
        text="--%"
    )

    salud_estado.config(
        text="Analizando...",
        fg=COLOR_PRIMARY_LIGHT
    )

    actualizar_card(
        cpu_valor,
        "Analizando..."
    )

    actualizar_card(
        ram_valor,
        "Esperando..."
    )

    actualizar_card(
        gpu_valor,
        "Esperando..."
    )

    actualizar_card(
        disco_valor,
        "Esperando..."
    )

    actualizar_card(
        temp_valor,
        "Esperando..."
    )

    actualizar_estado(
        "Iniciando escaneo de hardware...",
        COLOR_PRIMARY_LIGHT
    )

    hilo = threading.Thread(
        target=escanear_hardware,
        daemon=True
    )

    hilo.start()


def escanear_hardware():

    global datos_hardware

    try:

        datos = {}

        ventana.after(
            0,
            actualizar_estado,
            "Analizando sistema operativo...",
            COLOR_PRIMARY_LIGHT
        )

        datos["Sistema"] = obtener_sistema()

        ventana.after(
            0,
            actualizar_progreso,
            10
        )


        ventana.after(
            0,
            actualizar_estado,
            "Detectando procesador...",
            COLOR_PRIMARY_LIGHT
        )

        datos["CPU"] = obtener_cpu()

        texto_cpu = (
            f"{datos['CPU']['Procesador']}\n"
            f"{datos['CPU']['Nucleos_Fisicos']} núcleos / "
            f"{datos['CPU']['Hilos']} hilos"
        )

        ventana.after(
            0,
            actualizar_card,
            cpu_valor,
            texto_cpu
        )

        ventana.after(
            0,
            actualizar_progreso,
            25
        )


        ventana.after(
            0,
            actualizar_estado,
            "Analizando memoria RAM...",
            COLOR_PRIMARY_LIGHT
        )

        datos["RAM"] = obtener_ram()

        texto_ram = (
            f"{datos['RAM']['RAM_Total_GB']} GB\n"
            f"Uso: {datos['RAM']['Uso_RAM_Porcentaje']}%"
        )

        ventana.after(
            0,
            actualizar_card,
            ram_valor,
            texto_ram
        )

        ventana.after(
            0,
            actualizar_progreso,
            40
        )


        ventana.after(
            0,
            actualizar_estado,
            "Detectando tarjeta gráfica...",
            COLOR_PRIMARY_LIGHT
        )

        datos["GPU"] = obtener_gpu()

        if datos["GPU"]:

            gpu = datos["GPU"][0]

            texto_gpu = gpu.get(
                "Nombre",
                "No disponible"
            )

            vram = gpu.get(
                "VRAM_MB",
                "No disponible"
            )

            if isinstance(
                vram,
                (int, float)
            ):

                texto_gpu += (
                    f"\nVRAM: "
                    f"{round(vram / 1024, 2)} GB"
                )

        else:

            texto_gpu = (
                "No se detectó GPU"
            )

        ventana.after(
            0,
            actualizar_card,
            gpu_valor,
            texto_gpu
        )

        ventana.after(
            0,
            actualizar_progreso,
            55
        )


        ventana.after(
            0,
            actualizar_estado,
            "Detectando tarjeta madre...",
            COLOR_PRIMARY_LIGHT
        )

        datos["Motherboard"] = (
            obtener_motherboard()
        )

        ventana.after(
            0,
            actualizar_progreso,
            65
        )


        ventana.after(
            0,
            actualizar_estado,
            "Analizando almacenamiento...",
            COLOR_PRIMARY_LIGHT
        )

        datos["Discos"] = obtener_discos()

        if datos["Discos"]:

            disco = datos["Discos"][0]

            texto_disco = (
                f"{disco['Unidad']} "
                f"{disco['Capacidad_GB']} GB\n"
                f"Uso: "
                f"{disco['Uso_Porcentaje']}%"
            )

            if len(datos["Discos"]) > 1:

                texto_disco += (
                    f"\n"
                    f"{len(datos['Discos'])} "
                    f"unidades detectadas"
                )

        else:

            texto_disco = (
                "No disponible"
            )

        ventana.after(
            0,
            actualizar_card,
            disco_valor,
            texto_disco
        )

        ventana.after(
            0,
            actualizar_progreso,
            80
        )


        ventana.after(
            0,
            actualizar_estado,
            "Consultando temperaturas...",
            COLOR_PRIMARY_LIGHT
        )

        datos["Temperaturas"] = (
            obtener_temperaturas()
        )

        cpu_temp = (
            datos["Temperaturas"]
            .get(
                "CPU_C",
                "No disponible"
            )
        )

        gpu_temp = (
            datos["Temperaturas"]
            .get(
                "GPU_C",
                "No disponible"
            )
        )

        texto_temperatura = (
            f"CPU: "
            f"{cpu_temp}"
        )

        if cpu_temp != "No disponible":

            texto_temperatura += " °C"

        texto_temperatura += (
            f"\nGPU: "
            f"{gpu_temp}"
        )

        if gpu_temp != "No disponible":

            texto_temperatura += " °C"

        ventana.after(
            0,
            actualizar_card,
            temp_valor,
            texto_temperatura
        )

        ventana.after(
            0,
            actualizar_progreso,
            90
        )


        ventana.after(
            0,
            actualizar_estado,
            "Guardando información del equipo...",
            COLOR_PRIMARY_LIGHT
        )

        guardar_hardware(datos)

        datos_hardware = datos

        ventana.after(
            0,
            actualizar_progreso,
            100
        )

        ventana.after(
            0,
            escaneo_finalizado
        )

    except Exception as e:

        ventana.after(
            0,
            escaneo_error,
            str(e)
        )


def calcular_salud_basica():

    puntuacion = 100

    ram = datos_hardware.get(
        "RAM",
        {}
    )

    uso_ram = ram.get(
        "Uso_RAM_Porcentaje",
        0
    )

    if uso_ram >= 90:
        puntuacion -= 20

    elif uso_ram >= 80:
        puntuacion -= 10


    discos = datos_hardware.get(
        "Discos",
        []
    )

    for disco in discos:

        uso = disco.get(
            "Uso_Porcentaje",
            0
        )

        if uso >= 95:

            puntuacion -= 15
            break

        elif uso >= 85:

            puntuacion -= 8
            break


    temperaturas = datos_hardware.get(
        "Temperaturas",
        {}
    )

    temperatura_cpu = temperaturas.get(
        "CPU_C"
    )

    try:

        temperatura_cpu = float(
            temperatura_cpu
        )

        if temperatura_cpu >= 90:

            puntuacion -= 25

        elif temperatura_cpu >= 80:

            puntuacion -= 15

        elif temperatura_cpu >= 70:

            puntuacion -= 5

    except (
        TypeError,
        ValueError
    ):
        pass


    return max(
        0,
        min(
            100,
            puntuacion
        )
    )


def escaneo_finalizado():

    salud = calcular_salud_basica()

    salud_numero.config(
        text=f"{salud}%"
    )

    barra_salud["value"] = salud

    if salud >= 85:

        texto = "Excelente"
        color = COLOR_SUCCESS

    elif salud >= 70:

        texto = "Bueno"
        color = COLOR_PRIMARY_LIGHT

    elif salud >= 50:

        texto = "Necesita mejoras"
        color = COLOR_WARNING

    else:

        texto = "Requiere atención"
        color = COLOR_DANGER

    salud_estado.config(
        text=texto,
        fg=color
    )

    actualizar_estado(
        "Escaneo completado. hardware.json generado correctamente.",
        COLOR_SUCCESS
    )

    boton_escanear.config(
        state="normal"
    )

    pedir_presupuesto()


def pedir_presupuesto():

    ventana_presupuesto = tk.Toplevel(ventana)

    ventana_presupuesto.title(
        "Presupuesto de actualización"
    )

    ventana_presupuesto.geometry(
        "420x280"
    )

    ventana_presupuesto.resizable(
        False,
        False
    )

    ventana_presupuesto.configure(
        bg=COLOR_PANEL
    )

    ventana_presupuesto.transient(
        ventana
    )

    ventana_presupuesto.grab_set()


    titulo = tk.Label(
        ventana_presupuesto,
        text="Presupuesto disponible",
        bg=COLOR_PANEL,
        fg=COLOR_TEXT,
        font=(
            "Segoe UI",
            18,
            "bold"
        )
    )

    titulo.pack(
        pady=(30, 8)
    )


    descripcion = tk.Label(
        ventana_presupuesto,
        text=(
            "Ingresa cuánto deseas invertir en mejorar\n"
            "el hardware de tu equipo."
        ),
        bg=COLOR_PANEL,
        fg=COLOR_TEXT_SECONDARY,
        font=(
            "Segoe UI",
            10
        ),
        justify="center"
    )

    descripcion.pack(
        pady=(0, 20)
    )


    entrada = tk.Entry(
        ventana_presupuesto,
        font=(
            "Segoe UI",
            15
        ),
        justify="center",
        bg=COLOR_CARD,
        fg=COLOR_TEXT,
        insertbackground=COLOR_TEXT,
        relief="flat"
    )

    entrada.pack(
        ipadx=20,
        ipady=8,
        padx=50,
        fill="x"
    )

    entrada.focus()


    moneda = tk.Label(
        ventana_presupuesto,
        text="Pesos mexicanos (MXN)",
        bg=COLOR_PANEL,
        fg=COLOR_TEXT_SECONDARY,
        font=(
            "Segoe UI",
            9
        )
    )

    moneda.pack(
        pady=(5, 15)
    )


    def confirmar():

        valor = entrada.get().strip()

        if not valor:

            messagebox.showwarning(
                "Presupuesto",
                "Ingresa un presupuesto."
            )

            return

        try:

            presupuesto = int(
                valor.replace(
                    ",",
                    ""
                )
            )

            if presupuesto < 0:

                raise ValueError

        except ValueError:

            messagebox.showwarning(
                "Presupuesto",
                "Ingresa una cantidad válida."
            )

            return

        ventana_presupuesto.destroy()

        procesar_presupuesto(
            presupuesto
        )


    boton = ttk.Button(
        ventana_presupuesto,
        text="Analizar equipo",
        style="Scope.TButton",
        command=confirmar
    )

    boton.pack(
        pady=10
    )


    ventana_presupuesto.bind(
        "<Return>",
        lambda event: confirmar()
    )

def procesar_presupuesto(presupuesto):

    global presupuesto_actual
    global datos_resultados

    presupuesto_actual = presupuesto

    progreso["value"] = 0

    actualizar_estado(
        "Analizando hardware y presupuesto...",
        COLOR_PRIMARY_LIGHT
    )

    hilo = threading.Thread(
        target=ejecutar_motor_recomendaciones,
        args=(presupuesto,),
        daemon=True
    )

    hilo.start()

def ejecutar_motor_recomendaciones(
    presupuesto
):

    global datos_resultados

    try:

        ventana.after(
            0,
            actualizar_progreso,
            30
        )

        resultados = generar_recomendaciones(
            presupuesto
        )

        ventana.after(
            0,
            actualizar_progreso,
            70
        )

        datos_resultados = resultados

        ventana.after(
            0,
            actualizar_progreso,
            100
        )

        ventana.after(
            0,
            analisis_finalizado
        )

    except Exception as e:

        ventana.after(
            0,
            error_analisis,
            str(e)
        )

def analisis_finalizado():

    perfil = datos_resultados.get(
        "system_profile",
        {}
    )

    salud = perfil.get(
        "health",
        0
    )

    nivel = perfil.get(
        "level",
        "desconocido"
    )


    salud_numero.config(
        text=f"{salud}%"
    )

    barra_salud["value"] = salud


    if salud >= 85:

        texto = "Excelente"
        color = COLOR_SUCCESS

    elif salud >= 70:

        texto = "Bueno"
        color = COLOR_PRIMARY_LIGHT

    elif salud >= 50:

        texto = "Necesita mejoras"
        color = COLOR_WARNING

    else:

        texto = "Requiere atención"
        color = COLOR_DANGER


    salud_estado.config(
        text=texto,
        fg=color
    )


    recomendaciones = (
        datos_resultados.get(
            "recommendations",
            []
        )
    )


    actualizar_estado(
        (
            f"Análisis completado. "
            f"{len(recomendaciones)} recomendaciones generadas "
            f"con presupuesto de "
            f"${presupuesto_actual:,} MXN."
        ),
        COLOR_SUCCESS
    )


    messagebox.showinfo(
        "Análisis completado",
        (
            "El análisis de SCOPE finalizó correctamente.\n\n"
            f"Salud del equipo: {salud}%\n"
            f"Nivel: {nivel.capitalize()}\n"
            f"Presupuesto: ${presupuesto_actual:,} MXN\n"
            f"Recomendaciones: {len(recomendaciones)}\n\n"
            "El archivo resultados.json fue generado correctamente."
        )
    )

def error_analisis(error):

    progreso["value"] = 0

    actualizar_estado(
        "No fue posible generar las recomendaciones.",
        COLOR_DANGER
    )

    messagebox.showerror(
        "Error",
        (
            "Ocurrió un error durante "
            "el análisis de recomendaciones.\n\n"
            f"{error}"
        )
    )


def escaneo_error(error):

    progreso["value"] = 0

    boton_escanear.config(
        state="normal"
    )

    salud_estado.config(
        text="Error",
        fg=COLOR_DANGER
    )

    actualizar_estado(
        "Ocurrió un error durante el escaneo.",
        COLOR_DANGER
    )

    messagebox.showerror(
        "Error de escaneo",
        error
    )


def limpiar_panel():

    for widget in cards_container.winfo_children():

        widget.grid_forget()


def crear_panel_detalle(titulo, filas):

    limpiar_panel()

    panel = tk.Frame(
        cards_container,
        bg=COLOR_CARD,
        highlightbackground="#242424",
        highlightthickness=1
    )

    panel.grid(
        row=0,
        column=0,
        columnspan=2,
        sticky="nsew",
        padx=8,
        pady=8
    )

    encabezado = tk.Label(
        panel,
        text=titulo,
        bg=COLOR_CARD,
        fg=COLOR_TEXT,
        font=("Segoe UI", 20, "bold")
    )

    encabezado.pack(
        anchor="w",
        padx=25,
        pady=(25, 20)
    )


    for etiqueta, valor in filas:

        fila = tk.Frame(
            panel,
            bg=COLOR_CARD
        )

        fila.pack(
            fill="x",
            padx=25,
            pady=6
        )

        label = tk.Label(
            fila,
            text=etiqueta,
            bg=COLOR_CARD,
            fg=COLOR_TEXT_SECONDARY,
            font=("Segoe UI", 10),
            width=25,
            anchor="w"
        )

        label.pack(
            side="left"
        )

        value = tk.Label(
            fila,
            text=str(valor),
            bg=COLOR_CARD,
            fg=COLOR_TEXT,
            font=("Segoe UI", 11, "bold"),
            anchor="w",
            justify="left"
        )

        value.pack(
            side="left",
            fill="x",
            expand=True
        )


def mostrar_resumen():

    restaurar_dashboard()


def mostrar_sistema():

    sistema = datos_hardware.get(
        "Sistema",
        {}
    )

    motherboard = datos_hardware.get(
        "Motherboard",
        {}
    )

    filas = [
        (
            "Sistema operativo",
            sistema.get(
                "Sistema_Operativo",
                "No disponible"
            )
        ),
        (
            "Versión",
            sistema.get(
                "Version",
                "No disponible"
            )
        ),
        (
            "Arquitectura",
            sistema.get(
                "Arquitectura",
                "No disponible"
            )
        ),
        (
            "Nombre del equipo",
            sistema.get(
                "Nombre_Equipo",
                "No disponible"
            )
        ),
        (
            "Fabricante motherboard",
            motherboard.get(
                "Fabricante",
                "No disponible"
            )
        ),
        (
            "Modelo motherboard",
            motherboard.get(
                "Modelo",
                "No disponible"
            )
        )
    ]

    crear_panel_detalle(
        "Información del Sistema",
        filas
    )


def mostrar_cpu():

    cpu = datos_hardware.get(
        "CPU",
        {}
    )

    filas = [
        (
            "Procesador",
            cpu.get(
                "Procesador",
                "No disponible"
            )
        ),
        (
            "Núcleos físicos",
            cpu.get(
                "Nucleos_Fisicos",
                "No disponible"
            )
        ),
        (
            "Hilos",
            cpu.get(
                "Hilos",
                "No disponible"
            )
        ),
        (
            "Frecuencia",
            f"{cpu.get('Frecuencia_GHz', 'No disponible')} GHz"
        ),
        (
            "Uso actual",
            f"{cpu.get('Uso_CPU_Porcentaje', 'No disponible')}%"
        )
    ]

    crear_panel_detalle(
        "Procesador",
        filas
    )


def mostrar_ram():

    ram = datos_hardware.get(
        "RAM",
        {}
    )

    filas = [
        (
            "Memoria total",
            f"{ram.get('RAM_Total_GB', 0)} GB"
        ),
        (
            "Memoria usada",
            f"{ram.get('RAM_Usada_GB', 0)} GB"
        ),
        (
            "Memoria disponible",
            f"{ram.get('RAM_Libre_GB', 0)} GB"
        ),
        (
            "Uso de memoria",
            f"{ram.get('Uso_RAM_Porcentaje', 0)}%"
        )
    ]

    crear_panel_detalle(
        "Memoria RAM",
        filas
    )


def mostrar_gpu():

    gpus = datos_hardware.get(
        "GPU",
        []
    )

    if not gpus:

        crear_panel_detalle(
            "Tarjeta Gráfica",
            [
                (
                    "Estado",
                    "No se detectó GPU"
                )
            ]
        )

        return


    filas = []

    for indice, gpu in enumerate(
        gpus,
        start=1
    ):

        vram = gpu.get(
            "VRAM_MB",
            "No disponible"
        )

        if isinstance(
            vram,
            (int, float)
        ):

            vram = (
                f"{round(vram / 1024, 2)} GB"
            )


        filas.extend([
            (
                f"GPU {indice}",
                gpu.get(
                    "Nombre",
                    "No disponible"
                )
            ),
            (
                "VRAM",
                vram
            ),
            (
                "Driver",
                gpu.get(
                    "Driver",
                    "No disponible"
                )
            )
        ])


    crear_panel_detalle(
        "Tarjeta Gráfica",
        filas
    )


def mostrar_discos():

    discos = datos_hardware.get(
        "Discos",
        []
    )

    filas = []

    if not discos:

        filas.append(
            (
                "Estado",
                "No se detectaron unidades"
            )
        )


    for indice, disco in enumerate(
        discos,
        start=1
    ):

        filas.extend([
            (
                f"Unidad {indice}",
                disco.get(
                    "Unidad",
                    "No disponible"
                )
            ),
            (
                "Sistema de archivos",
                disco.get(
                    "Sistema_Archivos",
                    "No disponible"
                )
            ),
            (
                "Capacidad",
                f"{disco.get('Capacidad_GB', 0)} GB"
            ),
            (
                "Utilizado",
                f"{disco.get('Usado_GB', 0)} GB"
            ),
            (
                "Disponible",
                f"{disco.get('Libre_GB', 0)} GB"
            ),
            (
                "Uso",
                f"{disco.get('Uso_Porcentaje', 0)}%"
            )
        ])


    crear_panel_detalle(
        "Almacenamiento",
        filas
    )


def mostrar_temperaturas():

    temps = datos_hardware.get(
        "Temperaturas",
        {}
    )

    cpu_temp = temps.get(
        "CPU_C",
        "No disponible"
    )

    gpu_temp = temps.get(
        "GPU_C",
        "No disponible"
    )


    if cpu_temp != "No disponible":
        cpu_temp = f"{cpu_temp} °C"

    if gpu_temp != "No disponible":
        gpu_temp = f"{gpu_temp} °C"


    filas = [
        (
            "Temperatura CPU",
            cpu_temp
        ),
        (
            "Temperatura GPU",
            gpu_temp
        )
    ]

    crear_panel_detalle(
        "Temperaturas",
        filas
    )


def mostrar_presupuesto():

    if presupuesto_actual <= 0:

        filas = [
            (
                "Presupuesto",
                "Aún no se ha ingresado"
            )
        ]

    else:

        filas = [
            (
                "Presupuesto disponible",
                f"${presupuesto_actual:,} MXN"
            )
        ]


    crear_panel_detalle(
        "Presupuesto",
        filas
    )


def mostrar_recomendaciones():

    recomendaciones = datos_resultados.get(
        "recommendations",
        []
    )

    limpiar_panel()


    panel = tk.Frame(
        cards_container,
        bg=COLOR_CARD,
        highlightbackground="#242424",
        highlightthickness=1
    )

    panel.grid(
        row=0,
        column=0,
        columnspan=2,
        sticky="nsew",
        padx=8,
        pady=8
    )


    titulo = tk.Label(
        panel,
        text="Recomendaciones de SCOPE",
        bg=COLOR_CARD,
        fg=COLOR_TEXT,
        font=("Segoe UI", 20, "bold")
    )

    titulo.pack(
        anchor="w",
        padx=25,
        pady=(25, 20)
    )


    if not recomendaciones:

        mensaje = tk.Label(
            panel,
            text=(
                "Aún no existen recomendaciones.\n"
                "Realiza un escaneo e ingresa un presupuesto."
            ),
            bg=COLOR_CARD,
            fg=COLOR_TEXT_SECONDARY,
            font=("Segoe UI", 11),
            justify="left"
        )

        mensaje.pack(
            anchor="w",
            padx=25,
            pady=10
        )

        return


    for recomendacion in recomendaciones:

        card = tk.Frame(
            panel,
            bg=COLOR_CARD_2,
            highlightbackground="#282828",
            highlightthickness=1
        )

        card.pack(
            fill="x",
            padx=25,
            pady=8
        )


        componente = tk.Label(
            card,
            text=recomendacion.get(
                "component",
                "Recomendación"
            ),
            bg=COLOR_CARD_2,
            fg=COLOR_PRIMARY_LIGHT,
            font=("Segoe UI", 11, "bold")
        )

        componente.pack(
            anchor="w",
            padx=18,
            pady=(15, 4)
        )


        sugerencia = tk.Label(
            card,
            text=recomendacion.get(
                "suggestion",
                ""
            ),
            bg=COLOR_CARD_2,
            fg=COLOR_TEXT,
            font=("Segoe UI", 11, "bold"),
            wraplength=700,
            justify="left"
        )

        sugerencia.pack(
            anchor="w",
            padx=18
        )


        impacto = tk.Label(
            card,
            text=(
                "Impacto: "
                + recomendacion.get(
                    "impact",
                    "No disponible"
                )
            ),
            bg=COLOR_CARD_2,
            fg=COLOR_TEXT_SECONDARY,
            font=("Segoe UI", 9),
            wraplength=700,
            justify="left"
        )

        impacto.pack(
            anchor="w",
            padx=18,
            pady=(6, 2)
        )


        razon = tk.Label(
            card,
            text=(
                "Motivo: "
                + recomendacion.get(
                    "reason",
                    "No disponible"
                )
            ),
            bg=COLOR_CARD_2,
            fg=COLOR_TEXT_SECONDARY,
            font=("Segoe UI", 9),
            wraplength=700,
            justify="left"
        )

        razon.pack(
            anchor="w",
            padx=18,
            pady=2
        )


        costo = recomendacion.get(
            "cost",
            0
        )

        prioridad = recomendacion.get(
            "priority",
            0
        )


        datos = tk.Label(
            card,
            text=(
                f"Costo estimado: "
                f"${costo:,} MXN"
                if costo
                else "Costo estimado: Sin costo"
            )
            + f"     Prioridad: {prioridad}",
            bg=COLOR_CARD_2,
            fg=COLOR_TEXT,
            font=("Segoe UI", 9, "bold")
        )

        datos.pack(
            anchor="w",
            padx=18,
            pady=(5, 15)
        )


def exportar_resultados():

    if not datos_hardware:

        messagebox.showinfo(
            "SCOPE",
            "Primero realiza un escaneo."
        )

        return


    carpeta = os.path.dirname(
        os.path.abspath(__file__)
    )


    hardware_path = os.path.join(
        carpeta,
        "hardware.json"
    )


    if datos_resultados:

        resultados_path = os.path.join(
            carpeta,
            "resultados.json"
        )

        mensaje = (
            "Los archivos se encuentran en:\n\n"
            f"{hardware_path}\n"
            f"{resultados_path}"
        )

    else:

        mensaje = (
            "El archivo se encuentra en:\n\n"
            f"{hardware_path}"
        )


    messagebox.showinfo(
        "Archivos de SCOPE",
        mensaje
    )

def mostrar_seccion(nombre):

    if not datos_hardware and nombre not in [
        "Resumen del Equipo",
        "PWA"
    ]:

        messagebox.showinfo(
            "SCOPE",
            "Primero realiza un escaneo del equipo."
        )

        return


    titulo_central.config(
        text=nombre
    )


    if nombre == "Resumen del Equipo":

        mostrar_resumen()

    elif nombre == "Sistema":

        mostrar_sistema()

    elif nombre == "Procesador":

        mostrar_cpu()

    elif nombre == "Memoria RAM":

        mostrar_ram()

    elif nombre == "Tarjeta Gráfica":

        mostrar_gpu()

    elif nombre == "Almacenamiento":

        mostrar_discos()

    elif nombre == "Temperaturas":

        mostrar_temperaturas()

    elif nombre == "Presupuesto":

        mostrar_presupuesto()

    elif nombre == "Recomendaciones":

        mostrar_recomendaciones()

    elif nombre == "Exportar":

        exportar_resultados()


    actualizar_estado(
        f"Sección: {nombre}"
    )


def restaurar_dashboard():

    for widget in cards_container.winfo_children():

        widget.grid()


    titulo_central.config(
        text="Resumen del Equipo"
    )

def acerca_de():

    messagebox.showinfo(
        "Acerca de SCOPE",
        f"""
{APP_NAME}
{APP_VERSION}

Sistema de análisis de hardware
y recomendaciones de actualización.

Proyecto SCOPE
"""
    )


ventana = tk.Tk()

ventana.title(
    f"{APP_NAME} {APP_VERSION}"
)

ventana.geometry(
    "1200x760"
)

ventana.minsize(
    1050,
    650
)

ventana.configure(
    bg=COLOR_BG
)


style = ttk.Style()

style.theme_use(
    "clam"
)


style.configure(
    "Scope.TButton",
    background=COLOR_PRIMARY,
    foreground=COLOR_TEXT,
    borderwidth=0,
    padding=(15, 10),
    font=(
        "Segoe UI",
        10,
        "bold"
    )
)


style.map(
    "Scope.TButton",
    background=[
        (
            "active",
            COLOR_PRIMARY_LIGHT
        )
    ]
)


style.configure(
    "Sidebar.TButton",
    background=COLOR_PANEL,
    foreground=COLOR_TEXT_SECONDARY,
    borderwidth=0,
    padding=(15, 10),
    anchor="w",
    font=(
        "Segoe UI",
        10
    )
)


style.map(
    "Sidebar.TButton",
    background=[
        (
            "active",
            COLOR_CARD_2
        )
    ],
    foreground=[
        (
            "active",
            COLOR_TEXT
        )
    ]
)


style.configure(
    "Scope.Horizontal.TProgressbar",
    troughcolor="#252525",
    background=COLOR_PRIMARY,
    bordercolor="#252525",
    lightcolor=COLOR_PRIMARY,
    darkcolor=COLOR_PRIMARY
)


menu_bar = tk.Menu(
    ventana,
    bg="#111111",
    fg=COLOR_TEXT,
    tearoff=0
)

ventana.config(
    menu=menu_bar
)


menu_archivo = tk.Menu(
    menu_bar,
    tearoff=0
)

menu_archivo.add_command(
    label="Escanear equipo",
    command=iniciar_escaneo
)

menu_archivo.add_separator()

menu_archivo.add_command(
    label="Salir",
    command=ventana.destroy
)

menu_bar.add_cascade(
    label="Archivo",
    menu=menu_archivo
)


menu_escanear = tk.Menu(
    menu_bar,
    tearoff=0
)

menu_escanear.add_command(
    label="Nuevo escaneo",
    command=iniciar_escaneo
)

menu_bar.add_cascade(
    label="Escanear",
    menu=menu_escanear
)


menu_herramientas = tk.Menu(
    menu_bar,
    tearoff=0
)

menu_herramientas.add_command(
    label="Abrir PWA",
    command=abrir_pwa
)

menu_bar.add_cascade(
    label="Herramientas",
    menu=menu_herramientas
)


menu_ayuda = tk.Menu(
    menu_bar,
    tearoff=0
)

menu_ayuda.add_command(
    label="Acerca de",
    command=acerca_de
)

menu_bar.add_cascade(
    label="Ayuda",
    menu=menu_ayuda
)


toolbar = tk.Frame(
    ventana,
    bg=COLOR_PANEL,
    height=70
)

toolbar.pack(
    fill="x"
)


logo_container = tk.Frame(
    toolbar,
    bg=COLOR_PANEL
)

logo_container.pack(
    side="left",
    padx=20
)


logo_text = tk.Label(
    logo_container,
    text="SCOPE",
    bg=COLOR_PANEL,
    fg=COLOR_TEXT,
    font=(
        "Segoe UI",
        22,
        "bold"
    )
)

logo_text.pack(
    side="left"
)


version_text = tk.Label(
    logo_container,
    text="  Hardware Scanner",
    bg=COLOR_PANEL,
    fg=COLOR_PRIMARY_LIGHT,
    font=(
        "Segoe UI",
        10
    )
)

version_text.pack(
    side="left",
    pady=(8, 0)
)


boton_escanear = ttk.Button(
    toolbar,
    text="Escanear",
    style="Scope.TButton",
    command=iniciar_escaneo
)

boton_escanear.pack(
    side="left",
    padx=(30, 5),
    pady=14
)


boton_guardar = ttk.Button(
    toolbar,
    text="Guardar",
    style="Scope.TButton",
    command=exportar_resultados
)

boton_guardar.pack(
    side="left",
    padx=5,
    pady=14
)


boton_pwa = ttk.Button(
    toolbar,
    text="Abrir PWA",
    style="Scope.TButton",
    command=abrir_pwa
)

boton_pwa.pack(
    side="left",
    padx=5,
    pady=14
)


boton_info = ttk.Button(
    toolbar,
    text="Acerca de",
    style="Scope.TButton",
    command=acerca_de
)

boton_info.pack(
    side="left",
    padx=5,
    pady=14
)


contenedor = tk.Frame(
    ventana,
    bg=COLOR_BG
)

contenedor.pack(
    fill="both",
    expand=True
)


sidebar = tk.Frame(
    contenedor,
    bg=COLOR_PANEL,
    width=220
)

sidebar.pack(
    side="left",
    fill="y"
)

sidebar.pack_propagate(
    False
)


sidebar_title = tk.Label(
    sidebar,
    text="COMPONENTES",
    bg=COLOR_PANEL,
    fg=COLOR_TEXT_SECONDARY,
    font=(
        "Segoe UI",
        9,
        "bold"
    )
)

sidebar_title.pack(
    anchor="w",
    padx=20,
    pady=(25, 10)
)


opciones = [
    (
        "Resumen",
        "Resumen del Equipo"
    ),
    (
        "Sistema",
        "Sistema"
    ),
    (
        "Procesador",
        "Procesador"
    ),
    (
        "Memoria RAM",
        "Memoria RAM"
    ),
    (
        "Tarjeta gráfica",
        "Tarjeta Gráfica"
    ),
    (
        "Almacenamiento",
        "Almacenamiento"
    ),
    (
        "Temperaturas",
        "Temperaturas"
    )
]


for texto, nombre in opciones:

    boton = ttk.Button(
        sidebar,
        text=texto,
        style="Sidebar.TButton",
        command=lambda n=nombre: mostrar_seccion(n)
    )

    boton.pack(
        fill="x",
        padx=8,
        pady=2
    )


separador = tk.Frame(
    sidebar,
    bg="#262626",
    height=1
)

separador.pack(
    fill="x",
    padx=15,
    pady=20
)


reco_title = tk.Label(
    sidebar,
    text="ANÁLISIS",
    bg=COLOR_PANEL,
    fg=COLOR_TEXT_SECONDARY,
    font=(
        "Segoe UI",
        9,
        "bold"
    )
)

reco_title.pack(
    anchor="w",
    padx=20,
    pady=(0, 10)
)


analisis_opciones = [
    (
        "Presupuesto",
        "Presupuesto"
    ),
    (
        "Recomendaciones",
        "Recomendaciones"
    ),
    (
        "Exportar reporte",
        "Exportar"
    ),
    (
        "Abrir PWA",
        "PWA"
    )
]


for texto, nombre in analisis_opciones:

    if nombre == "PWA":

        command = abrir_pwa

    else:

        command = lambda n=nombre: mostrar_seccion(n)

    boton = ttk.Button(
        sidebar,
        text=texto,
        style="Sidebar.TButton",
        command=command
    )

    boton.pack(
        fill="x",
        padx=8,
        pady=2
    )


central = tk.Frame(
    contenedor,
    bg=COLOR_BG
)

central.pack(
    side="left",
    fill="both",
    expand=True,
    padx=25,
    pady=20
)


titulo_central = tk.Label(
    central,
    text="Resumen del Equipo",
    bg=COLOR_BG,
    fg=COLOR_TEXT,
    font=(
        "Segoe UI",
        24,
        "bold"
    )
)

titulo_central.pack(
    anchor="w"
)


subtitulo_central = tk.Label(
    central,
    text="Información general detectada por SCOPE",
    bg=COLOR_BG,
    fg=COLOR_TEXT_SECONDARY,
    font=(
        "Segoe UI",
        10
    )
)

subtitulo_central.pack(
    anchor="w",
    pady=(3, 20)
)


cards_container = tk.Frame(
    central,
    bg=COLOR_BG
)

cards_container.pack(
    fill="both",
    expand=True
)


for columna in range(2):

    cards_container.grid_columnconfigure(
        columna,
        weight=1
    )


def crear_card(
    parent,
    fila,
    columna,
    titulo
):

    card = tk.Frame(
        parent,
        bg=COLOR_CARD,
        highlightbackground="#242424",
        highlightthickness=1
    )

    card.grid(
        row=fila,
        column=columna,
        sticky="nsew",
        padx=8,
        pady=8
    )

    parent.grid_rowconfigure(
        fila,
        weight=1
    )

    title_label = tk.Label(
        card,
        text=titulo,
        bg=COLOR_CARD,
        fg=COLOR_TEXT_SECONDARY,
        font=(
            "Segoe UI",
            10
        )
    )

    title_label.pack(
        anchor="w",
        padx=18,
        pady=(18, 0)
    )

    value_label = tk.Label(
        card,
        text="Sin analizar",
        bg=COLOR_CARD,
        fg=COLOR_TEXT,
        font=(
            "Segoe UI",
            15,
            "bold"
        ),
        wraplength=350,
        justify="left"
    )

    value_label.pack(
        anchor="w",
        padx=18,
        pady=(8, 18)
    )

    return value_label


cpu_valor = crear_card(
    cards_container,
    0,
    0,
    "Procesador"
)


ram_valor = crear_card(
    cards_container,
    0,
    1,
    "Memoria RAM"
)


gpu_valor = crear_card(
    cards_container,
    1,
    0,
    "Tarjeta gráfica"
)


disco_valor = crear_card(
    cards_container,
    1,
    1,
    "Almacenamiento"
)


temp_valor = crear_card(
    cards_container,
    2,
    0,
    "Temperaturas"
)


health_card = tk.Frame(
    cards_container,
    bg=COLOR_CARD,
    highlightbackground=COLOR_PRIMARY,
    highlightthickness=1
)

health_card.grid(
    row=2,
    column=1,
    sticky="nsew",
    padx=8,
    pady=8
)


health_title = tk.Label(
    health_card,
    text="Salud del Equipo",
    bg=COLOR_CARD,
    fg=COLOR_TEXT_SECONDARY,
    font=(
        "Segoe UI",
        10
    )
)

health_title.pack(
    anchor="w",
    padx=18,
    pady=(15, 0)
)


salud_numero = tk.Label(
    health_card,
    text="--%",
    bg=COLOR_CARD,
    fg=COLOR_TEXT,
    font=(
        "Segoe UI",
        28,
        "bold"
    )
)

salud_numero.pack(
    anchor="w",
    padx=18,
    pady=(4, 0)
)


salud_estado = tk.Label(
    health_card,
    text="Esperando escaneo",
    bg=COLOR_CARD,
    fg=COLOR_TEXT_SECONDARY,
    font=(
        "Segoe UI",
        10
    )
)

salud_estado.pack(
    anchor="w",
    padx=18
)


barra_salud = ttk.Progressbar(
    health_card,
    orient="horizontal",
    mode="determinate",
    style="Scope.Horizontal.TProgressbar"
)

barra_salud.pack(
    fill="x",
    padx=18,
    pady=15
)


progress_container = tk.Frame(
    central,
    bg=COLOR_BG
)

progress_container.pack(
    fill="x",
    pady=(15, 0)
)


progreso = ttk.Progressbar(
    progress_container,
    orient="horizontal",
    mode="determinate",
    style="Scope.Horizontal.TProgressbar"
)

progreso.pack(
    fill="x"
)


status_bar = tk.Frame(
    ventana,
    bg="#0A0A0A",
    height=35
)

status_bar.pack(
    fill="x",
    side="bottom"
)


estado_label = tk.Label(
    status_bar,
    text="Listo. Presiona Escanear para comenzar.",
    bg="#0A0A0A",
    fg=COLOR_TEXT_SECONDARY,
    font=(
        "Segoe UI",
        9
    )
)

estado_label.pack(
    side="left",
    padx=15,
    pady=8
)


version_status = tk.Label(
    status_bar,
    text=f"{APP_NAME} {APP_VERSION}",
    bg="#0A0A0A",
    fg=COLOR_TEXT_SECONDARY,
    font=(
        "Segoe UI",
        9
    )
)

version_status.pack(
    side="right",
    padx=15
)


ventana.mainloop()