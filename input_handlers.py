#input_handlers.py
from __future__ import annotations
from typing import Callable, Optional, Tuple, TYPE_CHECKING, Union
from actions import Action, EscapeAction, BumpAction, ReloadAction, WaitAction, PickupAction,RangedAttackAction
from equipment_types import EquipmentType, ModificationType, ModificationSlot
import tcod
import colour
import exceptions
import actions
import os

if TYPE_CHECKING:
    from engine import Engine
    from entity import Item, Actor
    from components.body import Body, BodyPart
    from components.body_modification import Modification
    from components.consumable import Consumable
    from components.equippable import Equippable, RangedEquippable
    from components.equipment import Equipment
    

MOVE_KEYS = {
    # Arrow keys.
    tcod.event.KeySym.UP: (0, -1),
    tcod.event.KeySym.DOWN: (0, 1),
    tcod.event.KeySym.LEFT: (-1, 0),
    tcod.event.KeySym.RIGHT: (1, 0),
    tcod.event.KeySym.HOME: (-1, -1),
    tcod.event.KeySym.END: (-1, 1),
    tcod.event.KeySym.PAGEUP: (1, -1),
    tcod.event.KeySym.PAGEDOWN: (1, 1),

    # Numpad keys.
    tcod.event.KeySym.KP_1: (-1, 1),
    tcod.event.KeySym.KP_2: (0, 1),
    tcod.event.KeySym.KP_3: (1, 1),
    tcod.event.KeySym.KP_4: (-1, 0),
    tcod.event.KeySym.KP_6: (1, 0),
    tcod.event.KeySym.KP_7: (-1, -1),
    tcod.event.KeySym.KP_8: (0, -1),
    tcod.event.KeySym.KP_9: (1, -1),

    # Vi keys.
    tcod.event.KeySym.h: (-1, 0),
    tcod.event.KeySym.j: (0, 1),
    tcod.event.KeySym.k: (0, -1),
    tcod.event.KeySym.l: (1, 0),
    tcod.event.KeySym.y: (-1, -1),
    tcod.event.KeySym.u: (1, -1),
    tcod.event.KeySym.b: (-1, 1),
    tcod.event.KeySym.n: (1, 1),
}

WAIT_KEYS = {
    tcod.event.KeySym.PERIOD,
    tcod.event.KeySym.KP_5,
    tcod.event.KeySym.CLEAR,
}

CURSOR_Y_KEYS = {
    tcod.event.KeySym.UP: -1,
    tcod.event.KeySym.DOWN: 1,
    tcod.event.KeySym.PAGEUP: -10,
    tcod.event.KeySym.PAGEDOWN: 10,
}

CONFIRM_KEYS = {
    tcod.event.KeySym.RETURN,
    tcod.event.KeySym.KP_ENTER,
}
ActionOrHandler = Union[Action, "BaseEventHandler"]
"""An event handler return value which can trigger an action or switch active handlers.
If a handler is returned then it will become the active handler for future events.
If an action is returned it will be attempted and if it's valid then
MainGameEventHandler will become the active handler."""

