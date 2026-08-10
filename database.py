import os

from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()


MONGO_URI = os.getenv("MONGO_URI")

DATABASE_NAME = "scope_db"


def obtener_cliente():

    if not MONGO_URI:
        raise RuntimeError(
            "No se encontró MONGO_URI en las variables de entorno."
        )

    return MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000
    )


def obtener_db():

    cliente = obtener_cliente()

    return cliente[DATABASE_NAME]


def probar_conexion():

    try:

        cliente = obtener_cliente()

        cliente.admin.command("ping")

        print(
            "Conexion con MongoDB realizada correctamente."
        )

        return True

    except Exception as e:

        print(
            f"Error de MongoDB: {e}"
        )

        return False

def buscar_componentes(tipo, presupuesto):

    try:

        db = obtener_db()

        consulta = {
            "tipo": tipo,
            "precio_mxn": {
                "$lte": presupuesto
            },
            "activo": True
        }

        return list(
            db.componentes.find(
                consulta,
                {
                    "_id": 0
                }
            ).sort(
                "nivel_rendimiento",
                -1
            )
        )

    except Exception as e:

        print(
            f"MongoDB no disponible: {e}"
        )

        return []

def buscar_equipos(
    presupuesto,
    nivel_minimo=0
):

    try:

        db = obtener_db()

        consulta = {
            "precio_mxn": {
                "$lte": presupuesto
            },
            "nivel_rendimiento": {
                "$gte": nivel_minimo
            },
            "activo": True
        }

        return list(
            db.equipos.find(
                consulta,
                {
                    "_id": 0
                }
            ).sort(
                "nivel_rendimiento",
                -1
            )
        )

    except Exception as e:

        print(
            f"MongoDB no disponible: {e}"
        )

        return []

def obtener_componentes():

    db = obtener_db()

    return list(
        db.componentes.find(
            {
                "activo": True
            },
            {
                "_id": 0
            }
        )
    )


def obtener_equipos():

    db = obtener_db()

    return list(
        db.equipos.find(
            {
                "activo": True
            },
            {
                "_id": 0
            }
        )
    )





def buscar_componentes(
    tipo,
    presupuesto
):

    db = obtener_db()

    consulta = {
        "tipo": tipo,
        "precio_mxn": {
            "$lte": presupuesto
        },
        "activo": True
    }

    return list(
        db.componentes.find(
            consulta,
            {
                "_id": 0
            }
        ).sort(
            "nivel_rendimiento",
            -1
        )
    )


def buscar_equipos(
    presupuesto,
    nivel_minimo=0
):

    db = obtener_db()

    consulta = {
        "precio_mxn": {
            "$lte": presupuesto
        },
        "nivel_rendimiento": {
            "$gte": nivel_minimo
        },
        "activo": True
    }

    return list(
        db.equipos.find(
            consulta,
            {
                "_id": 0
            }
        ).sort(
            "nivel_rendimiento",
            -1
        )
    )


def buscar_componentes_compatibles(
    tipo,
    presupuesto,
    compatibilidad=None
):

    try:

        db = obtener_db()

        consulta = {
            "tipo": tipo,
            "precio_mxn": {
                "$lte": presupuesto
            },
            "activo": True
        }


        compatibilidad = (
            compatibilidad
            or {}
        )


        if tipo == "RAM":

            tecnologia = compatibilidad.get(
                "tipo_ram"
            )

            formato = compatibilidad.get(
                "formato_ram"
            )

            if (
                tecnologia
                and tecnologia != "Desconocido"
            ):

                consulta[
                    "compatibilidad.tecnologia"
                ] = tecnologia


            if (
                formato
                and formato != "Desconocido"
            ):

                consulta[
                    "compatibilidad.formato"
                ] = formato


        elif tipo == "CPU":

            socket = compatibilidad.get(
                "socket_cpu"
            )

            if (
                socket
                and socket != "Desconocido"
            ):

                consulta[
                    "compatibilidad.socket"
                ] = socket


        elif tipo == "SSD":

            interfaces = compatibilidad.get(
                "interfaces_almacenamiento",
                []
            )

            if interfaces:

                consulta[
                    "compatibilidad.interfaz"
                ] = {
                    "$in": interfaces
                }


        productos = list(
            db.componentes.find(
                consulta,
                {
                    "_id": 0
                }
            ).sort(
                "nivel_rendimiento",
                -1
            )
        )


        return productos

    except Exception as e:

        print(
            "Error consultando compatibilidad "
            f"en MongoDB: {e}"
        )

        return []


if __name__ == "__main__":

    probar_conexion()