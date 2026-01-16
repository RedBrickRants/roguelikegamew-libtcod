import copy
import traceback
import tcod
import colour

import entity_factories
import constants as const
import exceptions
import input_handlers
from entity import Entity
from engine import Engine
from procgen import generate_dungeon




def main() -> None:


    tileset = tcod.tileset.load_tilesheet(
        "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    player = copy.deepcopy(entity_factories.player)
    engine = Engine(player= player)
    engine.game_map = generate_dungeon(max_rooms=const.MAX_ROOMS, room_min_size=const.ROOM_MIN_SIZE, room_max_size=const.ROOM_MAX_SIZE, max_monsters_per_room = const.MAX_MONSTERS_PER_ROOM,max_items_per_room=const.MAX_ITEMS_PER_ROOM, map_width=const.MAP_WIDTH, map_height=const.MAP_HEIGHT, engine = engine)
    engine.update_fov()
    engine.message_log.add_message("Hello and welcome to yet another dungeon!", colour.welcome_text)
    handler: input_handlers.BaseEventHandler = input_handlers.MainGameEventHandler(engine)

    with tcod.context.new(
        columns = const.SCREEN_WIDTH,
        rows = const.SCREEN_HEIGHT,
        tileset=tileset,
        title="Yet Another Roguelike Tutorial",
        vsync=True,
    ) as context:
        root_console = tcod.console.Console(const.SCREEN_WIDTH, const.SCREEN_HEIGHT, order="F")
        try:
            while True:
                root_console.clear()
                handler.on_render(console=root_console)
                context.present(root_console)

                try:
                    for event in tcod.event.wait():
                        context.convert_event(event)
                        handler = handler.handle_events(event)
                except Exception:  # Handle exceptions in game.
                    traceback.print_exc()  # Print error to stderr.
                    # Then print the error to the message log.
                    if isinstance(handler, input_handlers.EventHandler):
                        handler.engine.message_log.add_message(
                            traceback.format_exc(), colour.error
                        )
        except exceptions.QuitWithoutSaving:
            raise
        except SystemExit:  # Save and quit.
            # TODO: Add the save function here
            raise
        except BaseException:  # Save on any other unexpected exception.
            # TODO: Add the save function here
            raise
            


if __name__ == "__main__":
    main()