import customtkinter as ctk
import pdfplumber
import os
import datetime
from tkinter import messagebox
from generador_pdf import crear_parte_pdf
from config import NOMBRES_PERSONAL, RUTA_CUADRANTES

# --- CONFIGURACIÓN VISUAL ---
ctk.set_appearance_mode("Light")
ctk.set_window_scaling(1.0)
ctk.set_widget_scaling(1.0)

ROJO_LORETO = "#C41E3A"
BLANCO = "#FFFFFF"

def limpiar_nombre(n):
    """Quita el 'D.' o 'Dª.' pero mantiene el empleo militar (Cbo., Sdo.)"""
    if not n: return ""
    # Reemplazamos el tratamiento por un espacio
    n = n.replace(" D. ", " ")
    n = n.replace(" Dª. ", " ")
    # Limpiamos posibles dobles espacios que hayan quedado
    return " ".join(n.split()).strip()

def leer_cuadrante_pdf():
    """Busca el cuadrante en la ruta modular y extrae S y R"""
    meses_nombres = ["enero", "febrero", "marzo", "abril", "mayo", "junio", 
                     "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    
    hoy_dt = datetime.datetime.now()
    mes_actual = meses_nombres[hoy_dt.month - 1]
    año_actual = hoy_dt.year
    
    nombre_archivo = f"cuadrante_{mes_actual}_{año_actual}.pdf"
    ruta_completa = os.path.join(RUTA_CUADRANTES, nombre_archivo)
    
    res = {"gs_ent": "", "ref_ent": "", "gs_sal": "", "ref_sal": ""}
    
    if not os.path.exists(ruta_completa): 
        print(f"Aviso: No se encontró el archivo {ruta_completa}")
        return res

    try:
        with pdfplumber.open(ruta_completa) as pdf:
            tabla = pdf.pages[0].extract_table()
            hoy = hoy_dt.day
            ayer = (hoy_dt - datetime.timedelta(days=1)).day
            
            fila_dias = tabla[1] 
            c_hoy = next((i for i, v in enumerate(fila_dias) if str(v).strip() == str(hoy)), -1)
            c_ayer = next((i for i, v in enumerate(fila_dias) if str(v).strip() == str(ayer)), -1)

            for fila in tabla[2:]:
                if not fila[0]: continue
                nom = limpiar_nombre(fila[0])
                if c_hoy != -1:
                    if fila[c_hoy] == 'S': res["gs_ent"] = nom
                    if fila[c_hoy] == 'R': res["ref_ent"] = nom
                if c_ayer != -1:
                    if fila[c_ayer] == 'S': res["gs_sal"] = nom
                    if fila[c_ayer] == 'R': res["ref_sal"] = nom
        return res
    except: 
        return res

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Seguridad Loreto - Gestión de Novedades")
        self.geometry("1000x820")
        self.configure(fg_color=BLANCO)
        
        # Encabezado
        header = ctk.CTkFrame(self, fg_color=ROJO_LORETO, height=70, corner_radius=0)
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="PARTE DIARIO DE NOVEDADES", text_color=BLANCO, 
                     font=("Arial", 22, "bold")).place(relx=0.5, rely=0.5, anchor="center")

        # Cuerpo
        f_per = ctk.CTkFrame(self, fg_color="#F9F9F9", border_color="#CCCCCC", border_width=1)
        f_per.pack(pady=10, padx=30, fill="x")
        grid = ctk.CTkFrame(f_per, fg_color="transparent")
        grid.pack(pady=15)

        self.gs_s = self.crear_combo(grid, "GS Saliente:", 0, 0)
        self.ref_s = self.crear_combo(grid, "Ref. Saliente:", 1, 0)
        self.gs_e = self.crear_combo(grid, "GS Entrante:", 0, 2)
        self.ref_e = self.crear_combo(grid, "Ref. Entrante:", 1, 2)

        f_mid = ctk.CTkFrame(self, fg_color="transparent")
        f_mid.pack(pady=10, padx=30, fill="x")
        self.pat = self.crear_txt(f_mid, "HORARIOS DE PATRULLAS", "left")
        self.ano = self.crear_txt(f_mid, "ANOMALÍAS DEL SERVICIO", "right")

        ctk.CTkLabel(self, text="NOVEDADES DEL DÍA", text_color=ROJO_LORETO, font=("Arial", 14, "bold")).pack()
        self.nov = ctk.CTkTextbox(self, height=200, border_width=1, border_color="#CCCCCC")
        self.nov.pack(pady=10, padx=30, fill="x")

        self.btn = ctk.CTkButton(self, text="GENERAR PARTE PDF", fg_color=ROJO_LORETO, 
                                 height=55, font=("Arial", 16, "bold"), command=self.guardar)
        self.btn.pack(pady=20, padx=30, fill="x")

        self.after(200, self.cargar_datos)

    def cargar_datos(self):
        info = leer_cuadrante_pdf()
        self.gs_s.set(info["gs_sal"])
        self.ref_s.set(info["ref_sal"])
        self.gs_e.set(info["gs_ent"])
        self.ref_e.set(info["ref_ent"])

    def crear_combo(self, m, t, r, c):
        ctk.CTkLabel(m, text=t).grid(row=r, column=c, padx=10, pady=5, sticky="e")
        cb = ctk.CTkComboBox(m, width=220, values=NOMBRES_PERSONAL)
        cb.grid(row=r, column=c+1, padx=10, pady=5)
        return cb

    def crear_txt(self, m, tit, l):
        fr = ctk.CTkFrame(m, fg_color=BLANCO, border_width=1, border_color="#DDDDDD")
        fr.pack(side=l, fill="both", expand=True, padx=5)
        ctk.CTkLabel(fr, text=tit, text_color=ROJO_LORETO, font=("Arial", 11, "bold")).pack(pady=2)
        t = ctk.CTkTextbox(fr, height=100, border_width=0)
        t.pack(fill="both", padx=5, pady=5)
        return t

    def guardar(self):
        datos = {
            "gs_saliente": self.gs_s.get(), "ref_saliente": self.ref_s.get(),
            "gs_entrante": self.gs_e.get(), "ref_entrante": self.ref_e.get(),
            "patrullas": self.pat.get("1.0", "end-1c"),
            "anomalias": self.ano.get("1.0", "end-1c"),
            "novedades": self.nov.get("1.0", "end-1c")
        }
        if not os.path.exists("Partes_Generados"): os.makedirs("Partes_Generados")
        res = crear_parte_pdf(datos, "Partes_Generados")
        if "ERROR" in res: messagebox.showerror("Error", res)
        else: os.startfile(res)

if __name__ == "__main__":
    App().mainloop()