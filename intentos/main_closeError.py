import os
import sys
import time
import getpass
import threading
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import cv2
import numpy as np
from PIL import ImageGrab

def obtener_carpeta_videos_sistema():
    """Obtiene la ruta oficial de la carpeta 'Vídeos' en Windows."""
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes
            buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
            ctypes.windll.shell32.SHGetFolderPathW(None, 14, None, 0, buf)
            if buf.value:
                return buf.value
        except Exception:
            pass
    return os.path.join(os.path.expanduser("~"), "Videos")

class ExamenRecorderApp:
    def __init__(self, root):
        self.root = root

        # Configuración de la ventana flotante sin borde ni título
        self.root.overrideredirect(True)
        self.root.geometry("140x45")
        self.root.configure(bg="#1e1e1e")
        self.root.attributes("-topmost", True)
        self.root.lift()

        # Etiqueta "● Rec"
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

        # Eventos para arrastrar la ventana
        self.offset_x = 0
        self.offset_y = 0
        for widget in (self.root, self.label_rec):
            widget.bind("<Button-1>", self.iniciar_arrastre)
            widget.bind("<B1-Motion>", self.arrastrar)

        # Control del hilo de grabación secundaria
        self.grabando = True
        self.hilo_grabacion = threading.Thread(target=self.grabar_pantalla, daemon=True)
        self.hilo_grabacion.start()

    def iniciar_arrastre(self, event):
        self.offset_x = event.x_root - self.root.winfo_x()
        self.offset_y = event.y_root - self.root.winfo_y()

    def arrastrar(self, event):
        x = event.x_root - self.offset_x
        y = event.y_root - self.offset_y
        self.root.geometry(f"+{x}+{y}")
        self.root.lift()

    def grabar_pantalla(self):
        """Bucle de captura de pantalla a 1 FPS con dimensiones garantizadas."""
        usuario = getpass.getuser()
        directorio_salida = obtener_carpeta_videos_sistema()
        os.makedirs(directorio_salida, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # NOTA: Si el reproductor por defecto de Windows falla con MP4, 
        # cambia la extensión a ".avi" y el codec a cv2.VideoWriter_fourcc(*'XVID')
        nombre_archivo = f"examen_{usuario}_{timestamp}.mp4"
        ruta_completa = os.path.join(directorio_salida, nombre_archivo)

        captura_inicial = ImageGrab.grab()
        ancho, alto = captura_inicial.size

        # CORRECCIÓN 1: Forzar dimensiones a números PARES exactos
        ancho = (ancho // 2) * 2
        alto = (alto // 2) * 2

        codec = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(ruta_completa, codec, 1.0, (ancho, alto))

        print(f"=== Grabación Iniciada ===")
        print(f"Usuario: {usuario}")
        print(f"Resolución ajustada: {ancho}x{alto}")
        print(f"Destino: {ruta_completa}")

        try:
            while self.grabando:
                inicio = time.time()

                img = ImageGrab.grab()
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                # CORRECCIÓN 2: Ajustar cada fotograma a las dimensiones exactas del códec
                frame = cv2.resize(frame, (ancho, alto))
                out.write(frame)

                transcurrido = time.time() - inicio
                tiempo_espera = max(0.0, 1.0 - transcurrido)
                time.sleep(tiempo_espera)
        finally:
            # CORRECCIÓN 3: Escribir metadatos y cerrar el contenedor de video correctamente
            out.release()
            print(f"\nGrabación finalizada y guardada en:\n{ruta_completa}")

    def confirmar_cierre(self):
        respuesta = messagebox.askyesno(
            "Confirmación",
            "¿Deseas finalizar el examen?",
            parent=self.root
        )
        if respuesta:
            self.grabando = False  # Detiene el bucle y ejecuta el out.release() en 'finally'
            time.sleep(0.5)        # Margen breve para escribir el archivo
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExamenRecorderApp(root)
    root.mainloop()