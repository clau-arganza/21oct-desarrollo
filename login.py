import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageSequence
from pathlib import Path
import json
import hashlib
import secrets
import hmac
import re

import users_dict


# ---------- COLORES Y ARCHIVOS ----------

FONDO = "#3DE3C9"
BLANCO = "#FFFFFF"
NEGRO = "#000000"

BASE = Path(__file__).resolve().parent
ARCHIVO_USUARIOS = BASE / "usuarios_registrados.json"
ARCHIVO_MEME = BASE / "meme.webp"
ARCHIVO_GIF = BASE / "saludo.gif"


# ---------- SEGURIDAD Y ALMACENAMIENTO ----------

def crear_hash(texto):
    sal = secrets.token_hex(16)

    resultado = hashlib.pbkdf2_hmac(
        "sha256",
        texto.encode("utf-8"),
        bytes.fromhex(sal),
        200000
    )

    return {
        "sal": sal,
        "hash": resultado.hex()
    }


def comprobar_hash(texto, datos):
    resultado = hashlib.pbkdf2_hmac(
        "sha256",
        texto.encode("utf-8"),
        bytes.fromhex(datos["sal"]),
        200000
    )

    return hmac.compare_digest(
        resultado.hex(),
        datos["hash"]
    )


def normalizar_respuesta(texto):
    return texto.strip().casefold()


def cargar_usuarios():
    if ARCHIVO_USUARIOS.exists():
        with ARCHIVO_USUARIOS.open(
            "r", encoding="utf-8"
        ) as archivo:
            datos = json.load(archivo)

        if not isinstance(datos, dict):
            raise ValueError(
                "El archivo de usuarios no tiene el formato esperado."
            )

        return datos

    return {}


def guardar_usuarios(datos):
    temporal = ARCHIVO_USUARIOS.with_suffix(".tmp")

    with temporal.open("w", encoding="utf-8") as archivo:
        json.dump(
            datos,
            archivo,
            ensure_ascii=False,
            indent=4
        )

    temporal.replace(ARCHIVO_USUARIOS)


def requisitos_password(password):
    return {
        "Al menos 10 caracteres": len(password) >= 10,
        "Una letra mayúscula": bool(
            re.search(r"[A-Z]", password)
        ),
        "Una letra minúscula": bool(
            re.search(r"[a-z]", password)
        ),
        "Un número": bool(
            re.search(r"\d", password)
        ),
        "Un símbolo, por ejemplo ! @ #": any(
            not caracter.isalnum()
            and not caracter.isspace()
            for caracter in password
        )
    }


# ---------- APLICACIÓN ----------

