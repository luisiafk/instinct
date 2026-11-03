import pygame
import sys

class TacticalVisualizer:
    """
    Visualizador gráfico avanzado basado en Pygame para la simulación INSTINCT ⚔️.
    Diseñado con estética de grimorio táctico y alto rendimiento.
    """
    def __init__(self, width=1280, height=720):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("INSTINCT ⚔️ — Simulación Táctica de Criaturas")
        self.clock = pygame.time.Clock()
        
        # Paleta de Colores (Grimorio Táctico / Fantasía Oscura)
        self.COLOR_BG = (15, 13, 11)         # Pergamino nocturno muy oscuro
        self.COLOR_PANEL = (24, 20, 16)      # Panel lateral de control
        self.COLOR_GRID = (38, 32, 25)       # Líneas sutiles del bioma
        self.COLOR_TEXT = (210, 198, 170)    # Pergamino claro
        self.COLOR_ACCENT = (190, 140, 70)   # Bronce / Dorado táctico
        self.COLOR_HP_HIGH = (46, 139, 87)   # Verde salud óptima
        self.COLOR_HP_MID = (205, 133, 63)   # Ámbar salud media
        self.COLOR_HP_LOW = (178, 34, 34)    # Rojo crítico
        
        # Tipografías seguras con respaldo y soporte de emojis nativos
        try:
            self.font_title = pygame.font.SysFont("Consolas", 18, bold=True)
            self.font_body = pygame.font.SysFont("Consolas", 14)
            self.font_small = pygame.font.SysFont("Consolas", 11)
            self.font_icon = pygame.font.SysFont("Segoe UI Emoji", 16) # Fuente dedicada para los iconos
        except:
            self.font_title = pygame.font.Font(None, 24)
            self.font_body = pygame.font.Font(None, 18)
            self.font_small = pygame.font.Font(None, 14)
            self.font_icon = pygame.font.Font(None, 18)
            
        self.paused = False
        self.fps = 60

    def handle_events(self):
        """Gestiona los controles de teclado: ESPACIO (Pausa), FLECHAS (Velocidad), ESC (Salir)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_UP:
                    self.fps = min(120, self.fps + 15)
                elif event.key == pygame.K_DOWN:
                    self.fps = max(10, self.fps - 15)
        return self.paused

    def draw_health_bar(self, surface, x, y, w, h, current, maximum):
        """Dibuja una barra de vida con gradiente de color según el estado de salud."""
        if maximum <= 0: maximum = 100
        ratio = max(0.0, min(1.0, current / maximum))
        
        hp_color = self.COLOR_HP_HIGH
        if ratio < 0.6: hp_color = self.COLOR_HP_MID
        if ratio < 0.3: hp_color = self.COLOR_HP_LOW

        pygame.draw.rect(surface, (40, 32, 25), (x, y, w, h))
        if ratio > 0:
            pygame.draw.rect(surface, hp_color, (x, y, int(w * ratio), h))
        pygame.draw.rect(surface, self.COLOR_ACCENT, (x, y, w, h), 1)

    def render(self, sim, world, level_name: str, tick: int, total_ticks: int):
        """Renderiza toda la interfaz gráfica leyendo directamente los objetos del simulador y el mundo."""
        self.handle_events()
        self.screen.fill(self.COLOR_BG)
        
        # --- 1. DISEÑO DEL PANEL LATERAL (HUD / GRIMORIO) ---
        hud_width = 440
        hud_rect = pygame.Rect(self.width - hud_width, 0, hud_width, self.height)
        pygame.draw.rect(self.screen, self.COLOR_PANEL, hud_rect)
        pygame.draw.line(self.screen, self.COLOR_ACCENT, (self.width - hud_width, 0), (self.width - hud_width, self.height), 2)

        # Cabecera del HUD
        title_surf = self.font_title.render(f"⚔️ BIOMA: {level_name.upper()}", True, self.COLOR_ACCENT)
        tick_surf = self.font_body.render(f"TICK: [ {tick:02d} / {total_ticks:02d} ]", True, self.COLOR_TEXT)
        status_text = "ESTADO: PAUSADO [ESPACIO]" if self.paused else f"ESTADO: ACTIVO ({self.fps} FPS)"
        status_surf = self.font_small.render(status_text, True, (200, 150, 80) if self.paused else (100, 180, 100))
        
        self.screen.blit(title_surf, (self.width - hud_width + 20, 20))
        self.screen.blit(tick_surf, (self.width - hud_width + 20, 50))
        self.screen.blit(status_surf, (self.width - hud_width + 20, 75))
        
        pygame.draw.line(self.screen, self.COLOR_GRID, (self.width - hud_width + 20, 100), (self.width - 20, 100), 1)
        
        # Lista de agentes activos usando lectura segura (getattr)
        y_offset = 115
        agents_header = self.font_body.render(" [ AGENTES ACTIVOS EN EL CAMPO ]", True, self.COLOR_TEXT)
        self.screen.blit(agents_header, (self.width - hud_width + 20, y_offset))
        y_offset += 30
        
        creatures = getattr(sim, 'creatures', [])
        if not creatures:
            dead_text = self.font_body.render(" ☠️ [SILENCIO SEPULCRAL] Sin agentes.", True, (160, 90, 90))
            self.screen.blit(dead_text, (self.width - hud_width + 20, y_offset))
        else:
            for c in creatures:
                if y_offset > self.height - 50:
                    break 
                
                species = getattr(c, 'species_name', getattr(c, 'name', 'Desconocido'))
                faction = getattr(c, 'faction', 'Neutral')
                x_pos = getattr(c, 'x', 0)
                y_pos = getattr(c, 'y', 0)
                age = getattr(c, 'age', 0)
                lifespan = getattr(c, 'lifespan', 100)
                health = getattr(c, 'health', 100)
                
                icon = "👹" if "Depredador" in species or "Asalto" in species else "🛡️"
                
                # Renderizado combinado con fuente de iconos para los emojis y cuerpo para el texto
                line1_icon = self.font_icon.render(icon, True, self.COLOR_ACCENT)
                line1_text = self.font_body.render(f" [{species}] <{faction}>", True, self.COLOR_TEXT)
                line2 = self.font_small.render(f"   Pos: ({x_pos}, {y_pos}) | Edad: {age}/{lifespan}", True, (160, 150, 130))
                
                self.screen.blit(line1_icon, (self.width - hud_width + 25, y_offset))
                self.screen.blit(line1_text, (self.width - hud_width + 50, y_offset))
                self.screen.blit(line2, (self.width - hud_width + 25, y_offset + 20))
                
                self.draw_health_bar(self.screen, self.width - hud_width + 25, y_offset + 40, 260, 10, health, 100)
                
                y_offset += 65

        # --- 2. ZONA DEL MAPA / BIOMA ---
        map_area_width = self.width - hud_width
        world_w = getattr(world, 'width', 10)
        world_h = getattr(world, 'height', 10)
        
        cell_size = min(map_area_width // max(1, world_w), self.height // max(1, world_h))
        map_origin_x = (map_area_width - (world_w * cell_size)) // 2
        map_origin_y = (self.height - (world_h * cell_size)) // 2
        
        # Dibujar cuadrícula y elementos del terreno/objetos
        for x in range(world_w):
            for y in range(world_h):
                rect = pygame.Rect(map_origin_x + x * cell_size, map_origin_y + y * cell_size, cell_size, cell_size)
                pygame.draw.rect(self.screen, self.COLOR_GRID, rect, 1)
                
                tile = world.get_tile(x, y)
                if tile:
                    if tile.game_object and not getattr(tile.game_object, 'walkable', True):
                        inner_rect = pygame.Rect(map_origin_x + x * cell_size + 2, map_origin_y + y * cell_size + 2, cell_size - 4, cell_size - 4)
                        pygame.draw.rect(self.screen, (55, 48, 40), inner_rect)
                    
        # Dibujar agentes encima del mapa
        for c in creatures:
            cx = map_origin_x + getattr(c, 'x', 0) * cell_size + cell_size // 2
            cy = map_origin_y + getattr(c, 'y', 0) * cell_size + cell_size // 2
            
            species = getattr(c, 'species_name', '')
            color = (210, 60, 60) if "Depredador" in species or "Asalto" in species else (60, 140, 210)
            
            radius = max(5, cell_size // 3)
            pygame.draw.circle(self.screen, color, (cx, cy), radius)
            pygame.draw.circle(self.screen, self.COLOR_TEXT, (cx, cy), radius, 1)

        pygame.display.flip()