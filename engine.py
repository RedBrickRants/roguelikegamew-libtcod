from __future__ import annotations
from typing import TYPE_CHECKING


from tcod.console import Console
from tcod.map import compute_fov



from message_log import MessageLog
from soundmanager import SoundManager
import time
import render_functions
import exceptions
import lzma
import dill
import constants as const

if TYPE_CHECKING:
     from entity import Actor
     from game_map import GameMap, GameWorld

class Engine:
     game_map: GameMap
     game_world: GameWorld
     def __init__(self, player: Actor):
          self.message_log = MessageLog()
          self.mouse_location = (0,0)
          self.player = player
          self.camera_x = 0
          self.camera_y = 0


          self.map_console = Console(const.MAP_VIEWPORT_WIDTH, const.MAP_VIEWPORT_HEIGHT, order="F")
          self.stats_console = Console(const.STATS_PANEL_WIDTH, const.STATS_PANEL_HEIGHT, order="F")
          self.inventory_console = Console(const.INVENTORY_PANEL_WIDTH, const.INVENTORY_PANEL_HEIGHT, order="F")
          self.log_console = Console(const.LOG_PANEL_WIDTH, const.LOG_PANEL_HEIGHT, order="F")

          self.context = None  
          self.root_console = None
     
     def __getstate__(self) -> dict:
        """Tell dill what to save by removing non-pickleable references."""
        state = self.__dict__.copy() # Copy the engine's data
        
        # Remove the system-heavy objects that cause the crash
        if "context" in state:
            del state["context"]
        if "root_console" in state:
            del state["root_console"]
        if "sound_manager" in state:
            del state["sound_manager"]
            
        return state

     def __setstate__(self, state: dict) -> None:
        """Restore the engine and restart the sound manager."""
        self.__dict__.update(state)
        
        # These will be re-assigned by your main loop in main.py
        self.context = None
        self.root_console = None
        
        # Re-initialize the sound manager so audio works on load
        self.sound_manager = SoundManager()


     def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                while entity.action_points.can_act():
                    action = entity.ai.execute()
                    if action is None: 
                         break

                    try:
                         action.perform() 
                              # Sequential Visuals & Sound spacing
                         if self.context and self.root_console:
                              if self.game_map.visible[entity.x, entity.y]:
                                   self.render(self.root_console)
                                   self.context.present(self.root_console)
                                   time.sleep(0.05)
                    except exceptions.Impossible:
                        continue

                    
          

     def update_fov(self) -> None:
          """Recalculate the FOV when notable changes happen"""
          self.game_map.visible[:] = compute_fov(
          self.game_map.tiles["transparent"], (self.player.x, self.player.y), radius=8) 
          self.game_map.explored |= self.game_map.visible

     def update_camera(self, map_viewport_width:int, map_viewport_height:int) -> None:
          """Center the camera on the player"""
          self.camera_x = self.player.x -map_viewport_width//2
          self.camera_y = self.player.y -map_viewport_height//2

          #Clamp Camera
          self.camera_x = max(0, min(self.camera_x, self.game_map.width-map_viewport_width))
          self.camera_y = max(0, min(self.camera_y, self.game_map.height-map_viewport_height))

          
     def render(self, console: Console) -> None:
          """Calls all necessary render functions in one central location"""
          console.clear()

          # Clear all sub-consoles
          self.map_console.clear()
          self.stats_console.clear()
          self.inventory_console.clear()
          self.log_console.clear()

          self.update_camera(map_viewport_width= const.MAP_VIEWPORT_WIDTH, map_viewport_height=const.MAP_VIEWPORT_HEIGHT)
          # Map 
          #print("attempting to render map")
          render_functions.render_map(
               self.map_console, 
               self.game_map, 
               self.camera_x, 
               self.camera_y, 
               viewport_width = const.MAP_VIEWPORT_WIDTH, 
               viewport_height = const.MAP_VIEWPORT_HEIGHT
               )
          #print("map rendered")
          #Entities
          render_functions.render_entities(
               self.map_console, 
               self.game_map, 
               self.camera_x, 
               self.camera_y
               )
          
          # Stats panel 
          render_functions.render_stats_panel(
               self.stats_console, 
               self.player,
               0,0,
               const.STATS_PANEL_WIDTH, 
               const.STATS_PANEL_HEIGHT  
          )
          
          # Inventory panel
          render_functions.render_inventory_panel(
               self.inventory_console,
               self.player,
               0,0,
               const.INVENTORY_PANEL_WIDTH,
               const.INVENTORY_PANEL_HEIGHT  
               )
          
          # Log 
          self.message_log.render(
               self.log_console, 
               0,0, 
               const.LOG_PANEL_WIDTH, 
               const.LOG_PANEL_HEIGHT
               )

          self.map_console.blit(console, dest_x=0, dest_y=0)
          self.stats_console.blit(console, dest_x=const.STATS_PANEL_X, dest_y=const.STATS_PANEL_Y)
          self.inventory_console.blit(console, dest_x=const.INVENTORY_PANEL_X, dest_y=const.INVENTORY_PANEL_Y)
          self.log_console.blit(console, dest_x=const.LOG_PANEL_X, dest_y=const.LOG_PANEL_Y)
          
          # Mouse hover
          render_functions.render_names_at_mouse(console, 0, 60, self)  # Was 43, now 60
     def save_as(self, filename: str)-> None:
          """Save this Engine instance as a compressed file."""
          save_data = lzma.compress(dill.dumps(self))
          with open(filename, "wb") as f:
            f.write(save_data)
