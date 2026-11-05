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

        # Configuración de la ventana flotante sin bordes
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

        # Variables de control y seguimiento de archivos
        self.ruta_avi = None
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
        """Graba fotogramas continuos en formato AVI / MJPEG resistente a fallos."""
        usuario = getpass.getuser()
        directorio_salida = obtener_carpeta_videos_sistema()
        os.makedirs(directorio_salida, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"examen_{usuario}_{timestamp}.avi"
        self.ruta_avi = os.path.join(directorio_salida, nombre_archivo)

        captura_inicial = ImageGrab.grab()
        ancho, alto = captura_inicial.size
        ancho = (ancho // 2) * 2
        alto = (alto // 2) * 2

        # Códec Motion JPEG (resiliente a cortes repentinos)
        codec = cv2.VideoWriter_fourcc(*'MJPG')
        out = cv2.VideoWriter(self.ruta_avi, codec, 1.0, (ancho, alto))

        try:
            while self.grabando:
                inicio = time.time()

                img = ImageGrab.grab()
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                frame = cv2.resize(frame, (ancho, alto))

                # Escribe cada fotograma en el disco de inmediato
                out.write(frame)

                transcurrido = time.time() - inicio
                tiempo_espera = max(0.0, 1.0 - transcurrido)
                time.sleep(tiempo_espera)
        finally:
            out.release()

    def convertir_avi_a_mp4(self, ruta_avi, ruta_mp4):
        """Re-codifica el archivo AVI a MP4 mediante OpenCV sin eliminar el original."""
        cap = cv2.VideoCapture(ruta_avi)
        if not cap.isOpened():
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 1.0
        ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        alto = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        codec_mp4 = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(ruta_mp4, codec_mp4, fps, (ancho, alto))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)

        cap.release()
        out.release()

    def _procesar_conversion(self, ventana_espera):
        # 1. Espera a que la grabación finalice adecuadamente y libere el archivo AVI
        if self.hilo_grabacion.is_alive():
            self.hilo_grabacion.join()

        # 2. Convierte el archivo a formato MP4
        if self.ruta_avi and os.path.exists(self.ruta_avi):
            ruta_mp4 = os.path.splitext(self.ruta_avi)[0] + ".mp4"
            self.convertir_avi_a_mp4(self.ruta_avi, ruta_mp4)

        # 3. Cierra la ventana emergente y finaliza el programa Tkinter
        self.root.after(0, ventana_espera.destroy)
        self.root.after(0, self.root.destroy)

    def confirmar_cierre(self):
        respuesta = messagebox.askyesno(
            "Confirmación",
            "¿Deseas finalizar el examen?",
            parent=self.root
        )
        if respuesta:
            self.grabando = False
            self.root.withdraw()  # Oculta la ventana flotante de grabación

            # Crear ventana centrar emergente de "Preparando vídeo..."
            ventana_espera = tk.Toplevel()
            ventana_espera.overrideredirect(True)
            ventana_espera.geometry("260x90")
            ventana_espera.configure(bg="#1e1e1e")
            ventana_espera.attributes("-topmost", True)

            # Ubicar la ventana en el centro de la pantalla
            ancho_pantalla = ventana_espera.winfo_screenwidth()
            alto_pantalla = ventana_espera.winfo_screenheight()
            pos_x = (ancho_pantalla // 2) - 130
            pos_y = (alto_pantalla // 2) - 45
            ventana_espera.geometry(f"+{pos_x}+{pos_y}")

            label_estado = tk.Label(
                ventana_espera,
                text="Preparando vídeo...",
                font=("Arial", 11, "bold"),
                fg="#ffffff",
                bg="#1e1e1e"
            )
            label_estado.pack(expand=True, pady=(15, 2))

            label_sub = tk.Label(
                ventana_espera,
                text="Por favor, espere...",
                font=("Arial", 9),
                fg="#aaaaaa",
                bg="#1e1e1e"
            )
            label_sub.pack(pady=(0, 15))

            # Ejecutar conversión en un hilo independiente para no congelar la GUI
            hilo_conversion = threading.Thread(
                target=self._procesar_conversion,
                args=(ventana_espera,),
                daemon=True
            )
            hilo_conversion.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExamenRecorderApp(root)
    root.mainloop()