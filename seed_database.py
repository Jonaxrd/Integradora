from database import obtener_db


db = obtener_db()


componentes = [

    {
        "nombre": "Kingston Fury Beast 16GB DDR4 3200MHz",
        "marca": "Kingston",
        "tipo": "RAM",
        "tecnologia": "DDR4",
        "capacidad_gb": 16,
        "frecuencia_mhz": 3200,
        "precio_mxn": 2537,
        "nivel_rendimiento": 70,

        "descripcion": (
            "Memoria DDR4 de 16 GB orientada a multitarea, "
            "gaming y uso general."
        ),

        "compatibilidad": {
            "tecnologia": "DDR4",
            "formato": "DIMM"
        },

        "imagen_url": (
            "https://http2.mlstatic.com/"
            "D_NQ_NP_2X_680890-MLA99850388159_112025-F.webp"
        ),

        "compra_url": (
            "https://www.mercadolibre.com.mx/"
            "memoria-ram-ddr4-16gb-3200mhz-kingston-fury-beast-"
            "1x16gb-negro-kf432c16bb16-para-pc-desktop/p/"
            "MLM41513563"
        ),

        "tienda": "Mercado Libre",
        "stock": True,
        "activo": True
    },


    {
        "nombre": "Kingston Fury Beast RGB 16GB DDR4 3200MHz",
        "marca": "Kingston",
        "tipo": "RAM",
        "tecnologia": "DDR4",
        "capacidad_gb": 16,
        "frecuencia_mhz": 3200,
        "precio_mxn": 2339,
        "nivel_rendimiento": 74,

        "descripcion": (
            "Memoria DDR4 de 16 GB con iluminación RGB "
            "orientada a equipos gaming."
        ),

        "compatibilidad": {
            "tecnologia": "DDR4",
            "formato": "DIMM"
        },

        "imagen_url": (
            "https://http2.mlstatic.com/"
            "D_NQ_NP_2X_699633-MLU73802925705_012024-F.webp"
        ),

        "compra_url": (
            "https://www.mercadolibre.com.mx/"
            "memoria-ram-kingston-fury-beast-rgb-ddr4-16gb-"
            "3200-mts/up/MLMU3045022597"
        ),

        "tienda": "Mercado Libre",
        "stock": True,
        "activo": True
    },


    {
        "nombre": "Kingston NV3 1TB NVMe",
        "marca": "Kingston",
        "tipo": "SSD",
        "interfaz": "NVMe",
        "capacidad_gb": 1000,
        "precio_mxn": 3799,
        "nivel_rendimiento": 78,

        "descripcion": (
            "SSD NVMe PCIe 4.0 de 1 TB orientado a mejorar "
            "tiempos de arranque, carga y transferencia."
        ),

        "compatibilidad": {
            "interfaz": "NVMe",
            "formato": "M.2"
        },

        "imagen_url": (
            "https://http2.mlstatic.com/"
            "D_NQ_NP_2X_682731-MLA99450928002_112025-F.webp"
        ),

        "compra_url": (
            "https://www.mercadolibre.com.mx/"
            "ssd-kingston-nv3-1tb-nvme-40-snv3s/"
            "up/MLMU3900924564"
        ),

        "tienda": "Mercado Libre",
        "stock": True,
        "activo": True
    },


    {
        "nombre": "Crucial BX500 1TB SATA",
        "marca": "Crucial",
        "tipo": "SSD",
        "interfaz": "SATA",
        "capacidad_gb": 1000,
        "precio_mxn": 3777,
        "nivel_rendimiento": 62,

        "descripcion": (
            "SSD SATA de 1 TB recomendado para equipos "
            "que no cuentan con soporte NVMe."
        ),

        "compatibilidad": {
            "interfaz": "SATA",
            "formato": "2.5"
        },

        "imagen_url": "",

        "compra_url": (
            "https://listado.mercadolibre.com.mx/"
            "ssd-crucial-bx500-1tb"
        ),

        "tienda": "Mercado Libre",
        "stock": True,
        "activo": True
    },


    {
        "nombre": "ASUS Dual GeForce RTX 4060 8GB",
        "marca": "ASUS / NVIDIA",
        "tipo": "GPU",
        "vram_gb": 8,
        "precio_mxn": 9199,
        "nivel_rendimiento": 86,

        "descripcion": (
            "Tarjeta gráfica RTX 4060 de 8 GB orientada "
            "a gaming en 1080p y aplicaciones gráficas."
        ),

        "compatibilidad": {
            "interfaz": "PCIe"
        },

        "imagen_url": "",

        "compra_url": (
            "https://articulo.mercadolibre.com.mx/"
            "MLM-1917039893-tarjeta-de-video-nvidia-asus-"
            "dual-geforce-rtx-4060-8gb-_JM"
        ),

        "tienda": "Mercado Libre",
        "stock": True,
        "activo": True
    },


    {
        "nombre": "XFX Radeon RX 7600 8GB",
        "marca": "XFX / AMD",
        "tipo": "GPU",
        "vram_gb": 8,
        "precio_mxn": 7808,
        "nivel_rendimiento": 82,

        "descripcion": (
            "Tarjeta gráfica Radeon RX 7600 de 8 GB "
            "orientada a gaming en resolución 1080p."
        ),

        "compatibilidad": {
            "interfaz": "PCIe"
        },

        "imagen_url": "",

        "compra_url": (
            "https://listado.mercadolibre.com.mx/"
            "radeon-rx-7600"
        ),

        "tienda": "Mercado Libre",
        "stock": True,
        "activo": True
    },


    {
        "nombre": "AMD Ryzen 5 5600GT",
        "marca": "AMD",
        "tipo": "CPU",
        "socket": "AM4",
        "nucleos": 6,
        "hilos": 12,
        "precio_mxn": 3169,
        "nivel_rendimiento": 73,

        "descripcion": (
            "Procesador de 6 núcleos y 12 hilos para "
            "actualización de plataformas AM4."
        ),

        "compatibilidad": {
            "socket": "AM4"
        },

        "imagen_url": "",

        "compra_url": (
            "https://listado.mercadolibre.com.mx/"
            "ryzen-5600g"
        ),

        "tienda": "Mercado Libre",
        "stock": True,
        "activo": True
    },


    {
        "nombre": "AMD Ryzen 5 7600X",
        "marca": "AMD",
        "tipo": "CPU",
        "socket": "AM5",
        "nucleos": 6,
        "hilos": 12,
        "precio_mxn": 3714,
        "nivel_rendimiento": 89,

        "descripcion": (
            "Procesador Ryzen 5 de generación AM5, "
            "orientado a plataformas modernas."
        ),

        "compatibilidad": {
            "socket": "AM5"
        },

        "imagen_url": "",

        "compra_url": (
            "https://listado.mercadolibre.com.mx/"
            "ryzen-5-7600"
        ),

        "tienda": "Mercado Libre",
        "stock": True,
        "activo": True
    }

]


