"""Ventana principal, navegación y dashboard visual de GymTracker."""

# GUÍA GENERAL DE LA INTERFAZ:
# Este módulo coordina las pantallas visibles de la aplicación.
# No contiene un servidor porque GymTracker es una aplicación de escritorio.
# Tampoco utiliza una base de datos; la persistencia futura será mediante JSON.
# CustomTkinter extiende los componentes tradicionales de Tkinter.
# Los Frames sirven como contenedores para agrupar partes relacionadas.
# Los Labels presentan información que el usuario no modifica directamente.
# Los Entry capturan texto y los Button ejecutan funciones mediante command.
# grid distribuye widgets en filas y columnas dentro de un mismo padre.
# pack ordena widgets de forma consecutiva dentro de otro contenedor.
# place se reserva para centrar la tarjeta inicial en toda la ventana.
# Nunca se mezclan gestores de geometría dentro del mismo widget padre.
# Los atributos que comienzan con self pertenecen a la instancia actual.
# Esos atributos permiten consultar o actualizar un componente más adelante.
# Las variables sin self son temporales y simplifican un bloque concreto.
# Los callbacks conectan acciones visuales con métodos de Python.
# La aplicación mantiene una sola ventana principal durante toda la sesión.
# Las vistas se superponen y tkraise selecciona cuál queda al frente.
# Este enfoque evita abrir muchas ventanas o duplicar la navegación.
# La Etapa 3 conserva la sesión y agrega el CRUD local de entrenamientos.

# CustomTkinter proporciona widgets con un estilo moderno.
import customtkinter as ctk

# Las pantallas secundarias viven en archivos separados para mantener ordenado el proyecto.
from app.archivos import VistaArchivos
from app.calendario import VistaCalendario
from app.entrenamientos import VistaEntrenamientos

# La validación del nombre evita que una entrada incorrecta cierre la aplicación.
from app.validaciones import validar_fecha, validar_nombre_usuario

# Esta utilidad garantiza que la carpeta data esté lista al iniciar la aplicación.
from app.utilidades import cargar_entrenamientos, preparar_almacenamiento


# RESUMEN DEL FLUJO DE EVENTOS:
# main.py crea la ventana y activa su ciclo mediante mainloop.
# La pantalla inicial recibe el nickname y ejecuta su validación.
# Una entrada correcta genera el mensaje mediante concatenación de strings.
# after espera 1500 milisegundos mientras la interfaz continúa respondiendo.
# El dashboard actualiza su saludo con el nombre de la sesión.
# Los botones laterales alternan las vistas sin cerrar la ventana.
# Cambiar usuario restaura la captura y repite el mismo proceso.
# Agregar entrenamiento abre solamente la validación de fecha.
# Ninguno de estos eventos implementa todavía operaciones CRUD.

# La apariencia oscura combina con la identidad visual elegida para fitness.
ctk.set_appearance_mode("dark")

# El tema azul sirve como respaldo para los componentes sin color personalizado.
ctk.set_default_color_theme("blue")


# La paleta central facilita cambiar la apariencia sin buscar colores en todo el código.
# Cada clave describe el uso del color y cada valor usa notación hexadecimal.
# Centralizar la paleta reduce errores al copiar colores entre componentes.
# fondo se aplica al área general y tarjeta distingue los paneles interiores.
# borde separa elementos cercanos sin producir un contraste excesivo.
# acento identifica botones principales, estados correctos y selecciones.
# acento_hover comunica que un botón puede presionarse al pasar el cursor.
# texto se reserva para títulos y texto_secundario para explicaciones.
# advertencia permite diferenciar información que necesita atención.
# Ningún color modifica datos ni interviene en las validaciones.
# La paleta conserva sin cambios el diseño creado durante la Etapa 1.
COLORES = {
    "fondo": "#080D13",
    "barra_lateral": "#0E161F",
    "tarjeta": "#131E29",
    "tarjeta_clara": "#1A2936",
    "borde": "#284052",
    "acento": "#3DDE8A",
    "acento_hover": "#2FC779",
    "acento_suave": "#163D2B",
    "acento_secundario": "#69B7FF",
    "texto": "#F7FAFC",
    "texto_secundario": "#94A7B8",
    "advertencia": "#FFC15A",
}


