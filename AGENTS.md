# AGENTS.md — App de control de pólizas (Seguros Horizonte · Grupo BN Seguros)

## Qué hay en este repo hoy (solo insumos, sin código aún)

- `Insumos_Control_Polizas/Maestro_Clientes.xlsx`: hoja `Clientes`, 20 filas, columnas `Cedula, Nombre_Completo, Correo, Telefono, Asesor`. **Verificado con pandas**: 20 clientes.
- `Insumos_Control_Polizas/polizas/`: 20 pólizas en PDF (6 SPC, 9 PCS, 5 AIS). Primera línea = aseguradora; luego líneas `Etiqueta: valor` (`Numero de poliza`, `Ramo`, `Tomador / Asegurado`, `Cedula`, `Vigencia desde`, `Vigencia hasta`, `Prima anual`, `Forma de pago`, `Suma asegurada`, `Asesor`). Fechas `dd/mm/aaaa`; montos tipo `CRC 228,000.00` (vacío = None).
- **No hay código, ni tests, ni CI.** Esta carpeta es la raíz del proyecto `control-polizas` de la Guía 2; la app se construye aquí capa por capa. La Guía 2 llama `data/` a la bodega; en este repo los insumos viven en `Insumos_Control_Polizas/`.

## Reglas de oro (evitan errores comunes)

1. **`Insumos_Control_Polizas/` es solo lectura**: nunca modificar ni borrar el Excel ni los PDF.
2. **Dependencias con `uv` (nunca pip)**: `uv add flask pandas openpyxl pdfplumber fpdf2`; ejecutar con `uv run app.py`. En Windows, arrancar con `iniciar_app.bat` (doble clic). **El agente nunca enciende la app por su cuenta**; el usuario la abre.
3. **Arquitectura por capas (respetar siempre)**:
   - `Insumos_Control_Polizas/` = bodega (solo lectura).
   - `models/datos.py`: único archivo que abre archivos (`cargar_clientes`, `leer_poliza`, `cargar_polizas`).
   - `models/polizas.py`: reglas del negocio (`FECHA_CORTE`, `DIAS_AVISO`, `estado_poliza`, `calcular_resultados`, `contar_por_estado`, `primas_por_aseguradora`, `buscar_inconsistencias`, `buscar_por_numero`).
   - `services/generador_aviso.py`: aviso de renovación en PDF con fpdf2.
   - `controllers/polizas_controller.py`: rutas Flask (`/`, `/aviso/<numero>`, `/descargar-avisos`); **no calcula**, solo llama al modelo y al servicio.
   - `views/` + `public/static/`: solo muestran datos.
4. Responder, comentar código y documentar en **español** (regla obligatoria del programa).

## Reglas del negocio (criterio de éxito, verificables)

- `FECHA_CORTE = date(2026, 11, 2)`; `DIAS_AVISO = 30`.
- `Vencida`: `hasta < FECHA_CORTE`. `Por vencer`: `0 <= dias_hasta_vencer <= DIAS_AVISO`. `Vigente`: más de 30 días.
- Cruzar cada póliza con el maestro por `Cedula` para obtener el correo.
- Inconsistencias: (1) cliente del maestro sin ninguna póliza (Javier Espinoza Leon); (2) póliza cuya cédula no está en el maestro (PCS-2026-0009); (3) póliza sin prima o con fecha ilegible (AIS-2026-0002).
- Primas por aseguradora: suma de primas de pólizas **no vencidas**, de mayor a menor.
- Resultado esperado con estos datos: **12 Vigentes, 5 Por vencer, 3 Vencidas, 3 inconsistencias**.
- Casos de control: AIS-2026-0001 (Laura Jimenez Solano) vence 14/11/2026, 12 días, Por vencer; PCS-2026-0001 (Carlos Mora Vargas) venció 23/09/2026, Vencida; SPC-2026-0001 (Ana Lucia Rojas Mendez) vence 21/05/2027, Vigente.

## Convenciones de trabajo

- Scripts auxiliares de una tarea: prefijo guion bajo (`_validar_datos.py`), se ejecutan con `python _script.py` y se borran al terminar. La app web es la excepción: `app.py`.
- `.gitignore` debe excluir `.venv` y `__pycache__`.
- Los acentos pueden verse como mojibake en PowerShell (artefacto de la terminal); los archivos están bien en UTF-8.

## Referencias

- `Guia2_App_Control_Polizas_OpenCode_uv_Flask_BN_Seguros.html` (carpeta padre `Grupo BN Seguros`): especificación paso a paso de la app.
- `App_Control_Polizas_Referencia.zip` (carpeta padre): app de referencia si algo se rompe.
- `AGENTS.md` y `CLAUDE.md` en la raíz del workspace (`Universidad Fundepos/`): convenciones globales del programa.
