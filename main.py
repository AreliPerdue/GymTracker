"""Punto de entrada de la aplicación GymTracker."""

# Se importa la ventana principal desde el paquete de la aplicación.
from app.interfaz import GymTrackerApp


# Esta función mantiene el inicio del programa fácil de identificar.
def main():
    """Crea la ventana y mantiene activa la interfaz gráfica."""

    # Se construye una sola instancia de la aplicación.
    aplicacion = GymTrackerApp()

    # mainloop espera y responde a los eventos del usuario.
    aplicacion.mainloop()


# Esta condición evita abrir la ventana al importar este archivo desde otro módulo.
if __name__ == "__main__":
    main()

