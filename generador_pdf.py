import os
import datetime
import io
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

def crear_parte_pdf(datos, carpeta_destino, ajustes):
    fecha_actual = datetime.datetime.now()
    fecha_str = fecha_actual.strftime("%d-%m-%Y")
    nombre_archivo = f"Parte_Novedades_{fecha_str}.pdf"
    ruta_completa = os.path.join(carpeta_destino, nombre_archivo)

    if os.path.exists(ruta_completa):
        try:
            with open(ruta_completa, "ab") as f:
                pass
        except PermissionError:
            return "BLOQUEADO: El PDF está abierto en Acrobat. Ciérralo antes de generar uno nuevo."

    try:
        if not os.path.exists(carpeta_destino): os.makedirs(carpeta_destino)
        
        PLANTILLA = "plantilla_formulario.pdf"
        if not os.path.exists(PLANTILLA):
            return "ERROR: No se encuentra 'plantilla_formulario.pdf' en la carpeta."
            
        reader = PdfReader(PLANTILLA)
        writer = PdfWriter()
        writer.append(reader)

        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

        campos = {
            "NOVEDADES": datos["novedades"],
            "HORARIOS PATRULLAS": datos["patrullas"],
            "ANOMALIAS SEVICIO": datos["anomalias"],
            "DÍA": str(fecha_actual.day),
            "AÑO": str(fecha_actual.year)[2:],
            "text_13lyun": datos["gs_saliente"],
            "text_15qudp": datos["ref_saliente"],
            "text_14trrn": datos["gs_entrante"],
            "text_16dddk": datos["ref_entrante"],
            "text_17dyei": meses[fecha_actual.month-1],
            "text_12xfvp": datos["novedades"],
            "Novedades_Dia": datos["novedades"]
        }

        for pagina in writer.pages:
            writer.update_page_form_field_values(pagina, campos)

        mapa_firmas = {f"{p['empleo']} {p['nombre']}": p["firma"] for p in ajustes.get("personal", [])}
        
        COORDENADAS = {
            "gs_saliente":  {"nombre": datos["gs_saliente"],  "pagina": 0, "x": 4.7, "y": 6.3},
            "gs_entrante":  {"nombre": datos["gs_entrante"],  "pagina": 0, "x": 13.7, "y": 6.3},
            "ref_saliente": {"nombre": datos["ref_saliente"], "pagina": 0, "x": 4.7, "y": 3.1},
            "ref_entrante": {"nombre": datos["ref_entrante"], "pagina": 0, "x": 13.7, "y": 3.1}
        }

        for rol, info in COORDENADAS.items():
            ruta = mapa_firmas.get(info["nombre"])
            if ruta and os.path.exists(ruta):
                packet = io.BytesIO()
                c = canvas.Canvas(packet, pagesize=(float(reader.pages[0].mediabox.width), float(reader.pages[0].mediabox.height)))
                c.drawImage(ruta, info["x"] * cm, info["y"] * cm, width=2.6 * cm, height=1.6 * cm, mask='auto')
                c.save()
                packet.seek(0)
                writer.pages[info["pagina"]].merge_page(PdfReader(packet).pages[0])

        with open(ruta_completa, "wb") as f:
            writer.write(f)
        return ruta_completa
    except Exception as e:
        return f"ERROR CRÍTICO: {str(e)}"