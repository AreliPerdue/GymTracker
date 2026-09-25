"""Funciones auxiliares pequeñas que pueden reutilizarse en la aplicación."""

# pathlib permite construir rutas que funcionan en distintos sistemas operativos.
from pathlib import Path

# json se usa para crear y, más adelante, leer la persistencia local.
import json


# La raíz se obtiene a partir de este archivo y no del lugar desde donde se ejecuta Python.
RUTA_PROYECTO = Path(__file__).resolve().parent.parent

# Estas rutas centrales evitan repetir nombres de carpetas en otros módulos.
RUTA_DATOS = RUTA_PROYECTO / "data"
RUTA_ENTRENAMIENTOS = RUTA_DATOS / "entrenamientos.json"
RUTA_REGISTROS = RUTA_DATOS / "registros"


# Esta función prepara el almacenamiento sin agregar información de ejemplo.
def preparar_almacenamiento():
    """Crea las carpetas y el JSON inicial si todavía no existen."""

    # parents=True también crea cualquier carpeta superior que haga falta.
    RUTA_REGISTROS.mkdir(parents=True, exist_ok=True)

    # Solo se escribe el archivo cuando no existe para no reemplazar datos futuros.
    if not RUTA_ENTRENAMIENTOS.exists():
        # Una lista vacía representa que aún no hay entrenamientos registrados.
        contenido_inicial = []

        # UTF-8 permite guardar correctamente acentos y otros caracteres en español.
        with RUTA_ENTRENAMIENTOS.open("w", encoding="utf-8") as archivo:
            json.dump(contenido_inicial, archivo, ensure_ascii=False, indent=4)

    # Un diccionario relaciona cada archivo inicial con su contenido predeterminado.
    archivos_iniciales = {
        "objetivos.txt": "Mis objetivos de entrenamiento.",
        "progreso.txt": "Registro personal de progreso.",
        "rutina_favorita.txt": "Mi rutina favorita.",
        "notas_gimnasio.txt": "Notas generales del gimnasio.",
    }

    # El ciclo comprueba individualmente los cuatro archivos académicos requeridos.
    for nombre_archivo, contenido in archivos_iniciales.items():
        ruta_archivo = RUTA_REGISTROS / nombre_archivo

        # Esta condición protege cualquier contenido escrito previamente por el usuario.
        if not ruta_archivo.exists():
            with ruta_archivo.open("w", encoding="utf-8") as archivo:
                archivo.write(contenido)


# El CRUD usa una sola ruta compartida para mantener la persistencia.
# Las funciones siguientes reciben listas y diccionarios comunes.
# Esto permite probar la persistencia sin una interfaz gráfica.

# Esta función concentra la lectura del archivo utilizado por el CRUD.
def cargar_entrenamientos():
    """Lee entrenamientos.json y devuelve una lista segura."""

    # Se prepara el archivo por si es la primera ejecución del proyecto.
    preparar_almacenamiento()

    # try/except evita cerrar la aplicación ante archivos vacíos o dañados.
    try:
        with RUTA_ENTRENAMIENTOS.open("r", encoding="utf-8") as archivo:
            entrenamientos = json.load(archivo)
    except (OSError, json.JSONDecodeError):
        return []

    # El archivo principal siempre debe contener una lista de diccionarios.
    if not isinstance(entrenamientos, list):
        return []

    # Solo se aceptan elementos con estructura de diccionario.
    return [dato for dato in entrenamientos if isinstance(dato, dict)]


# Esta función concentra la escritura para CREATE, UPDATE y DELETE.
def guardar_entrenamientos(entrenamientos):
    """Guarda la lista completa en JSON con texto legible y caracteres UTF-8."""

    # La carpeta se comprueba antes de intentar abrir el archivo para escritura.
    preparar_almacenamiento()

    # json.dump convierte las listas y diccionarios de Python a formato JSON.
    with RUTA_ENTRENAMIENTOS.open("w", encoding="utf-8") as archivo:
        json.dump(entrenamientos, archivo, ensure_ascii=False, indent=4)


