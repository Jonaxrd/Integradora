import json
import os
import sys
from dataclasses import dataclass

from database import (
    buscar_componentes,
    buscar_componentes_compatibles,
    buscar_equipos
)


@dataclass
class Recommendation:
    component: str
    suggestion: str
    impact: str
    cost: int = 0
    priority_score: float = 0.0
    reason: str = ""
    product: dict | None = None


def obtener_directorio_app():

    if getattr(
        sys,
        "frozen",
        False
    ):

        return os.path.dirname(
            sys.executable
        )

    return os.path.dirname(
        os.path.abspath(__file__)
    )


def load_hardware():

    ruta = os.path.join(
        obtener_directorio_app(),
        "hardware.json"
    )

    with open(
        ruta,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def parse_user_pc(data):

    cpu = data.get(
        "CPU",
        {}
    ).get(
        "Procesador",
        "Desconocido"
    )

    ram = data.get(
        "RAM",
        {}
    ).get(
        "RAM_Total_GB",
        0
    )

    ram_usage = data.get(
        "RAM",
        {}
    ).get(
        "Uso_RAM_Porcentaje",
        0
    )

    gpu_list = data.get(
        "GPU",
        []
    )

    gpu_name = "No detectada"
    gpu_vram = 0

    if gpu_list:

        gpu_name = gpu_list[0].get(
            "Nombre",
            "Desconocida"
        )

        try:

            gpu_vram = float(
                gpu_list[0].get(
                    "VRAM_MB",
                    0
                )
            )

        except Exception:

            gpu_vram = 0


    discos = data.get(
        "Discos",
        []
    )

    disco_lleno = False

    for disco in discos:

        if disco.get(
            "Uso_Porcentaje",
            0
        ) >= 85:

            disco_lleno = True
            break


    temperaturas = data.get(
        "Temperaturas",
        {}
    )

    cpu_temp = temperaturas.get(
        "CPU_C",
        "No disponible"
    )

    gpu_temp = temperaturas.get(
        "GPU_C",
        "No disponible"
    )

    compatibilidad = data.get(
    "Compatibilidad",
    {}
    )


    return {
        "cpu": cpu,
        "ram": ram,
        "ram_usage": ram_usage,
        "gpu_name": gpu_name,
        "gpu_vram": gpu_vram,
        "disco_lleno": disco_lleno,
        "cpu_temp": cpu_temp,
        "gpu_temp": gpu_temp,
        "tipo_equipo": compatibilidad.get(
            "tipo_equipo",
            "Desconocido"
        ),

        "tipo_ram": compatibilidad.get(
            "tipo_ram",
            "Desconocido"
        ),

        "formato_ram": compatibilidad.get(
            "formato_ram",
            "Desconocido"
        ),

        "socket_cpu": compatibilidad.get(
            "socket_cpu",
            "Desconocido"
        ),

    "interfaces_almacenamiento": compatibilidad.get(
        "interfaces_almacenamiento",
    []
)
}


def cpu_score(cpu):

    cpu = cpu.lower()

    if (
        "athlon" in cpu
        or "celeron" in cpu
        or "pentium" in cpu
    ):
        return 35

    if (
        "i3" in cpu
        or "ryzen 3" in cpu
    ):
        return 55

    if (
        "i5" in cpu
        or "ryzen 5" in cpu
    ):
        return 75

    if (
        "i7" in cpu
        or "ryzen 7" in cpu
    ):
        return 88

    if (
        "i9" in cpu
        or "ryzen 9" in cpu
    ):
        return 96

    return 50


def ram_score(ram):

    if ram < 8:
        return 30

    if ram < 16:
        return 55

    if ram < 32:
        return 80

    return 95


def gpu_score(
    gpu_name,
    gpu_vram
):

    nombre = gpu_name.lower()

    if (
        "intel" in nombre
        or "vega" in nombre
        or "uhd" in nombre
    ):
        return 40

    if gpu_vram >= 12000:
        return 95

    if gpu_vram >= 8000:
        return 85

    if gpu_vram >= 6000:
        return 72

    if gpu_vram >= 4000:
        return 60

    if gpu_vram > 0:
        return 45

    return 35


def health_score(pc):

    cpu = cpu_score(
        pc["cpu"]
    )

    ram = ram_score(
        pc["ram"]
    )

    gpu = gpu_score(
        pc["gpu_name"],
        pc["gpu_vram"]
    )

    score = (
        cpu * 0.40
        + ram * 0.30
        + gpu * 0.30
    )

    if pc["ram_usage"] >= 90:
        score -= 8

    if pc["disco_lleno"]:
        score -= 6

    try:

        if float(
            pc["cpu_temp"]
        ) >= 85:

            score -= 10

    except Exception:
        pass

    return max(
        0,
        min(
            100,
            round(score)
        )
    )


def classify(pc):

    score = health_score(
        pc
    )

    if score < 45:

        return {
            "level": "bajo",
            "health": score,
            "use": "Uso básico y tareas ligeras",
            "gaming": "Limitado para videojuegos modernos",
            "recommendation": (
                "Se recomienda priorizar "
                "actualizaciones de hardware"
            )
        }

    if score < 75:

        return {
            "level": "medio",
            "health": score,
            "use": "Uso general y multitarea",
            "gaming": (
                "Adecuado para gaming ligero o medio"
            ),
            "recommendation": (
                "El equipo puede mejorar "
                "con actualizaciones específicas"
            )
        }

    return {
        "level": "alto",
        "health": score,
        "use": "Uso avanzado y multitarea",
        "gaming": (
            "Buen rendimiento general para gaming"
        ),
        "recommendation": (
            "El equipo tiene un buen "
            "equilibrio de hardware"
        )
    }


def seleccionar_producto(
    tipo,
    presupuesto,
    pc
):

    compatibilidad = {
        "tipo_ram": pc.get(
            "tipo_ram"
        ),

        "formato_ram": pc.get(
            "formato_ram"
        ),

        "socket_cpu": pc.get(
            "socket_cpu"
        ),

        "interfaces_almacenamiento": pc.get(
            "interfaces_almacenamiento",
            []
        )
    }


    try:

        compatibles = (
            buscar_componentes_compatibles(
                tipo,
                presupuesto,
                compatibilidad
            )
        )


        if compatibles:

            producto = compatibles[0]

            producto[
                "compatibility_status"
            ] = "compatible"

            return producto


        productos = buscar_componentes(
            tipo,
            presupuesto
        )


        if productos:

            producto = productos[0]

            producto[
                "compatibility_status"
            ] = "verificar"

            return producto


        return None

    except Exception as e:

        print(
            f"Error buscando {tipo}: {e}"
        )

        return None

    try:

        productos = buscar_componentes(
            tipo,
            presupuesto
        )

        if not productos:
            return None

        return productos[0]

    except Exception as e:

        print(
            f"No fue posible consultar "
            f"MongoDB para {tipo}: {e}"
        )

        return None


def seleccionar_equipo(
    presupuesto,
    nivel_actual
):

    try:

        nivel_minimo = (
            nivel_actual + 20
        )

        equipos = buscar_equipos(
            presupuesto,
            nivel_minimo
        )

        if not equipos:
            return None

        return equipos[0]

    except Exception as e:

        print(
            "No fue posible consultar "
            f"equipos en MongoDB: {e}"
        )

        return None


def recommendations(
    pc,
    budget
):

    recs = []


    if pc["ram"] < 16:

        producto = seleccionar_producto(
            "RAM",
            budget,
            pc
        )

        recs.append(
            Recommendation(
                component="RAM",
                suggestion=(
                    "Ampliar memoria RAM "
                    "a mínimo 16 GB"
                ),
                impact=(
                    "Mejorará el rendimiento "
                    "en multitarea y aplicaciones modernas."
                ),
                cost=(
                    producto["precio_mxn"]
                    if producto
                    else 900
                ),
                priority_score=(
                    10
                    if pc["ram"] < 8
                    else 9
                ),
                reason=(
                    f"El equipo tiene aproximadamente "
                    f"{pc['ram']} GB de memoria RAM."
                ),
                product=producto
            )
        )

    elif pc["ram_usage"] >= 85:

        producto = seleccionar_producto(
            "RAM",
            budget,
            pc
        )

        recs.append(
            Recommendation(
                component="RAM",
                suggestion=(
                    "Considerar ampliar "
                    "la memoria RAM"
                ),
                impact=(
                    "Reducirá la saturación "
                    "cuando se ejecuten varias "
                    "aplicaciones al mismo tiempo."
                ),
                cost=(
                    producto["precio_mxn"]
                    if producto
                    else 1500
                ),
                priority_score=8,
                reason=(
                    "Actualmente se está utilizando "
                    f"aproximadamente "
                    f"{pc['ram_usage']}% de la RAM."
                ),
                product=producto
            )
        )


    gpu_s = gpu_score(
        pc["gpu_name"],
        pc["gpu_vram"]
    )

    if gpu_s <= 45:

        producto = seleccionar_producto(
            "GPU",
            budget,
            pc
        )

        recs.append(
            Recommendation(
                component="GPU",
                suggestion=(
                    "Considerar una tarjeta "
                    "gráfica dedicada"
                ),
                impact=(
                    "Mayor rendimiento en videojuegos, "
                    "edición y aplicaciones 3D."
                ),
                cost=(
                    producto["precio_mxn"]
                    if producto
                    else 4500
                ),
                priority_score=8,
                reason=(
                    f"GPU detectada: "
                    f"{pc['gpu_name']}."
                ),
                product=producto
            )
        )

    elif gpu_s <= 60:

        producto = seleccionar_producto(
            "GPU",
            budget,
            pc
        )

        recs.append(
            Recommendation(
                component="GPU",
                suggestion=(
                    "Actualizar la GPU "
                    "para gaming moderno"
                ),
                impact=(
                    "Permitirá utilizar "
                    "configuraciones gráficas más altas."
                ),
                cost=(
                    producto["precio_mxn"]
                    if producto
                    else 6500
                ),
                priority_score=7,
                reason=(
                    "La capacidad gráfica actual "
                    "puede limitar videojuegos recientes."
                ),
                product=producto
            )
        )


    cpu_s = cpu_score(
        pc["cpu"]
    )

    if (
    cpu_s < 50
    and pc["tipo_equipo"] != "Laptop"
    ):

        producto = seleccionar_producto(
            "CPU",
            budget,
            pc
        )

        recs.append(
            Recommendation(
                component="CPU",
                suggestion=(
                    "Considerar una plataforma "
                    "con procesador más moderno"
                ),
                impact=(
                    "Mejorará el rendimiento general "
                    "y reducirá cuellos de botella."
                ),
                cost=(
                    producto["precio_mxn"]
                    if producto
                    else 6000
                ),
                priority_score=9,
                reason=(
                    f"Procesador detectado: "
                    f"{pc['cpu']}."
                ),
                product=producto
            )
        )


    if pc["disco_lleno"]:

        producto = seleccionar_producto(
            "SSD",
            budget,
            pc
        )

        recs.append(
            Recommendation(
                component="Almacenamiento",
                suggestion=(
                    "Liberar espacio o "
                    "ampliar almacenamiento"
                ),
                impact=(
                    "Ayuda a mantener el rendimiento "
                    "y evita falta de espacio."
                ),
                cost=(
                    producto["precio_mxn"]
                    if producto
                    else 1000
                ),
                priority_score=8,
                reason=(
                    "Se detectó una unidad "
                    "con más del 85% de utilización."
                ),
                product=producto
            )
        )


    try:

        cpu_temp = float(
            pc["cpu_temp"]
        )

        if cpu_temp >= 85:

            recs.append(
                Recommendation(
                    component="Temperatura",
                    suggestion=(
                        "Revisar sistema "
                        "de refrigeración"
                    ),
                    impact=(
                        "Puede evitar thermal throttling "
                        "y proteger los componentes."
                    ),
                    cost=500,
                    priority_score=10,
                    reason=(
                        f"Temperatura de CPU detectada: "
                        f"{cpu_temp} °C."
                    )
                )
            )

        elif cpu_temp >= 75:

            recs.append(
                Recommendation(
                    component="Temperatura",
                    suggestion=(
                        "Realizar mantenimiento preventivo"
                    ),
                    impact=(
                        "Limpieza y cambio de pasta térmica "
                        "pueden mejorar temperaturas."
                    ),
                    cost=350,
                    priority_score=7,
                    reason=(
                        f"Temperatura de CPU detectada: "
                        f"{cpu_temp} °C."
                    )
                )
            )

    except Exception:
        pass


    recs.append(
        Recommendation(
            component="Optimización",
            suggestion=(
                "Revisar programas que "
                "inician con Windows"
            ),
            impact=(
                "Puede reducir consumo de RAM "
                "y mejorar el arranque."
            ),
            cost=0,
            priority_score=5,
            reason=(
                "Optimización de software "
                "sin inversión adicional."
            )
        )
    )


    perfil = classify(
        pc
    )

    if (
        perfil["level"] == "bajo"
        and budget >= 10000
    ):

        equipo = seleccionar_equipo(
            budget,
            perfil["health"]
        )

        if equipo:

            recs.append(
                Recommendation(
                    component="Equipo completo",
                    suggestion=(
                        "Considerar cambio de equipo "
                        "en lugar de continuar "
                        "actualizando la plataforma actual."
                    ),
                    impact=(
                        "Representa un salto generacional "
                        "significativo frente al "
                        "hardware actual."
                    ),
                    cost=equipo[
                        "precio_mxn"
                    ],
                    priority_score=10,
                    reason=(
                        "La plataforma actual presenta "
                        "limitaciones importantes y "
                        "el presupuesto permite considerar "
                        "un equipo más moderno."
                    ),
                    product=equipo
                )
            )


    posibles = [
        r
        for r in recs
        if r.cost <= budget
    ]


    if not posibles:

        posibles.append(
            Recommendation(
                component="Presupuesto",
                suggestion=(
                    "Ahorrar para una actualización "
                    "de mayor impacto"
                ),
                impact=(
                    "El presupuesto actual no permite "
                    "una actualización significativa."
                ),
                cost=0,
                priority_score=6,
                reason=(
                    "Las mejoras recomendadas "
                    "superan el presupuesto disponible."
                )
            )
        )


    posibles.sort(
        key=lambda x: x.priority_score,
        reverse=True
    )

    return posibles


def export(
    pc,
    profile,
    recs,
    budget
):

    data = {

        "system_profile": profile,

        "budget": budget,

        "hardware_summary": {

            "cpu": pc["cpu"],

            "ram_gb": pc["ram"],

            "ram_usage": pc[
                "ram_usage"
            ],

            "gpu": pc[
                "gpu_name"
            ],

            "gpu_vram_mb": pc[
                "gpu_vram"
            ],

            "cpu_temperature": pc[
                "cpu_temp"
            ],

            "gpu_temperature": pc[
                "gpu_temp"
            ]

        },

        "recommendations": [

            {
                "component": r.component,
                "suggestion": r.suggestion,
                "impact": r.impact,
                "cost": r.cost,
                "priority": r.priority_score,
                "reason": r.reason,
                "product": r.product
            }

            for r in recs
        ]
    }


    ruta_resultados = os.path.join(
        obtener_directorio_app(),
        "resultados.json"
    )


    with open(
        ruta_resultados,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )


    return data


def generar_recomendaciones(
    presupuesto,
    hardware=None
):

    if hardware is None:

        hardware = load_hardware()


    pc = parse_user_pc(
        hardware
    )


    profile = classify(
        pc
    )


    recs = recommendations(
        pc,
        presupuesto
    )


    return export(
        pc,
        profile,
        recs,
        presupuesto
    )


if __name__ == "__main__":

    budget = (
        int(sys.argv[1])
        if len(sys.argv) > 1
        else 3000
    )

    generar_recomendaciones(
        budget
    )