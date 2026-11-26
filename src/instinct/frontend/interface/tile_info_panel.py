
import pygame


class TileInfoPanel:
    """Muestra información de la casilla seleccionada."""

    def __init__(self):
        self.title_font = pygame.font.Font(None, 32)
        self.name_font = pygame.font.Font(None, 29)
        self.info_font = pygame.font.Font(None, 23)

    def draw(self, screen, rect, tile, position, colors):
        rect = pygame.Rect(rect)

        pygame.draw.rect(
            screen,
            colors["panel"],
            rect,
            border_radius=12,
        )

        pygame.draw.rect(
            screen,
            colors["accent"],
            rect,
            width=2,
            border_radius=12,
        )

        title = self.title_font.render(
            "INFORMACIÓN",
            True,
            colors["gold"],
        )

        screen.blit(title, (rect.x + 16, rect.y + 16))

        if tile is None:
            self._draw_empty(screen, rect, colors)
            return

        x = rect.x + 16
        y = rect.y + 65

        coordinate_text = self.info_font.render(
            f"Posición: ({position[0]}, {position[1]})",
            True,
            colors["secondary_text"],
        )

        screen.blit(coordinate_text, (x, y))
        y += 42

        terrain = tile.terrain

        y = self._draw_section(
            screen,
            "TERRENO",
            terrain.name,
            x,
            y,
            rect.width - 32,
            colors,
        )

        y = self._draw_property(
            screen,
            "Reserva",
            getattr(terrain, "reserve", 0),
            x,
            y,
            colors,
        )

        terrain_regen = getattr(
            terrain,
            "regen_rate",
            getattr(terrain, "regen", 0),
        )

        y = self._draw_property(
            screen,
            "Regeneración",
            terrain_regen,
            x,
            y,
            colors,
        )

        obj = tile.object

        if obj is not None:
            y += 18

            y = self._draw_section(
                screen,
                "OBJETO",
                obj.name,
                x,
                y,
                rect.width - 32,
                colors,
            )

            y = self._draw_property(
                screen,
                "Reserva",
                obj.reserve,
                x,
                y,
                colors,
            )

            y = self._draw_property(
                screen,
                "Reserva máxima",
                obj.resource_max,
                x,
                y,
                colors,
            )
            
            y = self._draw_property(
                screen,
                "Consumible",
                "Sí" if obj.consumable else "No",
                x,
                y,
                colors,
            )

            y = self._draw_property(
                screen,
                "Destructible",
                "Sí" if obj.destructible else "No",
                x,
                y,
                colors,
            )

            description = getattr(obj, "description", "")

            if description:
                y += 12
                self._draw_description(
                    screen,
                    description,
                    x,
                    y,
                    rect.width - 32,
                    colors,
                )

        elif tile.creature is not None:
            y += 18

            self._draw_section(
                screen,
                "CRIATURA",
                tile.creature.name,
                x,
                y,
                rect.width - 32,
                colors,
            )

        else:
            y += 18

            empty = self.info_font.render(
                "Casilla sin objeto.",
                True,
                colors["secondary_text"],
            )

            screen.blit(empty, (x, y))

    def _draw_section(
        self,
        screen,
        section,
        name,
        x,
        y,
        width,
        colors,
    ):
        label = self.info_font.render(
            section,
            True,
            colors["gold"],
        )

        screen.blit(label, (x, y))
        y += 27

        title = self.name_font.render(
            str(name),
            True,
            colors["text"],
        )

        screen.blit(title, (x, y))
        y += 38

        return y

    def _draw_property(self, screen, label, value, x, y, colors):
        text = self.info_font.render(
            f"{label}: {value}",
            True,
            colors["text"],
        )

        screen.blit(text, (x, y))
        return y + 29

    def _draw_description(
        self,
        screen,
        description,
        x,
        y,
        max_width,
        colors,
    ):
        label = self.info_font.render(
            "Descripción:",
            True,
            colors["gold"],
        )

        screen.blit(label, (x, y))
        y += 25

        words = description.split()
        lines = []
        current_line = ""

        for word in words:
            candidate = (
                f"{current_line} {word}".strip()
            )

            if self.info_font.size(candidate)[0] <= max_width:
                current_line = candidate
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        for line in lines:
            rendered = self.info_font.render(
                line,
                True,
                colors["text"],
            )

            screen.blit(rendered, (x, y))
            y += 25

    def _draw_empty(self, screen, rect, colors):
        text = "Selecciona una casilla u objeto."

        max_width = rect.width - 32
        words = text.split()
        lines = []
        current_line = ""

        # Ajustamos el mensaje al ancho interior del panel.
        for word in words:
            candidate = f"{current_line} {word}".strip()

            if self.info_font.size(candidate)[0] <= max_width:
                current_line = candidate
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        line_height = self.info_font.get_linesize() + 4
        total_height = len(lines) * line_height

        # Centramos el bloque completo, no cada línea por separado.
        y = rect.centery - total_height // 2

        for line in lines:
            rendered = self.info_font.render(
                line,
                True,
                colors["secondary_text"],
            )

            screen.blit(
                rendered,
                rendered.get_rect(
                    center=(rect.centerx, y + line_height // 2)
                ),
            )

            y += line_height
