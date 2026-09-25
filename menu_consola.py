"""Demostración complementaria del menú de archivos de GymTracker."""

# La consola reutiliza exactamente las mismas operaciones de la interfaz gráfica.
from app.gestor_archivos import (
    crear_archivo,
    escribir_archivo,
    leer_archivo,
    listar_archivos,
    normalizar_nombre_archivo,
)

# Estas validaciones conservan las reglas académicas de nombre y fecha.
from app.validaciones import validar_fecha, validar_nombre_usuario


# Esta función se usa al comenzar y al elegir Cambiar usuario.
def solicitar_usuario():
    """Solicita un nickname hasta recibir uno válido y lo devuelve."""

    # El while permite corregir el nombre sin finalizar el programa.
    while True:
        # input detiene la consola hasta que el usuario escribe una respuesta.
        nombre_escrito = input("Nombre o nickname: ")
        es_valido, resultado = validar_nombre_usuario(nombre_escrito)

        # Una entrada correcta actualiza la variable de la sesión actual.
        if es_valido:
            nombre_usuario = resultado

            # La f-string combina el saludo con el nickname capturado.
            print(f"\n¡Bienvenida, {nombre_usuario}, a GymTracker!\n")
            return nombre_usuario

        # Si no es válido, resultado contiene un mensaje comprensible.
        print(resultado)


# La tabla usa alineación de strings y no necesita librerías externas.
def mostrar_menu():
    """Imprime las opciones en dos columnas: OPCIÓN y ACCIÓN."""

    # Una lista de tuplas conserva juntas la opción y su acción.
    opciones = [
        ("1", "Leer archivo"),
        ("2", "Escribir archivo"),
        ("3", "Crear archivo"),
        ("4", "Cambiar usuario"),
        ("5", "Salir"),
    ]

    print("=" * 42)
    print("GYMTRACKER - ARCHIVOS")
    print("=" * 42)

    # <12 y <25 reservan espacios para formar las dos columnas requeridas.
    print(f"{'OPCIÓN':<12}{'ACCIÓN':<25}")
    print("-" * 42)

    # El ciclo presenta una fila de la tabla por cada tupla de la lista.
    for numero, accion in opciones:
        print(f"{numero:<12}{accion:<25}")

    print("=" * 42)


# Leer y escribir comparten esta selección para no duplicar lógica.
def seleccionar_archivo():
    """Muestra los TXT disponibles y devuelve el nombre seleccionado."""

    # La función consulta la misma carpeta data/registros usada por la GUI.
    try:
        archivos = listar_archivos()
    except (PermissionError, OSError):
        print("No fue posible consultar los archivos disponibles.")
        return None

    if not archivos:
        print("No hay archivos disponibles.")
        return None

    print("\nArchivos disponibles:\n")

    # enumerate numera la lista desde uno para facilitar la selección.
    for numero, nombre_archivo in enumerate(archivos, start=1):
        print(f"{numero}. {nombre_archivo}")

    seleccion = input("\nSelecciona un archivo: ").strip()

    # La conversión se protege porque el usuario puede escribir texto.
    try:
        posicion = int(seleccion) - 1
    except ValueError:
        print("Selección no válida.")
        return None

    # El condicional evita posiciones negativas o mayores que la lista.
    if posicion < 0 or posicion >= len(archivos):
        print("Selección no válida.")
        return None

    return archivos[posicion]


# La primera opción demuestra lectura de archivos con manejo de excepciones.
def opcion_leer():
    """Selecciona una nota y muestra su contenido en consola."""

    nombre_archivo = seleccionar_archivo()
    if nombre_archivo is None:
        return

    try:
        contenido = leer_archivo(nombre_archivo)
    except FileNotFoundError:
        print("El archivo ya no existe.")
    except PermissionError:
        print("No hay permiso para leer el archivo.")
    except OSError:
        print("No fue posible leer el archivo.")
    else:
        print(f"\n--- {nombre_archivo} ---\n")
        print(contenido)
        print("\n---")

    input("\nPresiona Enter para continuar...")


# La segunda opción reemplaza el contenido usando la escritura compartida.
def opcion_escribir():
    """Solicita contenido nuevo y actualiza un archivo seleccionado."""

    nombre_archivo = seleccionar_archivo()
    if nombre_archivo is None:
        return

    # Para esta demostración académica se captura una línea de texto.
    contenido_nuevo = input("Nuevo contenido: ")

    try:
        escribir_archivo(nombre_archivo, contenido_nuevo)
    except FileNotFoundError:
        print("El archivo ya no existe.")
    except PermissionError:
        print("No hay permiso para escribir el archivo.")
    except OSError:
        print("No fue posible actualizar el archivo.")
    else:
        print("Archivo actualizado correctamente.")


