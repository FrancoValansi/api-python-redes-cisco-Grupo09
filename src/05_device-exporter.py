# Modulos que se utilizaran
import requests
import csv
from pathlib import Path
from tabulate import tabulate

# URL del Network Controller
baseUri = "http://localhost:58000/api/v1"

# Carpeta raiz del repositorio
carpeta_proyecto = Path(__file__).resolve().parent.parent

# Carpeta donde se guardaran los CSV
carpeta = carpeta_proyecto / "Exportaciones"

# Crear la carpeta si no existe
carpeta.mkdir(parents=True, exist_ok=True)

# Credenciales
data = {
    "username": "admin",
    "password": "Redes2026!"
}

# Obtener ticket de autenticacion
headers = {"Content-Type": "application/json"}

resp = requests.post(
    baseUri + "/ticket",
    json=data,
    headers=headers
)

resp.raise_for_status()
result = resp.json()

ticket = result["response"]["serviceTicket"]

print("Autenticacion exitosa")

# Preparar encabezado para las consultas
headers = {"X-Auth-Token": ticket}

try:

    # ==================================
    # 1. CONSULTAR DISPOSITIVOS DE RED
    # ==================================

    resp = requests.get(
        baseUri + "/network-device",
        headers=headers
    )

    resp.raise_for_status()
    result = resp.json()

    dispositivos = []

    for item in result["response"]:
        dispositivos.append({
            "Hostname": item.get("hostname", "N/D"),
            "Serial Number": item.get("serialNumber", "N/D"),
            "Software Version": item.get("softwareVersion", "N/D")
        })

    # Mostrar tabla en pantalla
    print("\nDispositivos de Red:")
    print(tabulate(
        [[d["Hostname"], d["Serial Number"], d["Software Version"]]
         for d in dispositivos],
        headers=["Hostname", "Serial Number", "Software Version"],
        tablefmt="rst"
    ))

    # Exportar a CSV
    archivo = carpeta / "dispositivos_red.csv"

    with open(archivo, "w", newline="", encoding="utf-8-sig") as csvfile:
        campos = ["Hostname", "Serial Number", "Software Version"]
        escritor = csv.DictWriter(csvfile, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(dispositivos)

    print("\nArchivo de network-devices generado:", archivo)


    # ==================================
    # 2. CONSULTAR HOSTS
    # ==================================

    resp = requests.get(
        baseUri + "/host",
        headers=headers
    )

    resp.raise_for_status()
    result = resp.json()

    hosts = []

    for item in result["response"]:
        hosts.append({
            "Hostname": item.get("hostName", "N/D"),
            "Tipo": item.get("hostType", "N/D"),
            "IP": item.get("hostIp", "N/D")
        })

    # Mostrar tabla en pantalla
    print("\nHosts de la Red:")
    print(tabulate(
        [[h["Hostname"], h["Tipo"], h["IP"]] for h in hosts],
        headers=["Hostname", "Tipo", "IP"],
        tablefmt="rst"
    ))

    # Exportar a CSV
    archivo = carpeta / "hosts_red.csv"

    with open(archivo, "w", newline="", encoding="utf-8-sig") as csvfile:
        campos = ["Hostname", "Tipo", "IP"]
        escritor = csv.DictWriter(csvfile, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(hosts)

    print("\nArchivo de hosts generado:", archivo)

    print("\nExportacion finalizada correctamente.")

finally:

    # ==================================
    # 3. ELIMINAR TICKET DE AUTENTICACION
    # ==================================

    try:
        resp = requests.delete(
            baseUri + "/ticket",
            headers=headers
        )

        if resp.status_code in (200, 204):
            print("Ticket de autenticacion eliminado correctamente.")
        else:
            print("No se pudo confirmar la eliminacion del ticket.")
            print("Codigo de estado:", resp.status_code)

    except requests.RequestException as error:
        print("Error al intentar eliminar el ticket:", error)