class BaseEventHandler(tcod.event.EventDispatch[ActionOrHandler]):
    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handle an event and return the next active event handler."""
        state = self.dispatch(event)
        if isinstance(state, BaseEventHandler):
            return state
        assert not isinstance(state, Action), f"{self!r} can not handle actions."
        return self

    def on_render(self, console: tcod.console.Console) -> None:
        raise NotImplementedError()

    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()

class PopupMessage(BaseEventHandler):
    """Display a popup text window."""

    def __init__(self, parent_handler: BaseEventHandler, text: str):
        self.parent = parent_handler
        self.text = text

    def on_render(self, console: tcod.console.Console) -> None:
        """Render the parent and dim the result, then print the message on top."""
        self.parent.on_render(console)
        console.rgb["fg"] //= 8
        console.rgb["bg"] //= 8

        console.print(
            console.width // 2,
            console.height // 2,
            self.text,
            fg=colour.white,
            bg=colour.black,
            alignment=tcod.libtcodpy.CENTER,
        )

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[BaseEventHandler]:
        """Any key returns to the parent handler."""
        return self.parent

class EventHandler(BaseEventHandler):
    def __init__(self, engine: Engine):
        self.engine = engine
    
    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handle events for input handlers with an engine."""
        action_or_state = self.dispatch(event)
        if isinstance(action_or_state, BaseEventHandler):
            return action_or_state
        if self.handle_action(action_or_state):
            # A valid action was executeed.
            if not self.engine.player.is_alive:
                # The player was killed sometime during or after the action.
                return GameOverEventHandler(self.engine)
            
            elif self.engine.player.level.requires_level_up:
                return LevelUpEventHandler(self.engine)
            
            return MainGameEventHandler(self.engine)  # Return to the main handler.
        return self
    

    def handle_action(self, action: Optional[Action]) -> bool:
        """Handle actions returned from event methods.

        Returns True if the action will advance a turn.
        """
        if action is None:
            return False

        try:
            action.perform()
        except exceptions.Impossible as exc:
            self.engine.message_log.add_message(exc.args[0], colour.impossible)

            if not self.engine.player.action_points.can_act():
                self.engine.handle_enemy_turns()
                for entity in set(self.engine.game_map.actors):
                    entity.action_points.refresh()
                self.engine.update_fov()
                return True

            return False  # Skip enemy turn on exceptions.
        
        if self.engine.player.action_points.can_act() :
            # Player can keep acting
            self.engine.update_fov()
            return False  # Don't end turn yet

        self.engine.handle_enemy_turns()
        for entity in set(self.engine.game_map.actors):
            entity.action_points.refresh() 
        self.engine.update_fov()
        return True

    def ev_mousemotion(self, event:tcod.event.MouseMotion)-> None:
        map_x = event.tile.x + self.engine.camera_x
        map_y = event.tile.y + self.engine.camera_y
        if self.engine.game_map.in_bounds(map_x, map_y):
            self.engine.mouse_location = map_x, map_y
   
    def on_render(self, console:tcod.console.Console)-> None:
        self.engine.render(console)

class AskUserEventHandler(EventHandler):
    """Handles user input for actions which require special input."""


    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        """By default any key exits this input handler."""
        if event.sym in {  # Ignore modifier keys.
            tcod.event.KeySym.LSHIFT,
            tcod.event.KeySym.RSHIFT,
            tcod.event.KeySym.LCTRL,
            tcod.event.KeySym.RCTRL,
            tcod.event.KeySym.LALT,
            tcod.event.KeySym.RALT,
        }:
            return None
        return self.on_exit()

    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown
    ) -> Optional[ActionOrHandler]:
        """By default any mouse click exits this input handler."""
        return self.on_exit()

    def on_exit(self) -> Optional[ActionOrHandler]:
        """Called when the user is trying to exit or cancel an action.

        By default this returns to the main event handler.
        """
        return MainGameEventHandler(self.engine)   

class CharacterScreenEventHandler(AskUserEventHandler):
    TITLE = "Character Information"

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console)

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        y = 0

        width = len(self.TITLE) + 4

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=12,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        console.print(
            x=x + 1, y=y + 1, string=f"Level: {self.engine.player.level.current_level}"
        )
        console.print(
            x=x + 1, y=y + 2, string=f"XP: {self.engine.player.level.current_xp}"
        )
        console.print(
            x=x + 1,
            y=y + 3,
            string=f"XP for next Level: {self.engine.player.level.experience_to_next_level}",
        )

        console.print(
            x=x + 1, y=y + 4, string=f"Attack: {self.engine.player.fighter.strength}"
        )
        console.print(
            x=x + 1, y=y + 5, string=f"Defence: {self.engine.player.fighter.defence}"
        )
        console.print(
            x = x+1, y = y+6, string = f"Bonus AP: {self.engine.player.action_points.ap_bonuses}"
        )

