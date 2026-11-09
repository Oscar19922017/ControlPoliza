"""
Capa: controlador - el jefe de cocina.
Recibe pedidos del navegador, pide datos al modelo y al servicio, elige qué mostrar.
NO calcula nada: solo llama a models/ y services/.
"""

import io
import zipfile
from flask import Blueprint, render_template, send_file, abort

from models.polizas import (
    calcular_resultados,
    contar_por_estado,
    primas_por_aseguradora,
    buscar_inconsistencias,
    buscar_por_numero,
    FECHA_CORTE,
)
from services.generador_aviso import crear_aviso_pdf

polizas_bp = Blueprint("polizas", __name__)


@polizas_bp.route("/")
def inicio():
    """Tablero: contadores, primas por aseguradora, inconsistencias, tabla de pólizas, fecha de corte."""
    resultados = calcular_resultados()
    conteo = contar_por_estado(resultados)
    primas = primas_por_aseguradora(resultados)
    inconsistencias = buscar_inconsistencias(resultados)
    fecha_corte = FECHA_CORTE.strftime("%d/%m/%Y")
    return render_template(
        "inicio.html",
        resultados=resultados,
        conteo=conteo,
        primas=primas,
        inconsistencias=inconsistencias,
        fecha_corte=fecha_corte,
    )


@polizas_bp.route("/aviso/<numero>")
def aviso(numero):
    """Devuelve el aviso en PDF para ver en el navegador. 404 si no existe o está Vigente."""
    poliza = buscar_por_numero(numero)
    if poliza is None or poliza["estado"] == "Vigente":
        abort(404)
    pdf_bytes = crear_aviso_pdf(poliza)
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        download_name=f"aviso_{numero}.pdf",
    )


@polizas_bp.route("/descargar-avisos")
def descargar_avisos():
    """Arma en memoria un .zip con los avisos de todas las pólizas Por vencer y Vencidas."""
    resultados = calcular_resultados()
    pendientes = [r for r in resultados if r["estado"] in ("Por vencer", "Vencida")]

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for r in pendientes:
            pdf_bytes = crear_aviso_pdf(r)
            zf.writestr(f"aviso_{r['numero']}.pdf", pdf_bytes)
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype="application/zip",
        download_name="avisos_renovacion.zip",
        as_attachment=True,
    )
