import customtkinter as ctk
import os, datetime, threading, pdfplumber
from tkinter import messagebox, Canvas, filedialog
from PIL import Image, ImageDraw
from generador_pdf import crear_parte_pdf
from enviador_correo import enviar_parte_pdf
import config

ctk.set_appearance_mode("Light")
ROJO_LORETO = "#C41E3A"
BLANCO = "#FFFFFF"

def limpiar_nombre(n):
    if not n: return ""
    for b in ["SDO.", "CBO.", "CBO.1º", "1º", "D.", "Dª.", "SGT.", "SGTO.", ",", ".", "DON", "DOÑA"]:
        n = n.upper().replace(b, "")
    return " ".join(n.split()).strip().upper()

def son_la_misma_persona(n_pdf, n_lista):
    p_pdf = set(limpiar_nombre(n_pdf).split())
    p_lista = set(limpiar_nombre(n_lista).split())
    if not p_pdf or not p_lista: return False
    return len(p_pdf.intersection(p_lista)) >= 2

class VentanaFirma(ctk.CTkToplevel):
    def __init__(self, master, nombre, cb):
        super().__init__(master)
        self.title(f"Firma: {nombre}"); self.geometry("500x450"); self.attributes("-topmost", True); self.grab_set()
        self.cb = cb; self.nombre_persona = nombre; self.configure(fg_color=BLANCO)
        ctk.CTkLabel(self, text="Dibuja la firma", font=("Arial", 16, "bold")).pack(pady=10)
        self.canvas = Canvas(self, width=450, height=200, bg="white", highlightthickness=2)
        self.canvas.pack(pady=10)
        self.image = Image.new("RGBA", (450, 200), (255, 255, 255, 0))
        self.draw = ImageDraw.Draw(self.image)
        self.canvas.bind("<B1-Motion>", self.dibujar); self.lx, self.ly = None, None
        self.canvas.bind("<ButtonRelease-1>", lambda e: setattr(self, 'lx', None))
        btns = ctk.CTkFrame(self, fg_color="transparent"); btns.pack(pady=10)
        ctk.CTkButton(btns, text="Limpiar", fg_color="#777777", command=self.limpiar).pack(side="left", padx=10)
        ctk.CTkButton(btns, text="Confirmar", fg_color=ROJO_LORETO, command=self.confirmar).pack(side="left", padx=10)
    def dibujar(self, e):
        if self.lx:
            self.canvas.create_line(self.lx, self.ly, e.x, e.y, width=4, capstyle="round")
            self.draw.line([self.lx, self.ly, e.x, e.y], fill="black", width=4)
        self.lx, self.ly = e.x, e.y
    def limpiar(self):
        self.canvas.delete("all"); self.image = Image.new("RGBA", (450, 200), (255, 255, 255, 0)); self.draw = ImageDraw.Draw(self.image)
    def confirmar(self):
        if not os.path.exists("firmas"): os.makedirs("firmas")
        ruta = f"firmas/firma_{self.nombre_persona.replace(' ', '_').lower()}.png"
        self.image.save(ruta); self.cb(ruta); self.destroy()