class LevelUpEventHandler(AskUserEventHandler):
    TITLE = "Level Up"

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console)

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        console.draw_frame(
            x=x,
            y=0,
            width=35,
            height=8,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        console.print(x=x + 1, y=1, string="Congratulations! You level up!")
        console.print(x=x + 1, y=2, string="Select an attribute to increase.")

        console.print(
            x=x + 1,
            y=4,
            string=f"a) Constitution (+20 HP, from {self.engine.player.fighter.max_hp})",
        )
        console.print(
            x=x + 1,
            y=5,
            string=f"b) Strength (+1 attack, from {self.engine.player.fighter.strength})",
        )
        console.print(
            x=x + 1,
            y=6,
            string=f"c) Agility (+1 defence, from {self.engine.player.fighter.defence})",
        )

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.KeySym.a

        if 0 <= index <= 2:
            if index == 0:
                player.level.increase_max_hp()
            elif index == 1:
                player.level.increase_strength()
            else:
                player.level.increase_defence()
        else:
            self.engine.message_log.add_message("Invalid entry.", colour.invalid)

            return None

        return super().ev_keydown(event)

    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown
    ) -> Optional[ActionOrHandler]:
        """
        Don't allow the player to click to exit the menu, like normal.
        """
        return None

class InventoryEventHandler(AskUserEventHandler):
    """This handler lets the user select an item.

    What happens then depends on the subclass.
    """
    TITLE= "<missing title>"
    def on_render(self, console:tcod.console.Console)-> None:
        """Render an inventory menu, which displays the items in the inventory, and the letter to select them.
        Will move to a different position based on where the player is located, so the player can always see where
        they are.
        """
        super().on_render(console)
        number_of_items_in_inventory = len(self.engine.player.inventory.items)
        height = number_of_items_in_inventory+2

        if height <=3:
            height = 3
        
        if self.engine.player.x <=30:
            x = 40
        else:
            x = 0

        y = 0

        width = len(self.TITLE)+4

        console.draw_frame(
            x=x,
            y=y,
            width = width,
            height= height,
            title = self.TITLE,
            clear = True,
            fg =(255,255,255),
            bg = (0,0,0)
        )

        if number_of_items_in_inventory > 0:
            for i, item in enumerate(self.engine.player.inventory.items):
                item_key = chr(ord("a")+i)
                is_equipped = self.engine.player.equipment.item_is_equipped(item)

                item_string = f"({item_key}) {item.name}"

                if is_equipped:
                    item_string = f"{item_string} (E)"

                console.print(x + 1, y + i + 1, item_string)
        else:
            console.print(x+1, y+1, "[EMPTY]")
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        index = key -tcod.event.KeySym.a

        if 0 <= index <= 26:
            try:
                selected_item = player.inventory.items[index]
            except IndexError:
                self.engine.message_log.add_message("Invalid entry.", colour.invalid)
                return None
            return self.on_item_selected(selected_item)
        return super().ev_keydown(event)
    
    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        """Called when the user selects a valid item."""
        raise NotImplementedError()
    
class InventoryActivateHandler(InventoryEventHandler):
    """Handle using an inventory item."""

    TITLE = "Select an item to use"

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        if item.consumable:
            # Return the action for the selected item.
            return item.consumable.get_action(self.engine.player)
        elif item.equippable:
            return EquipmentSelectionHandler(self.engine, item)
        else:
            return None

class InventoryDropHandler(InventoryEventHandler):
    """Handle dropping an inventory item."""

    TITLE = "Select an item to drop"

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        """Drop this item."""
        return actions.DropItem(self.engine.player, item)
    
class EquipmentSelectionHandler(AskUserEventHandler):
    """Handles selecting which body part to equip an item to"""
    
    TITLE = "Select Body Part"
    
    def __init__(self, engine: Engine, item: Item):
        super().__init__(engine)
        self.item = item
        self.valid_parts = engine.player.equipment.get_valid_parts_for_item(item)
    
    def on_render(self, console: tcod.console.Console) -> None:
        """Render the body part selection menu"""
        super().on_render(console)
        
        player = self.engine.player
        
        # Position menu
        if player.x <= 30:
            x = 40
        else:
            x = 0
        y = 0
        
        height = len(self.valid_parts) + 4
        if height < 5:
            height = 5
        width = 35
        
        console.draw_frame(
            x=x, y=y,
            width=width, height=height,
            title=self.TITLE,
            clear=True,
            fg=colour.white,
            bg=colour.black
        )
        
        # Show item info
        console.print(
            x=x + 1, y=y + 1,
            string=f"Equip: {self.item.name}"
        )
        
        # Show valid body parts
        if not self.valid_parts:
            console.print(
                x=x + 1, y=y + 3,
                string="No valid body parts!",
                fg=colour.impossible
            )
        else:
            for i, part in enumerate(self.valid_parts):
                key = chr(ord("a") + i)
                
                # Show what's currently equipped
                current = player.equipment.equipped_items.get(part)
                status = ""
                if current:
                    status = f" [Currently: {current.name}]"
                
                console.print(
                    x=x + 1, y=y + 3 + i,
                    string=f"({key}) {part.name}{status}"
                )
    
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.KeySym.a
        
        if 0 <= index < len(self.valid_parts):
            selected_part = self.valid_parts[index]
            return actions.EquipAction(player, self.item, selected_part)
        
        return super().ev_keydown(event)

