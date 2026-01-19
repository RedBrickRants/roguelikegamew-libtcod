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
          #print(f"this is: {self.game_map.render(console)}")
          render_functions.render_map(console, self.game_map)
          render_functions.render_entities(console, self.game_map)
          self.message_log.render(console=console, x=21, y=45, width=40, height=5)
          render_functions.render_bar(console=console, current_value=self.player.fighter.hp, maximum_value= self.player.fighter.max_hp, total_width=20)
          render_functions.render_station_level(
            console=console,
            station_level=self.game_world.current_floor,
            location=(0, 47),
          )
          render_functions.render_names_at_mouse_location(
            console=console, x=21, y=44, engine=self
          )
          render_functions.render_ap_bar(
               console=console, current_ap=self.player.action_points.ap, maximum_ap=self.player.action_points.max_ap, location=(1, 48)
          )
     def save_as(self, filename: str)-> None:
          """Save this Engine instance as a compressed file."""
          save_data = lzma.compress(pickle.dumps(self))
          with open(filename, "wb") as f:
            f.write(save_data)
