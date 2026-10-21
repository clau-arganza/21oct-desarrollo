import tkinter as tk
from tkinter import messagebox
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
            return json.load(archivo)

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
        self.window.geometry("490x740")
        self.window.resizable(False, False)
        self.window.configure(bg=FONDO)

        self.usuarios = cargar_usuarios()
        self.mostrar_login()

    # ---------- ELEMENTOS VISUALES ----------

    def limpiar(self):
        for elemento in self.window.winfo_children():
            elemento.destroy()

    def pantalla(self, titulo, subtitulo=""):
        self.limpiar()

        tk.Label(
            self.window,
            text=titulo,
            font=("Arial", 21, "bold"),
            bg=FONDO,
            fg=NEGRO
        ).pack(pady=(25, 8))

        if subtitulo:
            tk.Label(
                self.window,
                text=subtitulo,
                font=("Arial", 10),
                bg=FONDO,
                fg=NEGRO,
                wraplength=410
            ).pack(pady=(0, 12))

        contenido = tk.Frame(
            self.window,
            bg=FONDO
        )
        contenido.pack(fill="x", padx=35)

        return contenido

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

        fila = tk.Frame(
            padre,
            bg=FONDO
        )
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

        # Ojito dibujado en negro para evitar emojis de colores
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
            visible = entrada.cget("show") == ""
            entrada.configure(show="•" if visible else "")
            dibujar_ojo(not visible)

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
        # Label para mantener el fondo turquesa también en Mac
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

        enlace.bind("<Button-1>", lambda event: accion())
        enlace.bind("<Return>", lambda event: accion())
        enlace.bind("<space>", lambda event: accion())

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

            estado.configure(text=f"Seguridad: {nivel}")

            for requisito, cumple in requisitos.items():
                simbolo = "✓" if cumple else "○"

                etiquetas[requisito].configure(
                    text=f"{simbolo} {requisito}"
                )

        variable.trace_add("write", actualizar)
        actualizar()

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

        self.usuario = self.campo(
            marco,
            "Usuario"
        )

        self.password = self.campo_password(
            marco,
            "Contraseña"
        )

        self.usuario.focus_set()

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
        marco = self.pantalla("CREAR CUENTA")

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
                    "La contraseña debe cumplir todos "
                    "los requisitos."
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
                messagebox.showinfo(
                    "Registro completado",
                    "Tu cuenta se ha creado. "
                    "Ya puedes iniciar sesión."
                )
                self.mostrar_login()

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

            if comprobar_hash(texto, datos["respuesta"]):
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