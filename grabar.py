import os
import sys
import time
import getpass
from datetime import datetime
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

def grabar_pantalla_examen():
    # 1. Usuario y ruta de salida
    usuario = getpass.getuser()
    directorio_salida = obtener_carpeta_videos_sistema()
    os.makedirs(directorio_salida, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"examen_{usuario}_{timestamp}.mp4"
    ruta_completa = os.path.join(directorio_salida, nombre_archivo)
    
    # 2. Obtener resolución nativa de la pantalla principal
    captura_inicial = ImageGrab.grab()
    ancho, alto = captura_inicial.size
    
    # 3. Configurar grabador de video a 1 FPS
    codec = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(ruta_completa, codec, 1.0, (ancho, alto))
    
    print(f"=== Grabación de Pantalla Iniciada ===")
    print(f"Usuario: {usuario}")
    print(f"Resolución: {ancho}x{alto}")
    print(f"Destino: {ruta_completa}")
    print("Para detener la grabación, presiona Ctrl+C en esta consola.")

    try:
        while True:
            inicio = time.time()
            
            # Capturar la pantalla completa
            img = ImageGrab.grab()
            
            # Convertir imagen PIL a matriz NumPy y cambiar de formato RGB a BGR (OpenCV)
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Escribir fotograma
            out.write(frame)
            
            # Ajustar la espera para asegurar 1 fotograma exacto por segundo
            transcurrido = time.time() - inicio
            tiempo_espera = max(0.0, 1.0 - transcurrido)
            time.sleep(tiempo_espera)

    except KeyboardInterrupt:
        print("\nDeteniendo grabación...")
    finally:
        out.release()
        print(f"Grabación guardada correctamente en:\n{ruta_completa}")

if __name__ == "__main__":
    grabar_pantalla_examen()