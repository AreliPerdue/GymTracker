"""Calendario mensual y consulta de entrenamientos guardados."""

# calendar construye semanas completas y date representa el día seleccionado.
import calendar
from datetime import date, timedelta

# CustomTkinter aporta los componentes visuales usados por el resto del proyecto.
import customtkinter as ctk

# Estas funciones reutilizan el mismo CRUD y el mismo archivo JSON de Entrenamientos.
from app.utilidades import (
    actualizar_entrenamiento,
    cargar_entrenamientos,
    generar_nuevo_id,
)
from app.validaciones import (
    convertir_entero_positivo,
    convertir_numero_no_negativo,
    texto_no_vacio,
)


# Los nombres en español evitan depender del idioma configurado en la computadora.
DIAS_SEMANA = (
    "lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"
)
MESES = (
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
)


class VistaCalendario(ctk.CTkFrame):
    """Muestra un mes completo y el entrenamiento de la fecha seleccionada."""

    def __init__(self, master, colores, al_registrar, al_editar, al_cambiar):
        # Un frame normal sí se eleva correctamente entre las vistas apiladas.
        super().__init__(master, fg_color=colores["fondo"], corner_radius=0)

        # La fecha seleccionada comienza en la fecha local actual del equipo.
        self.fecha_seleccionada = date.today()
        self.colores = colores
        self.al_registrar = al_registrar
        self.al_editar = al_editar
        self.al_cambiar = al_cambiar
        self.entrenamientos_fecha = []
        self.entrenamiento_actual = None
        self.id_seleccionado = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._crear_encabezado()

        # El detalle puede desplazarse sin ocultar la cuadrícula del mes.
        self.contenido = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=colores["borde"],
        )
        self.contenido.grid(
            row=2, column=0, padx=(34, 20), pady=(0, 24), sticky="nsew"
        )
        self.contenido.grid_columnconfigure(0, weight=1)
        self.actualizar_vista()

    def _crear_encabezado(self):
        """Crea el título de la pantalla y el acceso directo al día actual."""

        encabezado = ctk.CTkFrame(self, fg_color="transparent")
        encabezado.grid(row=0, column=0, padx=34, pady=(28, 12), sticky="ew")
        encabezado.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            encabezado,
            text="Calendario",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=self.colores["texto"],
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            encabezado,
            text="Consulta y administra el entrenamiento de cada día.",
            font=ctk.CTkFont(size=13),
            text_color=self.colores["texto_secundario"],
        ).grid(row=1, column=0, pady=(3, 0), sticky="w")

        ctk.CTkButton(
            encabezado,
            text="Hoy",
            width=92,
            height=38,
            corner_radius=11,
            fg_color=self.colores["acento_suave"],
            hover_color=self.colores["borde"],
            text_color=self.colores["acento"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.ir_a_hoy,
        ).grid(row=0, column=1, rowspan=2, sticky="e")

        navegacion = ctk.CTkFrame(
            self,
            corner_radius=16,
            fg_color=self.colores["tarjeta"],
            border_width=1,
            border_color=self.colores["borde"],
        )
        navegacion.grid(row=1, column=0, padx=34, pady=(0, 18), sticky="ew")
        navegacion.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            navegacion,
            text="‹",
            width=42,
            height=36,
            corner_radius=11,
            fg_color=self.colores["tarjeta_clara"],
            hover_color=self.colores["borde"],
            font=ctk.CTkFont(size=25),
            command=lambda: self.cambiar_mes(-1),
        ).grid(row=0, column=0, padx=(16, 8), pady=14)

        self.etiqueta_mes = ctk.CTkLabel(
            navegacion,
            text="",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colores["texto"],
        )
        self.etiqueta_mes.grid(row=0, column=1, padx=8, pady=14)

        ctk.CTkButton(
            navegacion,
            text="›",
            width=42,
            height=36,
            corner_radius=11,
            fg_color=self.colores["tarjeta_clara"],
            hover_color=self.colores["borde"],
            font=ctk.CTkFont(size=25),
            command=lambda: self.cambiar_mes(1),
        ).grid(row=0, column=2, padx=(8, 16), pady=14)

        self.cuadricula_calendario = ctk.CTkFrame(
            navegacion,
            fg_color="transparent",
        )
        self.cuadricula_calendario.grid(
            row=1, column=0, columnspan=3, padx=14, pady=(0, 14), sticky="ew"
        )
        for columna in range(7):
            self.cuadricula_calendario.grid_columnconfigure(
                columna, weight=1, uniform="dias_calendario"
            )

    def _dibujar_calendario(self, entrenamientos):
        """Dibuja las semanas del mes y señala hoy, la selección y los registros."""

        for componente in self.cuadricula_calendario.winfo_children():
            componente.destroy()

        nombre_mes = MESES[self.fecha_seleccionada.month - 1].capitalize()
        self.etiqueta_mes.configure(
            text=f"{nombre_mes} {self.fecha_seleccionada.year}"
        )

        nombres_dias = ("Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom")
        for columna, nombre_dia in enumerate(nombres_dias):
            ctk.CTkLabel(
                self.cuadricula_calendario,
                text=nombre_dia,
                height=25,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=self.colores["texto_secundario"],
            ).grid(row=0, column=columna, padx=3, pady=(0, 3), sticky="ew")

        fechas_con_entrenamiento = {
            entrenamiento.get("fecha")
            for entrenamiento in entrenamientos
            if isinstance(entrenamiento, dict)
        }
        hoy = date.today()
        semanas = calendar.Calendar(firstweekday=calendar.MONDAY).monthdatescalendar(
            self.fecha_seleccionada.year,
            self.fecha_seleccionada.month,
        )

        for fila, semana in enumerate(semanas, start=1):
            for columna, fecha_dia in enumerate(semana):
                es_mes_actual = fecha_dia.month == self.fecha_seleccionada.month
                es_seleccionada = fecha_dia == self.fecha_seleccionada
                es_hoy = fecha_dia == hoy
                tiene_entrenamiento = (
                    fecha_dia.strftime("%d/%m/%Y") in fechas_con_entrenamiento
                )

                texto = str(fecha_dia.day)
                if tiene_entrenamiento:
                    texto += "  •"

                color_fondo = "transparent"
                color_texto = (
                    self.colores["texto"]
                    if es_mes_actual
                    else self.colores["texto_secundario"]
                )
                color_hover = self.colores["tarjeta_clara"]
                if es_seleccionada:
                    color_fondo = self.colores["acento"]
                    color_texto = "#07130C"
                    color_hover = self.colores["acento_hover"]
                elif tiene_entrenamiento:
                    color_texto = self.colores["acento"]

                ctk.CTkButton(
                    self.cuadricula_calendario,
                    text=texto,
                    height=34,
                    corner_radius=9,
                    border_width=2 if es_hoy else 0,
                    border_color=self.colores["acento"],
                    fg_color=color_fondo,
                    hover_color=color_hover,
                    text_color=color_texto,
                    font=ctk.CTkFont(
                        size=12,
                        weight="bold" if es_hoy or es_seleccionada else "normal",
                    ),
                    command=lambda nueva_fecha=fecha_dia: self.seleccionar_fecha(
                        nueva_fecha
                    ),
                ).grid(row=fila, column=columna, padx=3, pady=2, sticky="ew")

    def seleccionar_fecha(self, nueva_fecha):
        """Selecciona un día de la cuadrícula y actualiza su detalle."""

        self.fecha_seleccionada = nueva_fecha
        self.id_seleccionado = None
        self.actualizar_vista()

    def cambiar_mes(self, cantidad_meses):
        """Avanza o retrocede un mes conservando un día válido."""

        indice_mes = self.fecha_seleccionada.month - 1 + cantidad_meses
        nuevo_anio = self.fecha_seleccionada.year + indice_mes // 12
        nuevo_mes = indice_mes % 12 + 1
        ultimo_dia = calendar.monthrange(nuevo_anio, nuevo_mes)[1]
        self.fecha_seleccionada = date(
            nuevo_anio,
            nuevo_mes,
            min(self.fecha_seleccionada.day, ultimo_dia),
        )
        self.id_seleccionado = None
        self.actualizar_vista()

    def ir_a_hoy(self):
        """Regresa al mes actual y selecciona la fecha local de hoy."""

        self.seleccionar_fecha(date.today())

    def cambiar_fecha(self, cantidad_dias):
        """Avanza o retrocede la fecha seleccionada exactamente un día."""

        # timedelta resuelve automáticamente cambios de mes, año y años bisiestos.
        self.fecha_seleccionada += timedelta(days=cantidad_dias)
        self.id_seleccionado = None
        self.actualizar_vista()

    def actualizar_vista(self):
        """Vuelve a leer el JSON y dibuja los datos de la fecha seleccionada."""

        # La comparación usa el mismo formato dd/mm/aaaa almacenado por el CRUD.
        fecha_buscada = self.fecha_seleccionada.strftime("%d/%m/%Y")
        entrenamientos = cargar_entrenamientos()
        self._dibujar_calendario(entrenamientos)
        self.entrenamientos_fecha = [
            entrenamiento
            for entrenamiento in entrenamientos
            if entrenamiento.get("fecha") == fecha_buscada
        ]

        # Se conserva la selección cuando solo se actualizó un ejercicio.
        seleccion = next(
            (
                entrenamiento
                for entrenamiento in self.entrenamientos_fecha
                if entrenamiento.get("idEntrenamiento") == self.id_seleccionado
            ),
            None,
        )
        self.entrenamiento_actual = seleccion or (
            self.entrenamientos_fecha[0] if self.entrenamientos_fecha else None
        )
        if self.entrenamiento_actual is not None:
            self.id_seleccionado = self.entrenamiento_actual.get("idEntrenamiento")

        # Destruir los widgets anteriores evita mezclar dos fechas en pantalla.
        for componente in self.contenido.winfo_children():
            componente.destroy()

        if self.entrenamiento_actual is None:
            self._mostrar_estado_vacio(fecha_buscada)
        else:
            self._mostrar_selector_si_es_necesario()
            self._mostrar_entrenamiento(self.entrenamiento_actual)

    def _mostrar_selector_si_es_necesario(self):
        """Permite elegir un registro cuando existen varios en la misma fecha."""

        if len(self.entrenamientos_fecha) <= 1:
            return

        opciones = []
        self.entrenamientos_por_opcion = {}
        for posicion, entrenamiento in enumerate(self.entrenamientos_fecha, start=1):
            texto = f"{posicion}. {entrenamiento.get('nombreRutina', 'Sin nombre')}"
            opciones.append(texto)
            self.entrenamientos_por_opcion[texto] = entrenamiento

        fila_selector = ctk.CTkFrame(self.contenido, fg_color="transparent")
        fila_selector.grid(row=0, column=0, pady=(0, 12), sticky="ew")
        fila_selector.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            fila_selector,
            text="Entrenamientos del día:",
            text_color=self.colores["texto_secundario"],
        ).grid(row=0, column=0, padx=(0, 10), sticky="w")

        selector = ctk.CTkOptionMenu(
            fila_selector,
            values=opciones,
            fg_color=self.colores["tarjeta_clara"],
            button_color=self.colores["acento"],
            button_hover_color=self.colores["acento_hover"],
            command=self._seleccionar_entrenamiento,
        )
        selector.grid(row=0, column=1, sticky="ew")

        opcion_actual = next(
            (
                opcion
                for opcion, entrenamiento in self.entrenamientos_por_opcion.items()
                if entrenamiento.get("idEntrenamiento") == self.id_seleccionado
            ),
            opciones[0],
        )
        selector.set(opcion_actual)

    def _seleccionar_entrenamiento(self, opcion):
        """Cambia la tarjeta consultada sin modificar ningún registro."""

        entrenamiento = self.entrenamientos_por_opcion.get(opcion)
        if entrenamiento is not None:
            self.id_seleccionado = entrenamiento.get("idEntrenamiento")
            self.actualizar_vista()

    def _mostrar_estado_vacio(self, fecha_texto):
        """Presenta una invitación a registrar cuando el día no tiene datos."""

        tarjeta = ctk.CTkFrame(
            self.contenido,
            height=330,
            corner_radius=20,
            fg_color=self.colores["tarjeta"],
            border_width=1,
            border_color=self.colores["borde"],
        )
        tarjeta.grid(row=0, column=0, sticky="ew")
        tarjeta.grid_propagate(False)

        ctk.CTkLabel(
            tarjeta,
            text="📅",
            font=ctk.CTkFont(size=44),
        ).pack(pady=(58, 10))
        ctk.CTkLabel(
            tarjeta,
            text="No hay entrenamiento registrado",
            font=ctk.CTkFont(size=21, weight="bold"),
            text_color=self.colores["texto"],
        ).pack()
        ctk.CTkLabel(
            tarjeta,
            text=f"Puedes preparar tu sesión para el {fecha_texto}.",
            text_color=self.colores["texto_secundario"],
        ).pack(pady=(5, 20))
        ctk.CTkButton(
            tarjeta,
            text="＋  Registrar entrenamiento",
            width=205,
            height=42,
            corner_radius=12,
            fg_color=self.colores["acento"],
            hover_color=self.colores["acento_hover"],
            text_color="#07130C",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda: self.al_registrar(fecha_texto),
        ).pack()

    def _mostrar_entrenamiento(self, entrenamiento):
        """Dibuja resumen, equipos, ejercicios, notas y acciones del registro."""

        fila_inicial = 1 if len(self.entrenamientos_fecha) > 1 else 0
        tarjeta = ctk.CTkFrame(
            self.contenido,
            corner_radius=20,
            fg_color=self.colores["tarjeta"],
            border_width=1,
            border_color=self.colores["borde"],
        )
        tarjeta.grid(row=fila_inicial, column=0, sticky="ew")
        tarjeta.grid_columnconfigure(1, weight=1)

        color_grupo = entrenamiento.get("colorGrupo", self.colores["acento"])
        es_hexadecimal = (
            isinstance(color_grupo, str)
            and len(color_grupo) == 7
            and color_grupo.startswith("#")
            and all(caracter in "0123456789abcdefABCDEF" for caracter in color_grupo[1:])
        )
        if not es_hexadecimal:
            color_grupo = self.colores["acento"]

        ctk.CTkLabel(
            tarjeta,
            text=entrenamiento.get("iconoGrupo", "🏋"),
            width=66,
            height=66,
            corner_radius=18,
            fg_color=color_grupo,
            text_color="#07130C",
            font=ctk.CTkFont(size=29),
        ).grid(row=0, column=0, rowspan=2, padx=(22, 15), pady=(22, 12))

        ctk.CTkLabel(
            tarjeta,
            text=entrenamiento.get("nombreRutina", "Rutina sin nombre"),
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colores["texto"],
        ).grid(row=0, column=1, padx=(0, 18), pady=(22, 0), sticky="sw")
        ctk.CTkLabel(
            tarjeta,
            text=entrenamiento.get("grupoMuscular", "Sin grupo muscular"),
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=color_grupo,
        ).grid(row=1, column=1, padx=(0, 18), pady=(0, 12), sticky="nw")

        acciones = ctk.CTkFrame(tarjeta, fg_color="transparent")
        acciones.grid(row=0, column=2, rowspan=2, padx=22, pady=22)
        ctk.CTkButton(
            acciones,
            text="✎  Editar entrenamiento",
            width=170,
            height=38,
            corner_radius=11,
            fg_color=self.colores["acento_secundario"],
            hover_color="#3D8DDB",
            command=lambda: self.al_editar(entrenamiento),
        ).pack()

        datos = ctk.CTkFrame(tarjeta, fg_color=self.colores["tarjeta_clara"], corner_radius=14)
        datos.grid(row=2, column=0, columnspan=3, padx=22, pady=(4, 14), sticky="ew")
        for columna in range(2):
            datos.grid_columnconfigure(columna, weight=1)

        peso = entrenamiento.get("pesoCorporal")
        peso_texto = "Sin registro" if peso in (None, "") else f"{peso} kg"
        duracion = entrenamiento.get("duracion")
        duracion_texto = "Sin registro" if duracion in (None, "") else f"{duracion} min"
        self._crear_dato_resumen(datos, 0, "PESO CORPORAL", peso_texto)
        self._crear_dato_resumen(datos, 1, "DURACIÓN", duracion_texto)

        ejercicios = entrenamiento.get("ejercicios", [])
        if not isinstance(ejercicios, list):
            ejercicios = []
        self._mostrar_equipos(tarjeta, ejercicios)
        self._mostrar_tabla_ejercicios(tarjeta, ejercicios)
        self._mostrar_notas(tarjeta, entrenamiento)

    def _crear_dato_resumen(self, master, columna, titulo, valor):
        """Construye una celda breve para peso o duración."""

        ctk.CTkLabel(
            master,
            text=titulo,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=self.colores["texto_secundario"],
        ).grid(row=0, column=columna, padx=20, pady=(12, 1), sticky="w")
        ctk.CTkLabel(
            master,
            text=valor,
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=self.colores["texto"],
        ).grid(row=1, column=columna, padx=20, pady=(0, 12), sticky="w")

    def _mostrar_equipos(self, tarjeta, ejercicios):
        """Obtiene y presenta equipos únicos a partir de la lista de ejercicios."""

        ctk.CTkLabel(
            tarjeta,
            text="EQUIPO UTILIZADO",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.colores["texto_secundario"],
        ).grid(row=3, column=0, columnspan=3, padx=22, pady=(5, 6), sticky="w")

        equipos = []
        for ejercicio in ejercicios:
            if not isinstance(ejercicio, dict):
                continue
            equipo = str(ejercicio.get("equipo", "")).strip()
            if equipo and equipo not in equipos:
                equipos.append(equipo)

        fila_equipos = ctk.CTkFrame(tarjeta, fg_color="transparent")
        fila_equipos.grid(row=4, column=0, columnspan=3, padx=22, pady=(0, 15), sticky="ew")
        for equipo in equipos or ["Sin equipo registrado"]:
            ctk.CTkLabel(
                fila_equipos,
                text=equipo,
                height=28,
                corner_radius=10,
                fg_color=self.colores["acento_suave"],
                text_color=self.colores["acento"],
                font=ctk.CTkFont(size=11, weight="bold"),
            ).pack(side="left", padx=(0, 7))

    def _mostrar_tabla_ejercicios(self, tarjeta, ejercicios):
        """Crea una tabla visual desplazable con los ejercicios de la rutina."""

        encabezado = ctk.CTkFrame(tarjeta, fg_color="transparent")
        encabezado.grid(row=5, column=0, columnspan=3, padx=22, pady=(2, 8), sticky="ew")
        encabezado.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            encabezado,
            text=f"RUTINA  ·  {len(ejercicios)} ejercicio(s)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colores["texto"],
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(
            encabezado,
            text="＋  Agregar ejercicio",
            width=158,
            height=34,
            corner_radius=10,
            fg_color=self.colores["acento"],
            hover_color=self.colores["acento_hover"],
            text_color="#07130C",
            command=self._abrir_formulario_ejercicio,
        ).grid(row=0, column=1, sticky="e")

        tabla = ctk.CTkScrollableFrame(
            tarjeta,
            height=230,
            corner_radius=14,
            fg_color=self.colores["tarjeta_clara"],
            scrollbar_button_color=self.colores["borde"],
        )
        tabla.grid(row=6, column=0, columnspan=3, padx=22, pady=(0, 15), sticky="ew")
        anchos = (3, 1, 1, 1, 2)
        for columna, peso in enumerate(anchos):
            tabla.grid_columnconfigure(columna, weight=peso, uniform="tabla")

        for columna, titulo in enumerate(("EJERCICIO", "PESO", "SERIES", "REPS", "EQUIPO")):
            ctk.CTkLabel(
                tabla,
                text=titulo,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=self.colores["texto_secundario"],
            ).grid(row=0, column=columna, padx=8, pady=(6, 9), sticky="w")

        if not ejercicios:
            ctk.CTkLabel(
                tabla,
                text="Todavía no hay ejercicios en esta rutina.",
                text_color=self.colores["texto_secundario"],
            ).grid(row=1, column=0, columnspan=5, padx=8, pady=35)
            return

        for fila, ejercicio in enumerate(ejercicios, start=1):
            if not isinstance(ejercicio, dict):
                continue
            valores = (
                ejercicio.get("nombreEjercicio", "Sin nombre"),
                f"{ejercicio.get('pesoEjercicio', 0)} kg",
                ejercicio.get("series", "-"),
                ejercicio.get("repeticiones", "-"),
                ejercicio.get("equipo", "Sin equipo"),
            )
            for columna, valor in enumerate(valores):
                ctk.CTkLabel(
                    tabla,
                    text=str(valor),
                    height=38,
                    anchor="w",
                    font=ctk.CTkFont(size=12, weight="bold" if columna == 0 else "normal"),
                    text_color=self.colores["texto"],
                ).grid(row=fila, column=columna, padx=8, pady=2, sticky="ew")

    def _mostrar_notas(self, tarjeta, entrenamiento):
        """Presenta las notas con su categoría usando valores seguros."""

        notas = entrenamiento.get("notas", "") or "Sin notas para este entrenamiento."
        categoria = entrenamiento.get("categoriaNota", "General")
        panel = ctk.CTkFrame(
            tarjeta,
            corner_radius=14,
            fg_color=self.colores["tarjeta_clara"],
        )
        panel.grid(row=7, column=0, columnspan=3, padx=22, pady=(0, 22), sticky="ew")
        panel.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            panel,
            text=f"NOTAS  ·  {categoria}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.colores["acento"],
        ).grid(row=0, column=0, padx=16, pady=(13, 3), sticky="w")
        ctk.CTkLabel(
            panel,
            text=notas,
            justify="left",
            wraplength=760,
            text_color=self.colores["texto"],
        ).grid(row=1, column=0, padx=16, pady=(0, 14), sticky="w")

    def _abrir_formulario_ejercicio(self):
        """Abre la captura pequeña para agregar al entrenamiento consultado."""

        if self.entrenamiento_actual is None:
            return
        FormularioEjercicioCalendario(
            self,
            self.colores,
            id_entrenamiento=self.entrenamiento_actual.get("idEntrenamiento"),
            al_guardar=self._despues_de_agregar_ejercicio,
        )

    def _despues_de_agregar_ejercicio(self):
        """Refresca todas las vistas después de persistir el nuevo ejercicio."""

        self.al_cambiar()
        self.actualizar_vista()


