# 🎥 GrabadorExamen

Veyond nos permite vigilar durante el examen, pero presenta problemas a la hora de revisar un caso concreto, este programa nos sirve para que durante cada examen haya un vídeo único de cada equipo y facilitar la revisión.

El ejecutable es portable por lo que es fácil de activar. Las dos grabaciones se guardarán en la carpeta vídeos del sistema operativo.

[DESCARGAR aqui](https://github.com/anderclases/GrabadorExamen/releases/tag/1).

## Protocolo de uso recomendado.

* Aunque el resultado final sea muy ligero (un vídeo de 2 horas ronda los 70 megas), sigue siendo un problema para subir al Mooodle, por eso, estamos pidiendo que lo suban a una carpeta compartida de Google Drive.
* Además ambos vídeos deben de mantenerse en el equipo del alumno y no ser aliminados a no ser que haya un permiso explicito del profesorado.
* Para no saturar el Drive hay que subir el archivo comprimido, tiene formato `.mp4` y un peso notablemente más bajo.

## 🚀 Características Principales

* **📌 Interfaz Flotante:**
  * Ventana que se puede arrastrar libremente por cualquier zona de la pantalla.
  * Indicador visual de grabación activa (`● Rec`) y botón para finalizar el examen.

* **🛡️ Grabación Resistente a Fallos:**
  * Captura streaming en directo de la grabación y almacena el resultado en un archivo `.avi`. Garantiza que el archivo sea **reproducible incluso si la aplicación se interrumpe abruptamente** (apagones, cierres forzados, etc.).

* **📉 Conversión y Compresión Ultra Ligera a MP4:**
  * Al finalizar la sesión, el sistema procesa el vídeo en un hilo secundario y genera una copia comprimida en formato `.mp4`.
  * **Caracteristicas de la Optimización de tamaño:**
    * Ajuste de resolución objetivo (720p / 540p).
    * Opción de captura en **escala de grises** (ideal para interfaces de texto/exámenes).
    * Reducción del ratio de fotogramas por segundo (FPS) adaptado a contenido estático.
  * Mantiene intacto el archivo `.avi` original para mamtenerlo cómo backup.

## 🛠️ Requisitos del Sistema

* **Lenguaje:** Python 3.8 o superior.
* **Librerías necesarias:**
  ```bash
  pip install opencv-python numpy pillow pyinstaller
  ```

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
