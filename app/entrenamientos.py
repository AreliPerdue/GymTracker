"""Interfaz del CRUD de entrenamientos y sus ejercicios."""

# CustomTkinter aporta los componentes de la interfaz de escritorio.
import customtkinter as ctk

# Las funciones de persistencia mantienen visible el uso sencillo de JSON.
from app.utilidades import (
    actualizar_entrenamiento,
    cargar_entrenamientos,
    crear_entrenamiento,
    eliminar_entrenamiento,
    generar_nuevo_id,
)

# Las validaciones convierten el texto de los campos a datos numéricos seguros.
from app.validaciones import (
    convertir_entero_positivo,
    convertir_numero_no_negativo,
    convertir_numero_positivo,
    texto_no_vacio,
    validar_fecha,
)


# Estas tuplas contienen opciones fijas y evitan sistemas de configuración complejos.
GRUPOS_MUSCULARES = (
    "Seleccionar", "Pierna", "Glúteo", "Pecho", "Espalda", "Brazo",
    "Hombro", "Core", "Cuerpo completo", "Descanso", "Otro",
)

# Las categorías permiten clasificar una nota con una elección sencilla.
CATEGORIAS_NOTA = ("General", "Progreso", "Técnica", "Recordatorio")

# El usuario ve nombres amigables y el JSON conserva el color hexadecimal.
COLORES_GRUPO = {
    "Verde": "#35D07F",
    "Azul": "#56A8FF",
    "Naranja": "#FFB84D",
    "Morado": "#A78BFA",
    "Rojo": "#FF6B6B",
}

# Los iconos son caracteres y no requieren archivos de imagen adicionales.
ICONOS_GRUPO = ("🏋", "🦵", "💪", "◎", "★")


# RECORRIDO EDUCATIVO DEL CRUD:
# CRUD resume cuatro operaciones: crear, consultar, modificar y eliminar.
# CREATE recibe los datos del formulario y agrega un diccionario al JSON.
# READ carga la lista almacenada y presenta un resumen de cada elemento.
# UPDATE reemplaza un diccionario sin cambiar su idEntrenamiento.
# DELETE excluye un diccionario después de solicitar confirmación.
# La persistencia vive en utilidades.py para no mezclar JSON con widgets.
# Esta vista llama funciones sencillas y después actualiza sus paneles.
# Un entrenamiento se representa mediante un diccionario de Python.
# Todos los entrenamientos se agrupan dentro de una lista de Python.
# Los ejercicios forman otra lista dentro de cada entrenamiento.
# Cada ejercicio también es un diccionario con seis campos definidos.
# Esta composición se transforma directamente a JSON mediante json.dump.
# json.load realiza el proceso inverso al volver a abrir la aplicación.
# No se necesitan clases de modelo para explicar esta estructura básica.
# Los identificadores permiten distinguir registros aunque compartan nombre.
# idEntrenamiento pertenece al registro principal guardado en el archivo.
# idEjercicio solo identifica elementos dentro de la lista del entrenamiento.
# Los IDs se obtienen buscando el máximo actual y sumando una unidad.
# Esta regla es suficiente para una aplicación local de una sola persona.
# Los valores predeterminados evitan errores al consultar registros antiguos.
# get permite leer una clave sin producir KeyError cuando no existe.
# Los campos visuales utilizan los mismos nombres conceptuales del modelo.
# Las funciones privadas comienzan con _ para indicar uso dentro de la clase.
# Los callbacks actualizan otras partes sin acoplarlas directamente al formulario.
# La aplicación se actualiza en memoria después de cada escritura exitosa.
# Cerrar y volver a abrir vuelve a cargar los mismos datos desde el archivo.
# Ninguna operación usa red, servidor, API o base de datos.
# Las decisiones mantienen el código dentro de Fundamentos de Programación.
# Los comentarios se concentran en decisiones que la estudiante puede explicar.