# Esta es la clase que representa toda la ventana de escritorio.
class GymTrackerApp(ctk.CTk):
    """Administra la ventana principal y el cambio entre pantallas."""

    # GUÍA EDUCATIVA DE LA VENTANA PRINCIPAL:
    # Heredar de CTk convierte esta clase en la ventana raíz del programa.
    # __init__ se ejecuta una sola vez cuando main.py crea GymTrackerApp.
    # Primero se preparan tamaño, colores y distribución de la ventana.
    # Después se construyen la barra lateral y las vistas principales.
    # Finalmente se coloca la pantalla de nickname sobre el dashboard.
    # El nombre se guarda en memoria y desaparece al cerrar el programa.
    # No se crean usuarios permanentes, contraseñas ni sesiones remotas.
    # self.vistas relaciona textos del menú con objetos CTkFrame.
    # self.botones_navegacion permite actualizar el botón seleccionado.
    # La primera columna de la ventana contiene la barra lateral fija.
    # La segunda columna crece y contiene la pantalla actualmente visible.
    # weight=1 indica qué fila o columna recibe el espacio adicional.
    # sticky="nsew" estira un componente hacia los cuatro puntos cardinales.
    # La pantalla inicial usa columnspan=2 para cubrir ambas columnas.
    # Al retirarla, el dashboard ya construido queda visible de inmediato.
    # after se usa para tareas breves programadas dentro del ciclo gráfico.
    # De esta forma no se llama time.sleep ni se congela la aplicación.
    # Todos los cambios de usuario reutilizan los mismos componentes visuales.
    # Este flujo mantiene el proyecto sencillo y adecuado para fundamentos.

    # El constructor configura la ventana antes de mostrar cualquier contenido.
    def __init__(self):
        super().__init__()

        # Se prepara el archivo JSON sin borrar información que pudiera existir.
        preparar_almacenamiento()

        # El título aparece en la barra superior del sistema operativo.
        self.title("GymTracker | Tu progreso, un entrenamiento a la vez")

        # Una ventana amplia permite distribuir bien las tarjetas del dashboard.
        self.geometry("1340x840")

        # El tamaño mínimo evita que los componentes se encimen al reducir la ventana.
        self.minsize(1080, 700)

        # La ventana completa utiliza el color base de la aplicación.
        self.configure(fg_color=COLORES["fondo"])

        # La segunda columna y la primera fila reciben todo el espacio disponible.
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # El nombre solo vive durante la sesión; no representa una cuenta real.
        self.nombre_usuario = ""

        # Estos diccionarios relacionan nombres de sección con sus widgets.
        self.botones_navegacion = {}
        self.vistas = {}

        # Primero se construye la navegación fija del lado izquierdo.
        self._crear_barra_lateral()

        # Este contenedor mostrará solo una pantalla a la vez.
        self.contenedor = ctk.CTkFrame(self, fg_color=COLORES["fondo"], corner_radius=0)
        self.contenedor.grid(row=0, column=1, sticky="nsew")
        self.contenedor.grid_columnconfigure(0, weight=1)
        self.contenedor.grid_rowconfigure(0, weight=1)

        # Todas las vistas se crean una vez y luego se alterna su visibilidad.
        self._crear_vistas()

        # Las estadísticas iniciales se calculan con los datos persistidos.
        self.actualizar_datos()

        # El dashboard queda preparado debajo de la pantalla inicial de usuario.
        self.mostrar_vista("Inicio")

        # La solicitud de nickname cubre la aplicación antes de mostrar el dashboard.
        self._crear_pantalla_usuario()
        self.pantalla_usuario.tkraise()

        # Un pequeño retraso permite enfocar el campo cuando ya existe la ventana.
        self.after(100, self.entrada_nombre.focus_set)

    # La barra lateral conserva accesible la navegación principal.
    def _crear_barra_lateral(self):
        """Construye el logotipo, el menú y la tarjeta de calendario."""

        # GUÍA EDUCATIVA DE LA BARRA LATERAL:
        # La barra permanece visible cuando el usuario cambia de sección.
        # Un ancho fijo mantiene alineados los botones del menú.
        # grid_propagate(False) impide que sus hijos cambien ese ancho.
        # La marca superior identifica el proyecto en todo momento.
        # Las opciones se guardan en una tupla porque son datos constantes.
        # enumerate entrega simultáneamente la fila y los datos del botón.
        # lambda conserva el nombre correspondiente dentro de cada command.
        # Sin el argumento seccion=nombre, todos podrían usar el último valor.
        # El color de la opción activa ayuda a ubicar la pantalla actual.
        # La tarjeta verde refuerza el acceso visible al calendario.
        # Cambiar usuario no elimina registros ni modifica el archivo JSON.
        # Esa opción solo regresa al formulario inicial de nickname.
        # La fila flexible separa el menú de las acciones inferiores.
        # El texto final recuerda que la aplicación trabajará localmente.

        # El ancho fijo da estabilidad visual mientras cambia el contenido central.
        barra = ctk.CTkFrame(
            self,
            width=246,
            corner_radius=0,
            fg_color=COLORES["barra_lateral"],
            border_width=0,
        )
        barra.grid(row=0, column=0, sticky="nsw")
        barra.grid_propagate(False)
        barra.grid_rowconfigure(6, weight=1)

        # La marca combina un símbolo sencillo con el nombre del proyecto.
        marca = ctk.CTkFrame(barra, fg_color="transparent")
        marca.grid(row=0, column=0, padx=24, pady=(28, 30), sticky="ew")

        # El cuadro verde funciona como un logotipo sin requerir una imagen externa.
        insignia = ctk.CTkLabel(
            marca,
            text="G",
            width=44,
            height=44,
            corner_radius=12,
            fg_color=COLORES["acento"],
            text_color="#07130C",
            font=ctk.CTkFont(size=21, weight="bold"),
        )
        insignia.grid(row=0, column=0, padx=(0, 10))

        # El nombre queda visible durante toda la navegación.
        ctk.CTkLabel(
            marca,
            text="GymTracker",
            font=ctk.CTkFont(size=21, weight="bold"),
            text_color=COLORES["texto"],
        ).grid(row=0, column=1)

        # El rótulo separa la identidad de la lista de opciones.
        ctk.CTkLabel(
            barra,
            text="MENÚ PRINCIPAL",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORES["texto_secundario"],
        ).grid(row=1, column=0, padx=26, pady=(0, 8), sticky="w")

        # Cada tupla contiene el texto de la sección y un símbolo visual.
        opciones = (
            ("Inicio", "⌂"),
            ("Calendario", "▦"),
            ("Entrenamientos", "◎"),
            ("Archivos", "{ }")
        )

        # Se utiliza el mismo estilo para los cuatro botones de navegación.
        for fila, (nombre, icono) in enumerate(opciones, start=2):
            boton = ctk.CTkButton(
                barra,
                text=f"{icono}    {nombre}",
                width=204,
                height=46,
                corner_radius=12,
                anchor="w",
                border_spacing=14,
                fg_color="transparent",
                hover_color=COLORES["tarjeta_clara"],
                text_color=COLORES["texto_secundario"],
                font=ctk.CTkFont(size=14, weight="bold"),
                command=lambda seccion=nombre: self.mostrar_vista(seccion),
            )
            boton.grid(row=fila, column=0, padx=20, pady=4)

            # Guardar el botón permite resaltar después la opción seleccionada.
            self.botones_navegacion[nombre] = boton

        # Esta tarjeta funciona como acceso adicional y visible al calendario.
        acceso_calendario = ctk.CTkFrame(
            barra,
            width=204,
            height=132,
            corner_radius=16,
            fg_color=COLORES["acento_suave"],
        )
        acceso_calendario.grid(row=7, column=0, padx=20, pady=(18, 16), sticky="s")
        acceso_calendario.grid_propagate(False)

        # El título corto refuerza el propósito de esta llamada a la acción.
        ctk.CTkLabel(
            acceso_calendario,
            text="PLANIFICA TU SEMANA",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORES["acento"],
        ).pack(pady=(17, 7))

        # Este botón abre exactamente la misma vista que la opción del menú.
        ctk.CTkButton(
            acceso_calendario,
            text="Abrir calendario  →",
            width=172,
            height=40,
            corner_radius=10,
            fg_color=COLORES["acento"],
            hover_color=COLORES["acento_hover"],
            text_color="#07130C",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.abrir_calendario,
        ).pack()

        # Esta opción vuelve a solicitar el nombre sin crear cuentas ni contraseñas.
        ctk.CTkButton(
            barra,
            text="⇄    Cambiar usuario",
            width=204,
            height=40,
            corner_radius=10,
            fg_color="transparent",
            hover_color=COLORES["tarjeta_clara"],
            text_color=COLORES["texto_secundario"],
            command=self.cambiar_usuario,
        ).grid(row=8, column=0, padx=20, pady=(0, 8))

        # La etiqueta inferior comunica que el proyecto usa persistencia local.
        ctk.CTkLabel(
            barra,
            text="Datos guardados localmente",
            font=ctk.CTkFont(size=11),
            text_color="#627281",
        ).grid(row=9, column=0, pady=(0, 16))

    # Separar la creación de vistas hace más fácil agregar nuevas pantallas después.
    def _crear_vistas(self):
        """Crea y coloca las cuatro pantallas principales dentro del contenedor."""

        # GUÍA EDUCATIVA DE LAS VISTAS:
        # Cada vista recibe como master el mismo contenedor central.
        # Por ello todas pueden ocupar la fila cero y la columna cero.
        # tkraise decide cuál de ellas aparece sobre las demás.
        # Inicio recibe callbacks para abrir Entrenamientos y Calendario.
        # Entrenamientos recibe un callback para enfocar su entrada de fecha.
        # Los callbacks evitan que una vista hija controle directamente a la raíz.
        # Calendario y Archivos conservan el comportamiento de la etapa anterior.
        # Ninguna vista se destruye durante la navegación.
        # Esto permite conservar temporalmente la fecha escrita por el usuario.

        # El dashboard se encarga de presentar el resumen visual de la aplicación.
        self.vistas["Inicio"] = VistaInicio(
            self.contenedor,
            COLORES,
            al_agregar=self.abrir_formulario_entrenamiento,
            al_calendario=self.abrir_calendario,
        )

        # Entrenamientos informa cada cambio para refrescar el dashboard.
        self.vistas["Entrenamientos"] = VistaEntrenamientos(
            self.contenedor,
            COLORES,
            al_cambiar=self.actualizar_datos,
        )

        # El calendario reutiliza el formulario y el CRUD de Entrenamientos.
        self.vistas["Calendario"] = VistaCalendario(
            self.contenedor,
            COLORES,
            al_registrar=lambda fecha: self.vistas["Entrenamientos"].abrir_formulario(
                fecha_inicial=fecha
            ),
            al_editar=self.vistas["Entrenamientos"].abrir_formulario,
            al_cambiar=self.actualizar_datos,
        )

        # Archivos explica el uso futuro de la persistencia JSON.
        self.vistas["Archivos"] = VistaArchivos(self.contenedor, COLORES)

        # Todas las vistas ocupan la misma celda para poder alternarlas con tkraise.
        for vista in self.vistas.values():
            vista.grid(row=0, column=0, sticky="nsew")

    # Este acceso se reutiliza desde la barra lateral y desde Inicio.
    def abrir_calendario(self):
        """Navega de forma explícita a la vista diaria del calendario."""

        self.mostrar_vista("Calendario")

    # Este método es el centro de la navegación entre pantallas.
    def mostrar_vista(self, nombre):
        """Coloca al frente una vista y actualiza el botón activo del menú."""

        # Primero se muestra la sección; después se actualiza su contenido.
        # Así el botón siempre produce una navegación visible e inmediata.
        self.vistas[nombre].tkraise()

        # READ recarga el JSON cada vez que se abre la sección de entrenamientos.
        if nombre == "Entrenamientos":
            self.vistas[nombre].recargar_lista()

        # Calendario vuelve a leer el JSON para mostrar cambios recientes.
        if nombre == "Calendario":
            self.vistas[nombre].actualizar_vista()

        # Archivos vuelve a consultar data/registros para reflejar notas nuevas.
        if nombre == "Archivos":
            self.vistas[nombre].recargar_lista()

        # Primero se restaura el aspecto neutral de todos los botones.
        for boton in self.botones_navegacion.values():
            boton.configure(
                fg_color="transparent",
                text_color=COLORES["texto_secundario"],
            )

        # Después se resalta solo la sección que el usuario está viendo.
        self.botones_navegacion[nombre].configure(
            fg_color=COLORES["acento_suave"],
            text_color=COLORES["acento"],
        )


    # Esta pantalla se superpone al resto hasta que exista un nombre válido.
    def _crear_pantalla_usuario(self):
        """Construye la solicitud inicial de nombre o nickname."""

        # GUÍA EDUCATIVA DEL USUARIO DE SESIÓN:
        # Esta pantalla no es un login porque no verifica ninguna identidad.
        # Su único objetivo es obtener un texto para personalizar el saludo.
        # La tarjeta se centra con coordenadas relativas entre cero y uno.
        # relx=0.5 y rely=0.5 representan la mitad del ancho y de la altura.
        # anchor="center" coloca el centro de la tarjeta en ese punto.
        # El nombre no se escribe en archivos y no sobrevive al cierre.
        # La validación ocurre al pulsar Continuar o al presionar Enter.
        # Un mensaje rojo explica una entrada inválida sin lanzar la aplicación.
        # Una entrada correcta reemplaza la pregunta por la bienvenida.
        # Los controles se ocultan mientras se muestra la transición.
        # grid_remove conserva la configuración para poder restaurarlos.
        # El texto "Preparando tu espacio" informa que existe una espera breve.
        # simular_espera programa el siguiente paso sin bloquear eventos.
        # Al cambiar usuario, los textos y el campo vuelven a su estado inicial.
        # focus_set deja el cursor preparado para comenzar a escribir.
        # La misma pantalla se reutiliza y no se crea una ventana adicional.
        # Esta decisión evita complejidad innecesaria para el proyecto académico.
        # No hay contraseñas, permisos, cuentas ni autenticación real.
        # El flujo solo representa al usuario actual de la sesión local.

        # El Frame ocupa las dos columnas para ocultar temporalmente la navegación.
        self.pantalla_usuario = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=COLORES["fondo"],
        )
        self.pantalla_usuario.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # La tarjeta central conserva el mismo lenguaje visual que el dashboard.
        tarjeta = ctk.CTkFrame(
            self.pantalla_usuario,
            width=500,
            height=500,
            corner_radius=24,
            fg_color=COLORES["tarjeta"],
            border_width=1,
            border_color=COLORES["borde"],
        )
        tarjeta.place(relx=0.5, rely=0.5, anchor="center")
        tarjeta.grid_propagate(False)
        tarjeta.grid_columnconfigure(0, weight=1)

        # La insignia identifica la aplicación sin utilizar recursos externos.
        ctk.CTkLabel(
            tarjeta,
            text="G",
            width=58,
            height=58,
            corner_radius=17,
            fg_color=COLORES["acento"],
            text_color="#07130C",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).grid(row=0, column=0, pady=(48, 12))

        # El nombre del proyecto permanece visible durante la captura del usuario.
        ctk.CTkLabel(
            tarjeta,
            text="GymTracker",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=COLORES["texto"],
        ).grid(row=1, column=0)

        # Esta etiqueta también mostrará el string de bienvenida construido después.
        self.etiqueta_pregunta = ctk.CTkLabel(
            tarjeta,
            text="Antes de comenzar, ¿cómo te llamas?",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORES["texto"],
        )
        self.etiqueta_pregunta.grid(row=2, column=0, padx=35, pady=(30, 6))

        # El texto aclara que el nickname solo personaliza la sesión actual.
        self.etiqueta_descripcion = ctk.CTkLabel(
            tarjeta,
            text="Usaremos tu nombre para personalizar tu espacio.",
            font=ctk.CTkFont(size=13),
            text_color=COLORES["texto_secundario"],
        )
        self.etiqueta_descripcion.grid(row=3, column=0, padx=35, pady=(0, 18))

        # El campo acepta el nombre que posteriormente aparecerá en el dashboard.
        self.entrada_nombre = ctk.CTkEntry(
            tarjeta,
            width=330,
            height=46,
            corner_radius=12,
            placeholder_text="Nombre o nickname",
            border_color=COLORES["borde"],
            fg_color=COLORES["fondo"],
        )
        self.entrada_nombre.grid(row=4, column=0)

        # La tecla Enter ofrece una alternativa al botón Continuar.
        self.entrada_nombre.bind("<Return>", lambda evento: self._procesar_nombre())

        # El mensaje de validación empieza vacío y no ocupa datos del usuario.
        self.etiqueta_error_nombre = ctk.CTkLabel(
            tarjeta,
            text="",
            height=30,
            font=ctk.CTkFont(size=12),
            text_color="#FF6B6B",
        )
        self.etiqueta_error_nombre.grid(row=5, column=0, padx=30, pady=(4, 0))

        # Continuar ejecuta la validación, pero no cierra la aplicación ante errores.
        self.boton_continuar = ctk.CTkButton(
            tarjeta,
            text="Continuar",
            width=180,
            height=44,
            corner_radius=12,
            fg_color=COLORES["acento"],
            hover_color=COLORES["acento_hover"],
            text_color="#07130C",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._procesar_nombre,
        )
        self.boton_continuar.grid(row=6, column=0, pady=(4, 35))

    # Este método conecta la validación del nickname con el saludo visual.
    def _procesar_nombre(self):
        """Valida el nombre y presenta la bienvenida antes del dashboard."""

        # La función devuelve un indicador y un nombre limpio o mensaje de error.
        es_valido, resultado = validar_nombre_usuario(self.entrada_nombre.get())

        # Una entrada incorrecta solo muestra ayuda y permite volver a intentarlo.
        if not es_valido:
            self.etiqueta_error_nombre.configure(text=resultado, text_color="#FF6B6B")
            self.entrada_nombre.focus_set()
            return

        # El nombre validado se conserva únicamente mientras la aplicación está abierta.
        self.nombre_usuario = resultado

        # OPERACIÓN CON STRINGS: se concatena texto con el nombre escrito por el usuario.
        mensaje_bienvenida = "¡Bienvenida, " + self.nombre_usuario + "!"

        # La captura se oculta para mostrar claramente el resultado de la operación.
        self.entrada_nombre.grid_remove()
        self.boton_continuar.grid_remove()
        self.etiqueta_pregunta.configure(text=mensaje_bienvenida)
        self.etiqueta_descripcion.configure(text="Tu espacio personal está casi listo.")
        self.etiqueta_error_nombre.configure(
            text="Preparando tu espacio...",
            text_color=COLORES["acento"],
        )

        # La transición se inicia después de presentar visualmente la bienvenida.
        self.simular_espera()

    # La función existe de forma explícita para cumplir el requisito académico.
    def simular_espera(self):
        """Simula una espera de 1.5 segundos sin congelar la interfaz gráfica."""

        # after programa la transición y permite que la ventana siga respondiendo.
        # 1500 milisegundos equivalen a 1.5 segundos y nunca superan los 5 segundos.
        self.after(1500, self._mostrar_dashboard)

    # Este método termina la transición y personaliza la pantalla de Inicio.
    def _mostrar_dashboard(self):
        """Oculta la captura de usuario y muestra el dashboard personalizado."""

        # El dashboard recibe el nombre real capturado, no un valor escrito en el código.
        self.vistas["Inicio"].actualizar_usuario(self.nombre_usuario)

        # Los contadores vuelven a leer el archivo al entrar con otro usuario.
        self.actualizar_datos()

        # Se selecciona Inicio y después se retira la pantalla superpuesta.
        self.mostrar_vista("Inicio")
        self.pantalla_usuario.grid_remove()

    # La opción lateral reinicia la captura sin manejar cuentas persistentes.
    def cambiar_usuario(self):
        """Regresa a la pantalla de nombre para iniciar otra sesión local."""

        # Se borra el nombre anterior tanto de la variable como del campo visual.
        self.nombre_usuario = ""
        self.entrada_nombre.delete(0, "end")

        # Las etiquetas recuperan sus textos originales para el siguiente usuario.
        self.etiqueta_pregunta.configure(text="Antes de comenzar, ¿cómo te llamas?")
        self.etiqueta_descripcion.configure(
            text="Usaremos tu nombre para personalizar tu espacio."
        )
        self.etiqueta_error_nombre.configure(text="", text_color="#FF6B6B")

        # Los controles ocultos durante la bienvenida vuelven a su misma posición.
        self.entrada_nombre.grid()
        self.boton_continuar.grid()

        # grid restaura la pantalla y tkraise garantiza que quede sobre el dashboard.
        self.pantalla_usuario.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.pantalla_usuario.tkraise()
        self.entrada_nombre.focus_set()

    # Los accesos de Inicio y Entrenamientos comparten el formulario de CREATE.
    def abrir_formulario_entrenamiento(self):
        """Muestra Entrenamientos y abre un formulario nuevo."""

        # El listado queda visible debajo de la ventana secundaria del formulario.
        self.mostrar_vista("Entrenamientos")
        self.vistas["Entrenamientos"].abrir_formulario()

    # Esta función conecta la persistencia con los indicadores del dashboard.
    def actualizar_datos(self):
        """Lee el JSON y actualiza las estadísticas sencillas de Inicio."""

        # cargar_entrenamientos devuelve una lista segura incluso ante JSON inválido.
        entrenamientos = cargar_entrenamientos()

        # La vista de Inicio calcula totales sin modificar la colección recibida.
        self.vistas["Inicio"].actualizar_estadisticas(entrenamientos)

        # Las vistas de consulta también reflejan inmediatamente cada escritura.
        self.vistas["Entrenamientos"].recargar_lista()
        self.vistas["Calendario"].actualizar_vista()


