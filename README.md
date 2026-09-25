# GymTracker — cómo ejecutarlo en Mac

Esta guía es para abrir GymTracker por primera vez en una Mac, aunque no tengas
experiencia usando Python. Ejecuta los comandos en el mismo orden.

## Primera vez

### 1. Abrir Terminal

Presiona `Command + Espacio`, escribe **Terminal** y presiona Enter.

### 2. Instalar las herramientas de Git

Copia este comando en Terminal y presiona Enter:

```bash
xcode-select --install
```

Si aparece una ventana, pulsa **Instalar** y espera a que termine. Si Terminal dice
que las herramientas ya están instaladas, continúa con el siguiente paso.

### 3. Comprobar Python

Ejecuta:

```bash
python3 --version
```

Si aparece `Python 3.10` o una versión mayor, continúa. Si no reconoce el comando
o muestra una versión anterior, abre la página de descarga con:

```bash
open https://www.python.org/downloads/macos/
```

Descarga e instala la versión más reciente de Python 3. Después cierra Terminal,
vuelve a abrirlo y ejecuta otra vez `python3 --version`.

### 4. Clonar el proyecto

Estos comandos guardan GymTracker en el Escritorio:

```bash
cd ~/Desktop
git clone https://github.com/Belakenobi/GymTracker.git
cd GymTracker
```

### 5. Crear el entorno de Python

Ejecuta este comando una sola vez:

```bash
python3 -m venv .venv
```

Ahora activa el entorno:

```bash
source .venv/bin/activate
```

Al activarse debe aparecer `(.venv)` al principio de la línea de Terminal.

### 6. Instalar lo necesario

Ejecuta ambos comandos y espera a que terminen:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 7. Abrir GymTracker

Ejecuta:

```bash
python main.py
```

Se abrirá la ventana de GymTracker. Para cerrar el programa, cierra esa ventana.

## Cómo abrirlo las siguientes veces

No necesitas volver a clonar el proyecto ni instalar las dependencias. Abre
Terminal y ejecuta:

```bash
cd ~/Desktop/GymTracker
source .venv/bin/activate
python main.py
```

