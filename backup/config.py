# config.py

# --- CONFIGURACIÓN DE RUTAS ---
RUTA_CUADRANTES = r"C:\Users\Bachir\Desktop\Proyecto_Loreto\Cuadrantes"

# --- MAPEO DE FIRMAS ---
MAPA_FIRMAS = {
    "Sdo. Bachir Boudlal Abdelkader": "firmas/bachir_boudlal_abdelkader.png",
    "Sdo. José Manuel Sotillo San Román": "firmas/jose_manuel_sotillo_san_roman.png",
    "Sdo. Javier Gómez Payán": "firmas/javier_gomez_payan.png",
    "Cbo. Félix José López Perona": "firmas/felix_jose_lopez_perona.png",
    "Cbo. Carlos Antonio Jiménez Díez": "firmas/carlos_antonio_jimenez_diez.png",
    "Cbo. María Teresa Lairón Peñarrubia": "firmas/teresa_lairon_penarrubia.png",
    "Cbo. Silvia de Paz González": "firmas/silvia_de_paz_gonzalez.png",
    "Cbo. Enrique González Arteaga": "firmas/enrique_gonzalez_arteaga.png",
    "Sdo. Alberto Delgado López": "firmas/alberto_delgado_lopez.png",
    "Sdo. Daniel de las Heras Ródenas": "firmas/daniel_de_las_heras_rodenas.png",
    "Sdo. Eduardo Elices Javega": "firmas/eduardo_elices_javega.png",
    "Sdo. David Rodríguez Benítez": "firmas/david_rodriguez_benitez.png",
    "Sdo. Pablo Sánchez Díaz": "firmas/pablo_sanchez_diaz.png",
    "Sdo. Fernando Ganchinho Domínguez": "firmas/fernando_ganchinho_dominguez.png",
}

# Lista limpia para los desplegables de la interfaz
NOMBRES_PERSONAL = [""] + sorted(list(MAPA_FIRMAS.keys()))