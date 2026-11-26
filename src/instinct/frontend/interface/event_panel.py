import pygame

from instinct.frontend.interface.widgets.scroll_panel import ScrollPanel


class EventPanel:
    """Panel que muestra los acontecimientos recientes de la simulación."""

    LINE_SPACING = 5
    EVENT_SPACING = 8
    HORIZONTAL_PADDING = 8
    VERTICAL_PADDING = 8

    def __init__(self, rect, theme_manager):
        self.rect = pygame.Rect(rect)
        self.theme_manager = theme_manager

        self.title_font = pygame.font.Font(None, 32)
        self.event_font = pygame.font.Font(None, 23)

        self.events = []
        self.wrapped_events = []

        self.line_height = self.event_font.get_linesize() + self.LINE_SPACING

        colors = theme_manager.colors

        self.scroll_panel = ScrollPanel(
            pygame.Rect(
                self.rect.x + 10,
                self.rect.y + 55,
                self.rect.width - 20,
                self.rect.height - 65,
            ),
            background=colors["panel"],
        )

    def set_rect(self, rect):
        """Actualiza la posición y las dimensiones del panel."""

        self.rect = pygame.Rect(rect)

        self.scroll_panel = ScrollPanel(
            pygame.Rect(
                self.rect.x + 10,
                self.rect.y + 55,
                self.rect.width - 20,
                self.rect.height - 65,
            ),
            background=self.theme_manager.colors["panel"],
        )

        # Volvemos a calcular los saltos de línea con el nuevo ancho.
        self.set_events(self.events)

    def _split_long_word(self, word, max_width):
        """Divide palabras excepcionalmente largas que no caben en una línea."""

        chunks = []
        current = ""

        for character in word:
            candidate = current + character

            if current and self.event_font.size(candidate)[0] > max_width:
                chunks.append(current)
                current = character
            else:
                current = candidate

        if current:
            chunks.append(current)

        return chunks

    def _wrap_text(self, text, max_width):
        """Distribuye el mensaje en líneas según el espacio disponible."""

        words = str(text).split()

        if not words:
            return [""]

        lines = []
        current_line = ""

        for word in words:
            candidate = (
                word if not current_line
                else f"{current_line} {word}"
            )

            if self.event_font.size(candidate)[0] <= max_width:
                current_line = candidate
                continue

            if current_line:
                lines.append(current_line)
                current_line = ""

            # Evitamos que una palabra muy larga desborde el panel.
            if self.event_font.size(word)[0] > max_width:
                chunks = self._split_long_word(word, max_width)
                lines.extend(chunks[:-1])
                current_line = chunks[-1]
            else:
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def set_events(self, events):
        """Actualiza los acontecimientos y calcula el espacio que necesitan."""

        self.events = list(events)[-200:]

        available_width = max(
            1,
            self.scroll_panel.rect.width - 2 * self.HORIZONTAL_PADDING,
        )

        self.wrapped_events = []

        content_height = self.VERTICAL_PADDING

        for event in self.events:
            message = f"[{event.tick}] {event.message}"

            lines = self._wrap_text(message, available_width)

            self.wrapped_events.append((event, lines))

            content_height += (
                len(lines) * self.line_height
                + self.EVENT_SPACING
            )

        content_height += self.VERTICAL_PADDING

        self.scroll_panel.set_content_height(
            max(self.scroll_panel.rect.height, content_height)
        )

    def handle_event(self, event):
        self.scroll_panel.handle_event(event)

    def draw(self, screen):
        colors = self.theme_manager.colors

        pygame.draw.rect(
            screen,
            colors["panel"],
            self.rect,
            border_radius=12,
        )

        pygame.draw.rect(
            screen,
            colors["accent"],
            self.rect,
            width=2,
            border_radius=12,
        )

        title = self.title_font.render(
            "ACONTECIMIENTOS",
            True,
            colors["gold"],
        )

        screen.blit(
            title,
            (self.rect.x + 15, self.rect.y + 15),
        )

        def draw_events(surface):
            y = self.VERTICAL_PADDING

            for event, lines in self.wrapped_events:
                category_color = colors["secondary_text"]

                if event.category in ("death", "danger"):
                    category_color = (230, 100, 100)

                elif event.category in ("success", "reproduction"):
                    category_color = colors["gold"]

                # Cada línea se dibuja por separado para evitar recortes.
                for line in lines:
                    text_surface = self.event_font.render(
                        line,
                        True,
                        category_color,
                    )

                    surface.blit(
                        text_surface,
                        (self.HORIZONTAL_PADDING, y),
                    )

                    y += self.line_height

                y += self.EVENT_SPACING

        self.scroll_panel.draw(
            screen,
            draw_content=draw_events,
        )    