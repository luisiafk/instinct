import pygame


class Selection:
    """Gestiona la selección de casillas y criaturas del mundo."""

    TILE_COLOR = (212, 174, 98)
    CREATURE_COLOR = (255, 220, 120)

    def __init__(self):
        self.selected_tile = None
        self.selected_creatures = []

    def handle_click(
        self,
        world,
        camera,
        mouse_position,
        shift=False,
    ):
        """Procesa un clic sobre el mundo."""

        if not camera.viewport.collidepoint(mouse_position):
            return

        tile_x, tile_y = camera.screen_to_tile(*mouse_position)

        if not world.in_bounds(tile_x, tile_y):
            if not shift:
                self.clear()
            return

        tile = world.get_tile(tile_x, tile_y)
        creature = tile.creature

        if not shift:
            self.clear()

        self.selected_tile = (tile_x, tile_y)

        if creature is not None:
            if shift:
                if creature in self.selected_creatures:
                    self.selected_creatures.remove(creature)
                else:
                    self.selected_creatures.append(creature)
            else:
                self.selected_creatures.append(creature)

    def clear(self):
        """Limpia toda la selección."""

        self.selected_tile = None
        self.selected_creatures.clear()

    def is_creature_selected(self, creature):
        """Comprueba si una criatura está seleccionada."""

        return creature in self.selected_creatures

    def is_tile_selected(self, x, y):
        """Comprueba si una casilla está seleccionada."""

        return self.selected_tile == (x, y)

    def get_selected_creatures(self):
        """Devuelve las criaturas seleccionadas."""

        return list(self.selected_creatures)

    def get_selected_tile(self):
        """Devuelve las coordenadas de la casilla seleccionada."""

        return self.selected_tile

    def draw(self, screen, camera, animation_controller):
        """Dibuja los indicadores visuales de selección."""

        previous_clip = screen.get_clip()
        screen.set_clip(camera.viewport)

        # Resaltar la última casilla seleccionada.
        if self.selected_tile is not None:
            x, y = self.selected_tile
            rect = camera.get_tile_rect(x, y)

            pygame.draw.rect(
                screen,
                self.TILE_COLOR,
                rect,
                max(1, round(camera.zoom)),
            )

        # El indicador debe acompañar el desplazamiento visual
        # de cada criatura, no quedarse en su casilla lógica.
        for creature in self.selected_creatures:
            visual_x, visual_y = (
                animation_controller.get_visual_position(creature)
            )

            center_x = (visual_x + 0.5) * camera.tile_size
            center_y = (visual_y + 0.5) * camera.tile_size

            screen_x, screen_y = camera.world_to_screen(
                center_x,
                center_y,
            )

            radius = max(5, camera.zoom * 15)

            pygame.draw.circle(
                screen,
                self.CREATURE_COLOR,
                (screen_x, screen_y),
                radius,
                max(1, round(camera.zoom)),
            )

        screen.set_clip(previous_clip)