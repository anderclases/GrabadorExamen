import os
import sys
import time
import getpass
import threading
import subprocess
import ctypes
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import cv2
import numpy as np
from PIL import ImageGrab

# CONFIGURACIÓN
INTERVALO_SEGUNDOS = 2.0  # Captura 1 fotograma cada 2 segundos (0.5 FPS)
ALTO_RESOLUCION_MP4 = 540 # Resolución vertical objetivo (540p)
ESCALA_DE_GRISES = True   # Convierte a blanco y negro para reducir espacio
ANCHO_VENTANA = 140
ALTO_VENTANA = 45

def obtener_carpeta_videos_sistema():
    """Obtiene la ruta oficial de la carpeta 'Vídeos' en Windows."""
    if sys.platform == "win32":
        try:
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
        self.arrastrando = False

        # Configuración de la ventana flotante sin bordes
        self.root.overrideredirect(True)
        self.root.geometry(f"{ANCHO_VENTANA}x{ALTO_VENTANA}")
        self.root.configure(bg="#1e1e1e")
        
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
            widget.bind("<ButtonRelease-1>", self.detener_arrastre)

        # Variables de control y rutas
        self.ruta_avi = None
        self.grabando = True
        self.hilo_grabacion = threading.Thread(target=self.grabar_pantalla, daemon=True)
        self.hilo_grabacion.start()

        # Configuración Topmost inicial y mantenimiento
        self.forzar_topmost()
        self._bucle_mantenimiento_topmost()

    def forzar_topmost(self):
        """Asegura que la ventana permanezca por encima de la barra de tareas de Windows."""
        self.root.attributes("-topmost", True)
        self.root.lift()
        if sys.platform == "win32":
            try:
                hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
                if not hwnd:
                    hwnd = self.root.winfo_id()
                # HWND_TOPMOST = -1, SWP_NOMOVE = 0x0002, SWP_NOSIZE = 0x0001, SWP_NOACTIVATE = 0x0010, SWP_SHOWWINDOW = 0x0040
                ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0010 | 0x0040)
            except Exception:
                pass

    def _bucle_mantenimiento_topmost(self):
        """Reaplica periódicamente la propiedad topmost solo cuando no se está arrastrando."""
        if self.grabando:
            if not self.arrastrando:
                self.forzar_topmost()
            self.root.after(500, self._bucle_mantenimiento_topmost)

    def iniciar_arrastre(self, event):
        self.arrastrando = True
        self.offset_x = event.x_root - self.root.winfo_x()
        self.offset_y = event.y_root - self.root.winfo_y()

    def detener_arrastre(self, event):
        self.arrastrando = False
        self.forzar_topmost()

    def arrastrar(self, event):
        x = event.x_root - self.offset_x
        y = event.y_root - self.offset_y

        ancho_pantalla = self.root.winfo_screenwidth()
        alto_pantalla = self.root.winfo_screenheight()

        # Restringir estrictamente dentro de los límites de la pantalla
        x = max(0, min(x, ancho_pantalla - ANCHO_VENTANA))
        y = max(0, min(y, alto_pantalla - ALTO_VENTANA))

        self.root.geometry(f"+{x}+{y}")

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

        fps_grabacion = 1.0 / INTERVALO_SEGUNDOS
        codec = cv2.VideoWriter_fourcc(*'MJPG')
        out = cv2.VideoWriter(self.ruta_avi, codec, fps_grabacion, (ancho, alto))

        try:
            while self.grabando:
                inicio = time.time()

                img = ImageGrab.grab()
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                if ESCALA_DE_GRISES:
                    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    frame = cv2.cvtColor(gris, cv2.COLOR_GRAY2BGR)

                frame = cv2.resize(frame, (ancho, alto))
                out.write(frame)

                transcurrido = time.time() - inicio
                tiempo_espera = max(0.0, INTERVALO_SEGUNDOS - transcurrido)
                time.sleep(tiempo_espera)
        finally:
            out.release()

    def convertir_avi_a_mp4_ultraligero(self, ruta_avi, ruta_mp4):
        """Convierte a MP4 aplicando escala 540p y compresión optimizada."""
        cap = cv2.VideoCapture(ruta_avi)
        if not cap.isOpened():
            return

        fps = cap.get(cv2.CAP_PROP_FPS) or (1.0 / INTERVALO_SEGUNDOS)
        ancho_orig = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        alto_orig = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        alto_nuevo = ALTO_RESOLUCION_MP4
        if alto_orig > 0:
            ancho_nuevo = (int(ancho_orig * (float(alto_nuevo) / alto_orig)) // 2) * 2
        else:
            ancho_nuevo = 960

        exe_ffmpeg = "ffmpeg.exe" if os.path.exists("ffmpeg.exe") else "ffmpeg"

        comando_ffmpeg = [
            exe_ffmpeg, '-y', '-i', ruta_avi,
            '-vf', f'scale={ancho_nuevo}:{alto_nuevo}',
            '-vcodec', 'libx264',
            '-crf', '34',
            '-preset', 'faster',
            '-pix_fmt', 'yuv420p',
            ruta_mp4
        ]

        try:
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            subprocess.run(
                comando_ffmpeg,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo
            )
            cap.release()
            return
        except Exception:
            pass

        codec_mp4 = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(ruta_mp4, codec_mp4, fps, (ancho_nuevo, alto_nuevo))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame_resized = cv2.resize(frame, (ancho_nuevo, alto_nuevo), interpolation=cv2.INTER_AREA)
            out.write(frame_resized)

        cap.release()
        out.release()

    def _procesar_conversion(self, ventana_espera):
        if self.hilo_grabacion.is_alive():
            self.hilo_grabacion.join()

        if self.ruta_avi and os.path.exists(self.ruta_avi):
            ruta_mp4 = os.path.splitext(self.ruta_avi)[0] + ".mp4"
            self.convertir_avi_a_mp4_ultraligero(self.ruta_avi, ruta_mp4)

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
            self.root.withdraw()

            ventana_espera = tk.Toplevel()
            ventana_espera.overrideredirect(True)
            ventana_espera.geometry("260x90")
            ventana_espera.configure(bg="#1e1e1e")
            ventana_espera.attributes("-topmost", True)

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
                text="Comprimiendo archivo MP4...",
                font=("Arial", 9),
                fg="#aaaaaa",
                bg="#1e1e1e"
            )
            label_sub.pack(pady=(0, 15))

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