class SelectIndexHandler(AskUserEventHandler):
    """Handles asking the user for an index on the map"""
    def __init__(self, engine: Engine):
        """Sets the cursor to the player when this handler is constructed."""
        super().__init__(engine)
        player = self.engine.player
        engine.mouse_location = player.x, player.y
    
    def on_render(self, console: tcod.console.Console)-> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)

        world_x, world_y = self.engine.mouse_location
        screen_x = world_x - self.engine.camera_x
        screen_y = world_y - self.engine.camera_y
        console.rgb["bg"][screen_x,screen_y] = colour.white
        console.rgb["fg"][screen_x,screen_y] = colour.black

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        """Check for key movement or confirmation keys."""
        key = event.sym
        if key in MOVE_KEYS:
            modifier = 1 #Holding modifier keys will speed up key movement.
            if event.mod & (tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT):
                modifier *= 5
            if event.mod & (tcod.event.KMOD_LCTRL | tcod.event.KMOD_RCTRL):
                modifier *= 10
            if event.mod & (tcod.event.KMOD_LALT | tcod.event.KMOD_RALT):
                modifier *= 20

            x,y = self.engine.mouse_location
            dx,dy = MOVE_KEYS[key]
            x += dx * modifier
            y += dy * modifier
            #Clamp the cursor index to the map size.
            x = max(0, min(x, self.engine.game_map.width - 1))
            y = max(0, min(y, self.engine.game_map.height - 1))
            self.engine.mouse_location = x, y
            return None
        elif key in CONFIRM_KEYS:
            return self.on_index_selected(*self.engine.mouse_location)
        return super().ev_keydown(event)
    
    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown
    ) -> Optional[ActionOrHandler]:
        """Left click confirms a selection."""
        if self.engine.game_map.in_bounds(*event.tile):
            if event.button == 1:
                return self.on_index_selected(*event.tile)
        return super().ev_mousebuttondown(event)
    
    def on_index_selected(self, x: int, y: int) -> Optional[ActionOrHandler]:
        """Called when an index is selected."""
        raise NotImplementedError()

class LookHandler(SelectIndexHandler):
    """Lets the player look around using the keyboard."""

    def on_index_selected(self, x: int, y: int) -> MainGameEventHandler:
        """Return to main handler."""
        self.engine.event_handler = MainGameEventHandler(self.engine)

class SingleRangedAttackHandler(SelectIndexHandler):
    """Handles targeting a single enemy. Only the enemy selected will be affected."""

    def __init__(
        self, engine: Engine, callback: Callable[[Tuple[int, int]], Optional[Action]]
    ):
        super().__init__(engine)

        self.callback = callback

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        return self.callback((x, y))
    
class AreaRangedAttackHandler(SelectIndexHandler):
    """Handles targeting an area within a given radius. Any entity within the area will be affected."""

    def __init__(
        self,
        engine: Engine,
        radius: int,
        callback: Callable[[Tuple[int, int]], Optional[Action]],
    ):
        super().__init__(engine)

        self.radius = radius
        self.callback = callback

    def on_render(self, console: tcod.console.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)

        x, y = self.engine.mouse_location

        # Draw a rectangle around the targeted area, so the player can see the affected tiles.
        console.draw_frame(
            x=x - self.radius - 1,
            y=y - self.radius - 1,
            width=self.radius ** 2,
            height=self.radius ** 2,
            fg=colour.red,
            clear=False,
        )

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        return self.callback((x, y))  
     
