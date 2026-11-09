"""
Capa: modelo - reglas del negocio (el recetario).
Decide estados, cuenta, suma primas y encuentra inconsistencias.
No abre archivos: recibe los datos ya leídos de models/datos.py.
"""

from datetime import date

from models.datos import cargar_clientes, cargar_polizas

FECHA_CORTE = date(2026, 11, 9)
DIAS_AVISO = 30


def estado_poliza(hasta, fecha_corte=FECHA_CORTE):
    """
    Devuelve el estado de una póliza según su fecha de vigencia hasta.
    if / elif / else:
    - "Sin fecha" si hasta es None
    - "Vencida" si hasta < fecha_corte
    - "Por vencer" si 0 <= días hasta vencer <= DIAS_AVISO
    - "Vigente" si más de DIAS_AVISO días
    """
    if hasta is None:
        return "Sin fecha"
    elif hasta < fecha_corte:
        return "Vencida"
    elif (hasta - fecha_corte).days <= DIAS_AVISO:
        return "Por vencer"
    else:
        return "Vigente"


def calcular_resultados(fecha_corte=FECHA_CORTE):
    """
    Cruza cada póliza con el maestro por cédula (correo y en_maestro),
    calcula los días hasta vencer y el estado.
    Devuelve lista de diccionarios ordenada de menos a más días
    (lo urgente primero).
    """
    df_clientes = cargar_clientes()
    polizas = cargar_polizas()

    # Índice de clientes por cédula para cruce rápido
    clientes_index = {}
    for _, fila in df_clientes.iterrows():
        cedula = str(fila["Cedula"]).strip()
        clientes_index[cedula] = {
            "nombre": fila.get("Nombre_Completo"),
            "correo": fila.get("Correo"),
            "telefono": fila.get("Telefono"),
            "asesor": fila.get("Asesor"),
        }

    # Cédulas que tienen al menos una póliza (para detectar clientes sin póliza)
    cedulas_con_poliza = set()
    for p in polizas:
        if p.get("cedula"):
            cedulas_con_poliza.add(str(p["cedula"]).strip())

    resultados = []
    for p in polizas:
        cedula = str(p.get("cedula") or "").strip()
        cliente = clientes_index.get(cedula)
        en_maestro = cliente is not None

        hasta = p.get("hasta")
        dias = (hasta - fecha_corte).days if hasta else None
        estado = estado_poliza(hasta, fecha_corte)

        resultados.append(
            {
                "numero": p.get("numero"),
                "archivo": p.get("archivo"),
                "aseguradora": p.get("aseguradora"),
                "ramo": p.get("ramo"),
                "nombre": p.get("nombre"),
                "cedula": cedula,
                "correo": cliente["correo"] if cliente else None,
                "en_maestro": en_maestro,
                "desde": p.get("desde"),
                "hasta": hasta,
                "dias": dias,
                "estado": estado,
                "prima": p.get("prima"),
                "pago": p.get("pago"),
                "suma": p.get("suma"),
                "asesor": p.get("asesor"),
            }
        )

    # Ordenar: primero los que tienen días (menos días = más urgente), los Sin fecha al final
    resultados.sort(
        key=lambda r: (r["dias"] is None, r["dias"] if r["dias"] is not None else 999999)
    )
    return resultados


def contar_por_estado(resultados):
    """Devuelve un diccionario con cuántas pólizas hay de cada estado."""
    conteo = {}
    for r in resultados:
        estado = r["estado"]
        conteo[estado] = conteo.get(estado, 0) + 1
    return conteo


def primas_por_aseguradora(resultados):
    """
    Devuelve un diccionario aseguradora -> suma de primas de pólizas no vencidas,
    ordenado de mayor a menor.
    """
    primas = {}
    for r in resultados:
        if r["estado"] != "Vencida" and r.get("prima") is not None:
            aseguradora = r["aseguradora"] or "Sin aseguradora"
            primas[aseguradora] = primas.get(aseguradora, 0) + r["prima"]
    return dict(sorted(primas.items(), key=lambda x: x[1], reverse=True))


def buscar_inconsistencias(resultados):
    """
    Devuelve una lista de textos con los 3 tipos de problema:
    1. cliente del maestro sin ninguna póliza
    2. póliza cuya cédula no está en el maestro
    3. póliza sin prima o con fecha ilegible
    """
    inconsistencias = []

    df_clientes = cargar_clientes()
    polizas = cargar_polizas()

    # Cédulas que aparecen en al menos una póliza
    cedulas_con_poliza = set()
    for p in polizas:
        if p.get("cedula"):
            cedulas_con_poliza.add(str(p["cedula"]).strip())

    # 1. Clientes del maestro sin ninguna póliza
    for _, fila in df_clientes.iterrows():
        cedula = str(fila["Cedula"]).strip()
        if cedula not in cedulas_con_poliza:
            inconsistencias.append(
                f"Cliente sin póliza: {fila.get('Nombre_Completo')} (cédula {cedula})"
            )

    # 2. Pólizas cuya cédula no está en el maestro
    # 3. Pólizas sin prima o con fecha ilegible
    for r in resultados:
        if not r["en_maestro"]:
            inconsistencias.append(
                f"Póliza {r['numero']} cédula {r['cedula']} no está en el maestro"
            )
        if r.get("prima") is None or r.get("hasta") is None:
            inconsistencias.append(
                f"Póliza {r['numero']} sin prima o fecha ilegible"
            )

    return inconsistencias


def buscar_por_numero(numero):
    """Busca una póliza por su número y devuelve su diccionario de resultado, o None."""
    for r in calcular_resultados():
        if r["numero"] == numero:
            return r
    return None
