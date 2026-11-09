"""
Capa: modelo - lectura de datos (bodega).
Único archivo de la app que abre archivos (Excel y PDF).
Nota: en este repositorio la bodega se llama Insumos_Control_Polizas/
(el template de la Guía 2 dice data/). Se usa la ruta real del repo.
"""

import os
from datetime import datetime

import pandas as pd
import pdfplumber

# Raíz del proyecto (un nivel arriba de models/)
RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETA_INSUMOS = os.path.join(RAIZ_PROYECTO, "Insumos_Control_Polizas")
CARPETA_POLIZAS = os.path.join(CARPETA_INSUMOS, "polizas")
ARCHIVO_CLIENTES = os.path.join(CARPETA_INSUMOS, "Maestro_Clientes.xlsx")

# Diccionario: etiqueta del PDF -> nombre del campo en el diccionario de salida
CAMPOS = {
    "Numero de poliza": "numero",
    "Ramo": "ramo",
    "Tomador / Asegurado": "nombre",
    "Cedula": "cedula",
    "Vigencia desde": "desde",
    "Vigencia hasta": "hasta",
    "Prima anual": "prima",
    "Forma de pago": "pago",
    "Suma asegurada": "suma",
    "Asesor": "asesor",
}


def cargar_clientes():
    """
    Lee data/Maestro_Clientes.xlsx (hoja Clientes) con pandas.
    Devuelve un DataFrame con Cedula como texto sin espacios.
    """
    df = pd.read_excel(ARCHIVO_CLIENTES, sheet_name="Clientes", dtype=str)
    df["Cedula"] = df["Cedula"].str.strip()
    return df


def _texto_a_fecha(texto):
    """Convierte 'dd/mm/aaaa' a objeto date. Devuelve None si está vacío o falla."""
    if texto is None or str(texto).strip() == "":
        return None
    return datetime.strptime(str(texto).strip(), "%d/%m/%Y").date()


def _texto_a_numero(texto):
    """
    Convierte 'CRC 228,000.00' a número (float).
    Devuelve None si está vacío o no se puede convertir.
    """
    if texto is None or str(texto).strip() == "":
        return None
    limpio = str(texto).replace("CRC", "").replace(",", "").strip()
    if limpio == "":
        return None
    return float(limpio)


def leer_poliza(ruta_pdf):
    """
    Abre un PDF de póliza con pdfplumber, toma la primera página.
    Primera línea = aseguradora.
    Recorre las líneas restantes: si tiene ':' y la etiqueta está en CAMPOS,
    guarda el valor. Convierte fechas y montos.
    Devuelve un diccionario con:
    archivo, aseguradora, numero, ramo, nombre, cedula, desde, hasta,
    prima, pago, suma, asesor.
    """
    nombre_archivo = os.path.basename(ruta_pdf)

    with pdfplumber.open(ruta_pdf) as pdf:
        texto = pdf.pages[0].extract_text() or ""

    lineas = texto.split("\n")

    # Primera línea es el nombre de la aseguradora
    aseguradora = lineas[0].strip() if lineas else ""

    poliza = {
        "archivo": nombre_archivo,
        "aseguradora": aseguradora,
        "numero": None,
        "ramo": None,
        "nombre": None,
        "cedula": None,
        "desde": None,
        "hasta": None,
        "prima": None,
        "pago": None,
        "suma": None,
        "asesor": None,
    }

    # Recorrer las demás líneas buscando etiquetas conocidas
    for linea in lineas[1:]:
        if ":" not in linea:
            continue
        etiqueta, valor = linea.split(":", 1)
        etiqueta = etiqueta.strip()
        valor = valor.strip()
        if etiqueta in CAMPOS:
            campo = CAMPOS[etiqueta]
            if campo in ("desde", "hasta"):
                poliza[campo] = _texto_a_fecha(valor)
            elif campo in ("prima", "suma"):
                poliza[campo] = _texto_a_numero(valor)
            else:
                poliza[campo] = valor

    return poliza


def cargar_polizas():
    """
    Recorre la carpeta de pólizas en orden alfabético y devuelve una lista
    con el diccionario de cada PDF leído por leer_poliza().
    """
    archivos = sorted(
        f for f in os.listdir(CARPETA_POLIZAS) if f.lower().endswith(".pdf")
    )
    polizas = []
    for archivo in archivos:
        ruta = os.path.join(CARPETA_POLIZAS, archivo)
        polizas.append(leer_poliza(ruta))
    return polizas
