# 🎥 ExamenRecorder App

**ExamenRecorder App** es una aplicación liviana de escritorio desarrollada en **Python** con **Tkinter** y **OpenCV**, diseñada para supervisar y grabar la pantalla durante la realización de exámenes en línea o evaluaciones académicas.

La herramienta combina una interfaz minimalista flotante con un sistema de grabación **resistente a fallos (fail-safe)** y una conversión post-examen optimizada para generar archivos de vídeo con un peso extraordinariamente bajo.

## 🚀 Características Principales

* **📌 Interfaz Flotante Minimalista:**
  * Ventana flotante sin bordes, siempre visible (`topmost`), que se puede arrastrar libremente por cualquier zona de la pantalla.
  * Indicador visual de grabación activa (`● Rec`) y botón discreto para finalizar el examen.

* **🛡️ Grabación Resiliente a Fallos (Buffer AVI / MJPEG):**
  * Captura continua mediante `Pillow` y `OpenCV` guardando cada fotograma directamente en disco.
  * El contenedor `.avi` con códec Motion JPEG (`MJPG`) garantiza que el archivo sea **reproducible incluso si la aplicación se interrumpe abruptamente** (apagones, cierres forzados, etc.).

* **📉 Conversión y Compresión Ultra Ligera a MP4:**
  * Al finalizar la sesión, el sistema procesa el vídeo en un hilo secundario y genera una copia comprimida en formato `.mp4`.
  * **Optimización de tamaño:**
    * Ajuste de resolución objetivo (720p / 540p).
    * Opción de captura en **escala de grises** (ideal para interfaces de texto/exámenes).
    * Reducción del ratio de fotogramas por segundo (FPS) adaptado a contenido estático.
  * Mantiene intacto el archivo `.avi` original para mayor seguridad.

* **⏳ Ventana Emergente de Estado:**
  * Muestra la pantalla flotante *"Preparando vídeo..."* al finalizar el examen para informar al usuario de que la conversión está en curso.
  * La ventana y el proceso se cierran de forma completamente automática al terminar.

* **🔇 Sin Pista de Audio:**
  * Centrado exclusivamente en la captura de vídeo para optimizar los recursos del sistema y reducir el espacio de almacenamiento al mínimo.

## 🛠️ Requisitos del Sistema

* **Lenguaje:** Python 3.8 o superior.
* **Librerías necesarias:**
  ```bash
  pip install opencv-python numpy pillow pyinstaller
  ```
* *(Opcional)* **FFmpeg:** Si `ffmpeg` está disponible en el sistema o en la carpeta raíz del script, la aplicación aplicará compresión avanzada H.264 (`libx264`) para lograr tamaños aún más reducidos.

## 📦 Compilación a Ejecutable (.exe)

Puedes convertir el script de Python en un único archivo ejecutable de Windows para que funcione en cualquier ordenador sin necesidad de tener Python instalado.

### 1. Instalación de PyInstaller

Asegúrate de instalar PyInstaller en tu entorno:

```bash
pip install pyinstaller
```

### 2. Comando Estándar de Compilación

Para generar el archivo ejecutable `.exe` sin ventana de consola en segundo plano:

```bash
python -m PyInstaller --onefile --noconsole --name "GrabadorExamen" main.py
```

### 3. Compilación con Icono Personalizado

Si dispones del archivo de icono (`.ico`), puedes asignarlo al ejecutable durante la compilación:

```bash
python -m PyInstaller --onefile --icon=icono.ico --noconsole --name "GrabadorExamen" main.py
```

#### Explicación de los Parámetros:
* `--onefile`: Empaqueta todo el proyecto y sus dependencias en un único archivo `.exe`.
* `--noconsole`: Oculta la ventana de comandos/consola de fondo, dejando solo visible la interfaz gráfica de Tkinter.
* `--name "GrabadorExamen"`: Define el nombre final del archivo ejecutable.
* `--icon=icono.ico`: (Opcional) Asigna la imagen de icono personalizada al ejecutable.

> **Nota:** Tras ejecutar el comando, el archivo ejecutable compilado estará listo dentro de la carpeta `/dist/GrabadorExamen.exe`.

## 📁 Ubicación de las Grabaciones

Los vídeos (`.avi` y `.mp4`) se almacenan automáticamente en la carpeta oficial de **Vídeos** del usuario en el sistema operativo:

* **Windows:** `C:\Users\<Usuario>\Videos\`
* **Formato del nombre:** `examen_<Usuario>_YYYYMMDD_HHMMSS.mp4`

## ⚙️ Flujo de Trabajo de la Aplicación

1. **Inicio:** Se lanza la barra flotante `● Rec` y comienza inmediatamente la captura en segundo plano.
2. **Duración del Examen:** La grabación escribe fotogramas en tiempo real en el archivo `.avi`.
3. **Cierre:** Al pulsar el botón `✕`, la aplicación solicita confirmación.
4. **Procesamiento:** Se oculta la barra, aparece la ventana *"Preparando vídeo..."* y se ejecuta la compresión a `.mp4`.
5. **Finalización:** Se libera el archivo y la aplicación finaliza limpiamente.

## 📜 Licencia y Créditos

* **Icono de la Aplicación:** Icono diseñado y alojado en [loading.io](https://loading.io/icon/fllmzd), utilizado bajo la licencia Creative Commons Attribution (**CC BY**).