equipos = [

    {
        "nombre": (
            "MSI Thin 15 Core i5 / RTX 4060 / "
            "16GB / 512GB SSD"
        ),

        "tipo": "Laptop",

        "cpu": "Intel Core i5",

        "ram_gb": 16,

        "almacenamiento_gb": 512,

        "gpu": "NVIDIA GeForce RTX 4060",

        "precio_mxn": 16999,

        "nivel_rendimiento": 88,

        "salto_generacional": True,

        "mejora_minima_recomendada": 25,

        "uso_recomendado": [
            "Gaming",
            "Programacion",
            "Edicion",
            "Multitarea"
        ],

        "descripcion": (
            "Laptop orientada a usuarios que necesitan un "
            "salto de rendimiento considerable frente a "
            "equipos con gráficos integrados."
        ),

        "imagen_url": "",

        "compra_url": (
            "https://listado.mercadolibre.com.mx/"
            "laptop-gamer-16gb"
        ),

        "tienda": "Mercado Libre",

        "stock": True,

        "activo": True
    },


    {
        "nombre": (
            "HP Victus Core i5 / RTX 4050 / "
            "16GB / 512GB SSD"
        ),

        "tipo": "Laptop",

        "cpu": "Intel Core i5",

        "ram_gb": 16,

        "almacenamiento_gb": 512,

        "gpu": "NVIDIA GeForce RTX 4050",

        "precio_mxn": 18499,

        "nivel_rendimiento": 84,

        "salto_generacional": True,

        "mejora_minima_recomendada": 20,

        "uso_recomendado": [
            "Gaming",
            "Programacion",
            "Edicion",
            "Multitarea"
        ],

        "descripcion": (
            "Equipo recomendado cuando actualizar los "
            "componentes de la computadora actual deja "
            "de ser económicamente conveniente."
        ),

        "imagen_url": "",

        "compra_url": (
            "https://listado.mercadolibre.com.mx/"
            "hp-victus-rtx-4060"
        ),

        "tienda": "Mercado Libre",

        "stock": True,

        "activo": True
    },


    {
        "nombre": (
            "PC Gaming Ryzen 5 7600 / "
            "RX 7600 / 16GB / 1TB"
        ),

        "tipo": "Desktop",

        "cpu": "AMD Ryzen 5 7600",

        "ram_gb": 16,

        "almacenamiento_gb": 1000,

        "gpu": "AMD Radeon RX 7600",

        "precio_mxn": 19999,

        "nivel_rendimiento": 90,

        "salto_generacional": True,

        "mejora_minima_recomendada": 30,

        "uso_recomendado": [
            "Gaming",
            "Programacion",
            "Edicion",
            "Streaming",
            "Multitarea"
        ],

        "descripcion": (
            "PC de escritorio con plataforma AM5 y "
            "gráficos dedicados para usuarios que buscan "
            "un salto generacional completo."
        ),

        "imagen_url": "",

        "compra_url": (
            "https://www.mercadolibre.com.mx/"
            "pc-gamer-xzgamc3b-ryzen-5-7600-16gb-1tb-"
            "rx7600-650w-wifi/up/MLMU3473817618"
        ),

        "tienda": "Mercado Libre",

        "stock": True,

        "activo": True
    }

]


db.componentes.delete_many({})
db.equipos.delete_many({})


resultado_componentes = (
    db.componentes.insert_many(
        componentes
    )
)


resultado_equipos = (
    db.equipos.insert_many(
        equipos
    )
)


print(
    "Base de datos inicializada correctamente."
)


print(
    f"Componentes insertados: "
    f"{len(resultado_componentes.inserted_ids)}"
)


print(
    f"Equipos insertados: "
    f"{len(resultado_equipos.inserted_ids)}"
)