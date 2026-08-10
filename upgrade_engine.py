import json
import os
import sys
from dataclasses import dataclass


@dataclass
class Recommendation:
    component: str
    suggestion: str
    impact: str
    cost: int = 0
    priority_score: float = 0.0
    reason: str = ""

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
    with open("hardware.json", "r", encoding="utf-8") as f:
        return json.load(f)


def parse_user_pc(data):
    cpu = data.get("CPU", {}).get("Procesador", "Desconocido")

    ram = data.get("RAM", {}).get("RAM_Total_GB", 0)
    ram_usage = data.get("RAM", {}).get("Uso_RAM_Porcentaje", 0)

    gpu_list = data.get("GPU", [])

    gpu_name = "No detectada"
    gpu_vram = 0

    if gpu_list:
        gpu_name = gpu_list[0].get("Nombre", "Desconocida")

        try:
            gpu_vram = float(gpu_list[0].get("VRAM_MB", 0))
        except:
            gpu_vram = 0

    discos = data.get("Discos", [])

    disco_lleno = False

    for disco in discos:
        if disco.get("Uso_Porcentaje", 0) >= 85:
            disco_lleno = True

    temperaturas = data.get("Temperaturas", {})

    cpu_temp = temperaturas.get("CPU_C", "No disponible")
    gpu_temp = temperaturas.get("GPU_C", "No disponible")

    return {
        "cpu": cpu,
        "ram": ram,
        "ram_usage": ram_usage,
        "gpu_name": gpu_name,
        "gpu_vram": gpu_vram,
        "disco_lleno": disco_lleno,
        "cpu_temp": cpu_temp,
        "gpu_temp": gpu_temp
    }


def cpu_score(cpu):
    cpu = cpu.lower()

    if "athlon" in cpu or "celeron" in cpu or "pentium" in cpu:
        return 35

    if "i3" in cpu or "ryzen 3" in cpu:
        return 55

    if "i5" in cpu or "ryzen 5" in cpu:
        return 75

    if "i7" in cpu or "ryzen 7" in cpu:
        return 88

    if "i9" in cpu or "ryzen 9" in cpu:
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


def gpu_score(gpu_name, gpu_vram):
    nombre = gpu_name.lower()

    if "intel" in nombre or "vega" in nombre or "uhd" in nombre:
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
    cpu = cpu_score(pc["cpu"])
    ram = ram_score(pc["ram"])
    gpu = gpu_score(pc["gpu_name"], pc["gpu_vram"])

    score = (
        cpu * 0.40 +
        ram * 0.30 +
        gpu * 0.30
    )

    if pc["ram_usage"] >= 90:
        score -= 8

    if pc["disco_lleno"]:
        score -= 6

    try:
        if float(pc["cpu_temp"]) >= 85:
            score -= 10
    except:
        pass

    return max(0, min(100, round(score)))


def classify(pc):
    score = health_score(pc)

    if score < 45:
        return {
            "level": "bajo",
            "health": score,
            "use": "Uso básico y tareas ligeras",
            "gaming": "Limitado para videojuegos modernos",
            "recommendation": "Se recomienda priorizar actualizaciones de hardware"
        }

    if score < 75:
        return {
            "level": "medio",
            "health": score,
            "use": "Uso general y multitarea",
            "gaming": "Adecuado para gaming ligero o medio",
            "recommendation": "El equipo puede mejorar con actualizaciones específicas"
        }

    return {
        "level": "alto",
        "health": score,
        "use": "Uso avanzado y multitarea",
        "gaming": "Buen rendimiento general para gaming",
        "recommendation": "El equipo tiene un buen equilibrio de hardware"
    }


