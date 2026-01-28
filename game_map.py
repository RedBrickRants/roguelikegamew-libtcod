from __future__ import annotations
from typing import List, Iterable,Iterator, Optional, TYPE_CHECKING
from entity import Actor, Item

import numpy as np #type: ignore
import tile_types
import colour

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity
    

class GameMap:
    """GAME MAP CLASS: is a store of value used to generate station Floor,"""
    #initializer takes width and height and assigns them
    def __init__(self,engine: Engine, width: int, height: int, entites: Iterable[Entity]=()):
        self.engine = engine
        self.width, self.height = width, height
        self.entities = set(entites) #set allows us to make an unordered collection of unique elements
        self.tiles = np.full((width, height), fill_value = tile_types.wall, order = "F")
        self.visible = np.full((width, height), fill_value= False, order= "F")
        self.explored = np.full((width, height), fill_value= False, order= "F")
        self.downstairs_location = (0, 0)
        self.upstairs_location = (0,0)

    @property
    def gamemap(self)-> GameMap:
        return self
    
    @property
    def actors(self)-> Iterator[Actor]:
        yield from(entity for entity in self.entities if isinstance(entity, Actor) and entity.is_alive)

    @property
    def items(self)-> Iterator[Item]:
        yield from (entity for entity in self.entities if isinstance(entity, Item))

    def get_blocking_entity_at_location(self, location_x: int, location_y: int)->Optional[Entity]:
        """Return the x and y value of a particular entity witht the "blocks_movement" attribute"""
        for entity in self.entities:
            if entity.blocks_movement and entity.x == location_x and entity.y == location_y:
                return entity
        return None
    
    def get_actor_at_location(self, x: int, y: int)-> Optional[Actor]:
        """Returns the x and y position of an "Actor"  at a given location"""
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor
        return None   

    def in_bounds(self, x:  int, y: int)->bool:
        """Returns true if the x and y are out of the map bounds"""
        return 0 <=x <self.width and 0 <= y< self.height


class GameWorld:
    """
    Holds the settings for the GameMap, and generates new maps when moving down the stairs.
    """

    def __init__(
        self,
        *,
        engine: Engine,
        map_width: int,
        map_height: int,
        max_rooms: int,
        room_min_size: int,
        room_max_size: int,
        current_floor: int = 0, 
    ):
        self.engine = engine

        self.map_width = map_width
        self.map_height = map_height

        self.max_rooms = max_rooms

        self.room_min_size = room_min_size
        self.room_max_size = room_max_size

        self.current_floor = current_floor
        self.floors: List[GameMap] = []

        

    def store_floor(self):
        """Appends the current GameMap object to the floor list"""
        if self.engine.player not in self.engine.game_map.entities:
            self.engine.game_map.entities.add(self.engine.player)
        self.floors.append(self.engine.game_map)  

    def traverse_floors(self, direction: str)-> None:
        """Allows the player to travel up and down the stairs"""
        if direction == "down":
            if not self.floors:
                self.floors.append(self.engine.game_map)

            next_floor = self.current_floor + 1
            if next_floor < len(self.floors):
                self.engine.game_map = self.floors[next_floor]
                self.engine.player.place(*self.engine.game_map.upstairs_location, self.engine.game_map)
                self.current_floor = next_floor
            else:
                new_floor = self.generate_floor()
                self.engine.game_map = new_floor
                self.floors.append(self.engine.game_map)
                self.engine.player.place(*self.engine.game_map.upstairs_location, self.engine.game_map)
                self.current_floor+=1
                
        if direction == "up":
            if self.current_floor ==0:
                self.engine.message_log.add_message("You cant go back up!",colour.descend)
                return
            self.current_floor -=1
            self.engine.game_map = self.floors[self.current_floor]

            if self.engine.player not in self.engine.game_map.entities:
                self.engine.game_map.entities.add(self.engine.player)
            self.engine.player.x, self.engine.player.y = self.engine.game_map.downstairs_location
         


    def generate_floor(self) -> None:
        """Generates  and returns GameMap objects"""
        from procgen import generate_station
        new_floor = generate_station(
            max_rooms=self.max_rooms,
            room_min_size=self.room_min_size,
            room_max_size=self.room_max_size,
            map_width=self.map_width,
            map_height=self.map_height,
            engine=self.engine,
        )
        return new_floor
        
