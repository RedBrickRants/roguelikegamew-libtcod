import copy
import tcod

import entity_factories
import constants as const
from entity import Entity
from engine import Engine
from procgen import generate_dungeon
from input_handlers import EventHandler



def main() -> None:


    tileset = tcod.tileset.load_tilesheet(
        "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    event_handler = EventHandler()
    player = copy.deepcopy(entity_factories.player)
    
    game_map = generate_dungeon(max_rooms=const.MAX_ROOMS, room_min_size=const.ROOM_MIN_SIZE, room_max_size=const.ROOM_MAX_SIZE, max_monsters_per_room = const.MAX_MONSTERS_PER_ROOM, map_width=const.MAP_WIDTH, map_height=const.MAP_HEIGHT, player=player)
    engine = Engine(event_handler=event_handler,game_map = game_map, player=player)

    with tcod.context.new(
        columns = const.SCREEN_WIDTH,
        rows = const.SCREEN_HEIGHT,
        tileset=tileset,
        title="Yet Another Roguelike Tutorial",
        vsync=True,
    ) as context:
        root_console = tcod.console.Console(const.SCREEN_WIDTH, const.SCREEN_HEIGHT, order="F")
        while True:
            engine.render(console=root_console, context=context)

            events = tcod.event.wait()

            engine.handle_events(events)


if __name__ == "__main__":
    main()