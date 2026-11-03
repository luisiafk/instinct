import os
import pygame
from loaders import load_terrains, load_objects, load_map
from simulation import Simulation
from entities import Creature
from ui import TacticalVisualizer

def main():
    # 1. Rutas absolutas dentro de 'src'
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    print(f"[*] Directorio base de trabajo: {BASE_DIR}")

    terrains_path = os.path.join(BASE_DIR, "terrains", "terrenos.te")
    objects_path = os.path.join(BASE_DIR, "objects", "objetos y recursos.ob")

    print(f"[*] Cargando terrenos desde: {terrains_path}")
    terrains = load_terrains(terrains_path)
    
    print(f"[*] Cargando objetos desde: {objects_path}")
    objects = load_objects(objects_path)

    # Definimos los mapas disponibles para las siguientes fases
    levels = [
        ("Bosque Ancestral", os.path.join(BASE_DIR, "maps", "bosque.map")),
        ("Desierto de Cenizas", os.path.join(BASE_DIR, "maps", "desierto.map")),
        ("Templo de Hielo", os.path.join(BASE_DIR, "maps", "hielo.map")),
        ("Abismo de Fuego", os.path.join(BASE_DIR, "maps", "fuego.map")),
    ]

    # Usamos un mapa de prueba mientras preparamos la seleccion de biomas
    level_name, map_path = levels[0]

    programs_dict = {}

    # Iniciamos el visualizador grafico
    print("[*] Iniciando interfaz grafica TacticalVisualizer...")
    visualizer = TacticalVisualizer(1280, 720)
    clock = pygame.time.Clock()

    print(f"\n--- CARGANDO BIOMA: {level_name} ({map_path}) ---")

    if not os.path.exists(map_path):
        print(f"[X] No se encontro el mapa en {map_path}")
        pygame.quit()
        return

    world = load_map(map_path, terrains, objects)
    sim = Simulation(world, seed=42)

    # Creamos las criaturas de prueba
    depredador = Creature(
        species_name="Depredador",
        faction="Rojas",
        health=100,
        lifespan=50,
        vision=5
    )

    recolector = Creature(
        species_name="Recolector",
        faction="Azules",
        health=80,
        lifespan=60,
        vision=6
    )

    sim.add_creature(depredador, 1, 1)
    sim.add_creature(
        recolector,
        min(world.width - 2, 5),
        min(world.height - 2, 5)
    )

    tick = 1
    turn_timer = 0.0
    turn_delay = 0.8

    # Mantenemos la simulacion activa hasta que el usuario salga
    running = True

    while running:
        # Mostramos el estado actual del mundo
        visualizer.render(sim, world, level_name, tick, None)

        # Esperamos mientras la simulacion esta pausada
        while visualizer.paused:
            visualizer.render(
                sim,
                world,
                level_name + " [PAUSADO]",
                tick,
                None
            )
            clock.tick(30)

        # Controlamos el tiempo de ejecucion
        dt = clock.tick(60) / 1000.0
        turn_timer += dt

        # Ejecutamos un nuevo tick cuando corresponde
        if turn_timer >= turn_delay:
            turn_timer = 0.0

            print(f"   -> Ejecutando Tick {tick} en {level_name}")

            sim.run_tick(programs_dict)
            tick += 1

    pygame.quit()

if __name__ == "__main__":
    main()