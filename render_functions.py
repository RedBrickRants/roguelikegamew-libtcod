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

def render_stats_panel(console, actor, x, y, width, height):
    """Render actor stats with HP and AP bars"""
    console.draw_frame(x, y, width, height, title=actor.name[:15], fg=colour.white, bg=colour.black, clear=True)
    
    cy = y + 1
    
    # HP bar
    hp_width = width - 4
    hp_filled = int((actor.fighter.hp / actor.fighter.max_hp) * hp_width)
    console.print(x + 2, cy, "HP:", fg=colour.white)
    cy += 1
    console.draw_rect(x + 2, cy, hp_width, 1, ch=1, bg=colour.bar_empty)
    if hp_filled > 0:
        console.draw_rect(x + 2, cy, hp_filled, 1, ch=1, bg=colour.bar_filled)
    console.print(x + 2, cy, f"{actor.fighter.hp}/{actor.fighter.max_hp}", fg=colour.bar_text)
    cy += 2
    
    # AP bar
    if hasattr(actor, 'action_points'):
        ap_width = width - 4
        ap_filled = int((actor.action_points.ap / actor.action_points.max_ap) * ap_width)
        console.print(x + 2, cy, "AP:", fg=colour.white)
        cy += 1
        filled = "o" * actor.action_points.ap
        empty = "." * (actor.action_points.max_ap - actor.action_points.ap)
        console.print(x + 2, cy, f"{filled}{empty}", fg=colour.white)
        cy += 2
    
    # Stats
    console.print(x + 2, cy, f"ATK: {actor.fighter.strength}", fg=colour.white)
    cy += 1
    console.print(x + 2, cy, f"DEF: {actor.fighter.defence}", fg=colour.white)
    cy += 1
    console.print(x + 2, cy, f"LVL: {actor.level.current_level}", fg=colour.white)


def render_inventory_panel(console, actor, x, y, width, height):
    """Render inventory"""
    console.draw_frame(x, y, width, height, title="Inventory", fg=colour.white, bg=colour.black, clear=True)
    
    cy = y + 1
    if not actor.inventory.items:
        console.print(x + 2, cy, "[Empty]", fg=colour.impossible)
        return
    
    max_items = height - 2
    for i, item in enumerate(actor.inventory.items[:max_items]):
        equipped = " (E)" if actor.equipment.item_is_equipped(item) else ""
        text = f"{item.name[:12]}{equipped}"
        console.print(x + 2, cy, text, fg=colour.white)
        cy += 1


def render_names_at_mouse(console, x, y, engine):
    """Show entity name at mouse with frame"""
    mx, my = engine.mouse_location
    if not engine.game_map.in_bounds(mx, my) or not engine.game_map.visible[mx, my]:
        return
    
    names = [e.name for e in engine.game_map.entities if e.x == mx and e.y == my]
    if names:
        text = ", ".join(names)
        console.print(x, y, text[:60], fg=colour.white)