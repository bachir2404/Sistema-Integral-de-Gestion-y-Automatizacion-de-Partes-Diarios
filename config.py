import json
import os

CONFIG_PATH = "ajustes.json"

def obtener_config_por_defecto():
    return {
        "pdf_cuadrante": "",
        "pdf_cabos": "",
        "ruta_partes": "Partes_Generados",
        "email_remitente": "",
        "pass_remitente": "",
        "personal": [],
        "jefes": []
    }

def cargar_ajustes():
    if not os.path.exists(CONFIG_PATH):
        guardar_ajustes(obtener_config_por_defecto())
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_ajustes(datos):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)