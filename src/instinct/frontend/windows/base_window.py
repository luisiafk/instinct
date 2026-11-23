
import pygame


class BaseWindow:
    """Clase base para las ventanas superpuestas de Instinct."""

    HEADER_HEIGHT = 42
    MIN_WIDTH = 240
    MIN_HEIGHT = 140

    def __init__(
        self,
        game,
        title,
        rect,
        modal=True,
        draggable=True,
        closable=True,
    ):
        self.game = game
        self.title = title

        self.rect = pygame.Rect(rect)

        self.rect.width = max(self.MIN_WIDTH, self.rect.width)
        self.rect.height = max(self.MIN_HEIGHT, self.rect.height)

        self.modal = modal
        self.draggable = draggable
        self.closable = closable

        self.visible = True
        self.manager = None

        self.dragging = False
        self.drag_offset = (0, 0)

        self.title_font = pygame.font.Font(None, 30)
        self.close_font = pygame.font.Font(None, 30)

    @property
    def header_rect(self):
        return pygame.Rect(
            self.rect.x,
            self.rect.y,
            self.rect.width,
            self.HEADER_HEIGHT,
        )

    @property
    def close_rect(self):
        size = 30

        return pygame.Rect(
            self.rect.right - size - 6,
            self.rect.y + 6,
            size,
            size,
        )

    def close(self):
        """Solicita al administrador cerrar esta ventana."""

        if self.manager is not None:
            self.manager.close(self)
        else:
            self.visible = False
            self.on_close()

    def on_open(self):
        """Se ejecuta al abrir la ventana."""

    def on_close(self):
        """Se ejecuta al cerrar la ventana."""

    def update(self, delta_time):
        """Actualiza el contenido de la ventana."""

    def handle_event(self, event):
        """Procesa los eventos de entrada.

        Devuelve True si la ventana consumió el evento.
        """

        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and self.closable:
                self.close()
                return True

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.closable and self.close_rect.collidepoint(event.pos):
                    self.close()
                    return True

                if self.draggable and self.header_rect.collidepoint(event.pos):
                    self.dragging = True

                    self.drag_offset = (
                        event.pos[0] - self.rect.x,
                        event.pos[1] - self.rect.y,
                    )

                    return True

                if self.rect.collidepoint(event.pos):
                    return self.handle_content_event(event)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging:
                self.dragging = False
                return True

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.rect.x = event.pos[0] - self.drag_offset[0]
                self.rect.y = event.pos[1] - self.drag_offset[1]

                self._keep_inside_screen()
                return True

        if self.rect.collidepoint(getattr(event, "pos", (-1, -1))):
            return self.handle_content_event(event)

        return False

    def handle_content_event(self, event):
        """Procesamiento de eventos específico de cada ventana."""

        return True

    def _keep_inside_screen(self):
        """Evita que la ventana desaparezca fuera de la pantalla."""

        screen_rect = self.game.screen.get_rect()

        self.rect.clamp_ip(screen_rect)

    def draw(self, screen):
        """Dibuja la estructura común de la ventana."""

        if not self.visible:
            return

        colors = self.game.theme_manager.colors

        panel_color = colors["panel"]
        accent_color = colors["accent"]
        text_color = colors["text"]
        secondary_color = colors["secondary_text"]

        # Panel principal.
        pygame.draw.rect(
            screen,
            panel_color,
            self.rect,
            border_radius=10,
        )

        pygame.draw.rect(
            screen,
            accent_color,
            self.rect,
            width=2,
            border_radius=10,
        )

        # Cabecera.
        pygame.draw.rect(
            screen,
            accent_color,
            self.header_rect,
            border_top_left_radius=9,
            border_top_right_radius=9,
        )

        title_surface = self.title_font.render(
            self.title,
            True,
            text_color,
        )

        screen.blit(
            title_surface,
            (self.rect.x + 14, self.rect.y + 10),
        )

        # Botón de cierre.
        if self.closable:
            close_color = (
                colors["gold"]
                if self.close_rect.collidepoint(pygame.mouse.get_pos())
                else secondary_color
            )

            close_surface = self.close_font.render(
                "X",
                True,
                close_color,
            )

            screen.blit(
                close_surface,
                close_surface.get_rect(center=self.close_rect.center),
            )

        # Contenido específico.
        self.draw_content(screen)

    def draw_content(self, screen):
        """Dibuja el contenido específico de cada ventana."""
