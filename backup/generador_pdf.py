import os
import datetime
import io
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from config import MAPA_FIRMAS  

def crear_parte_pdf(datos, carpeta_destino):
    try:
        fecha_actual = datetime.datetime.now()
        fecha_str = fecha_actual.strftime("%d-%m-%Y")
        nombre_archivo = f"Parte_Novedades_{fecha_str}.pdf"
        ruta_completa = os.path.join(carpeta_destino, nombre_archivo)
        
        PLANTILLA = "plantilla_formulario.pdf"
        if not os.path.exists(PLANTILLA):
            return f"ERROR: Falta el archivo '{PLANTILLA}'"
            
        reader = PdfReader(PLANTILLA)
        writer = PdfWriter()
        writer.append(reader)

        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

        # --- 1. RELLENAR TEXTOS ---
        campos_a_rellenar = {
            "NOVEDADES": datos["novedades"],
            "HORARIOS PATRULLAS": datos["patrullas"], # LÍNEA CORREGIDA
            "ANOMALIAS SEVICIO": datos["anomalias"], 
            "DÍA": str(fecha_actual.day),
            "AÑO": str(fecha_actual.year)[2:],
            "text_13lyun": datos["gs_saliente"],
            "text_15qudp": datos["ref_saliente"],
            "text_14trrn": datos["gs_entrante"],
            "text_16dddk": datos["ref_entrante"],
            "text_17dyei": meses[fecha_actual.month-1],
            "text_12xfvp": "" # Hueco vacío para la firma del Auxiliar Jefe
        }

        for pagina in writer.pages:
            writer.update_page_form_field_values(pagina, campos_a_rellenar)

        # --- 2. SISTEMA DE ESTAMPADO DE 4 FIRMAS ---
        
        # PANEL DE CALIBRACIÓN: Refuerzos bajados (y: 3.1)
        COORDENADAS_FIRMAS = {
            "gs_saliente":  {"nombre": datos["gs_saliente"],  "pagina": 0, "x": 4.7, "y": 6.3},
            "gs_entrante":  {"nombre": datos["gs_entrante"],  "pagina": 0, "x": 13.7, "y": 6.3},
            "ref_saliente": {"nombre": datos["ref_saliente"], "pagina": 0, "x": 4.7, "y": 3.1},
            "ref_entrante": {"nombre": datos["ref_entrante"], "pagina": 0, "x": 13.7, "y": 3.1}
        }

        print("\n--- INICIANDO ESTAMPADO MULTI-FIRMA ---")
        
        for rol, info in COORDENADAS_FIRMAS.items():
            nombre = info["nombre"]
            ruta_firma = MAPA_FIRMAS.get(nombre)
            
            if ruta_firma and os.path.exists(ruta_firma):
                print(f"Estampando firma de {nombre} ({rol})")
                
                packet = io.BytesIO()
                box = reader.pages[info["pagina"]].mediabox
                c = canvas.Canvas(packet, pagesize=(float(box.width), float(box.height)))
                
                # TAMAÑO
                c.drawImage(ruta_firma, info["x"] * cm, info["y"] * cm, width=2.6 * cm, height=1.6 * cm, mask='auto')
                c.save()
                packet.seek(0)
                
                capa_firma = PdfReader(packet)
                writer.pages[info["pagina"]].merge_page(capa_firma.pages[0])
            else:
                print(f"No hay firma para: {nombre} ({rol})")

        print("---------------------------------------\n")

        # --- 3. GUARDAR RESULTADO ---
        with open(ruta_completa, "wb") as f:
            writer.write(f)
        
        return ruta_completa
        
    except Exception as e:
        return f"ERROR CRÍTICO: {str(e)}"