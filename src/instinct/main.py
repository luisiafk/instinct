import os
import pygame
import random

from maps.loaders import load_terrains, load_objects, load_map
from simulation import Simulation
from entities import Creature
from ui import TacticalVisualizer
from backend.compiler import compile_file

def main():
    # 1. Rutas absolutas dentro de 'src'
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    print(f"[*] Directorio base de trabajo: {BASE_DIR}")

    terrains_path = os.path.join(BASE_DIR, "terrains", "terrenos.te")
    objects_path = os.path.join(BASE_DIR, "objects", "objetos.ob")
    scripts_dir = os.path.join(BASE_DIR, "scripts")

    print(f"[*] Cargando terrenos desde: {terrains_path}")
    terrains = load_terrains(terrains_path)

    print(f"[*] Cargando objetos desde: {objects_path}")
    objects = load_objects(objects_path)

    # Definir los mapas de campaña dentro de src/maps/
    levels = [
        ("Bosque Ancestral", os.path.join(BASE_DIR, "maps", "bosque.map")),
        ("Desierto de Cenizas", os.path.join(BASE_DIR, "maps", "desierto.map")),
        ("Templo de Hielo", os.path.join(BASE_DIR, "maps", "hielo.map")),
        ("Abismo de Fuego", os.path.join(BASE_DIR, "maps", "fuego.map")),
    ]



    print(f"[*] Cargando scripts desde: {scripts_dir}")
    programs_dict = {}
    creature_blueprints = {}
    if os.path.exists(scripts_dir):
        for filename in os.listdir(scripts_dir):
            if filename.endswith(".ins"):
                script_path = os.path.join(scripts_dir, filename)
                try:
                    program = compile_file(script_path)
                    species_name = program.header.creature # o program.header.creature_name
                    programs_dict[species_name] = program.statements  # o program.body
                    creature_blueprints[species_name] = {
                        'faction': program.header.faction,
                        'health': program.header.health,
                        'vision': program.header.vision,
                        'lifespan': program.header.lifespan
                    }
                    print(species_name)
                    print(f"   [OK] Compilado con éxito: {species_name}")
                except Exception as err:
                    print(f"   [X] Error en {filename}: {err}")


    total_ticks = 25  # Aumentamos un poco los ticks para disfrutar la simulación

    # Instanciar el visualizador gráfico
    print("[*] Iniciando interfaz gráfica TacticalVisualizer...")
    visualizer = TacticalVisualizer(1280, 720)
    clock = pygame.time.Clock()

    # 3. Bucle secuencial de niveles (Campaña)
    for level_name, map_path in levels:
        print(f"\n--- CARGANDO NIVEL: {level_name} ({map_path}) ---")
        if not os.path.exists(map_path):
            print(f"   [X] ¡ERROR CRÍTICO! No se encontró el mapa en {map_path}")
            continue

        world = load_map(width=20, height=15, terrains_dict=terrains, objects_dict=objects)
        sim = Simulation(world, seed=42)

        for species_name, data in creature_blueprints.items():
            creature_instance = Creature(
                species_name=species_name,
                faction=data['faction'],
                health=data['health'],
                lifespan=data['lifespan'],
                vision=data['vision']
            )

            placed = False
            attempts = 0
            while not placed and attempts < 100:
                pos_x = random.randint(0, world.width - 1)
                pos_y = random.randint(0, world.height - 1)

                placed = sim.add_creature(creature_instance, pos_x, pos_y)
                attempts += 1

            if placed:
                print(f"   [+] Criatura instanciada: [{species_name}] en {pos_x}, {pos_y}")
            else:
                print(f"   [!] No se pudo instanciar: {species_name} en {pos_x}, {pos_y}")


        tick = 1
        turn_timer = 0.0
        turn_delay = 0.8  # 0.8 segundos por turno para poder apreciarlo bien en pantalla

        # 4. Bucle de ejecución por Ticks
        running_level = True
        while tick <= total_ticks and running_level:
            # Renderizar la interfaz visual en tiempo real
            visualizer.render(sim, world, level_name, tick, total_ticks)

            # Manejar eventos de pausa (Barra espaciadora)
            while visualizer.paused:
                visualizer.render(sim, world, level_name + " [PAUSADO]", tick, total_ticks)
                pygame.time.delay(100)
                # Permitir cerrar la ventana o quitar pausa limpiamente
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return

            # Control de tiempo fluido (60 FPS)
            dt = clock.tick(60) / 1000.0
            turn_timer += dt

            # Ejecutar turno cuando transcurra el tiempo establecido
            if turn_timer >= turn_delay:
                turn_timer = 0.0
                print(f"   -> Ejecutando Tick {tick}/{total_ticks} en {level_name}")

                sim.run_tick(programs_dict)

                # Si mueren todas las criaturas, pasamos al siguiente nivel
                if not sim.creatures:
                    print(f"   [!] Todos los agentes han perecido en {level_name}.")
                    visualizer.render(sim, world, level_name + " (FIN DE NIVEL)", tick, total_ticks)
                    pygame.time.wait(1500)
                    break

                tick += 1

        pygame.time.wait(1000)

    print("\n" + "="*66)
    print("  🏆 ¡CAMPAÑA DE SIMULACIÓN INSTINCT COMPLETADA CON ÉXITO! 🏆")
    print("="*66)
    pygame.quit()

if __name__ == "__main__":
    main()