class FormularioEjercicioCalendario(ctk.CTkToplevel):
    """Captura un ejercicio y lo agrega mediante el CRUD existente."""

    def __init__(self, master, colores, id_entrenamiento, al_guardar):
        super().__init__(master)
        self.colores = colores
        self.id_entrenamiento = id_entrenamiento
        self.al_guardar = al_guardar

        self.title("Agregar ejercicio")
        self.geometry("560x545")
        self.resizable(False, False)
        self.configure(fg_color=colores["fondo"])
        self.transient(master.winfo_toplevel())
        self.grab_set()
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text="Agregar ejercicio",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=colores["texto"],
        ).grid(row=0, column=0, padx=28, pady=(24, 3), sticky="w")
        ctk.CTkLabel(
            self,
            text="Completa los datos para incorporarlo a la rutina de este día.",
            text_color=colores["texto_secundario"],
        ).grid(row=1, column=0, padx=28, pady=(0, 10), sticky="w")

        self.entradas = {}
        campos = (
            ("nombre", "Nombre del ejercicio *", "Ej. Sentadilla"),
            ("peso", "Peso en kg *", "Ej. 20 o 0"),
            ("series", "Series *", "Ej. 3"),
            ("repeticiones", "Repeticiones *", "Ej. 10"),
            ("equipo", "Equipo", "Ej. Barra"),
        )
        for fila, (clave, etiqueta, ejemplo) in enumerate(campos, start=2):
            contenedor = ctk.CTkFrame(self, fg_color="transparent")
            contenedor.grid(row=fila, column=0, padx=28, pady=4, sticky="ew")
            contenedor.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(
                contenedor,
                text=etiqueta,
                width=145,
                anchor="w",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=colores["texto_secundario"],
            ).grid(row=0, column=0, padx=(0, 10))
            entrada = ctk.CTkEntry(
                contenedor,
                height=38,
                placeholder_text=ejemplo,
                fg_color=colores["tarjeta"],
                border_color=colores["borde"],
            )
            entrada.grid(row=0, column=1, sticky="ew")
            self.entradas[clave] = entrada

        self.etiqueta_error = ctk.CTkLabel(
            self,
            text="",
            text_color="#FF6B6B",
        )
        self.etiqueta_error.grid(row=7, column=0, padx=28, pady=(5, 0), sticky="w")

        botones = ctk.CTkFrame(self, fg_color="transparent")
        botones.grid(row=8, column=0, padx=28, pady=(12, 24), sticky="e")
        ctk.CTkButton(
            botones,
            text="Cancelar",
            width=110,
            fg_color=colores["tarjeta_clara"],
            hover_color=colores["borde"],
            command=self.destroy,
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            botones,
            text="Guardar ejercicio",
            width=155,
            fg_color=colores["acento"],
            hover_color=colores["acento_hover"],
            text_color="#07130C",
            command=self._guardar,
        ).pack(side="left", padx=5)
        self.entradas["nombre"].focus_set()

    def _guardar(self):
        """Valida, agrega el ejercicio y persiste el entrenamiento completo."""

        nombre = self.entradas["nombre"].get().strip()
        if not texto_no_vacio(nombre):
            self.etiqueta_error.configure(text="Escribe el nombre del ejercicio.")
            return

        try:
            # Se reutilizan exactamente las validaciones del formulario principal.
            peso = convertir_numero_no_negativo(
                self.entradas["peso"].get(), "El peso del ejercicio"
            )
            series = convertir_entero_positivo(self.entradas["series"].get(), "Las series")
            repeticiones = convertir_entero_positivo(
                self.entradas["repeticiones"].get(), "Las repeticiones"
            )

            # Se vuelve a leer el JSON para no guardar una copia desactualizada.
            entrenamientos = cargar_entrenamientos()
            entrenamiento = next(
                (
                    registro
                    for registro in entrenamientos
                    if registro.get("idEntrenamiento") == self.id_entrenamiento
                ),
                None,
            )
            if entrenamiento is None:
                raise ValueError("El entrenamiento ya no existe.")

            ejercicios_guardados = entrenamiento.get("ejercicios", [])
            if not isinstance(ejercicios_guardados, list):
                ejercicios_guardados = []
            ejercicios = [
                ejercicio.copy()
                for ejercicio in ejercicios_guardados
                if isinstance(ejercicio, dict)
            ]

            ejercicio_nuevo = {
                "idEjercicio": generar_nuevo_id(ejercicios, "idEjercicio"),
                "nombreEjercicio": nombre,
                "pesoEjercicio": peso,
                "series": series,
                "repeticiones": repeticiones,
                "equipo": self.entradas["equipo"].get().strip() or "Sin equipo",
            }
            ejercicios.append(ejercicio_nuevo)

            # UPDATE conserva idEntrenamiento y escribe en data/entrenamientos.json.
            datos_actualizados = entrenamiento.copy()
            datos_actualizados["ejercicios"] = ejercicios
            if not actualizar_entrenamiento(self.id_entrenamiento, datos_actualizados):
                raise ValueError("No fue posible localizar el entrenamiento.")
        except ValueError as error:
            self.etiqueta_error.configure(text=str(error))
            return
        except OSError:
            self.etiqueta_error.configure(
                text="No fue posible guardar el ejercicio en entrenamientos.json."
            )
            return

        self.al_guardar()
        self.destroy()
