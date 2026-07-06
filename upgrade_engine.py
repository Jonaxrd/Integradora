import json
import sys
from dataclasses import dataclass


@dataclass
class Recommendation:
    component: str
    suggestion: str
    impact: str
    cost: int = 0
    priority_score: float = 0.0


def load_hardware():
    with open("hardware.json", "r", encoding="utf-8") as f:
        return json.load(f)


def parse_user_pc(data):
    cpu = data["CPU"]["Procesador"]
    ram = data["RAM"]["RAM_Total_GB"]

    gpu_list = data.get("GPU", [])
    gpu = len(gpu_list) > 0

    return {
        "cpu": cpu,
        "ram": ram,
        "gpu": gpu
    }


def cpu_score(cpu):
    cpu = cpu.lower()

    if "athlon" in cpu:
        return 4000
    if "i3" in cpu:
        return 7000
    if "ryzen 3" in cpu:
        return 8000
    if "ryzen 5" in cpu:
        return 12000
    if "ryzen 7" in cpu:
        return 16000

    return 6000


def classify(cpu_s, ram):
    if cpu_s < 6000:
        return {
            "level": "bajo",
            "use": "Uso básico / doméstico",
            "gaming": "No apto para gaming moderno",
            "recommendation": "Cambio de equipo a mediano plazo"
        }

    if cpu_s < 10000:
        return {
            "level": "medio",
            "use": "Uso general",
            "gaming": "Gaming ligero",
            "recommendation": "Equipo funcional"
        }

    return {
        "level": "alto",
        "use": "Uso avanzado",
        "gaming": "Gaming fluido",
        "recommendation": "Equipo sólido"
    }


def recommendations(pc, budget):

    recs = []
    s = cpu_score(pc["cpu"])
    profile = classify(s, pc["ram"])

    if budget <= 1500:
        recs.append(Recommendation(
            "Optimización",
            "Cerrar programas en segundo plano",
            "Mejora ligera sin costo",
            0,
            8
        ))

    elif budget <= 4000:
        recs.append(Recommendation(
            "SSD",
            "Instalar SSD",
            "Mejora enorme en velocidad",
            1200,
            10
        ))

    elif budget <= 8000:
        recs.append(Recommendation(
            "RAM",
            "Subir a 16GB",
            "Mejora multitarea",
            1500,
            9
        ))

    else:
        recs.append(Recommendation(
            "Sistema completo",
            "Cambiar de equipo",
            "Salto generacional",
            budget,
            10
        ))

    recs.sort(key=lambda x: x.priority_score, reverse=True)

    return recs, profile


def export(pc, profile, recs, budget):

    data = {
        "system_profile": profile,
        "budget": budget,
        "recommendations": [
            {
                "component": r.component,
                "suggestion": r.suggestion,
                "impact": r.impact,
                "cost": r.cost,
                "priority": r.priority_score
            }
            for r in recs
        ]
    }

    with open("resultados.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":

    pc = parse_user_pc(load_hardware())

    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 3000

    recs, profile = recommendations(pc, budget)

    export(pc, profile, recs, budget)