class MainGameEventHandler(EventHandler):
    def __init__(self, engine: Engine):
        self.engine = engine

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        action: Optional[Action] = None

        key = event.sym
        modifier = event.mod
        player = self.engine.player

        if key == tcod.event.KeySym.PERIOD and modifier & (
            tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT
        ):
            return actions.TakeStairsAction(player)

        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]
            action = BumpAction(player, dx,dy)
        elif key in WAIT_KEYS:
            action = WaitAction(player)

        elif key == tcod.event.KeySym.ESCAPE:
            action = EscapeAction(player)
        elif key == tcod.event.KeySym.q:
            action = EscapeAction(player)
        elif key == tcod.event.KeySym.v:
            return LogHistoryViewer(self.engine)
        elif key == tcod.event.KeySym.g:
            # Check how many items are at player location
            items_here = [
                item for item in self.engine.game_map.items
                if item.x == player.x and item.y == player.y
            ]
            
            if len(items_here) == 0:
                self.engine.message_log.add_message("There's nothing here to pick up.", colour.impossible)
                return None
            elif len(items_here) == 1:
                # Only one item, pick it up directly
                action = PickupAction(player)
            else:
                # Multiple items, show menu
                return PickupMenuHandler(self.engine, items_here)
        elif key == tcod.event.KeySym.i:
            return InventoryActivateHandler(self.engine)
        elif key == tcod.event.KeySym.d:
            return InventoryDropHandler(self.engine)
        elif key == tcod.event.KeySym.c:
            return CharacterScreenEventHandler(self.engine)
        elif key == tcod.event.KeySym.SLASH:
            return EnemyLookHandler(self.engine)
        
        elif key == tcod.event.KeySym.f:  
            gun = get_equipped_gun(player)
            if gun:
                return GunTargetingHandler(self.engine, gun)
            else:
                self.engine.message_log.add_message(
                    "You don't have a ranged weapon equipped!", 
                    colour.impossible
                )
                return None

        elif key == tcod.event.KeySym.r:  
            gun = get_equipped_gun(player)
            if gun:
                action = ReloadAction(player, gun)
            else:
                self.engine.message_log.add_message(
                    "You don't have a ranged weapon equipped!", 
                    colour.impossible
                )
                return None
        elif key == tcod.event.KeySym.s:
            return LookHandler(self.engine)
        elif key == tcod.event.KeySym.o:
            return DoorDirectionHandler(self.engine)


        # No valid key was pressed
        return action
    
class GameOverEventHandler(EventHandler):
    def on_quit(self) -> None:
        """Handle exiting out of a finished game."""
        if os.path.exists("savegame.sav"):
            os.remove("savegame.sav")  # Deletes the active save file.
        raise exceptions.QuitWithoutSaving()  # Avoid saving a finished game.

    def ev_quit(self, event: tcod.event.Quit) -> None:
        self.on_quit()

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        if event.sym == tcod.event.KeySym.ESCAPE or event.sym == tcod.event.KeySym.q:
            self.on_quit()
    
class LogHistoryViewer(EventHandler):
    #prints the history of  the log ona  larger window which can be navigated
    def __init__(self, engine:Engine):
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length

    def on_render(self, console:tcod.console.Console)-> None:
        super().on_render(console)
        log_console = tcod.console.Console(console.width -6, console.height -6)

        log_console.draw_frame(0,0, log_console.width, log_console.height)
        log_console.print_box(0,0, log_console.width, 1, "LOG HISTORY", alignment=tcod.constants.CENTER)

        #render the message log using the cursor
        self.engine.message_log.render_messages(
            log_console, 1, 1, log_console.width-2, log_console.height -2, 
            self.engine.message_log.messages[:self.cursor+1]
        )
        log_console.blit(console, 3, 3)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[MainGameEventHandler]:
        # Fancy conditional movement to make it feel right.
        if event.sym in CURSOR_Y_KEYS:
            adjust = CURSOR_Y_KEYS[event.sym]
            if adjust < 0 and self.cursor == 0:
                # Only move from the top to the bottom when you're on the edge.
                self.cursor = self.log_length - 1
            elif adjust > 0 and self.cursor == self.log_length - 1:
                # Same with bottom to top movement.
                self.cursor = 0
            else:
                # Otherwise move while staying clamped to the bounds of the history log.
                self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
        elif event.sym == tcod.event.KeySym.HOME:
            self.cursor = 0  # Move directly to the top message.
        elif event.sym == tcod.event.KeySym.END:
            self.cursor = self.log_length - 1  # Move directly to the last message.
        else:  # Any other key moves back to the main game state.
            return MainGameEventHandler(self.engine)
        return None
    
