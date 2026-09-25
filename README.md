# GymTracker

GymTracker es una aplicación de escritorio académica para registrar y consultar
entrenamientos de gimnasio. El proyecto utiliza Python, CustomTkinter y archivos
JSON para guardar información de forma local.

## Estado del proyecto

Actualmente incluye:

- Ventana principal con una interfaz moderna y adaptable.
- Navegación entre Inicio, Calendario, Entrenamientos y Archivos.
- Dashboard visual con tarjetas, último entrenamiento, grupos musculares y
  actividad semanal.
- Calendario mensual con selección de fechas y señalización del día actual.
- Preparación del archivo JSON de almacenamiento local.
- Captura y cambio del nombre o nickname del usuario durante la sesión.
- Bienvenida personalizada y transición no bloqueante de 1.5 segundos.
- Validación de fechas `dd/mm/aaaa` y conversión a `(día, mes, año)`.
- CRUD completo de entrenamientos con persistencia en JSON.
- Ejercicios anidados que pueden agregarse o quitarse desde el formulario.
- Contadores reales y último entrenamiento dentro del dashboard.

Las gráficas avanzadas y la gestión académica de archivos se implementarán en etapas posteriores.

## Requisitos

- Una computadora con Windows, macOS o Linux y entorno gráfico.
- Python 3.10 o una versión posterior.
- `pip`, incluido normalmente con Python.
- Tkinter. En Windows y macOS suele venir con Python; en algunas distribuciones
  Linux debe instalarse por separado.
- Conexión a Internet únicamente durante la instalación de dependencias.

> GymTracker es una aplicación de escritorio. No funciona directamente como sitio
> web, aplicación móvil ni en una terminal Linux sin entorno gráfico.

## Instalación paso a paso

### 1. Obtener el proyecto

Descarga y descomprime el proyecto o clónalo con Git. Después abre una terminal
dentro de la carpeta `gymtracker`, donde se encuentran `main.py` y
`requirements.txt`.

Ejemplo si la carpeta está en Descargas:

**Windows PowerShell**

```powershell
cd "$HOME\Downloads\gymtracker"
```

**Windows CMD**

```bat
cd %USERPROFILE%\Downloads\gymtracker
```

**macOS o Linux**

```bash
cd ~/Downloads/gymtracker
```

Si tu carpeta está en otro sitio, cambia esa ruta por la ubicación real.

### 2. Comprobar Python

**Windows**

```powershell
py --version
```

**macOS o Linux**

```bash
python3 --version
```

Debe mostrarse Python 3.10 o superior. Si el comando no existe, instala Python:

- Windows y macOS: descárgalo desde [python.org](https://www.python.org/downloads/).
- Linux: utiliza el administrador de paquetes de tu distribución.

En Windows, durante la instalación marca la opción **Add Python to PATH**.

### 3. Instalar soporte gráfico en Linux

Omite este paso en Windows y macOS. En Linux, usa el comando correspondiente si
`tkinter` no está instalado.

**Ubuntu, Debian y derivados**

```bash
sudo apt update
sudo apt install python3 python3-venv python3-tk
```

**Fedora**

```bash
sudo dnf install python3 python3-tkinter
```

**Arch Linux y derivados**

```bash
sudo pacman -S python tk
```

### 4. Crear un entorno virtual

El entorno virtual mantiene las librerías de GymTracker separadas del resto del
sistema. Solo se crea una vez.

**Windows PowerShell o CMD**

```powershell
py -m venv .venv
```

**macOS o Linux**

```bash
python3 -m venv .venv
```

### 5. Activar el entorno virtual

Debes activarlo cada vez que abras una terminal nueva para trabajar con el
proyecto.

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea el script, permite su ejecución solo para esa terminal y
vuelve a activarlo:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

**Windows CMD**

```bat
.venv\Scripts\activate.bat
```

**macOS o Linux**

```bash
source .venv/bin/activate
```

Cuando esté activo, normalmente aparecerá `(.venv)` al inicio de la línea de la
terminal.

### 6. Instalar las dependencias

Con el entorno virtual activo, ejecuta en cualquier sistema:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

El archivo `requirements.txt` instala la versión compatible de CustomTkinter.

### 7. Ejecutar la aplicación gráfica

Sin salir de la carpeta del proyecto y con el entorno activo:

```bash
python main.py
```

Se abrirá una ventana para escribir un nombre o nickname. Después podrás acceder
a Inicio, Calendario, Entrenamientos y Archivos.

### 8. Ejecutar el menú de consola opcional

El proyecto también incluye una demostración en terminal para administrar los
archivos de texto locales:

```bash
python menu_consola.py
```

### 9. Cerrar el entorno virtual

Cuando termines:

```bash
deactivate
```

## Uso en ejecuciones posteriores

Después de instalar todo por primera vez, no necesitas recrear el entorno ni
reinstalar dependencias. Abre una terminal en `gymtracker` y ejecuta:

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
python main.py
```

**Windows CMD**

```bat
.venv\Scripts\activate.bat
python main.py
```

**macOS o Linux**

```bash
source .venv/bin/activate
python main.py
```

## Datos locales

- Los entrenamientos se guardan en `data/entrenamientos.json`.
- Las notas y registros de texto se guardan en `data/registros/`.
- No se utiliza una cuenta, servidor ni base de datos externa.
- Para hacer una copia de seguridad, copia la carpeta `data/` completa.
- No cierres la aplicación mientras se esté guardando un entrenamiento.

## Solución de problemas

### `python` no se reconoce como comando

- En Windows prueba `py` en lugar de `python`.
- En macOS o Linux prueba `python3` antes de activar el entorno virtual.
- Comprueba que Python esté instalado y agregado al `PATH`.

### `No module named customtkinter`

Activa `.venv` y vuelve a instalar las dependencias:

```bash
python -m pip install -r requirements.txt
```

### `No module named tkinter`

En Linux instala el paquete gráfico indicado en el paso 3. En Windows o macOS,
reinstala Python desde python.org incluyendo Tcl/Tk.

### La ventana no aparece en Linux

La aplicación necesita una sesión gráfica. Comprueba que no estés en un servidor
sin escritorio y que la variable `DISPLAY` exista:

```bash
echo $DISPLAY
```

En WSL se recomienda ejecutar el proyecto con Python de Windows. WSLg también
puede mostrar la interfaz si está correctamente habilitado.

### El entorno virtual no se activa en PowerShell

Ejecuta estos comandos en la misma ventana:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Este cambio es temporal y desaparece al cerrar PowerShell.

### El JSON fue editado manualmente y la aplicación no muestra datos

`data/entrenamientos.json` debe contener una lista JSON válida. Puedes comprobarlo
desde la carpeta del proyecto:

```bash
python -m json.tool data/entrenamientos.json
```

## Estructura principal

```text
gymtracker/
├── main.py
├── app/
│   ├── interfaz.py
│   ├── entrenamientos.py
│   ├── calendario.py
│   ├── archivos.py
│   ├── gestor_archivos.py
│   ├── validaciones.py
│   └── utilidades.py
├── data/
│   ├── entrenamientos.json
│   └── registros/
└── assets/
```

