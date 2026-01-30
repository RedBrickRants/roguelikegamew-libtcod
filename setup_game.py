"""Handle the loading and initialization of game sessions."""
from __future__ import annotations
from typing import Optional
from engine import Engine
from game_map import GameWorld

from components.body_modification import ExtraBrain

import tcod
import copy
import lzma
import dill
import traceback
import colour
import entity_factories
import input_handlers
import constants as const

# Load the background image and remove the alpha channel.
background_image = tcod.image.load("menu_background.png")[:, :, :3]

def new_game() -> Engine:
    """Return a brand new game session as an Engine instance."""
    map_width = const.MAP_WIDTH 
    map_height = const.MAP_HEIGHT 

    room_max_size = const.ROOM_MAX_SIZE 
    room_min_size = const.ROOM_MIN_SIZE 
    max_rooms = const.MAX_ROOMS   
    
    
    player = copy.deepcopy(entity_factories.player)
    engine = Engine(player= player)
    engine.game_world = GameWorld(
        engine=engine,
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
    )
    engine.game_map = engine.game_world.generate_floor()
    engine.update_fov()

    engine.message_log.add_message(
        "Hello and welcome, adventurer, to yet another station!", colour.welcome_text
    )

    dagger = copy.deepcopy(entity_factories.dagger)
    leather_armor = copy.deepcopy(entity_factories.leather_armor)

    dagger.parent = player.inventory
    leather_armor.parent = player.inventory

    
    player.equipment.initialize_slots()
    player.inventory.items.append(dagger)
    left_arm = player.body.parts[2]  # Or find it properly
    
    player.equipment.toggle_equip(dagger, left_arm, add_message=False)
    
    player.inventory.items.append(leather_armor)
    torso = player.body.parts[1]
    player.equipment.toggle_equip(leather_armor, torso, add_message=False)

    # After giving player dagger and armor:
    test_brain_mod = copy.deepcopy(entity_factories.brain_mod_item)
    test_brain_mod.parent = player.inventory
    player.inventory.items.append(test_brain_mod)

   
    print(f"Player Stat bonuses: {engine.player.body.stat_bonuses}")
    print(f"Player equipped items: {[e.name for e in engine.player.equipment.equipped_items]}")
    print(f"Player AP bonuses: {engine.player.action_points.ap_bonuses}")
    print(f"Player max AP: {engine.player.action_points.max_ap}")
    print(f"Player body parts: {[p.name for p in engine.player.body.parts]}")
    print(f"Player body modifications: {[m.name for m in engine.player.body.applied_mods]}")
    print(f"Player initialized slots: {engine.player.equipment._initialized}")
        
    return engine

def load_game(filename: str) -> Engine:
    """Load an Engine instance from a file."""
    with open(filename, "rb") as f:
        engine = dill.loads(lzma.decompress(f.read()))
    assert isinstance(engine, Engine)
    return engine


class MainMenu(input_handlers.BaseEventHandler):
    """Handle the main menu rendering and input."""

    def on_render(self, console: tcod.console.Console) -> None:
        """Render the main menu on a background image."""
        console.draw_semigraphics(background_image, 0, 0)

        console.print(
            console.width // 2,
            console.height // 2 - 4,
            "TOMBS OF THE ANCIENT KINGS",
            fg=colour.menu_title,
            alignment=tcod.libtcodpy.CENTER,
        )
        console.print(
            console.width // 2,
            console.height - 2,
            "By (Your name here)",
            fg=colour.menu_title,
            alignment=tcod.libtcodpy.CENTER,
        )

        menu_width = 24
        for i, text in enumerate(
            ["[N] Play a new game", "[C] Continue last game", "[Q] Quit"]
        ):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust(menu_width),
                fg=colour.menu_text,
                bg=colour.black,
                alignment=tcod.libtcodpy.CENTER,
                bg_blend=tcod.libtcodpy.BKGND_ALPHA(64),
            )

    def ev_keydown(
        self, event: tcod.event.KeyDown
    ) -> Optional[input_handlers.BaseEventHandler]:
        if event.sym in (tcod.event.KeySym.q, tcod.event.KeySym.ESCAPE):
            raise SystemExit()
        elif event.sym == tcod.event.KeySym.c:
            try:
                return input_handlers.MainGameEventHandler(load_game("savegame.sav"))
            except FileNotFoundError:
                return input_handlers.PopupMessage(self, "No saved game to load.")
            except Exception as exc:
                traceback.print_exc()  # Print to stderr.
                return input_handlers.PopupMessage(self, f"Failed to load save:\n{exc}")
        elif event.sym == tcod.event.KeySym.n:
            return input_handlers.MainGameEventHandler(new_game())

        return None