# Los identificadores se calculan sin depender de una base de datos.
def generar_nuevo_id(elementos, nombre_campo):
    """Devuelve uno más que el identificador numérico mayor de una lista."""

    # La lista empieza con cero para que el primer identificador generado sea uno.
    identificadores = [0]

    # Cada diccionario puede contener un ID generado en una ejecución anterior.
    for elemento in elementos:
        try:
            identificadores.append(int(elemento.get(nombre_campo, 0)))
        except (AttributeError, TypeError, ValueError):
            # Un dato inválido se ignora y no impide trabajar con los demás.
            continue

    # max encuentra el ID mayor y la suma evita repetirlo.
    return max(identificadores) + 1


# CREATE agrega un diccionario nuevo y persiste la colección completa.
def crear_entrenamiento(entrenamiento):
    """Asigna un ID, guarda un entrenamiento y devuelve el registro creado."""

    # Se leen primero los registros que ya existen en el archivo local.
    entrenamientos = cargar_entrenamientos()

    # copy evita modificar accidentalmente el diccionario original del formulario.
    nuevo_entrenamiento = entrenamiento.copy()
    nuevo_entrenamiento["idEntrenamiento"] = generar_nuevo_id(
        entrenamientos, "idEntrenamiento"
    )

    # append agrega el nuevo diccionario al final de la lista.
    entrenamientos.append(nuevo_entrenamiento)
    guardar_entrenamientos(entrenamientos)
    return nuevo_entrenamiento


# UPDATE busca el ID indicado y conserva ese identificador durante la modificación.
def actualizar_entrenamiento(id_entrenamiento, datos_actualizados):
    """Reemplaza un entrenamiento existente y devuelve True si lo encontró."""

    # La lista se recorre junto con sus posiciones para reemplazar un elemento.
    entrenamientos = cargar_entrenamientos()
    for posicion, entrenamiento in enumerate(entrenamientos):
        if entrenamiento.get("idEntrenamiento") == id_entrenamiento:
            registro_actualizado = datos_actualizados.copy()
            registro_actualizado["idEntrenamiento"] = id_entrenamiento
            entrenamientos[posicion] = registro_actualizado
            guardar_entrenamientos(entrenamientos)
            return True

    # False informa a la interfaz que el ID no estaba en el archivo.
    return False


# DELETE crea una lista que excluye el registro seleccionado.
def eliminar_entrenamiento(id_entrenamiento):
    """Elimina por ID y devuelve True cuando la lista realmente cambió."""

    # Se conserva cada entrenamiento cuyo ID sea diferente al solicitado.
    entrenamientos = cargar_entrenamientos()
    restantes = [
        entrenamiento
        for entrenamiento in entrenamientos
        if entrenamiento.get("idEntrenamiento") != id_entrenamiento
    ]

    # Si el tamaño no cambia, el registro ya no existía y no se escribe el archivo.
    if len(restantes) == len(entrenamientos):
        return False

    # La nueva colección reemplaza el contenido anterior del JSON.
    guardar_entrenamientos(restantes)
    return True


# Esta función convierte una cantidad de minutos en un texto amigable.
def formatear_minutos(minutos):
    """Devuelve una duración breve como '45 min' o '1 h 20 min'."""

    # Menos de una hora se muestra directamente en minutos.
    if minutos < 60:
        return f"{minutos} min"

    # divmod obtiene horas completas y minutos restantes en una sola operación.
    horas, minutos_restantes = divmod(minutos, 60)

    # Si no sobran minutos, se evita mostrar un texto innecesario.
    if minutos_restantes == 0:
        return f"{horas} h"

    # El resultado conserva ambas unidades cuando son necesarias.
    return f"{horas} h {minutos_restantes} min"

