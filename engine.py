from __future__ import annotations
from typing import TYPE_CHECKING


from tcod.console import Console
from tcod.map import compute_fov



from message_log import MessageLog
import render_functions
import exceptions
import lzma
import pickle

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


     def handle_enemy_turns(self)-> None:
          for entity in set(self.game_map.actors)- {self.player}:
               if entity.ai:
                    while entity.action_points.can_act():
                         try:
                              action = entity.ai.execute()
                              if action is None:
                                   break
                              action.perform()
                         except exceptions.Impossible:
                              break 
          

     def update_fov(self) -> None:
          self.game_map.visible[:] = compute_fov(
          self.game_map.tiles["transparent"], (self.player.x, self.player.y), radius=6
          ) 
          self.game_map.explored |= self.game_map.visible
          
     def render(self, console: Console) -> None:
          console.clear()
          
          # Map and entities (now takes up more space)
          render_functions.render_map(console, self.game_map)
          render_functions.render_entities(console, self.game_map)
          
          # Stats panel - MOVE IT RIGHT
          render_functions.render_stats_panel(
               console, self.player,
               121, 0, 19, 21  # Was 61, now 121 (after the 120-wide map)
          )
          
          # Inventory panel
          render_functions.render_inventory_panel(
               console, self.player,
               121, 22, 19, 21  # Was 61, now 121
          )
          
          # Log - MOVE IT DOWN
          self.message_log.render(console, 0, 61, 120, 6)  # Was y=44, now 61
          
          # Mouse hover - MOVE IT DOWN
          render_functions.render_names_at_mouse(console, 0, 60, self)  # Was 43, now 60
     def save_as(self, filename: str)-> None:
          """Save this Engine instance as a compressed file."""
          save_data = lzma.compress(pickle.dumps(self))
          with open(filename, "wb") as f:
            f.write(save_data)