class Login:
    def __init__(self, ventana):
        self.window = ventana
        self.window.title("Acceso al programa")
        self.window.configure(bg=FONDO)
        self.window.resizable(True, True)

        self.animacion = None
        self.frames_gif = []
        self.duraciones_gif = []
        self.imagen_meme = None

        self.usuarios = cargar_usuarios()

        self.window.protocol(
            "WM_DELETE_WINDOW",
            self.cerrar
        )

        self.mostrar_login()

    # ---------- PANTALLAS ----------

    def detener_animacion(self):
        if self.animacion is not None:
            self.window.after_cancel(self.animacion)
            self.animacion = None

    def cerrar(self):
        self.detener_animacion()
        self.window.destroy()

    def limpiar(self):
        self.detener_animacion()

        for elemento in self.window.winfo_children():
            elemento.destroy()

        self.frames_gif = []
        self.duraciones_gif = []
        self.imagen_meme = None

    def pantalla(self, titulo, subtitulo="", ancho=490, alto=650):
        self.limpiar()

        # Ajusta el tamaño a la pantalla del ordenador.
        ancho = min(
            ancho,
            max(350, self.window.winfo_screenwidth() - 60)
        )
        alto = min(
            alto,
            max(400, self.window.winfo_screenheight() - 100)
        )

        self.window.geometry(f"{ancho}x{alto}")

        # Contenido desplazable para que no se corten los campos.
        contenedor = tk.Frame(self.window, bg=FONDO)
        contenedor.pack(fill="both", expand=True)

        barra = tk.Scrollbar(contenedor)
        barra.pack(side="right", fill="y")

        canvas = tk.Canvas(
            contenedor,
            bg=FONDO,
            highlightthickness=0,
            yscrollcommand=barra.set
        )
        canvas.pack(side="left", fill="both", expand=True)

        barra.configure(command=canvas.yview)

        pagina = tk.Frame(canvas, bg=FONDO)

        ventana_canvas = canvas.create_window(
            (0, 0),
            window=pagina,
            anchor="nw"
        )

        pagina.bind(
            "<Configure>",
            lambda event: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.bind(
            "<Configure>",
            lambda event: canvas.itemconfigure(
                ventana_canvas,
                width=event.width
            )
        )

        def rueda(event):
            if event.delta:
                paso = -1 if event.delta > 0 else 1
                canvas.yview_scroll(paso, "units")

        # Enlaza la rueda a los elementos de la pantalla actual.
        def enlazar_rueda(widget):
            widget.bind("<MouseWheel>", rueda, add="+")
            widget.bind(
                "<Button-4>",
                lambda event: canvas.yview_scroll(-1, "units"),
                add="+"
            )
            widget.bind(
                "<Button-5>",
                lambda event: canvas.yview_scroll(1, "units"),
                add="+"
            )

            for hijo in widget.winfo_children():
                enlazar_rueda(hijo)

        # Se ejecuta cuando ya se han creado los campos.
        pagina.after_idle(lambda: enlazar_rueda(contenedor))

        tk.Label(
            pagina,
            text=titulo,
            font=("Arial", 20, "bold"),
            bg=FONDO,
            fg=NEGRO,
            wraplength=ancho - 60
        ).pack(pady=(25, 8))

        if subtitulo:
            tk.Label(
                pagina,
                text=subtitulo,
                font=("Arial", 11),
                bg=FONDO,
                fg=NEGRO,
                wraplength=ancho - 70,
                justify="center"
            ).pack(pady=(0, 12))

        contenido = tk.Frame(pagina, bg=FONDO)
        contenido.pack(
            fill="x",
            padx=25,
            pady=(0, 25)
        )

        return contenido

    # ---------- ELEMENTOS VISUALES ----------

    def etiqueta(self, padre, texto):
        tk.Label(
            padre,
            text=texto,
            font=("Arial", 11),
            bg=FONDO,
            fg=NEGRO
        ).pack(anchor="w", pady=(10, 4))

    def campo(self, padre, texto, variable=None):
        self.etiqueta(padre, texto)

        entrada = tk.Entry(
            padre,
            textvariable=variable,
            font=("Arial", 12),
            bg=BLANCO,
            fg=NEGRO,
            insertbackground=NEGRO,
            selectbackground=NEGRO,
            selectforeground=BLANCO,
            relief="solid",
            bd=1
        )
        entrada.pack(fill="x", ipady=6)

        return entrada

    def campo_password(self, padre, texto, variable=None):
        self.etiqueta(padre, texto)

        fila = tk.Frame(padre, bg=FONDO)
        fila.pack(fill="x")

        entrada = tk.Entry(
            fila,
            textvariable=variable,
            show="•",
            font=("Arial", 12),
            bg=BLANCO,
            fg=NEGRO,
            insertbackground=NEGRO,
            selectbackground=NEGRO,
            selectforeground=BLANCO,
            relief="solid",
            bd=1
        )
        entrada.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=6
        )

        # Ojito pequeño dibujado en negro.
        ojo = tk.Canvas(
            fila,
            width=32,
            height=30,
            bg=FONDO,
            highlightthickness=0,
            cursor="hand2",
            takefocus=True
        )
        ojo.pack(side="right", padx=(6, 0))

        def dibujar_ojo(visible):
            ojo.delete("all")

            ojo.create_oval(
                3, 8, 29, 23,
                outline=NEGRO,
                width=2
            )

            ojo.create_oval(
                12, 11, 20, 20,
                fill=NEGRO,
                outline=NEGRO
            )

            if visible:
                ojo.create_line(
                    4, 27, 28, 4,
                    fill=NEGRO,
                    width=2
                )

        def alternar(event=None):
            estaba_visible = entrada.cget("show") == ""

            entrada.configure(
                show="•" if estaba_visible else ""
            )

            dibujar_ojo(not estaba_visible)

        dibujar_ojo(False)

        ojo.bind("<Button-1>", alternar)
        ojo.bind("<Return>", alternar)
        ojo.bind("<space>", alternar)

        return entrada

    def boton(self, padre, texto, accion):
        tk.Button(
            padre,
            text=texto,
            command=accion,
            font=("Arial", 12, "bold"),
            bg=BLANCO,
            fg=NEGRO,
            activebackground=BLANCO,
            activeforeground=NEGRO,
            highlightbackground=FONDO,
            pady=8,
            cursor="hand2"
        ).pack(fill="x", pady=(18, 5))

    def enlace(self, padre, texto, accion):
        enlace = tk.Label(
            padre,
            text=texto,
            font=("Arial", 10, "underline"),
            fg=NEGRO,
            bg=FONDO,
            cursor="hand2",
            takefocus=True
        )
        enlace.pack(pady=5)

        enlace.bind(
            "<Button-1>",
            lambda event: accion()
        )
        enlace.bind(
            "<Return>",
            lambda event: accion()
        )
        enlace.bind(
            "<space>",
            lambda event: accion()
        )

    def indicador_seguridad(self, padre, variable):
        estado = tk.Label(
            padre,
            text="Seguridad: sin contraseña",
            font=("Arial", 11, "bold"),
            bg=FONDO,
            fg=NEGRO
        )
        estado.pack(anchor="w", pady=(10, 4))

        etiquetas = {}

        for texto in requisitos_password(""):
            etiqueta = tk.Label(
                padre,
                text=f"○ {texto}",
                font=("Arial", 10),
                bg=FONDO,
                fg=NEGRO
            )
            etiqueta.pack(anchor="w")
            etiquetas[texto] = etiqueta

        def actualizar(*args):
            password = variable.get()
            requisitos = requisitos_password(password)
            puntos = sum(requisitos.values())

            if not password:
                nivel = "Sin contraseña"
            elif puntos <= 2:
                nivel = "Débil"
            elif puntos < 5:
                nivel = "Media"
            else:
                nivel = "Fuerte"

            estado.configure(
                text=f"Seguridad: {nivel}"
            )

            for requisito, cumple in requisitos.items():
                simbolo = "✓" if cumple else "○"

                etiquetas[requisito].configure(
                    text=f"{simbolo} {requisito}"
                )

        variable.trace_add("write", actualizar)
        actualizar()

    # ---------- MEME ----------

    def mostrar_meme(self, padre):
        try:
            with Image.open(ARCHIVO_MEME) as original:
                imagen = original.convert("RGB")

            # Recorta los márgenes del meme enviado.
            ancho, alto = imagen.size

            imagen = imagen.crop((
                int(ancho * 0.25),
                int(alto * 0.17),
                int(ancho * 0.75),
                int(alto * 0.83)
            ))

            imagen.thumbnail(
                (190, 310),
                Image.Resampling.LANCZOS
            )

            self.imagen_meme = ImageTk.PhotoImage(imagen)

            tk.Label(
                padre,
                image=self.imagen_meme,
                bg=FONDO
            ).pack(pady=(30, 12))

        except OSError:
            tk.Label(
                padre,
                text="No se pudo abrir meme.webp",
                font=("Arial", 10),
                bg=FONDO,
                fg=NEGRO,
                wraplength=190
            ).pack(pady=(30, 12))

        tk.Label(
            padre,
            text="ALTO AHÍ\n\n"
                 "Primero regístrese,\n"
                 "ciudadano.",
            font=("Arial", 12, "bold"),
            bg=FONDO,
            fg=NEGRO,
            justify="center"
        ).pack()

    # ---------- USUARIOS ANTIGUOS ----------

    def usuario_antiguo(self, nombre):
        for usuario in users_dict.users:
            if usuario["nickname"] == nombre:
                return usuario

        return None

    # ---------- INICIO DE SESIÓN ----------

    def mostrar_login(self):
        marco = self.pantalla(
            "INICIAR SESIÓN",
            "Introduce tu usuario y contraseña."
        )

        self.usuario = self.campo(marco, "Usuario")

        self.password = self.campo_password(
            marco,
            "Contraseña"
        )

        self.usuario.focus_set()

        self.password.bind(
            "<Return>",
            lambda event: self.iniciar_sesion()
        )

        self.boton(
            marco,
            "Acceder",
            self.iniciar_sesion
        )

        self.enlace(
            marco,
            "Crear una cuenta",
            self.mostrar_registro
        )

        self.enlace(
            marco,
            "He olvidado mi contraseña",
            self.mostrar_recuperacion
        )

    def iniciar_sesion(self):
        nombre = self.usuario.get().strip()
        password = self.password.get()

        if not nombre or not password:
            messagebox.showwarning(
                "Faltan datos",
                "Introduce usuario y contraseña."
            )
            return

        if nombre in self.usuarios:
            correcto = comprobar_hash(
                password,
                self.usuarios[nombre]["password"]
            )
        else:
            antiguo = self.usuario_antiguo(nombre)

            correcto = (
                antiguo is not None
                and antiguo["passw"] == password
            )

        if correcto:
            self.mostrar_bienvenida(nombre)
        else:
            messagebox.showerror(
                "Acceso incorrecto",
                "El usuario o la contraseña no son correctos."
            )

    def mostrar_bienvenida(self, nombre):
        marco = self.pantalla(
            "¡Bienvenido!",
            f"Has iniciado sesión como {nombre}."
        )

        self.boton(
            marco,
            "Cerrar sesión",
            self.mostrar_login
        )

    # ---------- REGISTRO ----------

    def mostrar_registro(self):
        contenido = self.pantalla(
            "CREAR CUENTA",
            ancho=760,
            alto=740
        )

        # Formulario a la izquierda.
        marco = tk.Frame(contenido, bg=FONDO)
        marco.pack(
            side="left",
            fill="x",
            expand=True,
            anchor="n"
        )

        # Meme a la derecha.
        lateral = tk.Frame(contenido, bg=FONDO)
        lateral.pack(
            side="right",
            padx=(25, 0),
            anchor="n"
        )

        self.mostrar_meme(lateral)

        usuario = self.campo(
            marco,
            "Nombre de usuario"
        )

        password_var = tk.StringVar()

        self.campo_password(
            marco,
            "Contraseña",
            password_var
        )

        self.indicador_seguridad(
            marco,
            password_var
        )

        confirmacion = self.campo_password(
            marco,
            "Repite la contraseña"
        )

        pregunta = self.campo(
            marco,
            "Escribe una pregunta de recuperación"
        )

        respuesta = self.campo_password(
            marco,
            "Respuesta secreta"
        )

        def registrar():
            nombre = usuario.get().strip()
            password = password_var.get()
            pregunta_texto = pregunta.get().strip()

            respuesta_texto = normalizar_respuesta(
                respuesta.get()
            )

            if not all([
                nombre,
                password,
                confirmacion.get(),
                pregunta_texto,
                respuesta_texto
            ]):
                messagebox.showwarning(
                    "Faltan datos",
                    "Completa todos los campos."
                )
                return

            if (
                nombre in self.usuarios
                or self.usuario_antiguo(nombre) is not None
            ):
                messagebox.showerror(
                    "Usuario existente",
                    "Ese nombre de usuario ya está registrado."
                )
                return

            if not all(
                requisitos_password(password).values()
            ):
                messagebox.showwarning(
                    "Contraseña insuficiente",
                    "La contraseña debe cumplir "
                    "todos los requisitos."
                )
                return

            if password != confirmacion.get():
                messagebox.showerror(
                    "Contraseñas distintas",
                    "Las contraseñas no coinciden."
                )
                return

            nuevos = dict(self.usuarios)

            nuevos[nombre] = {
                "password": crear_hash(password),
                "pregunta": pregunta_texto,
                "respuesta": crear_hash(respuesta_texto)
            }

            if self.persistir(nuevos):
                self.mostrar_registro_correcto(nombre)

        self.boton(
            marco,
            "Registrarme",
            registrar
        )

        self.enlace(
            marco,
            "Volver al inicio",
            self.mostrar_login
        )

        usuario.focus_set()

    # ---------- REGISTRO COMPLETADO Y GIF ----------

    def mostrar_registro_correcto(self, nombre):
        marco = self.pantalla(
            "¡YA ERES DE LOS NUESTROS!",
            f"Tu cuenta se ha creado correctamente, {nombre}.",
            alto=650
        )

        etiqueta_gif = tk.Label(
            marco,
            bg=FONDO,
            fg=NEGRO
        )
        etiqueta_gif.pack(pady=25)

        try:
            with Image.open(ARCHIVO_GIF) as gif:
                for frame in ImageSequence.Iterator(gif):
                    duracion = frame.info.get(
                        "duration", 100
                    )

                    imagen = frame.convert("RGBA")

                    imagen.thumbnail(
                        (330, 300),
                        Image.Resampling.LANCZOS
                    )

                    self.frames_gif.append(
                        ImageTk.PhotoImage(imagen)
                    )

                    self.duraciones_gif.append(
                        max(20, int(duracion or 100))
                    )

        except (OSError, ValueError):
            self.frames_gif = []
            self.duraciones_gif = []

            etiqueta_gif.configure(
                text="Tu cuenta está lista.\n"
                     "No se pudo abrir saludo.gif.",
                font=("Arial", 13),
                wraplength=350
            )

        def reproducir(indice=0):
            etiqueta_gif.configure(
                image=self.frames_gif[indice]
            )

            siguiente = (
                indice + 1
            ) % len(self.frames_gif)

            self.animacion = self.window.after(
                self.duraciones_gif[indice],
                reproducir,
                siguiente
            )

        if self.frames_gif:
            reproducir()

        tk.Label(
            marco,
            text="El comité de bienvenida te saluda.",
            font=("Arial", 12),
            bg=FONDO,
            fg=NEGRO
        ).pack(pady=10)

        self.boton(
            marco,
            "Iniciar sesión",
            self.mostrar_login
        )

    # ---------- RECUPERACIÓN ----------

    def mostrar_recuperacion(self):
        marco = self.pantalla(
            "RECUPERAR ACCESO",
            "Introduce tu usuario para cambiar la contraseña "
            "mediante tu pregunta de seguridad."
        )

        usuario = self.campo(
            marco,
            "Usuario"
        )

        def continuar():
            nombre = usuario.get().strip()
            datos = self.usuarios.get(nombre)

            if not datos or "respuesta" not in datos:
                messagebox.showerror(
                    "Recuperación no disponible",
                    "Este usuario no existe o no tiene "
                    "configurada una pregunta de recuperación."
                )
                return

            self.mostrar_pregunta(nombre)

        self.boton(
            marco,
            "Continuar",
            continuar
        )

        self.enlace(
            marco,
            "Volver al inicio",
            self.mostrar_login
        )

        usuario.focus_set()

    def mostrar_pregunta(self, nombre):
        datos = self.usuarios[nombre]

        marco = self.pantalla(
            "PREGUNTA DE SEGURIDAD",
            datos["pregunta"]
        )

        respuesta = self.campo_password(
            marco,
            "Tu respuesta"
        )

        def verificar():
            texto = normalizar_respuesta(
                respuesta.get()
            )

            if comprobar_hash(
                texto,
                datos["respuesta"]
            ):
                self.mostrar_nueva_password(nombre)
            else:
                messagebox.showerror(
                    "Respuesta incorrecta",
                    "La respuesta no coincide."
                )

        self.boton(
            marco,
            "Verificar respuesta",
            verificar
        )

        self.enlace(
            marco,
            "Volver al inicio",
            self.mostrar_login
        )

        respuesta.focus_set()

    def mostrar_nueva_password(self, nombre):
        marco = self.pantalla(
            "NUEVA CONTRASEÑA",
            "Elige una nueva contraseña para tu cuenta."
        )

        password_var = tk.StringVar()

        entrada = self.campo_password(
            marco,
            "Nueva contraseña",
            password_var
        )

        self.indicador_seguridad(
            marco,
            password_var
        )

        confirmacion = self.campo_password(
            marco,
            "Repite la nueva contraseña"
        )

        def cambiar():
            password = password_var.get()

            if not all(
                requisitos_password(password).values()
            ):
                messagebox.showwarning(
                    "Contraseña insuficiente",
                    "Cumple todos los requisitos de seguridad."
                )
                return

            if password != confirmacion.get():
                messagebox.showerror(
                    "Contraseñas distintas",
                    "Las contraseñas no coinciden."
                )
                return

            nuevos = dict(self.usuarios)

            nuevos[nombre] = {
                **self.usuarios[nombre],
                "password": crear_hash(password)
            }

            if self.persistir(nuevos):
                messagebox.showinfo(
                    "Contraseña actualizada",
                    "Ya puedes acceder con tu nueva contraseña."
                )

                self.mostrar_login()

        self.boton(
            marco,
            "Guardar contraseña",
            cambiar
        )

        self.enlace(
            marco,
            "Volver al inicio",
            self.mostrar_login
        )

        entrada.focus_set()

    # ---------- GUARDAR CAMBIOS ----------

    def persistir(self, nuevos):
        try:
            guardar_usuarios(nuevos)

        except OSError as error:
            messagebox.showerror(
                "No se pudo guardar",
                "No se han podido guardar los cambios:\n"
                f"{error}"
            )
            return False

        self.usuarios = nuevos
        return True


# ---------- EJECUCIÓN ----------

if __name__ == "__main__":
    ventana = tk.Tk()

    try:
        aplicacion = Login(ventana)

    except (OSError, ValueError) as error:
        messagebox.showerror(
            "Error al cargar usuarios",
            "No se ha podido leer el archivo de usuarios:\n"
            f"{error}"
        )
        ventana.destroy()

    else:
        ventana.mainloop()