class ModificationApplicationHandler(AskUserEventHandler):
    """Handles selecting which body part to apply a modification to"""

    TITLE = "Apply Modification"

    def __init__(self, engine: Engine, modification_item: Item, 
                    modification_class, initial_level: int):
        super().__init__(engine)
        self.modification_item = modification_item
        self.modification_class = modification_class
        self.initial_level = initial_level

    def on_render(self, console: tcod.console.Console) -> None:
        """Render body part selection menu"""
        super().on_render(console)
        
        player = self.engine.player
        body_parts = player.body.parts
        mod_instance = self.modification_class(level=self.initial_level)

        # Position menu
        if player.x <= 30:
            x = 40
        else:
            x = 0
        y = 0
        
        # Calculate menu size based on mod type
        if mod_instance.mod_type == ModificationType.INTRINSIC:
            height = 5  # Smaller menu for intrinsic
            width = 40
        else:
            height = len(body_parts) + 4
            width = 40
        
        console.draw_frame(
            x=x, y=y,
            width=width, height=height,
            title=self.TITLE,
            clear=True,
            fg=colour.white,
            bg=colour.black
        )
        
        # Show modification info
        mod_instance = self.modification_class(level=self.initial_level)
        console.print(
            x=x + 1, y=y + 1,
            string=f"Mod: {mod_instance.name} (Lvl {self.initial_level})"
        )
        console.print(
            x=x + 1, y=y + 2,
            string=f"Type: {mod_instance.mod_type}"
        )
        if mod_instance.mod_type == ModificationType.INTRINSIC:
            # Intrinsic mods have no choice - just confirm
            console.print(
                x=x + 1, y=y + 3,
                string="This mod alters your body's composition"
            )
            console.print(
                x=x + 1, y=y + 4,
                string="Press (a) to apply or ESC to cancel"
            )
        else:
            for i, part in enumerate(body_parts):
                key = chr(ord("a") + i)
                
                # Show what's already equipped
                current_internal = part.internal_modification
                current_external = part.external_modification
                
                status = ""
                if current_internal:
                    status += f" [I:{current_internal.name}]"
                if current_external:
                    status += f" [E:{current_external.name}]"
                
                console.print(
                    x=x + 1, y=y + 3 + i,
                    string=f"({key}) {part.name}{status}"
                )


    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        
        mod_instance = self.modification_class(level=self.initial_level)
        if mod_instance.mod_type == ModificationType.INTRINSIC:
            if key == tcod.event.KeySym.a:
                return self.apply_intrinsic_mod()
        else:
            index = key - tcod.event.KeySym.a
            if 0 <= index < len(player.body.parts):
                selected_part = player.body.parts[index]
                return self.on_body_part_selected(selected_part)
        
        return super().ev_keydown(event)
    



    def apply_intrinsic_mod(self) -> Optional[ActionOrHandler]:
        """Apply an intrinsic modification"""
        new_mod = self.modification_class(level=self.initial_level)
        
        if self.engine.player.body.intrinsic_modification:
            self.engine.message_log.add_message(
                "You already have an intrinsic modification!",
                colour.impossible
            )
            return None
        
        self.engine.player.body.intrinsic_modification = new_mod
        new_mod.parent = self.engine.player.body
        
        # Remove item and show message
        self.modification_item.consumable.consume()
        self.engine.message_log.add_message(
            f"Applied {new_mod.name} to your body!",
            colour.status_effect_applied
        )
        
        return MainGameEventHandler(self.engine)

    def on_body_part_selected(self, body_part: BodyPart) -> Optional[ActionOrHandler]:
        """Apply the modification to the selected body part"""
        
        
        # Create the modification instance
        new_mod = self.modification_class(level=self.initial_level)
        
        # Determine which slot based on mod type
        if new_mod.mod_type == ModificationType.INTERNAL:
            if body_part.internal_modification:
                self.engine.message_log.add_message(
                    f"The {body_part.name} already has an internal modification!",
                    colour.impossible
                )
                return None
            body_part.internal_modification = new_mod
            new_mod.parent = body_part
            
        elif new_mod.mod_type == ModificationType.EXTERNAL:
            if body_part.external_modification:
                self.engine.message_log.add_message(
                    f"The {body_part.name} already has an external modification!",
                    colour.impossible
                )
                return None
            body_part.external_modification = new_mod
            new_mod.parent = body_part
            
        elif new_mod.mod_type == "intrinsic":
            if self.engine.player.body.intrinsic_modification:
                self.engine.message_log.add_message(
                    "You already have an intrinsic modification!",
                    colour.impossible
                )
                return None
            self.engine.player.body.intrinsic_modification = new_mod
            new_mod.parent = self.engine.player.body  
        
        # Remove the item from inventory
        self.modification_item.consumable.consume()
        
        self.engine.message_log.add_message(
            f"Applied {new_mod.name} to {body_part.name}!",
            colour.status_effect_applied
        )
        
        return MainGameEventHandler(self.engine)

