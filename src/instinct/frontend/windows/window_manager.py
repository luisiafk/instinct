
class WindowManager:
    """Administra las ventanas superpuestas de la aplicación."""

    def __init__(self, game):
        self.game = game
        self.windows = []

    @property
    def active_window(self):
        """Devuelve la ventana superior visible."""

        for window in reversed(self.windows):
            if window.visible:
                return window

        return None

    @property
    def has_windows(self):
        return self.active_window is not None

    def open(self, window):
        """Abre una ventana y la coloca al frente."""

        if window in self.windows:
            self.bring_to_front(window)
            return

        window.manager = self
        window.visible = True

        self.windows.append(window)
        window.on_open()

    def close(self, window):
        """Cierra una ventana concreta."""

        if window not in self.windows:
            return

        self.windows.remove(window)

        window.visible = False
        window.dragging = False
        window.manager = None

        window.on_close()

    def close_active(self):
        """Cierra la ventana superior."""

        window = self.active_window

        if window is not None:
            self.close(window)

    def close_all(self):
        """Cierra todas las ventanas abiertas."""

        for window in self.windows.copy():
            self.close(window)

    def bring_to_front(self, window):
        """Coloca una ventana por encima de las demás."""

        if window not in self.windows:
            return

        self.windows.remove(window)
        self.windows.append(window)

    def handle_event(self, event):
        """Distribuye el evento desde la ventana superior."""

        self.windows = [
            window
            for window in self.windows
            if window.visible
        ]

        if not self.windows:
            return False

        window = self.active_window

        if window is None:
            return False

        if event.type in (
            __import__("pygame").MOUSEBUTTONDOWN,
            __import__("pygame").MOUSEBUTTONUP,
            __import__("pygame").MOUSEMOTION,
        ):
            position = getattr(event, "pos", None)

            if position is not None and window.rect.collidepoint(position):
                self.bring_to_front(window)

        consumed = window.handle_event(event)

        if consumed:
            return True

        # Una ventana modal bloquea la interacción con el fondo.
        if window.modal:
            return True

        return False

    def update(self, delta_time):
        """Actualiza todas las ventanas abiertas."""

        for window in self.windows.copy():
            if window.visible:
                window.update(delta_time)

    def draw(self, screen):
        """Dibuja las ventanas de abajo hacia arriba."""

        for window in self.windows:
            if window.visible:
                window.draw(screen)