# El dashboard conserva el desplazamiento dentro de una vista raíz estable.
class VistaInicio(ctk.CTkFrame):
    """Presenta el resumen visual de GymTracker con datos iniciales."""

    # GUÍA EDUCATIVA DEL DASHBOARD:
    # CTkScrollableFrame permite desplazarse si la altura disponible es menor.
    # Esta característica mejora el uso sin cambiar el diseño principal.
    # Dos columnas distribuyen las estadísticas inferiores del resumen.
    # El encabezado combina la marca, el saludo y la acción principal.
    # La etiqueta de saludo se conserva en self para actualizar su contenido.
    # actualizar_usuario recibe el nombre validado desde GymTrackerApp.
    # Una f-string inserta el nombre dentro del mensaje mostrado.
    # El salto de línea separa el saludo de la frase motivadora.
    # Las tarjetas numéricas permanecen en cero al no existir CRUD.
    # El último entrenamiento se calcula con datos reales o muestra un estado vacío.
    # Las barras inferiores continúan marcadas como vistas previas.
    # Por lo tanto no se presentan estadísticas inventadas como resultados.
    # Cada sección del dashboard se construye mediante un método privado.
    # El prefijo de guión bajo indica uso interno dentro de la clase.
    # El callback al_agregar abre exclusivamente la captura inicial de fecha.
    # El callback al_calendario conserva el acceso preparado en la Etapa 1.
    # Los colores llegan desde la misma paleta usada por toda la aplicación.
    # Ningún elemento de este dashboard escribe directamente en el JSON.
    # La personalización visual tampoco crea una cuenta persistente.

    # Se reciben acciones para no acoplar el dashboard a la ventana principal.
    def __init__(self, master, colores, al_agregar, al_calendario):
        super().__init__(master, fg_color=colores["fondo"], corner_radius=0)

        # Estas referencias se usarán en los botones de acceso rápido.
        self.colores = colores
        self.al_agregar = al_agregar
        self.al_calendario = al_calendario

        # El diccionario permite actualizar los tres valores sin reconstruir tarjetas.
        self.etiquetas_resumen = {}

        # La raíz normal permite que tkraise muestre Inicio correctamente. El
        # desplazamiento queda dentro de ella para conservar el diseño adaptable.
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.contenido = ctk.CTkScrollableFrame(
            self,
            fg_color=colores["fondo"],
            corner_radius=0,
            scrollbar_button_color=colores["borde"],
            scrollbar_button_hover_color=colores["acento"],
        )
        self.contenido.grid(row=0, column=0, sticky="nsew")

        # Dos columnas permiten colocar las secciones inferiores una junto a otra.
        self.contenido.grid_columnconfigure(0, weight=3, uniform="panel")
        self.contenido.grid_columnconfigure(1, weight=2, uniform="panel")

        # El dashboard se divide en bloques para mantener el código legible.
        self._crear_bienvenida()
        self._crear_resumen()
        self._crear_ultimo_entrenamiento()
        self._crear_grupos_musculares()
        self._crear_actividad_semanal()

    # El primer bloque saluda y muestra la acción principal.
    def _crear_bienvenida(self):
        """Crea el encabezado de bienvenida del dashboard."""

        # Una tarjeta amplia reúne la identidad, el saludo y la acción principal.
        encabezado = ctk.CTkFrame(
            self.contenido,
            corner_radius=22,
            fg_color=self.colores["tarjeta"],
            border_width=1,
            border_color=self.colores["borde"],
        )
        encabezado.grid(row=0, column=0, columnspan=2, sticky="ew", padx=22, pady=(22, 12))
        encabezado.grid_columnconfigure(0, weight=1)

        # Este contenedor agrupa el título y el mensaje de bienvenida.
        textos = ctk.CTkFrame(encabezado, fg_color="transparent")
        textos.grid(row=0, column=0, padx=28, pady=24, sticky="w")

        ctk.CTkLabel(
            textos,
            text="PÁGINA PRINCIPAL  ·  TU PROGRESO",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.colores["acento"],
        ).pack(anchor="w", pady=(0, 5))

        # El nombre grande deja clara la identidad de la aplicación.
        ctk.CTkLabel(
            textos,
            text="GymTracker",
            font=ctk.CTkFont(size=34, weight="bold"),
            text_color=self.colores["texto"],
        ).pack(anchor="w")

        # La etiqueta se guarda para actualizarla con el nombre capturado.
        self.etiqueta_saludo = ctk.CTkLabel(
            textos,
            text="Hola 👋  Este es el resumen de tu progreso.",
            font=ctk.CTkFont(size=14),
            text_color=self.colores["texto_secundario"],
            justify="left",
        )
        self.etiqueta_saludo.pack(anchor="w", pady=(4, 0))

        # Este es el acceso principal solicitado para agregar un entrenamiento.
        ctk.CTkButton(
            encabezado,
            text="+  Agregar entrenamiento",
            width=200,
            height=46,
            corner_radius=13,
            fg_color=self.colores["acento"],
            hover_color=self.colores["acento_hover"],
            text_color="#07130C",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.al_agregar,
        ).grid(row=0, column=1, padx=28, pady=24, sticky="e")


    # La ventana principal llama este método al terminar la espera de bienvenida.
    def actualizar_usuario(self, nombre):
        """Actualiza el saludo del dashboard con el nombre de la sesión."""

        # Una f-string combina el saludo con el valor capturado en la pantalla inicial.
        saludo = f"Hola, {nombre} 👋  Este es el resumen de tu progreso."

        # configure cambia el texto sin reconstruir el resto del dashboard.
        self.etiqueta_saludo.configure(text=saludo)


    # GUÍA DE ACTUALIZACIÓN DEL DASHBOARD:
    # La vista recibe la lista ya cargada y no abre el archivo por su cuenta.
    # Cada indicador se deriva con len, sum o un ciclo sencillo.
    # Los valores se convierten a texto antes de mostrarse.
    # Una duración antigua inválida se ignora con try/except.
    # validar_fecha permite comparar las fechas cronológicamente.
    # Para ordenar se cambia la tupla a (año, mes, día).
    # max encuentra el registro más reciente mediante esa clave.
    # Los cálculos se repiten tras CREATE, UPDATE y DELETE.
    # Ninguna gráfica compleja se conecta durante esta etapa.

    # Las estadísticas sencillas se calculan directamente a partir de listas y ciclos.
    def actualizar_estadisticas(self, entrenamientos):
        """Actualiza totales y muestra el entrenamiento de fecha más reciente."""

        # len obtiene la cantidad total de diccionarios guardados.
        total_entrenamientos = len(entrenamientos)

        # sum cuenta cada ejercicio anidado dentro de todos los entrenamientos.
        total_ejercicios = sum(
            len(entrenamiento.get("ejercicios", []))
            for entrenamiento in entrenamientos
        )

        # Las duraciones inválidas de archivos antiguos se ignoran de forma segura.
        total_minutos = 0
        for entrenamiento in entrenamientos:
            try:
                total_minutos += int(entrenamiento.get("duracion", 0))
            except (TypeError, ValueError):
                continue

        # configure modifica solo el texto numérico de las tarjetas existentes.
        self.etiquetas_resumen["Entrenamientos"].configure(text=str(total_entrenamientos))
        self.etiquetas_resumen["Ejercicios"].configure(text=str(total_ejercicios))
        self.etiquetas_resumen["Minutos entrenados"].configure(text=str(total_minutos))

        # Un estado vacío se conserva cuando la lista no contiene registros.
        if not entrenamientos:
            self.etiqueta_ultimo_entrenamiento.configure(
                text="Aún no hay entrenamientos registrados. Tu próxima sesión aparecerá aquí."
            )
            self.etiqueta_icono_ultimo.configure(
                text="○", text_color=self.colores["texto_secundario"]
            )
            return

        # Esta función transforma dd/mm/aaaa a (año, mes, día) para ordenar.
        def clave_fecha(entrenamiento):
            try:
                dia, mes, anio = validar_fecha(entrenamiento.get("fecha", ""))
                return anio, mes, dia
            except (TypeError, ValueError):
                return 0, 0, 0

        # max localiza el entrenamiento más reciente según la fecha validada.
        ultimo = max(entrenamientos, key=clave_fecha)
        self.etiqueta_icono_ultimo.configure(
            text=ultimo.get("iconoGrupo", "◎"), text_color=self.colores["acento"]
        )
        texto_ultimo = (
            f"{ultimo.get('nombreRutina', 'Sin nombre')}\n"
            f"{ultimo.get('fecha', 'Sin fecha')} • "
            f"{ultimo.get('grupoMuscular', 'Sin grupo')} • "
            f"{ultimo.get('duracion', 0)} min"
        )
        self.etiqueta_ultimo_entrenamiento.configure(text=texto_ultimo)


    # Las tres tarjetas muestran contadores en cero hasta contar con datos reales.
    def _crear_resumen(self):
        """Construye las tarjetas de entrenamientos, ejercicios y minutos."""

        # GUÍA EDUCATIVA DEL RESUMEN:
        # Un Frame transparente agrupa las tres tarjetas sin agregar otro fondo.
        # uniform asigna el mismo tamaño visual a sus tres columnas.
        # Cada tupla contiene título, valor, símbolo y color del indicador.
        # El operador * desempaqueta esos cuatro datos al llamar la función.
        # Esta técnica reduce bloques duplicados y mantiene el orden visible.
        # Los contadores no se conectan todavía con entrenamientos.json.
        # Mostrar cero representa correctamente una instalación sin registros.
        # Los símbolos de texto evitan requerir archivos de imagen adicionales.
        # La tarjeta reutilizable recibe su posición como un parámetro.
        # rowspan permite al símbolo cubrir las filas de título y valor.
        # Los bordes suaves diferencian las tarjetas sobre el fondo oscuro.
        # Esta parte conserva el diseño original solicitado en la Etapa 1.
        # La Etapa 3 calcula solo totales; las barras musculares siguen como vista previa.
        # Los valores reales se incorporarán cuando exista el CRUD completo.

        # Este contenedor ocupa el ancho completo y reparte tres columnas iguales.
        resumen = ctk.CTkFrame(self.contenido, fg_color="transparent")
        resumen.grid(row=1, column=0, columnspan=2, sticky="ew", padx=14, pady=4)

        # Cada columna tiene el mismo peso para mantener tarjetas equilibradas.
        for columna in range(3):
            resumen.grid_columnconfigure(columna, weight=1, uniform="resumen")

        # Los valores empiezan en cero y se reemplazan al cargar los datos reales del JSON.
        tarjetas = (
            ("Entrenamientos", "0", "◎", self.colores["acento"]),
            ("Ejercicios", "0", "+", self.colores["acento_secundario"]),
            ("Minutos entrenados", "0", "◷", self.colores["advertencia"]),
        )

        # La función auxiliar evita repetir la configuración de cada tarjeta.
        for columna, datos in enumerate(tarjetas):
            self._crear_tarjeta_resumen(resumen, columna, *datos)

    # Una función pequeña encapsula la estructura repetida de los indicadores.
    def _crear_tarjeta_resumen(self, master, columna, titulo, valor, icono, color):
        """Dibuja una tarjeta numérica dentro del contenedor indicado."""

        # La tarjeta utiliza borde sutil para separarse del fondo oscuro.
        tarjeta = ctk.CTkFrame(
            master,
            height=128,
            corner_radius=18,
            fg_color=self.colores["tarjeta"],
            border_width=1,
            border_color=self.colores["borde"],
        )
        tarjeta.grid(row=0, column=columna, sticky="nsew", padx=8, pady=8)
        tarjeta.grid_propagate(False)
        tarjeta.grid_columnconfigure(1, weight=1)

        # Una línea de acento identifica visualmente cada tipo de indicador.
        ctk.CTkFrame(
            tarjeta,
            width=4,
            height=76,
            corner_radius=3,
            fg_color=color,
        ).grid(row=0, column=0, rowspan=2, padx=(15, 0), pady=18, sticky="ns")

        # El nombre del indicador se muestra en la esquina superior izquierda.
        ctk.CTkLabel(
            tarjeta,
            text=titulo,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colores["texto_secundario"],
        ).grid(row=0, column=1, padx=16, pady=(20, 4), sticky="w")

        # El valor se conserva para reemplazarlo cuando cambie el archivo JSON.
        etiqueta_valor = ctk.CTkLabel(
            tarjeta,
            text=valor,
            font=ctk.CTkFont(size=34, weight="bold"),
            text_color=self.colores["texto"],
        )
        etiqueta_valor.grid(row=1, column=1, padx=16, sticky="w")

        # El título funciona como llave para Entrenamientos, Ejercicios y Minutos.
        self.etiquetas_resumen[titulo] = etiqueta_valor

        # El icono usa el color propio de cada tipo de resumen.
        ctk.CTkLabel(
            tarjeta,
            text=icono,
            width=42,
            height=42,
            corner_radius=12,
            fg_color=self.colores["tarjeta_clara"],
            text_color=color,
            font=ctk.CTkFont(size=23, weight="bold"),
        ).grid(row=0, column=2, rowspan=2, padx=18, pady=20)

    # El panel de último entrenamiento comienza con un estado vacío honesto.
    def _crear_ultimo_entrenamiento(self):
        """Crea la sección que después mostrará el registro más reciente."""

        # La tarjeta se extiende por todo el ancho antes de las estadísticas inferiores.
        panel = ctk.CTkFrame(
            self.contenido,
            corner_radius=18,
            fg_color=self.colores["tarjeta"],
            border_width=1,
            border_color=self.colores["borde"],
        )
        panel.grid(row=2, column=0, columnspan=2, sticky="ew", padx=22, pady=12)
        panel.grid_columnconfigure(1, weight=1)

        self.etiqueta_icono_ultimo = ctk.CTkLabel(
            panel,
            text="○",
            width=78,
            height=78,
            corner_radius=18,
            fg_color=self.colores["tarjeta_clara"],
            text_color=self.colores["texto_secundario"],
            font=ctk.CTkFont(size=32, weight="bold"),
        )
        self.etiqueta_icono_ultimo.grid(
            row=0, column=0, rowspan=2, padx=(22, 16), pady=22
        )

        # El encabezado nombra la sección solicitada en el dashboard.
        ctk.CTkLabel(
            panel,
            text="Último entrenamiento",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=self.colores["texto"],
        ).grid(row=0, column=1, pady=(22, 4), sticky="sw")

        # Esta etiqueta se actualiza con el registro de fecha más reciente.
        self.etiqueta_ultimo_entrenamiento = ctk.CTkLabel(
            panel,
            text="Aún no hay entrenamientos registrados. Tu próxima sesión aparecerá aquí.",
            font=ctk.CTkFont(size=13),
            text_color=self.colores["texto_secundario"],
            justify="left",
        )
        self.etiqueta_ultimo_entrenamiento.grid(
            row=1, column=1, pady=(3, 22), sticky="nw"
        )

        # El botón ofrece otra ruta visible hacia el futuro formulario.
        ctk.CTkButton(
            panel,
            text="Comenzar  →",
            width=112,
            height=34,
            corner_radius=10,
            fg_color="transparent",
            border_width=1,
            border_color=self.colores["acento"],
            hover_color=self.colores["acento_suave"],
            text_color=self.colores["acento"],
            command=self.al_agregar,
        ).grid(row=0, column=2, rowspan=2, padx=22)

    # Esta sección es una vista previa y no pretende representar estadísticas reales.
    def _crear_grupos_musculares(self):
        """Muestra una maqueta de la distribución por grupo muscular."""

        # El panel ocupa la columna izquierda del dashboard inferior.
        panel = ctk.CTkFrame(
            self.contenido,
            corner_radius=18,
            fg_color=self.colores["tarjeta"],
            border_width=1,
            border_color=self.colores["borde"],
        )
        panel.grid(row=3, column=0, sticky="nsew", padx=(22, 10), pady=(4, 24))
        panel.grid_columnconfigure(0, weight=1)

        # El encabezado aclara que se trata de una representación visual futura.
        ctk.CTkLabel(
            panel,
            text="Grupos musculares",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=self.colores["texto"],
        ).grid(row=0, column=0, padx=20, pady=(18, 2), sticky="w")

        # Esta etiqueta evita confundir las barras de ejemplo con resultados reales.
        ctk.CTkLabel(
            panel,
            text="Vista previa · sin datos todavía",
            font=ctk.CTkFont(size=11),
            text_color=self.colores["texto_secundario"],
        ).grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")

        # Cada elemento define un grupo, un color y una longitud puramente decorativa.
        grupos = (
            ("Pecho", 0.72, self.colores["acento"]),
            ("Espalda", 0.58, self.colores["acento_secundario"]),
            ("Pierna", 0.44, self.colores["advertencia"]),
        )

        # Las barras anticipan el tipo de estadística que se conectará en otra etapa.
        for fila, (nombre, progreso, color) in enumerate(grupos, start=2):
            ctk.CTkLabel(
                panel,
                text=nombre,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.colores["texto_secundario"],
            ).grid(row=fila * 2, column=0, padx=20, pady=(5, 2), sticky="w")

            # La barra no tiene texto numérico porque todavía no existe un cálculo real.
            barra = ctk.CTkProgressBar(
                panel,
                height=8,
                corner_radius=4,
                fg_color=self.colores["tarjeta_clara"],
                progress_color=color,
            )
            barra.grid(row=fila * 2 + 1, column=0, padx=20, pady=(0, 6), sticky="ew")
            barra.set(progreso)

    # La actividad semanal utiliza barras verticales sencillas y etiquetas de días.
    def _crear_actividad_semanal(self):
        """Construye una vista previa de la actividad de una semana."""

        # El panel derecho complementa la distribución por grupo muscular.
        panel = ctk.CTkFrame(
            self.contenido,
            corner_radius=18,
            fg_color=self.colores["tarjeta"],
            border_width=1,
            border_color=self.colores["borde"],
        )
        panel.grid(row=3, column=1, sticky="nsew", padx=(10, 22), pady=(4, 24))

        # Las siete columnas representan los días de la semana.
        for columna in range(7):
            panel.grid_columnconfigure(columna, weight=1)

        # El título ocupa todas las columnas del pequeño gráfico.
        ctk.CTkLabel(
            panel,
            text="Actividad semanal",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=self.colores["texto"],
        ).grid(row=0, column=0, columnspan=4, padx=20, pady=(18, 2), sticky="w")

        # Este botón usa el callback de Calendario que antes no estaba conectado.
        ctk.CTkButton(
            panel,
            text="Ver calendario  →",
            width=118,
            height=32,
            corner_radius=9,
            fg_color=self.colores["acento_suave"],
            hover_color=self.colores["acento"],
            text_color=self.colores["acento"],
            command=self.al_calendario,
        ).grid(row=0, column=4, columnspan=3, padx=16, pady=(15, 0), sticky="e")

        # Se especifica que las alturas actuales son solo parte del diseño inicial.
        ctk.CTkLabel(
            panel,
            text="Vista previa",
            font=ctk.CTkFont(size=11),
            text_color=self.colores["texto_secundario"],
        ).grid(row=1, column=0, columnspan=7, padx=20, sticky="w")

        # Los valores decorativos permiten apreciar el aspecto futuro del gráfico.
        dias = (("L", 34), ("M", 58), ("X", 42), ("J", 76), ("V", 50), ("S", 68), ("D", 28))

        # Cada barra se alinea en la parte inferior para sugerir una gráfica real.
        for columna, (dia, altura) in enumerate(dias):
            contenedor_barra = ctk.CTkFrame(panel, fg_color="transparent", height=112)
            contenedor_barra.grid(row=2, column=columna, padx=4, pady=(12, 0), sticky="s")
            contenedor_barra.grid_propagate(False)

            # La barra activa usa verde y un fondo oscuro para mantener buen contraste.
            ctk.CTkFrame(
                contenedor_barra,
                width=14,
                height=altura,
                corner_radius=7,
                fg_color=self.colores["acento"],
            ).pack(side="bottom", pady=2)

            # Una letra compacta identifica cada día debajo de su barra.
            ctk.CTkLabel(
                panel,
                text=dia,
                font=ctk.CTkFont(size=11),
                text_color=self.colores["texto_secundario"],
            ).grid(row=3, column=columna, pady=(0, 14))
