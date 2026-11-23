
import pygame

from instinct.frontend.menu.background_renderer import BackgroundRenderer
from instinct.frontend.menu.logo_renderer import LogoRenderer
from instinct.frontend.menu.particle_system import ParticleSystem
from instinct.frontend.scenes.base_scene import BaseScene
from instinct.frontend.scenes.simulation_scene import SimulationScene
from instinct.frontend.scenes.new_simulation import NewSimulationScene

class MenuButton:
    """Botón sencillo para el menú principal."""

    def __init__(self, text, rect, callback=None, enabled=True):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.callback = callback
        self.enabled = enabled
        self.hovered = False

        self.font = pygame.font.SysFont("georgia", 25)

    def handle_event(self, event):
        if not self.enabled:
            return

        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos) and self.callback:
                self.callback()

    def draw(self, screen):
        if not self.enabled:
            background = (35, 34, 51)
            border = (75, 70, 90)
            text_color = (105, 101, 117)

        elif self.hovered:
            background = (77, 57, 105)
            border = (222, 190, 119)
            text_color = (255, 239, 205)

        else:
            background = (41, 39, 71)
            border = (118, 84, 168)
            text_color = (225, 216, 237)

        pygame.draw.rect(
            screen,
            background,
            self.rect,
            border_radius=8,
        )

        pygame.draw.rect(
            screen,
            border,
            self.rect,
            width=2,
            border_radius=8,
        )

        text_surface = self.font.render(
            self.text,
            True,
            text_color,
        )

        text_rect = text_surface.get_rect(
            center=self.rect.center
        )

        screen.blit(text_surface, text_rect)


class MainMenu(BaseScene):
    """Escena principal de Instinct."""

    def __init__(self, game):
        super().__init__(game)

        self.screen_size = None

        self.background = None
        self.particles = None
        self.logo = LogoRenderer()

        self.buttons = []

        self._initialize_visuals()

    def _initialize_visuals(self):
        """Inicializa los componentes visuales."""

        size = self.game.screen.get_size()
        self.screen_size = size

        self.background = BackgroundRenderer(size)

        self.particles = ParticleSystem(
            size[0],
            size[1],
            particle_count=55,
        )

        self._create_buttons()

    def _create_buttons(self):
        """Crea los botones del menú."""

        width, height = self.screen_size

        button_width = 330
        button_height = 54
        spacing = 14

        center_x = width // 2

        start_y = int(height * 0.49)

        def button_rect(index):
            y = start_y + index * (button_height + spacing)

            return (
                center_x - button_width // 2,
                y,
                button_width,
                button_height,
            )

        self.buttons = [
            MenuButton(
                "Nueva simulación",
                button_rect(0),
                callback=self._new_simulation,
            ),

            MenuButton(
                "Cargar mundo",
                button_rect(1),
                enabled=False,
            ),

            MenuButton(
                "Mundos recientes",
                button_rect(2),
                enabled=False,
            ),

            MenuButton(
                "Configuración",
                button_rect(3),
                enabled=False,
            ),

            MenuButton(
                "Salir",
                button_rect(4),
                callback=self._quit_game,
            ),
        ]

    def _new_simulation(self):
        """Abre la configuración de una nueva simulación."""

        self.game.scene_manager.change_scene(
            NewSimulationScene(self.game)
        )

    def _quit_game(self):
        """Solicita el cierre de la aplicación."""

        pygame.event.post(
            pygame.event.Event(pygame.QUIT)
        )

    def _handle_resize(self, screen):
        """Reconstruye los componentes dependientes del tamaño."""

        new_size = screen.get_size()

        if new_size == self.screen_size:
            return

        self.screen_size = new_size

        self.background = BackgroundRenderer(new_size)

        self.particles.resize(
            new_size[0],
            new_size[1],
        )

        self._create_buttons()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._quit_game()
            return

        for button in self.buttons:
            button.handle_event(event)

    def update(self, dt):
        self.background.update(dt)
        self.particles.update(dt)

    def draw(self, screen):
        self._handle_resize(screen)

        width, height = screen.get_size()

        # Paisaje.
        self.background.draw(screen)

        # Partículas.
        self.particles.draw(screen)

        # Capa oscura para mejorar la lectura de los botones.
        overlay = pygame.Surface(
            (width, height),
            pygame.SRCALPHA,
        )

        overlay.fill((8, 8, 20, 45))
        screen.blit(overlay, (0, 0))

        # Logotipo.
        self.logo.draw(
            screen,
            width // 2,
            int(height * 0.23),
        )

        # Botones.
        for button in self.buttons:
            button.draw(screen)

        # Versión.
        version_font = pygame.font.SysFont("arial", 15)

        version = version_font.render(
            "INSTINCT | SIMULADOR DE ECOSISTEMAS",
            True,
            (137, 132, 155),
        )

        screen.blit(
            version,
            (20, height - 30),
        )
