from __future__ import annotations
from typing import Tuple, TYPE_CHECKING
import constants as const 
import numpy as np #type: ignore
import colour
import tile_types

if TYPE_CHECKING:
    from tcod  import console
    from engine import Engine
    from game_map import GameMap

def get_names_at_location(x:int, y:int, game_map:GameMap)-> str:
    if not game_map.in_bounds(x, y) or not game_map.visible[x, y]:
        return ""
    names = ", ".join(entity.name for entity in game_map.entities if entity.x ==x and entity.y == y)
    return names.capitalize()

def render_bar( 
        console: console.Console, 
        current_value: int, 
        maximum_value: int, 
        total_width: int
    )->None:
    bar_width = int(float(current_value)/maximum_value * total_width)
    console.draw_rect(x=0, y=45, width= total_width, height= 1, ch=1, bg=colour.bar_empty)
    if bar_width>0:
        console.draw_rect(x=0, y=45, width=bar_width,height=1, ch=1, bg=colour.bar_filled)

    console.print(x=1, y=45, string=f"HP:{current_value}/{maximum_value}", fg=colour.bar_text)

def render_station_level(
    console: console.Console, station_level: int, location: Tuple[int, int]
) -> None:
    """
    Render the level the player is currently on, at the given location.
    """
    x, y = location

    console.print(x=x, y=y, string=f"station level: {station_level}")

def render_names_at_mouse_location(
        console: console.Console, x: int, y: int, engine: Engine
)-> None:
    mouse_x, mouse_y = engine.mouse_location
    names_at_mouse_location = get_names_at_location(
        x=mouse_x, y=mouse_y, game_map=engine.game_map
    )
    console.print (x=x, y=y, string=names_at_mouse_location)

def render_ap_bar(
    console: console.Console,
    current_ap: int,
    maximum_ap: int,
    location: Tuple[int, int]
) -> None:
    x, y = location
    
    # Visual bar like HP bar
    bar_width = maximum_ap
    filled = "█" * current_ap
    empty = "░" * (maximum_ap - current_ap)
    
    console.print(
        x=x, y=y, 
        string=f"AP:[{empty}{filled}] {current_ap}/{maximum_ap}", 
        fg=colour.bar_text
    )
    

def render_map(console: console.Console, game_map:GameMap)-> None:
    #Using the Console class’s tiles_rgb method, we can quickly render the entire map
    console.rgb[0:game_map.width, 0:game_map.height] = np.select( 
        condlist=[game_map.visible, game_map.explored], 
        choicelist=[game_map.tiles["light"], 
        game_map.tiles["dark"]], 
        default=tile_types.SHROUD )


def render_entities(console: console.Console, game_map: GameMap) -> None:
    entities_sorted_for_rendering = sorted(
            game_map.entities, key=lambda x: x.render_order.value
        )
    for entity in entities_sorted_for_rendering:
            if game_map.visible[entity.x, entity.y]:
                console.print(entity.x, entity.y, entity.glyph, fg=entity.colour)

def render_stats():
    pass

def render_log ():
    pass

def render_death_screen(console):
    console.clear()
    console.print(const.MAP_VIEW_WIDTH // 2 - 5, const.MAP_VIEW_HEIGHT // 2, "YOU DIED", fg=(255, 0, 0))
    console.print(const.MAP_VIEW_WIDTH // 2 - 10, const.MAP_VIEW_HEIGHT // 2 + 2, "Press 'q' to quit", fg=(255, 255, 255))