def recommendations(pc, budget):
    recs = []

    # RAM
    if pc["ram"] < 8:
        recs.append(
            Recommendation(
                component="RAM",
                suggestion="Actualizar a mínimo 16 GB de RAM",
                impact="Mejorará considerablemente la multitarea y estabilidad.",
                cost=1200,
                priority_score=10,
                reason=f"El equipo tiene aproximadamente {pc['ram']} GB de RAM."
            )
        )

    elif pc["ram"] < 16:
        recs.append(
            Recommendation(
                component="RAM",
                suggestion="Ampliar la memoria RAM a 16 GB",
                impact="Mejor rendimiento en multitarea, navegación y videojuegos.",
                cost=900,
                priority_score=9,
                reason="16 GB es un punto recomendado para uso moderno."
            )
        )

    elif pc["ram_usage"] >= 85:
        recs.append(
            Recommendation(
                component="RAM",
                suggestion="Considerar ampliar la memoria RAM",
                impact="Reducirá saturación cuando se ejecuten varias aplicaciones.",
                cost=1500,
                priority_score=8,
                reason=f"Actualmente se está utilizando aproximadamente {pc['ram_usage']}% de la RAM."
            )
        )

    # GPU
    gpu_s = gpu_score(pc["gpu_name"], pc["gpu_vram"])

    if gpu_s <= 45:
        recs.append(
            Recommendation(
                component="GPU",
                suggestion="Considerar una tarjeta gráfica dedicada",
                impact="Mayor rendimiento en videojuegos, edición y aplicaciones 3D.",
                cost=4500,
                priority_score=8,
                reason=f"GPU detectada: {pc['gpu_name']}."
            )
        )

    elif gpu_s <= 60:
        recs.append(
            Recommendation(
                component="GPU",
                suggestion="Actualizar la GPU para gaming moderno",
                impact="Permitirá usar configuraciones gráficas más altas.",
                cost=6500,
                priority_score=7,
                reason="La capacidad gráfica actual puede limitar videojuegos recientes."
            )
        )

    # CPU
    cpu_s = cpu_score(pc["cpu"])

    if cpu_s < 50:
        recs.append(
            Recommendation(
                component="CPU",
                suggestion="Considerar una plataforma con procesador más moderno",
                impact="Mejorará rendimiento general y reducirá cuellos de botella.",
                cost=6000,
                priority_score=9,
                reason=f"Procesador detectado: {pc['cpu']}."
            )
        )

    # Almacenamiento
    if pc["disco_lleno"]:
        recs.append(
            Recommendation(
                component="Almacenamiento",
                suggestion="Liberar espacio o ampliar almacenamiento",
                impact="Ayuda a mantener el rendimiento y evita falta de espacio.",
                cost=1000,
                priority_score=8,
                reason="Se detectó una unidad con más del 85% de utilización."
            )
        )

    # Temperatura CPU
    try:
        cpu_temp = float(pc["cpu_temp"])

        if cpu_temp >= 85:
            recs.append(
                Recommendation(
                    component="Temperatura",
                    suggestion="Revisar sistema de refrigeración",
                    impact="Puede evitar thermal throttling y proteger los componentes.",
                    cost=500,
                    priority_score=10,
                    reason=f"Temperatura de CPU detectada: {cpu_temp} °C."
                )
            )

        elif cpu_temp >= 75:
            recs.append(
                Recommendation(
                    component="Temperatura",
                    suggestion="Realizar mantenimiento preventivo",
                    impact="Limpieza y cambio de pasta térmica pueden mejorar temperaturas.",
                    cost=350,
                    priority_score=7,
                    reason=f"Temperatura de CPU detectada: {cpu_temp} °C."
                )
            )

    except:
        pass

    # Optimización gratuita
    recs.append(
        Recommendation(
            component="Optimización",
            suggestion="Revisar programas que inician con Windows",
            impact="Puede reducir consumo de RAM y mejorar el arranque.",
            cost=0,
            priority_score=5,
            reason="Optimización de software sin inversión adicional."
        )
    )

    # Filtrar por presupuesto
    posibles = [
        r for r in recs
        if r.cost <= budget
    ]

    # Si ninguna mejora física entra en presupuesto
    if not posibles:
        posibles.append(
            Recommendation(
                component="Presupuesto",
                suggestion="Ahorrar para una actualización de mayor impacto",
                impact="El presupuesto actual no permite una actualización significativa.",
                cost=0,
                priority_score=6,
                reason="Las mejoras recomendadas superan el presupuesto disponible."
            )
        )

    posibles.sort(
        key=lambda x: x.priority_score,
        reverse=True
    )

    return posibles


def export(pc, profile, recs, budget):
    data = {
        "system_profile": profile,
        "budget": budget,
        "hardware_summary": {
            "cpu": pc["cpu"],
            "ram_gb": pc["ram"],
            "ram_usage": pc["ram_usage"],
            "gpu": pc["gpu_name"],
            "gpu_vram_mb": pc["gpu_vram"],
            "cpu_temperature": pc["cpu_temp"],
            "gpu_temperature": pc["gpu_temp"]
        },
        "recommendations": [
            {
                "component": r.component,
                "suggestion": r.suggestion,
                "impact": r.impact,
                "cost": r.cost,
                "priority": r.priority_score,
                "reason": r.reason
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


def generar_recomendaciones(presupuesto, hardware=None):

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
    import sys

    budget = (
        int(sys.argv[1])
        if len(sys.argv) > 1
        else 3000
    )

    generar_recomendaciones(budget)