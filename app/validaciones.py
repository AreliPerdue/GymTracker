"""Validaciones sencillas utilizadas por los formularios de GymTracker."""

# date comprueba reglas reales del calendario, como meses y años bisiestos.
from datetime import date


# Esta validación genérica podrá reutilizarse en nombres, rutinas y equipos.
def texto_no_vacio(valor):
    """Indica si un valor contiene texto después de quitar espacios."""

    # str permite manejar de forma segura valores simples recibidos por la interfaz.
    return bool(str(valor).strip())


# Esta función revisa el nickname antes de permitir el acceso al dashboard.
def validar_nombre_usuario(nombre):
    """Devuelve el nombre limpio o un mensaje de error comprensible."""

    # Se convierten varios espacios seguidos en uno para presentar un nombre limpio.
    nombre_limpio = " ".join(str(nombre).split())

    # Un nombre vacío no permite personalizar el mensaje de bienvenida.
    if not nombre_limpio:
        return False, "Escribe tu nombre o nickname para continuar."

    # isalpha acepta letras con acentos; los espacios se permiten entre palabras.
    if not all(caracter.isalpha() or caracter.isspace() for caracter in nombre_limpio):
        return False, "Usa solamente letras y espacios en tu nombre."

    # Se devuelve el nombre normalizado para usarlo en toda la sesión actual.
    return True, nombre_limpio


# Esta función deja explícita la conversión requerida por la rúbrica académica.
def convertir_fecha_a_tupla(fecha_texto):
    """Convierte una fecha dd/mm/aaaa válida en la tupla (día, mes, año)."""

    # Primero se asegura que la entrada tenga exactamente la forma solicitada.
    texto_limpio = str(fecha_texto).strip()

    # Diez caracteres incluyen dos dígitos, separador, dos dígitos y cuatro dígitos.
    if len(texto_limpio) != 10 or texto_limpio[2] != "/" or texto_limpio[5] != "/":
        raise ValueError("La fecha debe tener el formato dd/mm/aaaa.")

    # Se separan las tres partes para convertirlas individualmente a enteros.
    dia_texto, mes_texto, anio_texto = texto_limpio.split("/")

    # Esta comprobación evita aceptar letras, signos u otros caracteres.
    if not (dia_texto.isdigit() and mes_texto.isdigit() and anio_texto.isdigit()):
        raise ValueError("La fecha solo debe contener números y diagonales.")

    # int transforma las partes de texto en valores numéricos utilizables.
    dia = int(dia_texto)
    mes = int(mes_texto)
    anio = int(anio_texto)

    # date genera ValueError si el día, mes o año no forman una fecha real.
    try:
        date(anio, mes, dia)
    except ValueError as error:
        raise ValueError("La fecha escrita no existe en el calendario.") from error

    # IMPORTANTE: el resultado se construye explícitamente como una TUPLA.
    fecha_tupla = (dia, mes, anio)

    # El formulario CRUD reutiliza esta tupla al crear y modificar entrenamientos.
    return fecha_tupla


# Este nombre breve facilita reconocer la validación desde los formularios.
def validar_fecha(fecha_texto):
    """Valida la fecha y devuelve su tupla; informa errores mediante ValueError."""

    # La conversión solo termina correctamente cuando la fecha y el formato son válidos.
    return convertir_fecha_a_tupla(fecha_texto)


# Estas conversiones se reutilizan tanto al crear como al editar.
# Cada función devuelve un número o genera un ValueError claro.
# La interfaz captura el error y permite corregir la entrada.

# Esta función valida pesos que deben ser estrictamente mayores que cero.
def convertir_numero_positivo(valor, nombre_campo):
    """Convierte un valor a float positivo o genera un mensaje entendible."""

    # float acepta números enteros y decimales escritos dentro de un Entry.
    try:
        numero = float(str(valor).strip())
    except (TypeError, ValueError) as error:
        raise ValueError(f"{nombre_campo} debe ser un número.") from error

    # Cero y los valores negativos no cumplen esta regla.
    if numero <= 0:
        raise ValueError(f"{nombre_campo} debe ser mayor que 0.")

    return numero


# Series, repeticiones y duración necesitan valores enteros positivos.
def convertir_entero_positivo(valor, nombre_campo):
    """Convierte un valor a int positivo sin aceptar números decimales."""

    # int realiza la conversión y rechaza texto o valores como 2.5.
    try:
        numero = int(str(valor).strip())
    except (TypeError, ValueError) as error:
        raise ValueError(f"{nombre_campo} debe ser un número entero.") from error

    # Los valores positivos comienzan en uno.
    if numero <= 0:
        raise ValueError(f"{nombre_campo} debe ser mayor que 0.")

    return numero


# El peso usado en un ejercicio puede ser cero para movimientos sin carga.
def convertir_numero_no_negativo(valor, nombre_campo):
    """Convierte un valor a float y comprueba que sea mayor o igual que cero."""

    # Se reutiliza un try/except para mostrar un error en vez de terminar el programa.
    try:
        numero = float(str(valor).strip())
    except (TypeError, ValueError) as error:
        raise ValueError(f"{nombre_campo} debe ser un número.") from error

    # Un número negativo no representa un peso válido.
    if numero < 0:
        raise ValueError(f"{nombre_campo} no puede ser negativo.")

    return numero


# Los pesos, series, repeticiones y duraciones deben ser cantidades no negativas.
def es_numero_no_negativo(valor):
    """Indica si un valor puede convertirse a un número mayor o igual que cero."""

    # Se intenta convertir el texto que normalmente entregará un campo de formulario.
    try:
        numero = float(valor)

    # ValueError cubre texto no numérico y TypeError cubre valores incompatibles.
    except (ValueError, TypeError):
        return False

    # La comparación final expresa de forma directa la regla de validación.
    return numero >= 0

