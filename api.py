import os

from flask import Flask, request, jsonify
from pymongo import MongoClient


app = Flask(__name__)


MONGO_URI = os.getenv(
    "MONGO_URI"
)

DATABASE_NAME = "scope_db"


def obtener_db():

    if not MONGO_URI:

        raise RuntimeError(
            "MONGO_URI no está configurado."
        )

    cliente = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000
    )

    return cliente[
        DATABASE_NAME
    ]


@app.get("/")
def inicio():

    return jsonify({
        "status": "ok",
        "service": "SCOPE API"
    })


@app.get(
    "/api/componentes/todos"
)
def componentes_todos():

    try:

        db = obtener_db()

        componentes = list(
            db.componentes.find(
                {
                    "activo": True
                },
                {
                    "_id": 0
                }
            )
        )

        return jsonify(
            componentes
        )

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


@app.get(
    "/api/equipos/todos"
)
def equipos_todos():

    try:

        db = obtener_db()

        equipos = list(
            db.equipos.find(
                {
                    "activo": True
                },
                {
                    "_id": 0
                }
            )
        )

        return jsonify(
            equipos
        )

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


@app.get(
    "/api/componentes"
)
def componentes():

    try:

        tipo = request.args.get(
            "tipo",
            ""
        )

        presupuesto = request.args.get(
            "presupuesto",
            type=int
        )


        if (
            not tipo
            or presupuesto is None
        ):

            return jsonify({
                "error": (
                    "tipo y presupuesto "
                    "son requeridos"
                )
            }), 400


        db = obtener_db()


        consulta = {

            "tipo": tipo,

            "precio_mxn": {
                "$lte": presupuesto
            },

            "activo": True
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


        return jsonify(
            productos
        )

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


@app.get(
    "/api/equipos"
)
def equipos():

    try:

        presupuesto = request.args.get(
            "presupuesto",
            type=int
        )

        nivel_minimo = request.args.get(
            "nivel_minimo",
            default=0,
            type=int
        )


        if presupuesto is None:

            return jsonify({
                "error": (
                    "presupuesto es requerido"
                )
            }), 400


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


        resultados = list(
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


        return jsonify(
            resultados
        )

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


@app.get(
    "/api/componentes/compatibles"
)
def componentes_compatibles():

    try:

        tipo = request.args.get(
            "tipo",
            ""
        )

        presupuesto = request.args.get(
            "presupuesto",
            type=int
        )


        if (
            not tipo
            or presupuesto is None
        ):

            return jsonify({
                "error": (
                    "tipo y presupuesto "
                    "son requeridos"
                )
            }), 400


        tipo_ram = request.args.get(
            "tipo_ram"
        )

        formato_ram = request.args.get(
            "formato_ram"
        )

        socket_cpu = request.args.get(
            "socket_cpu"
        )

        interfaces = request.args.get(
            "interfaces",
            ""
        )


        db = obtener_db()


        consulta = {

            "tipo": tipo,

            "precio_mxn": {
                "$lte": presupuesto
            },

            "activo": True
        }


        if tipo == "RAM":

            if tipo_ram:

                consulta[
                    "compatibilidad.tecnologia"
                ] = tipo_ram


            if formato_ram:

                consulta[
                    "compatibilidad.formato"
                ] = formato_ram


        elif tipo == "CPU":

            if socket_cpu:

                consulta[
                    "compatibilidad.socket"
                ] = socket_cpu


        elif tipo == "SSD":

            if interfaces:

                lista_interfaces = [
                    item.strip()
                    for item
                    in interfaces.split(",")
                    if item.strip()
                ]


                if lista_interfaces:

                    consulta[
                        "compatibilidad.interfaz"
                    ] = {
                        "$in": lista_interfaces
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


        return jsonify(
            productos
        )

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )