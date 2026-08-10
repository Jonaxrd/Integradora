import requests


API_URL = "https://TU-SERVICIO.onrender.com"

TIMEOUT = 15


def probar_conexion():

    try:

        response = requests.get(
            f"{API_URL}/",
            timeout=TIMEOUT
        )

        response.raise_for_status()

        data = response.json()

        print(
            "Conexion con SCOPE API realizada correctamente."
        )

        print(
            f"Servicio: {data.get('service', 'SCOPE API')}"
        )

        return True

    except Exception as e:

        print(
            f"Error conectando con SCOPE API: {e}"
        )

        return False


def obtener_componentes():

    try:

        response = requests.get(
            f"{API_URL}/api/componentes/todos",
            timeout=TIMEOUT
        )

        response.raise_for_status()

        return response.json()

    except Exception as e:

        print(
            f"Error obteniendo componentes: {e}"
        )

        return []


def obtener_equipos():

    try:

        response = requests.get(
            f"{API_URL}/api/equipos/todos",
            timeout=TIMEOUT
        )

        response.raise_for_status()

        return response.json()

    except Exception as e:

        print(
            f"Error obteniendo equipos: {e}"
        )

        return []


def buscar_componentes(
    tipo,
    presupuesto
):

    try:

        response = requests.get(
            f"{API_URL}/api/componentes",
            params={
                "tipo": tipo,
                "presupuesto": presupuesto
            },
            timeout=TIMEOUT
        )

        response.raise_for_status()

        return response.json()

    except Exception as e:

        print(
            f"Error consultando componentes: {e}"
        )

        return []


def buscar_equipos(
    presupuesto,
    nivel_minimo=0
):

    try:

        response = requests.get(
            f"{API_URL}/api/equipos",
            params={
                "presupuesto": presupuesto,
                "nivel_minimo": nivel_minimo
            },
            timeout=TIMEOUT
        )

        response.raise_for_status()

        return response.json()

    except Exception as e:

        print(
            f"Error consultando equipos: {e}"
        )

        return []


def buscar_componentes_compatibles(
    tipo,
    presupuesto,
    compatibilidad=None
):

    try:

        compatibilidad = (
            compatibilidad
            or {}
        )

        params = {
            "tipo": tipo,
            "presupuesto": presupuesto
        }


        tipo_ram = compatibilidad.get(
            "tipo_ram"
        )

        formato_ram = compatibilidad.get(
            "formato_ram"
        )

        socket_cpu = compatibilidad.get(
            "socket_cpu"
        )

        interfaces = compatibilidad.get(
            "interfaces_almacenamiento",
            []
        )


        if (
            tipo_ram
            and tipo_ram != "Desconocido"
        ):

            params["tipo_ram"] = tipo_ram


        if (
            formato_ram
            and formato_ram != "Desconocido"
        ):

            params[
                "formato_ram"
            ] = formato_ram


        if (
            socket_cpu
            and socket_cpu != "Desconocido"
        ):

            params[
                "socket_cpu"
            ] = socket_cpu


        if interfaces:

            params[
                "interfaces"
            ] = ",".join(
                interfaces
            )


        response = requests.get(
            f"{API_URL}/api/componentes/compatibles",
            params=params,
            timeout=TIMEOUT
        )

        response.raise_for_status()

        return response.json()

    except Exception as e:

        print(
            "Error consultando compatibilidad "
            f"desde SCOPE API: {e}"
        )

        return []


if __name__ == "__main__":

    probar_conexion()