# La tercera opción demuestra input, tupla, strings y creación segura.
def opcion_crear():
    """Solicita datos válidos o permite cancelar y regresar al menú."""

    # La instrucción permanece visible durante toda la captura.
    print("\nEscribe 0 o 'cancelar' para volver al menú.")

    # Este while conserva al usuario dentro de la opción hasta crear o cancelar.
    while True:
        nombre = input("Nombre del archivo (debe terminar en .txt): ").strip()

        # La cancelación funciona desde el primer campo del formulario.
        if nombre.lower() in ("0", "cancelar"):
            print("Creación cancelada.")
            return

        # Aunque el gestor normaliza nombres, la consola pide .txt claramente.
        if not nombre.lower().endswith(".txt"):
            print("El nombre debe terminar en .txt.")
            continue

        # Se valida el nombre antes de solicitar los demás datos.
        try:
            nombre_normalizado = normalizar_nombre_archivo(nombre)
            archivos_existentes = listar_archivos()
        except ValueError as error:
            print(error)
            continue
        except (PermissionError, OSError):
            print("No fue posible consultar los archivos existentes.")
            return

        # Detectar el duplicado evita pedir fecha y contenido innecesariamente.
        if nombre_normalizado in archivos_existentes:
            print("Ya existe un archivo con ese nombre.")
            continue

        # Este while vuelve a pedir solamente la fecha cuando es inválida.
        while True:
            fecha_texto = input("Fecha (dd/mm/aaaa): ").strip()

            if fecha_texto.lower() in ("0", "cancelar"):
                print("Creación cancelada.")
                return

            try:
                # validar_fecha convierte explícitamente a (día, mes, año).
                fecha_tupla = validar_fecha(fecha_texto)
            except ValueError as error:
                print(error)
                print("Intenta escribir la fecha nuevamente.")
                continue

            # La fecha correcta permite avanzar al campo de contenido.
            break

        # El contenido también puede corregirse sin reiniciar toda la opción.
        while True:
            contenido = input("Contenido: ").strip()

            if contenido.lower() in ("0", "cancelar"):
                print("Creación cancelada.")
                return

            if not contenido:
                print("El contenido no puede estar vacío.")
                continue

            break

        # La tupla validada se usa para reconstruir la fecha del archivo.
        dia, mes, anio = fecha_tupla
        fecha_formateada = f"{dia:02d}/{mes:02d}/{anio:04d}"

        try:
            nombre_creado = crear_archivo(
                nombre_normalizado,
                fecha_formateada,
                contenido,
            )
        except FileExistsError:
            # También se protege si la GUI creó el archivo durante la captura.
            print("Ya existe un archivo con ese nombre.")
            continue
        except ValueError as error:
            print(error)
            continue
        except PermissionError:
            print("No hay permiso para crear el archivo.")
            return
        except OSError:
            print("No fue posible crear el archivo.")
            return

        print(f"Archivo creado correctamente: {nombre_creado}")
        return


# Esta es la función principal y contiene el while solicitado por la rúbrica.
def menu_principal():
    """Repite el menú hasta que el usuario seleccione la opción 5."""

    # El usuario inicial se solicita antes de presentar las operaciones.
    usuario_actual = solicitar_usuario()

    # WHILE PRINCIPAL: repite menú, input y acción hasta seleccionar Salir.
    while True:
        mostrar_menu()
        opcion = input("Selecciona una opción: ").strip()

        # Los if/elif comparan strings y dirigen cada elección.
        if opcion == "1":
            opcion_leer()
        elif opcion == "2":
            opcion_escribir()
        elif opcion == "3":
            opcion_crear()
        elif opcion == "4":
            # La variable cambia sin reiniciar el script ni crear otro menú.
            usuario_actual = solicitar_usuario()
        elif opcion == "5":
            # break termina normalmente el ciclo while principal.
            break
        else:
            print("Opción no válida. Intenta nuevamente.")

    # El mensaje aparece una sola vez después de salir del while.
    print("Gracias por usar GymTracker. ¡Hasta pronto!")


# Esta condición permite importar el archivo sin ejecutar el menú interactivo.
if __name__ == "__main__":
    menu_principal()