class EnemyLookHandler(SelectIndexHandler):
    def on_index_selected(self, x: int, y: int) -> Optional[ActionOrHandler]:
        target = self.engine.game_map.get_actor_at_location(x, y)
        if target:
            # We found someone! Let's switch to the info screen.
            return EnemyInfoHandler(self.engine, target)
        
        # If no one is there, we just go back to the main game.
        return MainGameEventHandler(self.engine)
    
class EnemyInfoHandler(AskUserEventHandler):
    TITLE = "Enemy Information"
    def __init__(self, engine: Engine, target: Actor):
        super().__init__(engine)
        self.target = target
    
    def on_render(self, console: tcod.console.Console) -> None:
        """Render body part selection menu"""
        super().on_render(console)

        target = self.target

        if target.x <= 30:
            x = 40
        else:
            x = 0
        y = 0

        height = 11
        width = 30

        console.draw_frame(
            x = x,
            y = y,
            width = width, height=height,
            title = self.TITLE,
            clear= True,
            fg =colour.white,
            bg = colour.black
        )
        
        console.print(
            x=x+1, y=y+2,
            string = f"Name: {target.name}"
        )
        console.print(
            x=x+1, y=y+3,
            string = f"HP: {target.fighter.hp}/{target.fighter.max_hp}"
        )
        console.print(
            x=x+1, y=y+4,
            string = f"Character: {target.glyph}"
        )
        console.print(
            x=x+1, y=y+5,
            string = f"Attack: {target.fighter.strength}"
        )
        console.print(
            x=x+1, y=y+6,
            string = f"Defence: {target.fighter.defence}"
        )
        console.print(
            x=x+1, y=y+7,
            string = f"AP: {target.action_points.ap}/{target.action_points.max_ap}"
        )
        console.print(
            x=x+1, y=y+8,
            string = f"Mods: {target.body.applied_mods}"
        )

        ##for i, line in enumerate():
          #  pass

