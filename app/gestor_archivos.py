"""Funciones estándar para administrar las notas TXT de GymTracker."""

# La ruta compartida garantiza que GUI y consola usen la misma carpeta.
from app.utilidades import RUTA_REGISTROS, preparar_almacenamiento

# La creación conserva la validación y tupla de fecha del proyecto.
from app.validaciones import validar_fecha


# Esta función evita nombres vacíos, rutas y caracteres no permitidos.
def normalizar_nombre_archivo(nombre_archivo):
    """Devuelve un nombre seguro que termina en .txt o genera ValueError."""

    # Se quitan espacios exteriores y se reducen espacios repetidos a uno.
    nombre_limpio = " ".join(str(nombre_archivo).strip().split())

    # El usuario puede escribir la extensión con mayúsculas o minúsculas.
    if nombre_limpio.lower().endswith(".txt"):
        nombre_limpio = nombre_limpio[:-4].strip()

    # Un nombre vacío no permite identificar el nuevo archivo.
    if not nombre_limpio:
        raise ValueError("Escribe un nombre para el archivo.")

    # Solo se aceptan letras, números, espacios, guion y guion bajo.
    caracteres_validos = all(
        caracter.isalnum() or caracter in " _-"
        for caracter in nombre_limpio
    )
    if not caracteres_validos:
        raise ValueError(
            "Usa solamente letras, números, espacios, guion o guion bajo."
        )

    # Agregar la extensión garantiza que todos sean archivos de texto.
    return nombre_limpio + ".txt"


# La lista solo incluye notas TXT ubicadas directamente en data/registros.
def listar_archivos():
    """Devuelve una lista ordenada con los nombres disponibles."""

    # También garantiza que existan la carpeta y los cuatro archivos iniciales.
    preparar_almacenamiento()

    # LISTA DE PYTHON: cada elemento encontrado es un nombre, no una ruta externa.
    archivos_disponibles = [
        ruta.name
        for ruta in RUTA_REGISTROS.iterdir()
        if ruta.is_file() and ruta.suffix == ".txt"
    ]

    # El orden alfabético hace coincidir la numeración visible con la selección.
    return sorted(archivos_disponibles, key=str.lower)


# Esta función realiza la lectura compartida por GUI y consola.
def leer_archivo(nombre_archivo):
    """Lee en UTF-8 una nota ubicada dentro de data/registros."""

    # La normalización impide usar diagonales o acceder a carpetas externas.
    nombre_seguro = normalizar_nombre_archivo(nombre_archivo)
    ruta_archivo = RUTA_REGISTROS / nombre_seguro

    # El modo r abre el archivo exclusivamente para lectura.
    with ruta_archivo.open("r", encoding="utf-8") as archivo:
        return archivo.read()


# Esta función realiza la escritura compartida por ambas interfaces.
def escribir_archivo(nombre_archivo, contenido):
    """Reemplaza en UTF-8 el contenido de una nota existente."""

    # La misma regla de nombre protege el flujo de modificación.
    nombre_seguro = normalizar_nombre_archivo(nombre_archivo)
    ruta_archivo = RUTA_REGISTROS / nombre_seguro

    # No se crea silenciosamente un archivo que desapareció tras seleccionarlo.
    if not ruta_archivo.exists():
        raise FileNotFoundError(nombre_seguro)

    # El modo w reemplaza el contenido del archivo seleccionado.
    with ruta_archivo.open("w", encoding="utf-8") as archivo:
        archivo.write(contenido)


# Esta función realiza la creación compartida de notas nuevas.
def crear_archivo(nombre_archivo, fecha_texto, contenido_usuario):
    """Crea una nota, utiliza la fecha-tupla y devuelve su nombre seguro."""

    # El nombre normalizado siempre apunta directamente a data/registros.
    nombre_seguro = normalizar_nombre_archivo(nombre_archivo)
    ruta_archivo = RUTA_REGISTROS / nombre_seguro

    # Un archivo duplicado nunca se sobrescribe automáticamente.
    if ruta_archivo.exists():
        raise FileExistsError(nombre_seguro)

    # validar_fecha devuelve explícitamente la TUPLA (día, mes, año).
    fecha_tupla = validar_fecha(fecha_texto)

    # La tupla se utiliza para reconstruir la fecha almacenada en el TXT.
    dia, mes, anio = fecha_tupla
    fecha_normalizada = f"{dia:02d}/{mes:02d}/{anio:04d}"

    # Una operación con strings combina fecha y contenido personal.
    contenido_final = "Fecha: " + fecha_normalizada + "\n\n" + contenido_usuario.strip()

    # El modo x crea el archivo y también protege contra duplicados inesperados.
    with ruta_archivo.open("x", encoding="utf-8") as archivo:
        archivo.write(contenido_final)

    return nombre_seguro

