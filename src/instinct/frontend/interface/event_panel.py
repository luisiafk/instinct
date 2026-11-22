import pygame

from instinct.frontend.interface.widgets.scroll_panel import ScrollPanel


class EventPanel:
    def __init__(self, rect, theme_manager):
        self.rect = pygame.Rect(rect)
        self.theme_manager = theme_manager

        self.title_font = pygame.font.Font(None, 32)
        self.event_font = pygame.font.Font(None, 23)

        self.events = []

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

    def set_events(self, events):
        self.events = list(events)[-200:]

        content_height = max(
            self.scroll_panel.rect.height,
            len(self.events) * 38 + 12,
        )
        
        self.scroll_panel.set_content_height(content_height)

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
            y = 8

            for event in self.events:
                category_color = colors["secondary_text"]

                if event.category in ("death", "danger"):
                    category_color = (230, 100, 100)
                elif event.category in ("success", "reproduction"):
                    category_color = colors["gold"]

                text = self.event_font.render(
                    f"[{event.tick}] {event.message}",
                    True,
                    category_color,
                )

                surface.blit(text, (8, y))
                y += 38

        self.scroll_panel.draw(
            screen,
            draw_content=draw_events,
        )