class PickupMenuHandler(AskUserEventHandler):
    """Handle picking up items when multiple are on one tile."""

    TITLE = "Pick up which item?"

    def __init__(self, engine: Engine, items_at_location: list):
        super().__init__(engine)
        self.items_at_location = items_at_location

    def on_render(self, console: tcod.console.Console) -> None:
        """Render the pickup menu."""
        super().on_render(console)
        
        number_of_items = len(self.items_at_location)
        height = number_of_items + 3  # +3 for title, "all" option, and padding

        if height <= 4:
            height = 4
        
        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        y = 0
        width = len(self.TITLE) + 4

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=height,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0)
        )

        # Show items
        for i, item in enumerate(self.items_at_location):
            item_key = chr(ord("a") + i)
            console.print(x + 1, y + i + 1, f"({item_key}) {item.name}")
        
        # "Pick up all" option
        all_key = chr(ord("a") + len(self.items_at_location))
        console.print(x + 1, y + len(self.items_at_location) + 1, f"({all_key}) Pick up all")

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.KeySym.a

        if 0 <= index < len(self.items_at_location):
            # Pick up single item
            selected_item = self.items_at_location[index]
            action = actions.PickupSpecificItemAction(player, selected_item)
            
            # Execute the action directly
            try:
                action.perform()
            except exceptions.Impossible as exc:
                self.engine.message_log.add_message(exc.args[0], colour.impossible)
                return self  # Stay in menu on error
            
            # Check if there are still items on the ground
            items_remaining = [
                item for item in self.engine.game_map.items
                if item.x == player.x and item.y == player.y
            ]
            
            if items_remaining:
                # Update the menu with remaining items
                return PickupMenuHandler(self.engine, items_remaining)
            else:
                # No items left, return to game
                return MainGameEventHandler(self.engine)
                
        elif index == len(self.items_at_location):
            # Pick up all
            action = actions.PickupAllAction(player, self.items_at_location)
            try:
                action.perform()
            except exceptions.Impossible as exc:
                self.engine.message_log.add_message(exc.args[0], colour.impossible)
                return self
            
            # After picking up all, return to game
            return MainGameEventHandler(self.engine)
        
        return super().ev_keydown(event)

class DoorDirectionHandler(AskUserEventHandler):
    """Ask which direction to open/close a door (no AP cost)"""
    
    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console)
        self.engine.message_log.add_message(
            "Which direction? (movement keys or ESC to cancel)",
            colour.needs_target
        )
    
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        key = event.sym
        
        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]
            return actions.ToggleDoorAction(self.engine.player, dx, dy)
        
        # ESC or any other key cancels
        return super().ev_keydown(event)
    
class GunTargetingHandler(SelectIndexHandler):
    """Select a target for gun attacks - shows line of fire"""
    
    def __init__(self, engine: Engine, weapon: RangedEquippable):
        super().__init__(engine)
        self.weapon = weapon
    
    def on_render(self, console: tcod.console.Console) -> None:
        """Highlight the targeting line and show range"""
        super().on_render(console)
        
        world_x, world_y = self.engine.mouse_location
        player_x, player_y = self.engine.player.x, self.engine.player.y
        
        # Calculate distance
        distance = max(abs(world_x - player_x), abs(world_y - player_y))
        
        # Draw line of fire
        line = tcod.los.bresenham((player_x, player_y), (world_x, world_y)).tolist()
        
        for x, y in line:
            if (x, y) == (player_x, player_y):
                continue  # Skip player position
            
            screen_x = x - self.engine.camera_x
            screen_y = y - self.engine.camera_y
            
            # Check if in viewport
            if 0 <= screen_x < console.width and 0 <= screen_y < console.height:
                # Color based on range and line of sight
                if distance > self.weapon.max_range:
                    line_color = colour.impossible  # Out of range
                elif not self.engine.game_map.tiles["transparent"][x, y]:
                    line_color = colour.invalid  # Blocked
                else:
                    line_color = colour.needs_target 

                console.rgb["bg"][screen_x, screen_y] = line_color
        
        # Display info
        info_y = 0
        console.print(
            0, info_y,
            f"Ammo: {self.weapon.current_ammo}/{self.weapon.max_ammo}  "
            f"Range: {distance}/{self.weapon.max_range}  "
            f"DMG: {self.weapon.damage}  Pierce: {self.weapon.pierce}",
            fg=colour.white
        )
    
    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        """Fire at the selected location"""
        return RangedAttackAction(self.engine.player, (x, y), self.weapon)


# Add this function to help detect equipped guns in MainGameEventHandler
def get_equipped_gun(actor: Actor) -> Optional[RangedEquippable]:
    """Check if actor has a ranged weapon equipped"""

    
    if not hasattr(actor, 'equipment'):
        return None
    
    for item in actor.equipment.equipped_items.values():
        if item and item.equippable.equipment_type == EquipmentType.RANGEDWEAPON:
            return item.equippable
    
    return None