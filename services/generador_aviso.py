"""
Capa: servicio - la imprenta.
Crea el aviso de renovación de póliza en PDF (A4 vertical) con fpdf2 y lo devuelve en bytes.
"""

from fpdf import FPDF


def _latin1(texto):
    """Convierte texto a latin-1 para que las tildes no fallen con Helvetica."""
    if texto is None:
        return ""
    return str(texto).encode("latin-1", "replace").decode("latin-1")


def crear_aviso_pdf(poliza):
    """
    Crea un aviso de renovación en PDF (A4 vertical) y lo devuelve en bytes.

    poliza: diccionario con claves como nombre, numero, aseguradora, ramo,
            cedula, hasta, dias, estado, prima, pago, asesor.
    """
    nombre = poliza.get("nombre") or "Cliente"
    numero = poliza.get("numero") or "Sin número"
    aseguradora = poliza.get("aseguradora") or "Sin aseguradora"
    ramo = poliza.get("ramo") or "No registrado"
    cedula = poliza.get("cedula") or "No registrada"
    hasta = poliza.get("hasta")
    dias = poliza.get("dias")
    estado = poliza.get("estado") or "Vigente"
    prima = poliza.get("prima")
    pago = poliza.get("pago") or "No registrado"
    asesor = poliza.get("asesor") or "No asignado"

    # Formatear fecha de vigencia
    if hasta:
        vigencia_texto = hasta.strftime("%d/%m/%Y")
    else:
        vigencia_texto = "Sin fecha"

    # Formatear prima
    if prima is not None:
        prima_texto = f"CRC {prima:,.0f}".replace(",", ".")
    else:
        prima_texto = "No registrada"

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Fuente Helvetica (built-in)
    pdf.set_font("Helvetica", size=11)

    # --- Banda superior roja (#AE1800) ---
    pdf.set_fill_color(174, 24, 0)
    pdf.rect(0, 0, 210, 22, style="F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_xy(10, 6)
    pdf.cell(0, 7, _latin1("Corredora de Seguros Horizonte"), ln=True, align="L")
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_xy(10, 14)
    pdf.cell(0, 7, _latin1("Aviso de renovación de póliza"), ln=True, align="L")
    pdf.ln(10)

    # --- Saludo ---
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 7, _latin1(f"Estimado(a) {nombre}:"), ln=True)
    pdf.ln(4)

    # --- Párrafo según estado ---
    if estado == "Vencida":
        pdf.multi_cell(
            0, 6,
            _latin1(
                f"Su póliza {numero} venció el {vigencia_texto}. "
                f"Por favor comuníquese con su asesor ({asesor}) para renovarla cuanto antes."
            ),
        )
    elif estado == "Por vencer":
        pdf.multi_cell(
            0, 6,
            _latin1(
                f"Su póliza {numero} vence el {vigencia_texto}, es decir, en {dias} días. "
                f"Su asesor ({asesor}) se comunicará con usted para coordinar la renovación."
            ),
        )
    else:
        pdf.multi_cell(
            0, 6,
            _latin1(
                f"Su póliza {numero} está vigente hasta el {vigencia_texto}. "
                f"No requiere acción en este momento."
            ),
        )
    pdf.ln(8)

    # --- Tabla de datos ---
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(230, 227, 226)  # gris claro para encabezado
    headers = ["Campo", "Valor"]
    datos = [
        ("Número de póliza", numero),
        ("Aseguradora", aseguradora),
        ("Ramo", ramo),
        ("Cédula", cedula),
        ("Vigencia hasta", vigencia_texto),
        ("Prima anual", prima_texto),
        ("Forma de pago", pago),
    ]

    ancho_campo = 55
    ancho_valor = 140

    # Encabezado de tabla
    pdf.cell(ancho_campo, 7, _latin1(headers[0]), border=1, fill=True)
    pdf.cell(ancho_valor, 7, _latin1(headers[1]), border=1, fill=True, ln=True)

    # Filas
    pdf.set_font("Helvetica", size=10)
    for campo, valor in datos:
        pdf.cell(ancho_campo, 7, _latin1(campo), border=1)
        pdf.cell(ancho_valor, 7, _latin1(valor), border=1, ln=True)

    pdf.ln(10)

    # --- Pie de página gris ---
    pdf.set_y(-25)
    pdf.set_fill_color(230, 227, 226)
    pdf.rect(0, pdf.get_y(), 210, 20, style="F")
    pdf.set_text_color(100, 100, 100)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_xy(10, pdf.get_y() + 5)
    pdf.multi_cell(
        0, 4,
        _latin1(
            "Documento ficticio para fines académicos. Universidad Fundepos · "
            "Técnico en Inteligencia Artificial Empresarial · Módulo 2 · Grupo BN Seguros."
        ),
    )

    # Devolver bytes del PDF
    pdf_output = pdf.output(dest="S")
    if isinstance(pdf_output, str):
        return pdf_output.encode("latin-1")
    return bytes(pdf_output)