# Esta vista administra el listado, la consulta y las acciones principales del CRUD.
class VistaEntrenamientos(ctk.CTkFrame):
    """Muestra entrenamientos guardados y permite crearlos, editarlos o eliminarlos."""

    # La función al_cambiar actualiza el dashboard después de modificar el JSON.
    def __init__(self, master, colores, al_cambiar):
        super().__init__(master, fg_color=colores["fondo"])

        # Los valores compartidos se conservan como atributos de la vista.
        self.colores = colores
        self.al_cambiar = al_cambiar
        self.entrenamientos = []
        self.entrenamiento_seleccionado = None
        self.botones_entrenamientos = {}

        # El contenido principal crece junto con la ventana.
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # La interfaz se divide en encabezado, mensajes y zona de consulta.
        self._crear_encabezado()
        self._crear_zona_contenido()
        self.recargar_lista()

    # El encabezado conserva el diseño y la acción solicitada en etapas anteriores.
    def _crear_encabezado(self):
        """Crea el título y el botón para abrir un formulario vacío."""

        # Un contenedor transparente alinea título y botón en la misma fila.
        encabezado = ctk.CTkFrame(self, fg_color="transparent")
        encabezado.grid(row=0, column=0, sticky="ew", padx=34, pady=(28, 8))
        encabezado.grid_columnconfigure(0, weight=1)

        # El título identifica la sección activa.
        ctk.CTkLabel(
            encabezado,
            text="Entrenamientos",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=self.colores["texto"],
        ).grid(row=0, column=0, sticky="w")

        # CREATE comienza con un formulario limpio al pulsar este botón.
        ctk.CTkButton(
            encabezado,
            text="＋  Nuevo entrenamiento",
            width=188,
            height=42,
            corner_radius=12,
            fg_color=self.colores["acento"],
            hover_color=self.colores["acento_hover"],
            text_color="#07130C",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.abrir_formulario,
        ).grid(row=0, column=1, sticky="e")

        # La etiqueta informa el resultado de guardar, editar o eliminar.
        self.etiqueta_estado = ctk.CTkLabel(
            self,
            text="Selecciona un entrenamiento para consultar sus detalles.",
            font=ctk.CTkFont(size=12),
            text_color=self.colores["texto_secundario"],
        )
        self.etiqueta_estado.grid(row=1, column=0, padx=34, pady=(0, 8), sticky="w")

    # La zona central separa la lista de la consulta detallada.
    def _crear_zona_contenido(self):
        """Construye los paneles de listado y detalle."""

        # Dos columnas permiten consultar sin abandonar la lista completa.
        zona = ctk.CTkFrame(self, fg_color="transparent")
        zona.grid(row=2, column=0, sticky="nsew", padx=26, pady=(0, 26))
        zona.grid_columnconfigure(0, weight=2, uniform="entrenamientos")
        zona.grid_columnconfigure(1, weight=3, uniform="entrenamientos")
        zona.grid_rowconfigure(0, weight=1)

        # El panel izquierdo contendrá una tarjeta por entrenamiento.
        self.panel_lista = ctk.CTkScrollableFrame(
            zona,
            corner_radius=22,
            fg_color=self.colores["tarjeta"],
            border_width=1,
            border_color=self.colores["borde"],
            label_text="HISTORIAL",
            label_text_color=self.colores["texto_secundario"],
        )
        self.panel_lista.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.panel_lista.grid_columnconfigure(0, weight=1)

        # El panel derecho se reconstruye cuando el usuario selecciona un registro.
        self.panel_detalle = ctk.CTkScrollableFrame(
            zona,
            corner_radius=22,
            fg_color=self.colores["tarjeta"],
            border_width=1,
            border_color=self.colores["borde"],
            label_text="RESUMEN DE SESIÓN",
            label_text_color=self.colores["texto_secundario"],
        )
        self.panel_detalle.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self.panel_detalle.grid_columnconfigure(0, weight=1)

    # READ vuelve a consultar el archivo para reflejar datos persistidos.
    def recargar_lista(self):
        """Lee el JSON y vuelve a dibujar el listado de entrenamientos."""

        # cargar_entrenamientos maneja archivos ausentes, vacíos o inválidos.
        self.entrenamientos = cargar_entrenamientos()

        # Se destruyen solamente las tarjetas visuales, nunca los datos del archivo.
        for componente in self.panel_lista.winfo_children():
            componente.destroy()
        self.botones_entrenamientos = {}

        # Un estado vacío orienta al usuario cuando todavía no existen registros.
        if not self.entrenamientos:
            ctk.CTkLabel(
                self.panel_lista,
                text="Aún no hay entrenamientos.\nCrea el primero con el botón superior.",
                font=ctk.CTkFont(size=14),
                text_color=self.colores["texto_secundario"],
                justify="center",
            ).grid(row=0, column=0, padx=20, pady=45)
            self.entrenamiento_seleccionado = None
            self._mostrar_detalle_vacio()
            return

        # Se crea una tarjeta resumida para cada diccionario leído del JSON.
        for fila, entrenamiento in enumerate(self.entrenamientos):
            self._crear_tarjeta_lista(entrenamiento, fila)

        # Tras recargar se conserva la selección si su ID todavía existe.
        id_actual = None
        if self.entrenamiento_seleccionado:
            id_actual = self.entrenamiento_seleccionado.get("idEntrenamiento")

        # next busca el mismo entrenamiento y devuelve None si fue eliminado.
        seleccionado = next(
            (
                dato for dato in self.entrenamientos
                if dato.get("idEntrenamiento") == id_actual
            ),
            None,
        )

        # Si ya no existe selección, se muestra el primer registro disponible.
        self.mostrar_detalle(seleccionado or self.entrenamientos[0])

    # GUÍA EDUCATIVA DE READ Y LOS PANELES:
    # recargar_lista solicita una copia actual de la colección persistida.
    # Esto permite reflejar cambios sin cerrar ni reiniciar GymTracker.
    # winfo_children obtiene los componentes creados dentro de un contenedor.
    # destroy elimina representaciones visuales, pero nunca toca el archivo JSON.
    # Un ciclo vuelve a crear una tarjeta por cada diccionario cargado.
    # enumerate entrega la posición usada como fila de la cuadrícula.
    # El orden del JSON se conserva dentro del listado mostrado.
    # Cada tarjeta usa un callback que conserva su propio entrenamiento.
    # dato=entrenamiento evita que todas las lambdas usen el último elemento.
    # Pulsar una tarjeta no modifica el registro seleccionado.
    # mostrar_detalle realiza exclusivamente una operación de lectura visual.
    # El panel derecho se limpia antes de presentar el siguiente registro.
    # Los campos se agrupan en una tupla para reducir código duplicado.
    # Otro ciclo crea una etiqueta por cada par de nombre y valor.
    # Los ejercicios necesitan un ciclo porque su cantidad es variable.
    # indice comienza en uno para presentar una numeración natural.
    # max(len(ejercicios), 1) también reserva espacio cuando no existen.
    # La nota usa wraplength para permanecer dentro del ancho del panel.
    # Editar y Eliminar aparecen al consultar un entrenamiento guardado.
    # El diccionario seleccionado queda disponible para esas operaciones.
    # Si DELETE retira ese ID, la selección se limpia explícitamente.
    # Si una recarga conserva el ID, next recupera su versión actualizada.
    # El valor alternativo None indica que la búsqueda no encontró coincidencia.
    # El primer registro se selecciona para aprovechar el panel de detalle.
    # Un archivo vacío presenta instrucciones claras en ambos paneles.
    # get tolera claves antiguas mediante textos como "Sin fecha".
    # Esta tolerancia permite consultar datos de versiones anteriores.
    # Los diccionarios originales no cambian al construir las etiquetas.
    # La separación lista/detalle mantiene una navegación sencilla.
    # CTkScrollableFrame permite revisar colecciones extensas.
    # READ no necesita try/except adicional dentro de esta clase.
    # cargar_entrenamientos ya maneja un JSON vacío o inválido.
    # Las excepciones de escritura solo corresponden a las otras operaciones.
    # Cada bloque captura así los errores que realmente puede producir.

    # Cada tarjeta resume los datos solicitados para la operación READ.
    def _crear_tarjeta_lista(self, entrenamiento, fila):
        """Agrega un botón de resumen que permite seleccionar un entrenamiento."""

        # get ofrece valores de respaldo ante registros antiguos incompletos.
        icono = entrenamiento.get("iconoGrupo", "◎")
        rutina = entrenamiento.get("nombreRutina", "Sin nombre")
        fecha = entrenamiento.get("fecha", "Sin fecha")
        grupo = entrenamiento.get("grupoMuscular", "Sin grupo")
        duracion = entrenamiento.get("duracion", 0)

        # El texto combina dos líneas para conservar una lista compacta.
        resumen = f"{icono}  {rutina}\n     {fecha} • {grupo} • {duracion} min"

        # Cada botón entrega su propio diccionario al método de detalle.
        boton = ctk.CTkButton(
            self.panel_lista,
            text=resumen,
            height=72,
            corner_radius=14,
            anchor="w",
            border_width=1,
            border_color=self.colores["borde"],
            fg_color=self.colores["tarjeta_clara"],
            hover_color=self.colores["acento_suave"],
            text_color=self.colores["texto"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda dato=entrenamiento: self.mostrar_detalle(dato),
        )
        boton.grid(row=fila, column=0, sticky="ew", padx=8, pady=6)
        self.botones_entrenamientos[entrenamiento.get("idEntrenamiento")] = boton

    # Esta ayuda limpia el panel derecho antes de dibujar otro contenido.
    def _limpiar_detalle(self):
        """Destruye los widgets del detalle actual."""

        # winfo_children devuelve los componentes que pertenecen al panel.
        for componente in self.panel_detalle.winfo_children():
            componente.destroy()

    # El estado vacío mantiene el panel derecho comprensible.
    def _mostrar_detalle_vacio(self):
        """Muestra una indicación cuando no existe un registro seleccionado."""

        # Se limpia cualquier consulta anterior antes de colocar el mensaje.
        self._limpiar_detalle()
        ctk.CTkLabel(
            self.panel_detalle,
            text="Selecciona o crea un entrenamiento\npara ver su información completa.",
            font=ctk.CTkFont(size=15),
            text_color=self.colores["texto_secundario"],
            justify="center",
        ).grid(row=0, column=0, padx=25, pady=55)

    # READ presenta todos los campos, incluidos ejercicios y notas.
    def mostrar_detalle(self, entrenamiento):
        """Dibuja los datos completos del entrenamiento seleccionado."""

        # El diccionario seleccionado se conserva para Editar y Eliminar.
        self.entrenamiento_seleccionado = entrenamiento

        # Las tarjetas no seleccionadas recuperan su estilo neutral.
        for boton in self.botones_entrenamientos.values():
            boton.configure(
                fg_color=self.colores["tarjeta_clara"],
                text_color=self.colores["texto"],
                border_color=self.colores["borde"],
            )

        # La tarjeta activa usa acento verde para conectar lista y detalle.
        id_seleccionado = entrenamiento.get("idEntrenamiento")
        if id_seleccionado in self.botones_entrenamientos:
            self.botones_entrenamientos[id_seleccionado].configure(
                fg_color=self.colores["acento_suave"],
                text_color=self.colores["acento"],
                border_color=self.colores["acento"],
            )

        self._limpiar_detalle()

        # Nombre e icono forman el encabezado principal del detalle.
        titulo = (
            f"{entrenamiento.get('iconoGrupo', '◎')}  "
            f"{entrenamiento.get('nombreRutina', 'Sin nombre')}"
        )
        ctk.CTkLabel(
            self.panel_detalle,
            text=titulo,
            font=ctk.CTkFont(size=21, weight="bold"),
            text_color=self.colores["texto"],
        ).grid(row=0, column=0, padx=20, pady=(18, 12), sticky="w")

        # Una lista de tuplas permite dibujar los campos sin repetir widgets.
        peso = entrenamiento.get("pesoCorporal")
        peso_texto = "No registrado" if peso in (None, "") else f"{peso} kg"
        campos = (
            ("Fecha", entrenamiento.get("fecha", "Sin fecha")),
            ("Grupo muscular", entrenamiento.get("grupoMuscular", "Sin grupo")),
            ("Peso corporal", peso_texto),
            ("Duración", f"{entrenamiento.get('duracion', 0)} minutos"),
            ("Categoría", entrenamiento.get("categoriaNota", "General")),
            ("Color", entrenamiento.get("colorGrupo", "Sin color")),
        )

        # Cada fila presenta una etiqueta y el valor guardado en el JSON.
        for fila, (etiqueta, valor) in enumerate(campos, start=1):
            ctk.CTkLabel(
                self.panel_detalle,
                text=f"{etiqueta}:  {valor}",
                font=ctk.CTkFont(size=13),
                text_color=self.colores["texto_secundario"],
            ).grid(row=fila, column=0, padx=20, pady=3, sticky="w")

        # La sección de ejercicios enumera las listas anidadas del entrenamiento.
        fila_ejercicios = len(campos) + 1
        ctk.CTkLabel(
            self.panel_detalle,
            text="Ejercicios",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=self.colores["texto"],
        ).grid(row=fila_ejercicios, column=0, padx=20, pady=(15, 5), sticky="w")

        # Si no existen ejercicios se conserva un mensaje explícito.
        ejercicios = entrenamiento.get("ejercicios", [])
        if not ejercicios:
            ctk.CTkLabel(
                self.panel_detalle,
                text="Sin ejercicios registrados.",
                text_color=self.colores["texto_secundario"],
            ).grid(row=fila_ejercicios + 1, column=0, padx=20, sticky="w")
        else:
            # Cada ejercicio muestra nombre, peso, series, repeticiones y equipo.
            for indice, ejercicio in enumerate(ejercicios, start=1):
                texto = (
                    f"{indice}. {ejercicio.get('nombreEjercicio', 'Sin nombre')}  ·  "
                    f"{ejercicio.get('pesoEjercicio', 0)} kg  ·  "
                    f"{ejercicio.get('series', 0)} x {ejercicio.get('repeticiones', 0)}\n"
                    f"    Equipo: {ejercicio.get('equipo', 'Sin equipo')}"
                )
                ctk.CTkLabel(
                    self.panel_detalle,
                    text=texto,
                    justify="left",
                    text_color=self.colores["texto_secundario"],
                ).grid(row=fila_ejercicios + indice, column=0, padx=20, pady=4, sticky="w")

        # Las notas se colocan después de la cantidad variable de ejercicios.
        fila_notas = fila_ejercicios + max(len(ejercicios), 1) + 1
        notas = entrenamiento.get("notas", "") or "Sin notas."
        ctk.CTkLabel(
            self.panel_detalle,
            text=f"Notas\n{notas}",
            justify="left",
            wraplength=440,
            font=ctk.CTkFont(size=13),
            text_color=self.colores["texto_secundario"],
        ).grid(row=fila_notas, column=0, padx=20, pady=(14, 12), sticky="w")

        # Los botones completan UPDATE y DELETE para el registro seleccionado.
        acciones = ctk.CTkFrame(self.panel_detalle, fg_color="transparent")
        acciones.grid(row=fila_notas + 1, column=0, padx=20, pady=(5, 20), sticky="w")

        # Editar abre exactamente el mismo formulario usado para crear.
        ctk.CTkButton(
            acciones,
            text="✎  Editar",
            width=120,
            fg_color=self.colores["acento_secundario"],
            hover_color="#3D8DDB",
            command=lambda: self.abrir_formulario(entrenamiento),
        ).pack(side="left", padx=(0, 8))

        # Eliminar solicita confirmación antes de cambiar el archivo.
        ctk.CTkButton(
            acciones,
            text="✕  Eliminar",
            width=120,
            fg_color="#B94747",
            hover_color="#963939",
            command=lambda: self.confirmar_eliminacion(entrenamiento),
        ).pack(side="left")

    # El mismo formulario recibe None para CREATE o un diccionario para UPDATE.
    def abrir_formulario(self, entrenamiento=None, fecha_inicial=None):
        """Abre el formulario vacío o rellenado con datos existentes."""

        # La fecha opcional permite crear desde el día consultado en Calendario.
        FormularioEntrenamiento(
            self,
            self.colores,
            entrenamiento=entrenamiento,
            al_guardar=self._despues_de_cambio,
            fecha_inicial=fecha_inicial,
        )

    # Este callback refresca la lista y comunica el cambio al dashboard.
    def _despues_de_cambio(self, mensaje):
        """Actualiza la interfaz sin reiniciar el programa."""

        # El mensaje permanece visible en la parte superior de la sección.
        self.etiqueta_estado.configure(text=mensaje, text_color=self.colores["acento"])
        self.recargar_lista()
        self.al_cambiar()

    # GUÍA EDUCATIVA DE DELETE:
    # Eliminar es la operación que requiere una confirmación adicional.
    # La ventana secundaria muestra claramente el efecto de la acción.
    # Cancelar destruye esa ventana sin llamar ninguna función CRUD.
    # Confirmar obtiene idEntrenamiento del diccionario seleccionado.
    # eliminar_entrenamiento filtra la lista cargada mediante ese ID.
    # Si ningún elemento coincide, devuelve False y conserva el archivo.
    # Si existe, guarda la lista restante y devuelve True.
    # OSError protege la interfaz ante un problema al escribir el JSON.
    # Un borrado correcto limpia la selección que ya no es válida.
    # recargar_lista reconstruye las tarjetas con los elementos restantes.
    # al_cambiar solicita también la actualización del dashboard.
    # El contador, los minutos y el último entrenamiento se recalculan.
    # La aplicación principal permanece abierta durante este proceso.
    # La confirmación usa el mismo estilo visual que el resto del proyecto.
    # No se elimina ningún archivo completo, solo el diccionario elegido.

    # DELETE usa una ventana pequeña para evitar eliminaciones accidentales.
    def confirmar_eliminacion(self, entrenamiento):
        """Muestra las opciones Cancelar y Eliminar antes de borrar."""

        # CTkToplevel crea una ventana secundaria vinculada a GymTracker.
        confirmacion = ctk.CTkToplevel(self)
        confirmacion.title("Confirmar eliminación")
        confirmacion.geometry("430x220")
        confirmacion.resizable(False, False)
        confirmacion.configure(fg_color=self.colores["fondo"])
        confirmacion.transient(self.winfo_toplevel())
        confirmacion.grab_set()

        # La pregunta solicitada explica con claridad la acción irreversible.
        ctk.CTkLabel(
            confirmacion,
            text="¿Seguro que deseas eliminar este entrenamiento?",
            wraplength=350,
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=self.colores["texto"],
        ).pack(padx=30, pady=(42, 25))

        # Un contenedor mantiene juntas las dos respuestas posibles.
        botones = ctk.CTkFrame(confirmacion, fg_color="transparent")
        botones.pack()

        # Cancelar cierra solamente la confirmación y no modifica datos.
        ctk.CTkButton(
            botones,
            text="Cancelar",
            width=120,
            fg_color=self.colores["tarjeta_clara"],
            hover_color=self.colores["borde"],
            command=confirmacion.destroy,
        ).pack(side="left", padx=6)

        # Esta función interna conoce el registro y la ventana que debe cerrar.
        def eliminar_confirmado():
            # Se captura un posible error de escritura para mantener abierta la app.
            try:
                eliminado = eliminar_entrenamiento(entrenamiento.get("idEntrenamiento"))
            except OSError:
                self.etiqueta_estado.configure(
                    text="No fue posible escribir el archivo de entrenamientos.",
                    text_color="#FF6B6B",
                )
                confirmacion.destroy()
                return

            # Solo se anuncia éxito cuando el identificador fue encontrado.
            confirmacion.destroy()
            if eliminado:
                self.entrenamiento_seleccionado = None
                self._despues_de_cambio("Entrenamiento eliminado correctamente")
            else:
                self.etiqueta_estado.configure(
                    text="El entrenamiento ya no existe.",
                    text_color="#FF6B6B",
                )
                self.recargar_lista()

        # El botón rojo ejecuta DELETE después de la confirmación explícita.
        ctk.CTkButton(
            botones,
            text="Eliminar",
            width=120,
            fg_color="#B94747",
            hover_color="#963939",
            command=eliminar_confirmado,
        ).pack(side="left", padx=6)


# GUÍA EDUCATIVA DEL FORMULARIO COMPARTIDO:
# El constructor recibe None para crear un entrenamiento nuevo.
# Para editar recibe el diccionario seleccionado dentro del listado.
# id_edicion decide la operación sin mantener dos formularios separados.
# None representa CREATE y un número existente representa UPDATE.
# Ambos flujos comparten exactamente las mismas reglas de validación.
# Esto evita diferencias accidentales entre crear y modificar registros.
# CTkToplevel mantiene el formulario separado del listado principal.
# transient relaciona esta ventana secundaria con GymTracker.
# grab_set dirige la interacción al formulario hasta cerrarlo.
# Un Frame desplazable permite acceder al contenido en pantallas bajas.
# Dos columnas equilibran los campos generales del entrenamiento.
# Los asteriscos identifican los datos obligatorios antes de guardar.
# Los Entry entregan texto aunque se esperen valores numéricos.
# Por eso las conversiones ocurren durante la validación final.
# Los OptionMenu limitan varios campos a opciones conocidas.
# El color visible se traduce a hexadecimal antes de persistirse.
# Durante UPDATE se realiza la traducción inversa para mostrarlo.
# CTkTextbox admite las diferentes líneas de una nota.
# Su índice "1.0" significa primera línea y carácter cero.
# _rellenar_entrada evita repetir delete e insert varias veces.
# Los números guardados se convierten a str para mostrarse.
# El valor None del peso corporal deja el campo vacío.
# Los ejercicios originales se copian antes de permitir cambios.
# Cancelar descarta esas copias sin escribir el archivo.
# Guardar construye un diccionario nuevo desde los controles.
# El formulario no modifica directamente la lista que aparece detrás.
# Primero persiste y después ejecuta el callback visual.
# El callback recibe un mensaje diferente para CREATE y UPDATE.
# La lista y el dashboard se actualizan sin reiniciar el programa.
# destroy cierra solamente esta ventana tras una operación exitosa.
# Ante una entrada inválida, el formulario permanece abierto.
# La etiqueta superior presenta el primer error encontrado.
# Los campos permanecen independientes hasta pulsar Guardar.
# El formulario no crea cuentas ni depende del nickname actual.
# Los entrenamientos pertenecen al archivo local de GymTracker.
# La interfaz reutiliza la paleta creada en las etapas anteriores.
# No se agregan dependencias para construir esta ventana.
# Todos los datos siguen siendo listas, diccionarios y valores simples.
# Este flujo puede explicarse con conceptos de programación fundamental.

# Esta ventana se reutiliza para CREATE y UPDATE sin duplicar formularios.
class FormularioEntrenamiento(ctk.CTkToplevel):
    """Captura un entrenamiento y administra su lista temporal de ejercicios."""

    # El diccionario opcional indica si se crea o se edita un registro.
    def __init__(self, master, colores, entrenamiento, al_guardar, fecha_inicial=None):
        super().__init__(master)

        # Los atributos conservan el modo, los colores y el callback de actualización.
        self.colores = colores
        self.al_guardar = al_guardar
        self.entrenamiento_original = entrenamiento
        self.id_edicion = None if entrenamiento is None else entrenamiento.get("idEntrenamiento")
        self.fecha_tupla = None

        # Cada ejercicio se copia para poder cancelar sin alterar el diccionario original.
        ejercicios_originales = [] if entrenamiento is None else entrenamiento.get("ejercicios", [])
        self.ejercicios = [ejercicio.copy() for ejercicio in ejercicios_originales]

        # La ventana usa un tamaño amplio, pero mantiene dimensiones razonables.
        self.title("Nuevo entrenamiento" if entrenamiento is None else "Editar entrenamiento")
        self.geometry("900x780")
        self.minsize(820, 680)
        self.configure(fg_color=colores["fondo"])
        self.transient(master.winfo_toplevel())
        self.grab_set()

        # El Frame desplazable permite acceder a todo el formulario en pantallas bajas.
        self.formulario = ctk.CTkScrollableFrame(
            self,
            fg_color=colores["fondo"],
            corner_radius=0,
            scrollbar_button_color=colores["borde"],
        )
        self.formulario.pack(fill="both", expand=True)
        self.formulario.grid_columnconfigure(0, weight=1)
        self.formulario.grid_columnconfigure(1, weight=1)

        # Se construyen por bloques los datos generales, ejercicios y acciones.
        self._crear_encabezado()
        self._crear_datos_generales()
        self._crear_seccion_ejercicios()
        self._crear_acciones()

        # UPDATE rellena el mismo formulario con la información persistida.
        if entrenamiento is not None:
            self._cargar_datos(entrenamiento)
        elif fecha_inicial:
            # CREATE desde Calendario conserva visible el día que el usuario eligió.
            self._rellenar_entrada(self.entrada_fecha, fecha_inicial)

        # La lista temporal se dibuja incluso cuando comienza vacía.
        self._dibujar_ejercicios()
        self.entrada_fecha.focus_set()

    # Un encabezado breve comunica si la operación es crear o editar.
    def _crear_encabezado(self):
        """Crea el título y la etiqueta general de mensajes."""

        # El texto depende de la presencia de un ID de edición.
        titulo = "Nuevo entrenamiento" if self.id_edicion is None else "Editar entrenamiento"
        ctk.CTkLabel(
            self.formulario,
            text=titulo,
            font=ctk.CTkFont(size=27, weight="bold"),
            text_color=self.colores["texto"],
        ).grid(row=0, column=0, columnspan=2, padx=28, pady=(22, 4), sticky="w")

        # Esta etiqueta muestra errores de validación sin cerrar la ventana.
        self.etiqueta_error = ctk.CTkLabel(
            self.formulario,
            text="Completa los datos principales y agrega los ejercicios que necesites.",
            font=ctk.CTkFont(size=12),
            text_color=self.colores["texto_secundario"],
        )
        self.etiqueta_error.grid(row=1, column=0, columnspan=2, padx=28, pady=(0, 12), sticky="w")

    # Esta función auxiliar evita repetir la creación de etiquetas y Entry.
    def _crear_campo(self, fila, columna, texto, placeholder=""):
        """Crea una etiqueta y devuelve su campo de entrada."""

        # La etiqueta explica qué dato espera el formulario.
        ctk.CTkLabel(
            self.formulario,
            text=texto,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colores["texto_secundario"],
        ).grid(row=fila, column=columna, padx=28, pady=(7, 3), sticky="w")

        # El Entry comparte colores y se adapta al ancho de su columna.
        entrada = ctk.CTkEntry(
            self.formulario,
            height=40,
            corner_radius=10,
            placeholder_text=placeholder,
            fg_color=self.colores["tarjeta"],
            border_color=self.colores["borde"],
        )
        entrada.grid(row=fila + 1, column=columna, padx=28, pady=(0, 4), sticky="ew")
        return entrada

    # Los datos generales corresponden directamente al modelo del entrenamiento.
    def _crear_datos_generales(self):
        """Construye campos de fecha, rutina, grupo, peso, duración y notas."""

        # Los campos de texto se crean en dos columnas para mantener una vista compacta.
        self.entrada_fecha = self._crear_campo(2, 0, "Fecha *", "dd/mm/aaaa")
        self.entrada_rutina = self._crear_campo(2, 1, "Nombre de rutina *", "Ej. Pierna completa")

        # El grupo muscular utiliza las opciones predeterminadas de la especificación.
        ctk.CTkLabel(
            self.formulario,
            text="Grupo muscular *",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colores["texto_secundario"],
        ).grid(row=4, column=0, padx=28, pady=(7, 3), sticky="w")
        self.selector_grupo = ctk.CTkOptionMenu(
            self.formulario,
            values=list(GRUPOS_MUSCULARES),
            fg_color=self.colores["tarjeta_clara"],
            button_color=self.colores["acento"],
            button_hover_color=self.colores["acento_hover"],
        )
        self.selector_grupo.grid(row=5, column=0, padx=28, pady=(0, 4), sticky="ew")
        self.selector_grupo.set("Seleccionar")

        # El peso corporal es opcional y acepta números decimales positivos.
        self.entrada_peso = self._crear_campo(4, 1, "Peso corporal", "Ej. 60.5")

        # La duración es obligatoria y debe representar minutos enteros positivos.
        self.entrada_duracion = self._crear_campo(6, 0, "Duración en minutos *", "Ej. 65")

        # La categoría de nota se limita a opciones sencillas.
        ctk.CTkLabel(
            self.formulario,
            text="Categoría de nota",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colores["texto_secundario"],
        ).grid(row=6, column=1, padx=28, pady=(7, 3), sticky="w")
        self.selector_categoria = ctk.CTkOptionMenu(
            self.formulario,
            values=list(CATEGORIAS_NOTA),
            fg_color=self.colores["tarjeta_clara"],
            button_color=self.colores["acento"],
            button_hover_color=self.colores["acento_hover"],
        )
        self.selector_categoria.grid(row=7, column=1, padx=28, pady=(0, 4), sticky="ew")

        # Los selectores visuales guardan un color y un icono dentro del registro.
        ctk.CTkLabel(
            self.formulario,
            text="Color del grupo",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colores["texto_secundario"],
        ).grid(row=8, column=0, padx=28, pady=(7, 3), sticky="w")
        self.selector_color = ctk.CTkOptionMenu(
            self.formulario,
            values=list(COLORES_GRUPO.keys()),
            fg_color=self.colores["tarjeta_clara"],
            button_color=self.colores["acento"],
            button_hover_color=self.colores["acento_hover"],
        )
        self.selector_color.grid(row=9, column=0, padx=28, pady=(0, 4), sticky="ew")

        # El icono seleccionado aparecerá en el listado y en el detalle.
        ctk.CTkLabel(
            self.formulario,
            text="Icono del grupo",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colores["texto_secundario"],
        ).grid(row=8, column=1, padx=28, pady=(7, 3), sticky="w")
        self.selector_icono = ctk.CTkOptionMenu(
            self.formulario,
            values=list(ICONOS_GRUPO),
            fg_color=self.colores["tarjeta_clara"],
            button_color=self.colores["acento"],
            button_hover_color=self.colores["acento_hover"],
        )
        self.selector_icono.grid(row=9, column=1, padx=28, pady=(0, 4), sticky="ew")

        # Las notas admiten varias líneas de texto libre.
        ctk.CTkLabel(
            self.formulario,
            text="Notas",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colores["texto_secundario"],
        ).grid(row=10, column=0, columnspan=2, padx=28, pady=(8, 3), sticky="w")
        self.entrada_notas = ctk.CTkTextbox(
            self.formulario,
            height=78,
            corner_radius=10,
            fg_color=self.colores["tarjeta"],
            border_width=1,
            border_color=self.colores["borde"],
        )
        self.entrada_notas.grid(row=11, column=0, columnspan=2, padx=28, pady=(0, 10), sticky="ew")

    # GUÍA EDUCATIVA DE LOS EJERCICIOS:
    # La sección pertenece al formulario del entrenamiento principal.
    # No existe un CRUD independiente para los ejercicios.
    # Cada ejercicio se valida antes de incorporarlo a la lista.
    # El nombre es obligatorio porque identifica el movimiento.
    # El peso acepta cero para una actividad sin carga adicional.
    # Un peso negativo no representa un valor válido.
    # Series y repeticiones deben ser enteros positivos.
    # int rechaza los valores decimales y el texto no numérico.
    # Un equipo vacío se normaliza como "Sin equipo".
    # Un diccionario agrupa los seis datos del ejercicio.
    # generar_nuevo_id revisa los IDs de la lista temporal.
    # Si la lista está vacía, el primer idEjercicio es uno.
    # Durante UPDATE los ejercicios anteriores conservan sus IDs.
    # Uno nuevo recibe el máximo existente más uno.
    # append incorpora el diccionario al final de la lista.
    # Agregar no escribe todavía entrenamientos.json.
    # La escritura ocurre al guardar todo el entrenamiento.
    # Por eso Cancelar puede descartar todos los cambios temporales.
    # La representación visual se reconstruye después de cada cambio.
    # Quitar utiliza una comprensión basada en idEjercicio.
    # Esa comprensión crea una lista nueva de forma segura.
    # La lambda del botón conserva el ID de su fila.
    # Los campos se limpian después de agregar correctamente.
    # focus_set prepara la captura del siguiente ejercicio.
    # Una entrada incorrecta conserva sus valores para corregirlos.
    # error_ejercicio muestra errores separados de los datos generales.
    # El modelo siempre guarda ejercicios como una lista.
    # Las copias evitan compartir un diccionario mutable por accidente.
    # READ recorre esta lista para presentar todos sus datos.
    # UPDATE vuelve a guardar la lista completa modificada.
    # DELETE principal elimina también sus ejercicios anidados.
    # Esto ocurre porque forman parte del mismo diccionario.
    # La estructura se convierte directamente al formato JSON.
    # Aquí se practican listas, ciclos, condicionales y diccionarios.

    # Los ejercicios se capturan uno a uno y permanecen en una lista temporal.
    def _crear_seccion_ejercicios(self):
        """Construye campos para agregar y quitar ejercicios antes de guardar."""

        # Un panel separado distingue los ejercicios de los datos principales.
        panel = ctk.CTkFrame(
            self.formulario,
            corner_radius=16,
            fg_color=self.colores["tarjeta"],
            border_width=1,
            border_color=self.colores["borde"],
        )
        panel.grid(row=12, column=0, columnspan=2, padx=28, pady=10, sticky="ew")

        # Cinco columnas distribuyen los datos compactos de un ejercicio.
        for columna in range(5):
            panel.grid_columnconfigure(columna, weight=1)

        # El título deja clara la relación anidada con el entrenamiento.
        ctk.CTkLabel(
            panel,
            text="EJERCICIOS",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colores["texto"],
        ).grid(row=0, column=0, columnspan=5, padx=16, pady=(14, 7), sticky="w")

        # Esta ayuda local crea etiquetas y campos dentro del panel de ejercicios.
        def campo_ejercicio(columna, texto, placeholder):
            ctk.CTkLabel(
                panel,
                text=texto,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=self.colores["texto_secundario"],
            ).grid(row=1, column=columna, padx=6, sticky="w")
            entrada = ctk.CTkEntry(
                panel,
                height=36,
                placeholder_text=placeholder,
                fg_color=self.colores["fondo"],
                border_color=self.colores["borde"],
            )
            entrada.grid(row=2, column=columna, padx=6, pady=(3, 8), sticky="ew")
            return entrada

        # Los cinco Entry corresponden exactamente al modelo de ejercicio solicitado.
        self.ejercicio_nombre = campo_ejercicio(0, "Nombre *", "Sentadilla")
        self.ejercicio_peso = campo_ejercicio(1, "Peso *", "0")
        self.ejercicio_series = campo_ejercicio(2, "Series *", "3")
        self.ejercicio_repeticiones = campo_ejercicio(3, "Repeticiones *", "10")
        self.ejercicio_equipo = campo_ejercicio(4, "Equipo", "Barra")

        # El botón valida y agrega un diccionario a self.ejercicios.
        ctk.CTkButton(
            panel,
            text="+ Agregar ejercicio",
            width=155,
            height=36,
            fg_color=self.colores["acento_secundario"],
            hover_color="#3D8DDB",
            command=self._agregar_ejercicio,
        ).grid(row=3, column=0, columnspan=5, pady=(2, 10))

        # Los errores del ejercicio aparecen dentro de su propia sección.
        self.error_ejercicio = ctk.CTkLabel(
            panel,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#FF6B6B",
        )
        self.error_ejercicio.grid(row=4, column=0, columnspan=5, padx=14)

        # Este Frame se reconstruye al agregar o quitar elementos de la lista.
        self.lista_ejercicios = ctk.CTkFrame(panel, fg_color="transparent")
        self.lista_ejercicios.grid(row=5, column=0, columnspan=5, padx=12, pady=(4, 12), sticky="ew")
        self.lista_ejercicios.grid_columnconfigure(0, weight=1)

    # La parte inferior confirma o cancela toda la operación.
    def _crear_acciones(self):
        """Crea los botones para cerrar o guardar el formulario."""

        # Un Frame transparente alinea ambos botones a la derecha.
        acciones = ctk.CTkFrame(self.formulario, fg_color="transparent")
        acciones.grid(row=13, column=0, columnspan=2, padx=28, pady=(8, 28), sticky="e")

        # Cancelar cierra la ventana sin tocar entrenamientos.json.
        ctk.CTkButton(
            acciones,
            text="Cancelar",
            width=120,
            fg_color=self.colores["tarjeta_clara"],
            hover_color=self.colores["borde"],
            command=self.destroy,
        ).pack(side="left", padx=6)

        # Guardar ejecuta CREATE o UPDATE según self.id_edicion.
        texto_boton = "Guardar entrenamiento" if self.id_edicion is None else "Guardar cambios"
        ctk.CTkButton(
            acciones,
            text=texto_boton,
            width=180,
            fg_color=self.colores["acento"],
            hover_color=self.colores["acento_hover"],
            text_color="#07130C",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._guardar,
        ).pack(side="left", padx=6)

    # Esta utilidad escribe un valor dentro de un Entry existente.
    def _rellenar_entrada(self, entrada, valor):
        """Limpia un Entry y coloca el valor recibido cuando no es None."""

        # delete evita mezclar el valor actual con el nuevo.
        entrada.delete(0, "end")
        if valor is not None:
            entrada.insert(0, str(valor))

    # UPDATE rellena todos los controles usando el diccionario persistido.
    def _cargar_datos(self, entrenamiento):
        """Coloca los valores actuales en el formulario de edición."""

        # Los Entry reciben texto aunque el JSON conserve números.
        self._rellenar_entrada(self.entrada_fecha, entrenamiento.get("fecha", ""))
        self._rellenar_entrada(self.entrada_rutina, entrenamiento.get("nombreRutina", ""))
        self._rellenar_entrada(self.entrada_peso, entrenamiento.get("pesoCorporal"))
        self._rellenar_entrada(self.entrada_duracion, entrenamiento.get("duracion", ""))

        # Los OptionMenu recuperan los valores guardados o alternativas seguras.
        self.selector_grupo.set(entrenamiento.get("grupoMuscular", "Seleccionar"))
        self.selector_categoria.set(entrenamiento.get("categoriaNota", "General"))
        self.selector_icono.set(entrenamiento.get("iconoGrupo", ICONOS_GRUPO[0]))

        # El nombre visible del color se obtiene a partir del hexadecimal persistido.
        color_guardado = entrenamiento.get("colorGrupo")
        nombre_color = next(
            (nombre for nombre, codigo in COLORES_GRUPO.items() if codigo == color_guardado),
            "Verde",
        )
        self.selector_color.set(nombre_color)

        # CTkTextbox usa índices de texto en lugar de posiciones numéricas simples.
        self.entrada_notas.delete("1.0", "end")
        self.entrada_notas.insert("1.0", entrenamiento.get("notas", ""))

    # El ejercicio se valida antes de incorporarlo a la lista temporal.
    def _agregar_ejercicio(self):
        """Construye un diccionario de ejercicio y actualiza su lista visual."""

        # El nombre se limpia y se verifica como campo obligatorio.
        nombre = self.ejercicio_nombre.get().strip()
        if not texto_no_vacio(nombre):
            self.error_ejercicio.configure(text="Escribe el nombre del ejercicio.")
            return

        # Los campos numéricos usan funciones que generan mensajes comprensibles.
        try:
            peso = convertir_numero_no_negativo(
                self.ejercicio_peso.get(), "El peso del ejercicio"
            )
            series = convertir_entero_positivo(self.ejercicio_series.get(), "Las series")
            repeticiones = convertir_entero_positivo(
                self.ejercicio_repeticiones.get(), "Las repeticiones"
            )
        except ValueError as error:
            self.error_ejercicio.configure(text=str(error))
            return

        # El equipo vacío se normaliza a un texto informativo.
        equipo = self.ejercicio_equipo.get().strip() or "Sin equipo"

        # El ID del ejercicio es uno mayor que el máximo de la lista actual.
        ejercicio = {
            "idEjercicio": generar_nuevo_id(self.ejercicios, "idEjercicio"),
            "nombreEjercicio": nombre,
            "pesoEjercicio": peso,
            "series": series,
            "repeticiones": repeticiones,
            "equipo": equipo,
        }

        # append agrega el diccionario al entrenamiento que todavía se está editando.
        self.ejercicios.append(ejercicio)
        self.error_ejercicio.configure(text="")
        self._limpiar_campos_ejercicio()
        self._dibujar_ejercicios()

    # Los campos quedan listos para capturar inmediatamente otro ejercicio.
    def _limpiar_campos_ejercicio(self):
        """Vacía las cinco entradas de la sección de ejercicios."""

        # Un ciclo evita repetir cinco llamadas idénticas a delete.
        for entrada in (
            self.ejercicio_nombre,
            self.ejercicio_peso,
            self.ejercicio_series,
            self.ejercicio_repeticiones,
            self.ejercicio_equipo,
        ):
            entrada.delete(0, "end")

        # El cursor vuelve al nombre para agilizar capturas consecutivas.
        self.ejercicio_nombre.focus_set()

    # La lista se vuelve a dibujar para reflejar altas y eliminaciones temporales.
    def _dibujar_ejercicios(self):
        """Muestra los ejercicios agregados y un botón para quitar cada uno."""

        # Se eliminan los renglones anteriores antes de presentar el estado actual.
        for componente in self.lista_ejercicios.winfo_children():
            componente.destroy()

        # El mensaje vacío explica que los ejercicios son opcionales en la captura.
        if not self.ejercicios:
            ctk.CTkLabel(
                self.lista_ejercicios,
                text="Todavía no agregas ejercicios.",
                text_color=self.colores["texto_secundario"],
            ).grid(row=0, column=0, pady=5, sticky="w")
            return

        # Cada ejercicio produce un resumen y una acción para quitarlo.
        for fila, ejercicio in enumerate(self.ejercicios):
            texto = (
                f"{ejercicio['nombreEjercicio']} · {ejercicio['pesoEjercicio']} kg · "
                f"{ejercicio['series']} x {ejercicio['repeticiones']} · {ejercicio['equipo']}"
            )
            ctk.CTkLabel(
                self.lista_ejercicios,
                text=texto,
                text_color=self.colores["texto"],
            ).grid(row=fila, column=0, padx=4, pady=4, sticky="w")

            # La lambda conserva el ID correspondiente a la fila actual.
            ctk.CTkButton(
                self.lista_ejercicios,
                text="Quitar",
                width=70,
                height=28,
                fg_color="#B94747",
                hover_color="#963939",
                command=lambda id_ejercicio=ejercicio["idEjercicio"]: self._quitar_ejercicio(
                    id_ejercicio
                ),
            ).grid(row=fila, column=1, padx=4, pady=4)

    # Quitar solo afecta la lista temporal hasta que se guarde el entrenamiento.
    def _quitar_ejercicio(self, id_ejercicio):
        """Elimina de la lista temporal el ejercicio que coincide con el ID."""

        # Una comprensión conserva todos los ejercicios excepto el seleccionado.
        self.ejercicios = [
            ejercicio
            for ejercicio in self.ejercicios
            if ejercicio.get("idEjercicio") != id_ejercicio
        ]
        self._dibujar_ejercicios()

    # GUÍA EDUCATIVA DE VALIDACIÓN Y FECHA:
    # _construir_entrenamiento revisa todo antes de escribir JSON.
    # validar_fecha conserva el requisito desarrollado en la Etapa 2.
    # La entrada usa obligatoriamente el formato dd/mm/aaaa.
    # Una fecha imposible provoca ValueError con un mensaje comprensible.
    # El resultado correcto queda en self.fecha_tupla.
    # Esa variable contiene exactamente (día, mes, año).
    # Los tres valores se desempaquetan en dia, mes y anio.
    # La tupla se usa para reconstruir la fecha almacenada.
    # :02d agrega cero a un día o mes de una cifra.
    # :04d conserva cuatro posiciones para el año.
    # CREATE y UPDATE llaman a esta misma función.
    # La fecha editada también vuelve a validarse y convertirse.
    # texto_no_vacio revisa el nombre después de quitar espacios.
    # "Seleccionar" representa que todavía falta elegir un grupo.
    # El peso corporal vacío se almacena como None.
    # JSON transforma None al valor null automáticamente.
    # Un peso proporcionado debe ser decimal y mayor que cero.
    # La duración debe ser un entero mayor que cero.
    # Las notas se limpian para retirar saltos finales.
    # Categoría, color e icono provienen de selectores sencillos.
    # COLORES_GRUPO traduce el nombre a código hexadecimal.
    # La lista de ejercicios se copia al diccionario final.
    # El resultado incluye todas las claves del modelo solicitado.
    # idEntrenamiento se asigna después, en la persistencia.
    # CREATE genera el ID leyendo los registros existentes.
    # UPDATE conserva el identificador original del registro.
    # Separar validación y guardado facilita probar cada parte.
    # ValueError detiene el flujo antes de obtener datos incompletos.
    # _guardar captura ese error y mantiene abierta la ventana.
    # Ninguna conversión inválida llega al archivo principal.
    # La validación protege las sumas usadas en el dashboard.
    # También garantiza fechas reales para encontrar la más reciente.
    # Cada mensaje identifica el campo que debe corregirse.
    # No se usan excepciones donde una condición simple es suficiente.

    # Esta función valida todos los campos antes de construir el diccionario final.
    def _construir_entrenamiento(self):
        """Devuelve un diccionario válido listo para CREATE o UPDATE."""

        # La fecha conserva el requisito de convertirse explícitamente a una tupla.
        self.fecha_tupla = validar_fecha(self.entrada_fecha.get())

        # La TUPLA (día, mes, año) se usa para reconstruir la fecha normalizada.
        dia, mes, anio = self.fecha_tupla
        fecha_normalizada = f"{dia:02d}/{mes:02d}/{anio:04d}"

        # Rutina y grupo son campos obligatorios del modelo.
        nombre_rutina = self.entrada_rutina.get().strip()
        if not texto_no_vacio(nombre_rutina):
            raise ValueError("Escribe el nombre de la rutina.")

        grupo_muscular = self.selector_grupo.get()
        if grupo_muscular == "Seleccionar":
            raise ValueError("Selecciona un grupo muscular.")

        # Un peso corporal vacío se guarda como None; si existe debe ser positivo.
        peso_texto = self.entrada_peso.get().strip()
        peso_corporal = None
        if peso_texto:
            peso_corporal = convertir_numero_positivo(peso_texto, "El peso corporal")

        # La duración siempre debe ser un entero mayor que cero.
        duracion = convertir_entero_positivo(self.entrada_duracion.get(), "La duración")

        # Los textos y selectores restantes no requieren conversiones numéricas.
        notas = self.entrada_notas.get("1.0", "end").strip()
        categoria = self.selector_categoria.get()
        color = COLORES_GRUPO[self.selector_color.get()]
        icono = self.selector_icono.get()

        # El diccionario respeta todos los nombres establecidos en el modelo original.
        return {
            "fecha": fecha_normalizada,
            "grupoMuscular": grupo_muscular,
            "pesoCorporal": peso_corporal,
            "duracion": duracion,
            "nombreRutina": nombre_rutina,
            "ejercicios": [ejercicio.copy() for ejercicio in self.ejercicios],
            "notas": notas,
            "categoriaNota": categoria,
            "colorGrupo": color,
            "iconoGrupo": icono,
        }

    # GUÍA EDUCATIVA DE GUARDADO Y EXCEPCIONES:
    # _guardar valida antes de elegir la operación CRUD.
    # ValueError agrupa problemas esperados de las entradas.
    # OSError agrupa problemas de acceso o escritura del archivo.
    # Ambos errores se muestran sin cerrar GymTracker.
    # CREATE se reconoce cuando id_edicion es None.
    # crear_entrenamiento lee primero los datos persistidos.
    # Después genera el ID, agrega el diccionario y guarda JSON.
    # UPDATE se reconoce cuando id_edicion contiene un número.
    # actualizar_entrenamiento localiza ese ID mediante un ciclo.
    # El nuevo diccionario reemplaza su posición y conserva el ID.
    # False evita anunciar éxito si el registro ya desapareció.
    # json.dump escribe la lista completa con indentación legible.
    # ensure_ascii=False conserva acentos e iconos directamente.
    # El mensaje de éxito aparece después de escribir el archivo.
    # El callback vuelve a leer JSON para refrescar la interfaz.
    # El dashboard utiliza esa misma colección actualizada.
    # Este orden evita presentar datos que no pudieron persistirse.
    # La ventana solo se destruye después del éxito.
    # Ante errores permanece abierta para permitir correcciones.
    # mainloop continúa activo durante todas las operaciones.
    # Las funciones CRUD pueden probarse sin abrir la interfaz.
    # Un archivo temporal permite verificar la persistencia con seguridad.
    # La separación es clara sin introducir patrones avanzados.
    # Todo el flujo utiliza funciones y estructuras básicas.

    # Guardar elige CREATE o UPDATE y mantiene el mismo ID durante la edición.
    def _guardar(self):
        """Valida el formulario, persiste el registro y actualiza la interfaz."""

        # Las entradas incorrectas generan mensajes sin cerrar GymTracker.
        try:
            entrenamiento = self._construir_entrenamiento()

            # Un ID ausente identifica el flujo CREATE.
            if self.id_edicion is None:
                crear_entrenamiento(entrenamiento)
                mensaje = "Entrenamiento guardado correctamente"
            else:
                # UPDATE conserva self.id_edicion dentro del registro reemplazado.
                actualizado = actualizar_entrenamiento(self.id_edicion, entrenamiento)
                if not actualizado:
                    raise ValueError("El entrenamiento que intentas editar ya no existe.")
                mensaje = "Entrenamiento actualizado correctamente"

        # ValueError corresponde a fechas, textos o números inválidos.
        except ValueError as error:
            self.etiqueta_error.configure(text=str(error), text_color="#FF6B6B")
            return

        # OSError informa problemas de permisos o escritura sin terminar el programa.
        except OSError:
            self.etiqueta_error.configure(
                text="No fue posible guardar entrenamientos.json.",
                text_color="#FF6B6B",
            )
            return

        # El callback actualiza lista y dashboard antes de cerrar el formulario.
        self.al_guardar(mensaje)
        self.destroy()