class VentanaEditorPersonal(ctk.CTkToplevel):
    def __init__(self, master, cb, datos=None):
        super().__init__(master); self.title("Personal"); self.geometry("450x400"); self.attributes("-topmost", True); self.grab_set()
        self.cb = cb; self.orig = datos; self.r_f = datos['firma'] if datos else ""; self.configure(fg_color=BLANCO)
        self.ent_e = ctk.CTkOptionMenu(self, values=["Sdo.", "Cbo.", "Cbo. 1º", "Sgt."]); self.ent_e.pack(pady=10)
        if datos: self.ent_e.set(datos['empleo'])
        self.ent_n = ctk.CTkEntry(self, placeholder_text="Nombre Completo", width=300); self.ent_n.pack(pady=10)
        if datos: self.ent_n.insert(0, datos['nombre'])
        ctk.CTkButton(self, text="✎ Firma Digital", command=lambda: VentanaFirma(self, self.ent_n.get(), self.f_c)).pack(pady=10)
        self.lbl = ctk.CTkLabel(self, text="✅ Firma OK" if self.r_f else "❌ Sin firma"); self.lbl.pack()
        ctk.CTkButton(self, text="Guardar", fg_color="green", command=self.validar).pack(pady=20)
    def f_c(self, r): self.r_f = r; self.lbl.configure(text="✅ Firma OK")
    def validar(self):
        if not self.ent_n.get() or not self.r_f: return messagebox.showwarning("Error", "Falta nombre o firma.")
        self.cb({"empleo": self.ent_e.get(), "nombre": self.ent_n.get(), "firma": self.r_f}, self.orig); self.destroy()

