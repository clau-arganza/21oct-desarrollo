#--------------------------------
# python -m tkinter
#
# https://docs.python.org/3/library/tkinter.html
#
#--------------------------------

import tkinter as tk

# 1. Crear la ventana principal
root = tk.Tk()
root.title("Mi primera ventana")
root.geometry("300x200")

# 2. Agregar un widget (etiqueta)
etiqueta = tk.Label(root, text="¡Hola, Tkinter!")
etiqueta.pack(pady=20)

# 3. Iniciar el bucle de eventos
root.mainloop()
