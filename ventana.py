import tkinter as tk
from tkinter import messagebox

class VentanaRec:
    def __init__(self, root):
        self.root = root

        # Eliminar marco del sistema operativo
        self.root.overrideredirect(True)

        # Dimensiones reducidas
        self.root.geometry("140x45")

        # Color de fondo
        self.root.configure(bg="#1e1e1e")

        # MANTENER SIEMPRE ENCIMA (Topmost + Lift)
        self.root.attributes("-topmost", True)
        self.root.lift()

        # Etiqueta "Rec"
        self.label_rec = tk.Label(
            self.root,
            text="● Rec",
            font=("Arial", 11, "bold"),
            fg="#ff4d4d",
            bg="#1e1e1e"
        )
        self.label_rec.pack(side="left", padx=(15, 0), expand=True)

        # Botón para cerrar (✕)
        self.btn_cerrar = tk.Button(
            self.root,
            text="✕",
            font=("Arial", 10, "bold"),
            fg="#888888",
            bg="#1e1e1e",
            activeforeground="#ffffff",
            activebackground="#cc0000",
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self.confirmar_cierre
        )
        self.btn_cerrar.pack(side="right", padx=(0, 10))

        # Variables para desplazamiento
        self.offset_x = 0
        self.offset_y = 0

        # Eventos de arrastre
        for widget in (self.root, self.label_rec):
            widget.bind("<Button-1>", self.iniciar_arrastre)
            widget.bind("<B1-Motion>", self.arrastrar)

    def iniciar_arrastre(self, event):
        self.offset_x = event.x_root - self.root.winfo_x()
        self.offset_y = event.y_root - self.root.winfo_y()

    def arrastrar(self, event):
        x = event.x_root - self.offset_x
        y = event.y_root - self.offset_y
        self.root.geometry(f"+{x}+{y}")
        # Reforzar posición superior durante el movimiento
        self.root.lift()

    def confirmar_cierre(self):
        # Asegurar que el diálogo de confirmación quede por encima
        respuesta = messagebox.askyesno(
            "Confirmación", 
            "¿Deseas finalizar el examen?", 
            parent=self.root
        )
        if respuesta:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = VentanaRec(root)
    root.mainloop()