class VentanaEditorJefe(ctk.CTkToplevel):
    def __init__(self, master, cb, datos=None):
        super().__init__(master); self.title("Añadir / Editar Jefe"); self.geometry("400x300"); self.attributes("-topmost", True); self.grab_set()
        self.cb = cb; self.orig = datos; self.configure(fg_color=BLANCO)
        self.ent_n = ctk.CTkEntry(self, placeholder_text="Nombre", width=300); self.ent_n.pack(pady=10)
        if datos: self.ent_n.insert(0, datos['nombre'])
        self.ent_m = ctk.CTkEntry(self, placeholder_text="Correo", width=300); self.ent_m.pack(pady=10)
        if datos: self.ent_m.insert(0, datos['email'])
        ctk.CTkButton(self, text="Guardar", fg_color="green", command=self.v).pack(pady=20)
    def v(self):
        if not self.ent_n.get() or not self.ent_m.get(): return messagebox.showwarning("Error", "Faltan datos.")
        self.cb({"nombre": self.ent_n.get(), "email": self.ent_m.get()}, self.orig); self.destroy()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Seguridad Loreto"); self.geometry("1150x950"); self.configure(fg_color=BLANCO)
        self.ajustes = config.cargar_ajustes()
        header = ctk.CTkFrame(self, fg_color=ROJO_LORETO, height=70, corner_radius=0); header.pack(fill="x")
        ctk.CTkLabel(header, text="PARTE DIARIO DE NOVEDADES", text_color=BLANCO, font=("Arial", 22, "bold")).place(relx=0.5, rely=0.5, anchor="center")
        self.tabs = ctk.CTkTabview(self, segmented_button_selected_color=ROJO_LORETO, fg_color="#F2F2F2"); self.tabs.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.tab_gen = self.tabs.add("GENERAR PARTE")
        self.tab_pers = self.tabs.add("PERSONAL")
        self.tab_conf = self.tabs.add("CONFIGURACIÓN")
        self.tab_ayuda = self.tabs.add("AYUDA")
        
        self.setup_gen(); self.setup_pers(); self.setup_conf(); self.setup_ayuda()
        self.update_listas_ui()
        self.after(1000, self.auto_lectura_cuadrantes)

    def setup_gen(self):
        # ScrollableFrame envuelve todo el contenido para soportar scroll vertical
        sc = ctk.CTkScrollableFrame(self.tab_gen, fg_color="transparent")
        sc.pack(fill="both", expand=True, padx=0, pady=0)

        f_p = ctk.CTkFrame(sc, fg_color=BLANCO, border_width=1, border_color="#DDDDDD"); f_p.pack(pady=10, fill="x", padx=10)
        ctk.CTkLabel(f_p, text="PERSONAL DE SERVICIO", font=("Arial", 11, "bold"), text_color=ROJO_LORETO).pack(pady=5)
        grid = ctk.CTkFrame(f_p, fg_color="transparent"); grid.pack(pady=10)
        self.gs_s = self.crear_combo(grid, "GS Sal:", 0, 0); self.ref_s = self.crear_combo(grid, "Ref Sal:", 1, 0)
        self.gs_e = self.crear_combo(grid, "GS Ent:", 0, 2); self.ref_e = self.crear_combo(grid, "Ref Ent:", 1, 2)

        f_d = ctk.CTkFrame(sc, fg_color="#FAFAFA", border_width=1, border_color="#DDDDDD"); f_d.pack(pady=5, fill="x", padx=10)
        ctk.CTkLabel(f_d, text="DESTINATARIOS (CABO 1º)", font=("Arial", 11, "bold"), text_color=ROJO_LORETO).pack(pady=5)
        row_d = ctk.CTkFrame(f_d, fg_color="transparent"); row_d.pack(pady=5)
        self.dest1 = ctk.CTkComboBox(row_d, values=[""], width=250); self.dest1.pack(side="left", padx=10)
        self.dest2 = ctk.CTkComboBox(row_d, values=[""], width=250); self.dest2.pack(side="left", padx=10)

        f_m = ctk.CTkFrame(sc, fg_color="transparent"); f_m.pack(fill="both", expand=True, pady=5, padx=10)
        self.pat = self.crear_txt(f_m, "HORARIOS DE PATRULLAS", "left"); self.ano = self.crear_txt(f_m, "ANOMALÍAS", "right")

        f_nov = ctk.CTkFrame(sc, fg_color="transparent"); f_nov.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(f_nov, text="NOVEDADES DEL DÍA", font=("Arial", 12, "bold"), text_color=ROJO_LORETO).pack(anchor="w")
        self.nov = ctk.CTkTextbox(f_nov, height=130, border_width=1, border_color="#CCCCCC"); self.nov.pack(pady=5, fill="x")

        f_bt = ctk.CTkFrame(sc, fg_color="transparent"); f_bt.pack(fill="x", pady=10, padx=10)
        self.env_v = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(f_bt, text="Tramitar envío por correo tras revisión", variable=self.env_v).pack(pady=5)
        self.btn_gen = ctk.CTkButton(f_bt, text="GENERAR PARTE PDF", fg_color=ROJO_LORETO, height=55, font=("Arial", 16, "bold"), command=self.g_pdf); self.btn_gen.pack(pady=5, fill="x")

    def g_pdf(self):
        datos = {"gs_saliente": self.gs_s.get(), "ref_saliente": self.ref_s.get(), "gs_entrante": self.gs_e.get(), "ref_entrante": self.ref_e.get(), "patrullas": self.pat.get("1.0", "end-1c"), "anomalias": self.ano.get("1.0", "end-1c"), "novedades": self.nov.get("1.0", "end-1c")}
        r = crear_parte_pdf(datos, self.ajustes.get("ruta_partes", "Partes_Generados"), self.ajustes)
        if "BLOQUEADO" in r: return messagebox.showwarning("Cierra el PDF", r)
        if "ERROR" in r: return messagebox.showerror("Fallo", r)
        try:
            os.startfile(r)
        except AttributeError:
            import subprocess, sys
            subprocess.call(["open" if sys.platform == "darwin" else "xdg-open", r])
        emails = [j['email'] for j in self.ajustes['jefes'] if j['nombre'] in [self.dest1.get(), self.dest2.get()]]
        if self.env_v.get() and emails:
            if messagebox.askyesno("Confirmación", "¿Es correcto el PDF? Pulse SÍ para enviar."):
                self.btn_gen.configure(text="ENVIANDO...", state="disabled")
                threading.Thread(target=self.p_env, args=(r, emails)).start()
        else: messagebox.showinfo("Éxito", "Guardado localmente.")

    def p_env(self, r, emails):
        res = enviar_parte_pdf(self.ajustes.get("email_remitente"), self.ajustes.get("pass_remitente"), emails, r, datetime.datetime.now().strftime("%d-%m-%Y"))
        self.btn_gen.configure(text="GENERAR PARTE PDF", state="normal")
        if res == "EXITO": messagebox.showinfo("OK", "Enviado correctamente.")
        else: messagebox.showerror("Fallo de envío", res)

    def setup_conf(self):
        f_r = ctk.CTkFrame(self.tab_conf, fg_color=BLANCO, border_width=1); f_r.pack(pady=10, fill="x", padx=20)
        self.m_rem = ctk.CTkEntry(f_r, placeholder_text="Tu Correo", width=350); self.m_rem.pack(pady=5); self.m_rem.insert(0, self.ajustes.get("email_remitente", ""))
        self.p_rem = ctk.CTkEntry(f_r, placeholder_text="Pass Aplicación", width=350, show="*"); self.p_rem.pack(pady=5); self.p_rem.insert(0, self.ajustes.get("pass_remitente", ""))
        ctk.CTkButton(f_r, text="Guardar Credenciales", command=self.s_rem).pack(pady=10)
        f_rt = ctk.CTkFrame(self.tab_conf, fg_color=BLANCO, border_width=1); f_rt.pack(pady=10, fill="x", padx=20)
        self.c_row_file(f_rt, "PDF Personal:", "pdf_cuadrante")
        self.c_row_file(f_rt, "PDF Cabos 1º:", "pdf_cabos")
        self.c_row_dir(f_rt, "Carpeta Partes:", "ruta_partes")
        f_tj = ctk.CTkFrame(self.tab_conf, fg_color="transparent"); f_tj.pack(fill="x", pady=15, padx=20)
        ctk.CTkButton(f_tj, text="+ Añadir Jefe", fg_color="green", command=lambda: VentanaEditorJefe(self, self.save_j)).pack(side="right")
        self.sc_j = ctk.CTkScrollableFrame(self.tab_conf, fg_color=BLANCO, border_width=1); self.sc_j.pack(fill="both", expand=True, padx=20, pady=10); self.render_jefes()

    def c_row_file(self, m, t, k):
        r = ctk.CTkFrame(m, fg_color="transparent"); r.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(r, text=t, width=120, anchor="w").pack(side="left")
        lbl = ctk.CTkLabel(r, text=self.ajustes.get(k, ""), text_color="gray"); lbl.pack(side="left", expand=True)
        ctk.CTkButton(r, text="Seleccionar", width=80, command=lambda: self.sel_f(k, lbl)).pack(side="right")

    def c_row_dir(self, m, t, k):
        r = ctk.CTkFrame(m, fg_color="transparent"); r.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(r, text=t, width=120, anchor="w").pack(side="left")
        lbl = ctk.CTkLabel(r, text=self.ajustes.get(k, ""), text_color="gray"); lbl.pack(side="left", expand=True)
        ctk.CTkButton(r, text="Cambiar", width=80, command=lambda: self.sel_d(k, lbl)).pack(side="right")

    def sel_f(self, k, l):
        f = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if f: self.ajustes[k] = f; l.configure(text=f); config.guardar_ajustes(self.ajustes)

    def sel_d(self, k, l):
        d = filedialog.askdirectory(); 
        if d: self.ajustes[k] = d; l.configure(text=d); config.guardar_ajustes(self.ajustes)

    def setup_pers(self):
        f_t = ctk.CTkFrame(self.tab_pers, fg_color="transparent"); f_t.pack(fill="x", pady=10, padx=20)
        ctk.CTkButton(f_t, text="+ Añadir Personal", fg_color="green", command=lambda: VentanaEditorPersonal(self, self.save_p)).pack(side="right")
        self.sc_p = ctk.CTkScrollableFrame(self.tab_pers, fg_color=BLANCO, border_width=1); self.sc_p.pack(fill="both", expand=True, padx=20, pady=10); self.render_pers()
    def render_pers(self):
        for w in self.sc_p.winfo_children(): w.destroy()
        for p in self.ajustes.get("personal", []):
            item = ctk.CTkFrame(self.sc_p, fg_color="#F9F9F9"); item.pack(fill="x", pady=2, padx=5)
            ctk.CTkLabel(item, text=f"{p['empleo']} {p['nombre']}", width=350, anchor="w").pack(side="left", padx=15)
            ctk.CTkButton(item, text="X", fg_color="#C41E3A", width=40, command=lambda n=p['nombre']: self.del_e("personal", n)).pack(side="right", padx=5)
            ctk.CTkButton(item, text="Edit", fg_color="#555555", width=60, command=lambda d=p: VentanaEditorPersonal(self, self.save_p, d)).pack(side="right", padx=5)
    def render_jefes(self):
        for w in self.sc_j.winfo_children(): w.destroy()
        for j in self.ajustes.get("jefes", []):
            item = ctk.CTkFrame(self.sc_j, fg_color="#F9F9F9"); item.pack(fill="x", pady=2, padx=5)
            ctk.CTkLabel(item, text=f"{j['nombre']} ({j['email']})", anchor="w").pack(side="left", padx=15, expand=True)
            ctk.CTkButton(item, text="X", fg_color="#C41E3A", width=40, command=lambda n=j['nombre']: self.del_e("jefes", n)).pack(side="right", padx=5)
    def save_p(self, res, orig):
        if orig: self.ajustes["personal"] = [x for x in self.ajustes["personal"] if x["nombre"] != orig["nombre"]]
        self.ajustes["personal"].append(res); config.guardar_ajustes(self.ajustes); self.update_listas_ui(); self.render_pers()
    def save_j(self, res, orig):
        if orig: self.ajustes["jefes"] = [x for x in self.ajustes["jefes"] if x["nombre"] != orig["nombre"]]
        self.ajustes["jefes"].append(res); config.guardar_ajustes(self.ajustes); self.update_listas_ui(); self.render_jefes()
    def del_e(self, cat, nom):
        if messagebox.askyesno("Confirmar", "¿Eliminar?"):
            if cat == "personal":
                for p in self.ajustes["personal"]:
                    if p['nombre'] == nom and os.path.exists(p['firma']):
                        try:
                            os.remove(p['firma'])
                        except OSError:
                            pass
            self.ajustes[cat] = [x for x in self.ajustes[cat] if x['nombre'] != nom]
            config.guardar_ajustes(self.ajustes); self.update_listas_ui()
            if cat == "personal": self.render_pers()
            else: self.render_jefes()
    def s_rem(self):
        self.ajustes["email_remitente"], self.ajustes["pass_remitente"] = self.m_rem.get(), self.p_rem.get()
        config.guardar_ajustes(self.ajustes); messagebox.showinfo("OK", "Guardado.")
    def update_listas_ui(self):
        n = [""] + [f"{p['empleo']} {p['nombre']}" for p in self.ajustes.get("personal", [])]
        jl = [""] + [j['nombre'] for j in self.ajustes.get("jefes", [])]
        for cb in [self.gs_s, self.ref_s, self.gs_e, self.ref_e]: cb.configure(values=n)
        self.dest1.configure(values=jl); self.dest2.configure(values=jl)

    def auto_lectura_cuadrantes(self):
        h = datetime.datetime.now(); h_d = h.day
        ap = self.ajustes.get("pdf_cuadrante", "")
        aj = self.ajustes.get("pdf_cabos", "")
        if ap and os.path.exists(ap):
            try:
                with pdfplumber.open(ap) as pdf:
                    tabla = pdf.pages[0].extract_table()
                    c_h = -1; c_a = -1
                    for row in tabla[:4]:
                        for i, v in enumerate(row):
                            if v and str(h_d) == str(v).strip(): c_h = i
                            if v and str(h_d-1) == str(v).strip(): c_a = i
                    if c_h != -1:
                        for f in tabla:
                            t_h, t_a = str(f[c_h]).upper() if f[c_h] else "", str(f[c_a]).upper() if (c_a!=-1 and f[c_a]) else ""
                            for p in self.ajustes['personal']:
                                if son_la_misma_persona(f[0], p['nombre']):
                                    full = f"{p['empleo']} {p['nombre']}"
                                    if t_h == "S": self.gs_e.set(full)
                                    if t_a == "S": self.gs_s.set(full)
                                    if t_h == "R": self.ref_e.set(full)
                                    if t_a == "R": self.ref_s.set(full)
            except: pass
        if aj and os.path.exists(aj):
            try:
                with pdfplumber.open(aj) as pdf:
                    tabla = pdf.pages[0].extract_table()
                    c_d = -1
                    for r in tabla[:4]:
                        for i, v in enumerate(r):
                            if v and str(h_d) == str(v).strip(): c_d = i; break
                    if c_d != -1:
                        for f in tabla:
                            if f[c_d] and "S" in str(f[c_d]).upper():
                                for j in self.ajustes['jefes']:
                                    if son_la_misma_persona(f[0], j['nombre']):
                                        if not self.dest1.get(): self.dest1.set(j['nombre'])
                                        elif not self.dest2.get(): self.dest2.set(j['nombre'])
            except: pass

    def setup_ayuda(self):
        tb = ctk.CTkTextbox(self.tab_ayuda, font=("Arial", 14), wrap="word")
        tb.pack(fill="both", expand=True, padx=20, pady=20)
        texto = """
# GUÍA DE USO - SEGURIDAD LORETO

## 1. CONFIGURACIÓN INICIAL
* **Correo**: Introduce tu cuenta de Gmail y la contraseña de aplicación (16 caracteres).
* **Archivos**: Selecciona directamente el archivo PDF del cuadrante general y el cuadrante de Cabos 1º.
* **Guardado**: Selecciona la carpeta donde se almacenarán los Partes de Novedades generados.

## 2. GESTIÓN DE PERSONAL Y JEFES
* **Pestaña Personal**: Añade los datos y captura la firma digital. Requisito indispensable para que las firmas aparezcan en el PDF.
* **Pestaña Configuración (Cabos 1º)**: Añade los nombres y correos electrónicos de los destinatarios.

## 3. GENERACIÓN DEL PARTE
* **Auto-completado**: El programa lee los PDF seleccionados y asigna automáticamente al personal entrante (S u R hoy) y saliente (S u R ayer).
* **Destinatarios**: Se extraen automáticamente del cuadrante de Cabos 1º si están de servicio.
* **Relleno manual**: Completa patrullas, anomalías y novedades del día.

## 4. ENVÍO
* **Revisar PDF**: Al pulsar "Generar", se abrirá Adobe Acrobat o tu visor predeterminado.
* **Confirmar**: Tras revisar, pulsa "SÍ" en la ventana emergente para tramitar el correo.
* **Sin red o desmarcado**: El PDF se guardará localmente en la carpeta elegida.
        """
        tb.insert("0.0", texto)
        tb.configure(state="disabled")

    def crear_combo(self, m, t, r, c):
        ctk.CTkLabel(m, text=t).grid(row=r, column=c, padx=10, pady=5, sticky="e")
        cb = ctk.CTkComboBox(m, values=[""], width=220); cb.grid(row=r, column=c+1, padx=10, pady=5); return cb
    def crear_txt(self, m, tit, l):
        fr = ctk.CTkFrame(m, fg_color=BLANCO, border_width=1); fr.pack(side=l, fill="both", expand=True, padx=5)
        ctk.CTkLabel(fr, text=tit, text_color=ROJO_LORETO, font=("Arial", 11, "bold")).pack()
        t = ctk.CTkTextbox(fr, height=75, border_width=0); t.pack(fill="both", padx=5, pady=5); return t

if __name__ == "__main__": App().mainloop()