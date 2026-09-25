"""Lectura, escritura y creación de notas personales de GymTracker."""

# CustomTkinter mantiene el diseño oscuro y verde de la aplicación.
import customtkinter as ctk

# GUI y consola reutilizan estas funciones puras sin duplicar su lógica.
from app.gestor_archivos import (
    crear_archivo,
    escribir_archivo,
    leer_archivo,
    listar_archivos,
)


# Esta clase presenta la lista y el editor dentro de la navegación principal.
class VistaArchivos(ctk.CTkFrame):
    """Permite consultar, editar y crear notas personales de entrenamiento."""

    # La vista recibe la paleta para conservar la apariencia de GymTracker.
    def __init__(self, master, colores):
        super().__init__(master, fg_color=colores["fondo"])

        # Estos atributos representan el estado actual de la pantalla.
        self.colores = colores
        self.archivos_disponibles = []
        self.archivo_seleccionado = None
        self.botones_archivos = {}

        # La zona de contenido se expande junto con la ventana principal.
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # La pantalla se divide en encabezado, estado y dos paneles.
        self._crear_encabezado()
        self._crear_paneles()
        self.recargar_lista()

    # El encabezado conserva el mismo estilo utilizado en otras secciones.
    def _crear_encabezado(self):
        """Crea el título y la etiqueta utilizada para mensajes."""

        # El título identifica claramente la sección seleccionada.
        ctk.CTkLabel(
            self,
            text="Archivos",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=self.colores["texto"],
        ).grid(row=0, column=0, sticky="w", padx=34, pady=(28, 4))

        # Los resultados y errores se presentan sin cerrar la aplicación.
        self.etiqueta_estado = ctk.CTkLabel(
            self,
            text="Selecciona una nota personal para leerla o modificarla.",
            font=ctk.CTkFont(size=12),
            text_color=self.colores["texto_secundario"],
        )
        self.etiqueta_estado.grid(row=1, column=0, sticky="w", padx=34, pady=(0, 10))

    # Los dos paneles siguen el diseño lista/editor solicitado.
    def _crear_paneles(self):
        """Construye la lista de archivos y el editor de texto."""

        # La columna derecha recibe más espacio para editar contenido.
        zona = ctk.CTkFrame(self, fg_color="transparent")
        zona.grid(row=2, column=0, sticky="nsew", padx=26, pady=(0, 26))
        zona.grid_columnconfigure(0, weight=2, uniform="archivos")
        zona.grid_columnconfigure(1, weight=3, uniform="archivos")
        zona.grid_rowconfigure(0, weight=1)

        # El contenedor izquierdo agrupa la lista y el botón de creación.
        panel_izquierdo = ctk.CTkFrame(
            zona,
            corner_radius=22,
            fg_color=self.colores["tarjeta"],
            border_width=1,
            border_color=self.colores["borde"],
        )
        panel_izquierdo.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        panel_izquierdo.grid_columnconfigure(0, weight=1)
        panel_izquierdo.grid_rowconfigure(1, weight=1)

        # El rótulo explica qué representa la lista encontrada en la carpeta.
        ctk.CTkLabel(
            panel_izquierdo,
            text="MIS NOTAS",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colores["texto_secundario"],
        ).grid(row=0, column=0, padx=18, pady=(18, 8), sticky="w")

        # Este Frame desplazable puede mostrar más de los cuatro archivos iniciales.
        self.panel_lista = ctk.CTkScrollableFrame(
            panel_izquierdo,
            fg_color="transparent",
            corner_radius=0,
        )
        self.panel_lista.grid(row=1, column=0, padx=8, pady=4, sticky="nsew")
        self.panel_lista.grid_columnconfigure(0, weight=1)

        # El formulario de creación se abre desde una acción visible.
        ctk.CTkButton(
            panel_izquierdo,
            text="＋  Nueva nota",
            height=40,
            corner_radius=11,
            fg_color=self.colores["acento"],
            hover_color=self.colores["acento_hover"],
            text_color="#07130C",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.abrir_formulario_nuevo,
        ).grid(row=2, column=0, padx=16, pady=16, sticky="ew")

        # El panel derecho contiene nombre, editor y botón de guardado.
        panel_editor = ctk.CTkFrame(
            zona,
            corner_radius=22,
            fg_color=self.colores["tarjeta"],
            border_width=1,
            border_color=self.colores["borde"],
        )
        panel_editor.grid(row=0, column=1, padx=(8, 0), sticky="nsew")
        panel_editor.grid_columnconfigure(0, weight=1)
        panel_editor.grid_rowconfigure(1, weight=1)

        # El nombre cambia cuando se selecciona un elemento de la lista.
        self.etiqueta_nombre = ctk.CTkLabel(
            panel_editor,
            text="EDITOR DE NOTAS",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colores["texto"],
        )
        self.etiqueta_nombre.grid(row=0, column=0, padx=20, pady=(18, 10), sticky="w")

        # CTkTextbox permite leer y modificar notas de varias líneas.
        self.editor = ctk.CTkTextbox(
            panel_editor,
            corner_radius=12,
            fg_color=self.colores["fondo"],
            border_width=1,
            border_color=self.colores["borde"],
            font=ctk.CTkFont(size=14),
        )
        self.editor.grid(row=1, column=0, padx=20, pady=(0, 12), sticky="nsew")

        # El contenido modificado se escribe en el mismo archivo seleccionado.
        ctk.CTkButton(
            panel_editor,
            text="✓  Guardar cambios",
            width=160,
            height=40,
            corner_radius=11,
            fg_color=self.colores["acento"],
            hover_color=self.colores["acento_hover"],
            text_color="#07130C",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.guardar_cambios,
        ).grid(row=2, column=0, padx=20, pady=(0, 18), sticky="e")

    # La lista de Python se vuelve a construir al entrar o crear una nota.
    def recargar_lista(self):
        """Busca los TXT disponibles y actualiza sus botones."""

        # Se eliminan botones anteriores antes de representar el estado actual.
        for componente in self.panel_lista.winfo_children():
            componente.destroy()
        self.botones_archivos = {}

        # PermissionError y OSError evitan que un problema cierre GymTracker.
        try:
            self.archivos_disponibles = listar_archivos()
        except PermissionError:
            self.archivos_disponibles = []
            self._mostrar_estado("No hay permiso para leer la carpeta de registros.", error=True)
            return
        except OSError:
            self.archivos_disponibles = []
            self._mostrar_estado("No fue posible consultar los archivos.", error=True)
            return

        # El ciclo crea un botón por cada nombre de la lista encontrada.
        for fila, nombre_archivo in enumerate(self.archivos_disponibles):
            boton = ctk.CTkButton(
                self.panel_lista,
                text=f"📄  {nombre_archivo}",
                height=46,
                corner_radius=12,
                anchor="w",
                border_width=1,
                border_color=self.colores["borde"],
                fg_color=self.colores["tarjeta_clara"],
                hover_color=self.colores["acento_suave"],
                text_color=self.colores["texto"],
                font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda nombre=nombre_archivo: self.seleccionar_archivo(nombre),
            )
            boton.grid(row=fila, column=0, padx=4, pady=5, sticky="ew")
            self.botones_archivos[nombre_archivo] = boton

        # Si la nota abierta sigue existiendo, conserva su indicador al regresar.
        if self.archivo_seleccionado in self.botones_archivos:
            self.botones_archivos[self.archivo_seleccionado].configure(
                fg_color=self.colores["acento_suave"],
                text_color=self.colores["acento"],
                border_color=self.colores["acento"],
            )

    # Seleccionar ejecuta READ y coloca el contenido dentro del editor.
    def seleccionar_archivo(self, nombre_archivo):
        """Lee una nota seleccionada y muestra su contenido editable."""

        # Las excepciones presentan mensajes específicos sin terminar el programa.
        try:
            contenido = leer_archivo(nombre_archivo)
        except FileNotFoundError:
            self.archivo_seleccionado = None
            self._mostrar_estado("El archivo ya no existe.", error=True)
            self.recargar_lista()
            return
        except PermissionError:
            self._mostrar_estado("No hay permiso para leer este archivo.", error=True)
            return
        except OSError:
            self._mostrar_estado("No fue posible leer el archivo.", error=True)
            return

        # El nombre seleccionado se conserva para el guardado posterior.
        self.archivo_seleccionado = nombre_archivo

        # Primero se devuelve cada botón a su apariencia neutral.
        for boton in self.botones_archivos.values():
            boton.configure(
                fg_color=self.colores["tarjeta_clara"],
                text_color=self.colores["texto"],
                border_color=self.colores["borde"],
            )

        # La nota abierta utiliza el verde de acento como indicador visual.
        if nombre_archivo in self.botones_archivos:
            self.botones_archivos[nombre_archivo].configure(
                fg_color=self.colores["acento_suave"],
                text_color=self.colores["acento"],
                border_color=self.colores["acento"],
            )

        self.etiqueta_nombre.configure(text=f"📄  {nombre_archivo}")
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", contenido)
        self._mostrar_estado("Archivo abierto correctamente.")

    # Esta acción corresponde a la modificación del TXT seleccionado.
    def guardar_cambios(self):
        """Escribe el texto del editor dentro del archivo actual."""

        # Guardar sin selección produciría una operación ambigua.
        if self.archivo_seleccionado is None:
            self._mostrar_estado("Selecciona un archivo antes de guardar.", error=True)
            return

        # Se conserva todo el contenido visible, salvo el salto automático final.
        contenido = self.editor.get("1.0", "end-1c")

        # Los errores de archivos permanecen controlados dentro de la interfaz.
        try:
            escribir_archivo(self.archivo_seleccionado, contenido)
        except FileNotFoundError:
            self.archivo_seleccionado = None
            self._mostrar_estado("El archivo ya no existe.", error=True)
            self.recargar_lista()
            return
        except PermissionError:
            self._mostrar_estado("No hay permiso para escribir este archivo.", error=True)
            return
        except OSError:
            self._mostrar_estado("No fue posible guardar los cambios.", error=True)
            return

        self._mostrar_estado("Cambios guardados correctamente.")

    # El formulario pide exclusivamente nombre, fecha y contenido inicial.
    def abrir_formulario_nuevo(self):
        """Abre una ventana sencilla para crear otro archivo TXT."""

        # CTkToplevel conserva la pantalla de archivos visible detrás.
        ventana = ctk.CTkToplevel(self)
        ventana.title("Nuevo archivo")
        ventana.geometry("520x520")
        ventana.resizable(False, False)
        ventana.configure(fg_color=self.colores["fondo"])
        ventana.transient(self.winfo_toplevel())
        ventana.grab_set()
        ventana.grid_columnconfigure(0, weight=1)
        ventana.grid_rowconfigure(6, weight=1)

        # El encabezado explica el propósito de la ventana secundaria.
        ctk.CTkLabel(
            ventana,
            text="Nueva nota de entrenamiento",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=self.colores["texto"],
        ).grid(row=0, column=0, padx=30, pady=(26, 16), sticky="w")

        # Nombre y fecha utilizan campos independientes y mensajes de ejemplo.
        ctk.CTkLabel(
            ventana,
            text="Nombre del archivo",
            text_color=self.colores["texto_secundario"],
        ).grid(row=1, column=0, padx=30, sticky="w")
        entrada_nombre = ctk.CTkEntry(
            ventana,
            height=40,
            placeholder_text="medidas o medidas.txt",
            fg_color=self.colores["tarjeta"],
            border_color=self.colores["borde"],
        )
        entrada_nombre.grid(row=2, column=0, padx=30, pady=(4, 12), sticky="ew")

        ctk.CTkLabel(
            ventana,
            text="Fecha",
            text_color=self.colores["texto_secundario"],
        ).grid(row=3, column=0, padx=30, sticky="w")
        entrada_fecha = ctk.CTkEntry(
            ventana,
            height=40,
            placeholder_text="dd/mm/aaaa",
            fg_color=self.colores["tarjeta"],
            border_color=self.colores["borde"],
        )
        entrada_fecha.grid(row=4, column=0, padx=30, pady=(4, 12), sticky="ew")

        ctk.CTkLabel(
            ventana,
            text="Contenido inicial",
            text_color=self.colores["texto_secundario"],
        ).grid(row=5, column=0, padx=30, sticky="w")
        entrada_contenido = ctk.CTkTextbox(
            ventana,
            height=130,
            fg_color=self.colores["tarjeta"],
            border_width=1,
            border_color=self.colores["borde"],
        )
        entrada_contenido.grid(row=6, column=0, padx=30, pady=(4, 8), sticky="nsew")

        # La etiqueta local permite corregir el formulario sin cerrarlo.
        etiqueta_error = ctk.CTkLabel(
            ventana,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#FF6B6B",
        )
        etiqueta_error.grid(row=7, column=0, padx=30, pady=(0, 4))

        # Esta función interna conserva acceso directo a los tres campos.
        def confirmar_creacion():
            contenido_inicial = entrada_contenido.get("1.0", "end-1c")

            # ValueError incluye tanto nombres como fechas incorrectas.
            try:
                nombre_creado = crear_archivo(
                    entrada_nombre.get(),
                    entrada_fecha.get(),
                    contenido_inicial,
                )
            except FileExistsError:
                etiqueta_error.configure(text="Ya existe un archivo con ese nombre.")
                return
            except ValueError as error:
                etiqueta_error.configure(text=str(error))
                return
            except PermissionError:
                etiqueta_error.configure(text="No hay permiso para crear el archivo.")
                return
            except OSError:
                etiqueta_error.configure(text="No fue posible crear el archivo.")
                return

            # El formulario se cierra y la lista refleja inmediatamente el quinto archivo.
            ventana.destroy()
            self.recargar_lista()
            self.seleccionar_archivo(nombre_creado)
            self._mostrar_estado("Archivo creado correctamente.")

        # El botón ejecuta la validación y creación sin cerrar ante errores.
        ctk.CTkButton(
            ventana,
            text="Crear archivo",
            width=160,
            height=40,
            fg_color=self.colores["acento"],
            hover_color=self.colores["acento_hover"],
            text_color="#07130C",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=confirmar_creacion,
        ).grid(row=8, column=0, padx=30, pady=(4, 22))

        entrada_nombre.focus_set()

    # Un solo método mantiene uniformes los mensajes de la pantalla.
    def _mostrar_estado(self, mensaje, error=False):
        """Presenta un mensaje con color normal o de error."""

        # Rojo identifica errores y verde confirma operaciones correctas.
        color = "#FF6B6B" if error else self.colores["acento"]
        self.etiqueta_estado.configure(text=mensaje, text_color=color)
