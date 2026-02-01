from __future__ import annotations
from typing import Dict, Iterator, List, Tuple, TYPE_CHECKING
import entity_factories
from entity_mod_management import apply_random_modification
from entity import Actor
from game_map import GameMap
import tile_types
import tcod
import random

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

max_items_by_floor = [
    (0, 1),
    (4, 2),
]

max_monsters_by_floor = [
    (0, 2),
    (4, 3),
    (6, 5),
]

item_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(entity_factories.health_potion, 35), 
        (entity_factories.numb_down_item, 100),
        (entity_factories.big_arm_item, 100), 
        (entity_factories.sword, 100),
        (entity_factories.pistol, 100),
        (entity_factories.rifle, 100),
        (entity_factories.laser_pistol, 10)
        
        ],

    2: [(entity_factories.confusion_scroll, 10)],
    4: [(entity_factories.lightning_scroll, 25), 
        (entity_factories.sword, 5)],

    6: [(entity_factories.fireball_scroll, 25), 
        (entity_factories.chain_mail, 15)],
}

enemy_chances: Dict[int, List[Tuple[Entity, int]]] = {
    0: [(entity_factories.orc, 80)],
    3: [(entity_factories.troll, 15)],
    5: [(entity_factories.troll, 30)],
    7: [(entity_factories.troll, 60)],
}


def get_max_value_for_floor(
    max_value_by_floor: List[Tuple[int, int]], 
    floor: int
) -> int:
    current_value = 0

    for floor_minimum, value in max_value_by_floor:
        if floor_minimum > floor:
            break
        else:
            current_value = value

    return current_value


def get_entities_at_random(
    weighted_chances_by_floor: Dict[int, List[Tuple[Entity, int]]],
    number_of_entities: int,
    floor: int,
) -> List[Entity]:
    entity_weighted_chances = {}

    for key, values in weighted_chances_by_floor.items():
        if key > floor:
            break
        else:
            for value in values:
                entity = value[0]
                weighted_chance = value[1]
                entity_weighted_chances[entity] = weighted_chance

    entities = list(entity_weighted_chances.keys())
    entity_weighted_chance_values = list(entity_weighted_chances.values())

    chosen_entities = random.choices(
        entities, weights=entity_weighted_chance_values, k=number_of_entities
    )
    return chosen_entities

class RectRoom:
    def __init__(self, x: int, y: int, width: int, height: int ):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y +height

    @property
    def center(self) -> Tuple[int, int]:
        center_x = (self.x1 +self.x2) // 2
        center_y = (self.y1 +self.y2) //2
        return center_x, center_y
    
    #find the area of a given room by taking the two corners
    #
    @property
    def area(self)->Tuple[int, int]:
        #self.x1+1 so we account for the walls
        return slice(self.x1+1, self.x2), slice(self.y1+1, self.y2)
    
    #return a bool of room overlap 
    def intersect(self, other: RectRoom) -> bool:
        return(self.x1 <= other.x2 
               and self.x2 >= other.x1 
               and self.y1 <=other.y2 
               and self.y2 >=other.y1
               )
    


def place_entities(room: RectRoom, station: GameMap, floor_number: int,) -> None:
    number_of_monsters = random.randint(
        0, get_max_value_for_floor(max_monsters_by_floor, floor_number)
    )
    number_of_items = random.randint(
        0, get_max_value_for_floor(max_items_by_floor, floor_number)
    )

    monsters: List[Entity] = get_entities_at_random(
        enemy_chances, number_of_monsters, floor_number
    )
    items: List[Entity] = get_entities_at_random(
        item_chances, number_of_items, floor_number
    )


    for entity in monsters + items:
        x = random.randint(room.x1 +1, room.x2-1)
        y = random.randint(room.y1 +1, room.y2 -1)
        if not any(entity.x ==x and entity.y == y for entity in station.entities):
            spawned = entity.spawn(station, x, y)
            if isinstance(spawned, Actor) and spawned.ai:
                apply_random_modification(spawned, floor_number)
                

#create L shaped tunels between these two points
def tunnels_between(start: Tuple[int, int], end: Tuple[int, int]) -> Iterator[Tuple[int, int]]:
    x1, y1 = start
    x2, y2  = end

    if random.random() < 0.5:
        corner_x, corner_y = x2, y1
    else:
        corner_x, corner_y = x1,y2
    for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
        yield x, y #special return that returns items one at a time instead of all at once like return
    for x, y in tcod.los.bresenham( (corner_x, corner_y), (x2, y2)).tolist():
        yield x, y #special return that returns items one at a time instead of all at once like return

def is_door_possible(station: GameMap, x: int, y: int) -> bool:
    if (station.tiles[x-1, y] == tile_types.floor and station.tiles[x+1, y] == tile_types.floor and
        station.tiles[x, y-1] != tile_types.floor and station.tiles[x, y+1] != tile_types.floor):
        return True

    if (station.tiles[x, y-1] == tile_types.floor and station.tiles[x, y+1] == tile_types.floor and
        station.tiles[x-1, y] != tile_types.floor and station.tiles[x+1, y] != tile_types.floor):
        return True

    return False

def generate_station(
        max_rooms: int, 
        room_min_size: int, 
        room_max_size: int, 
        map_width, map_height, 
        engine: Engine
    )-> GameMap:
    player = engine.player
    station = GameMap(engine, map_width, map_height, entites=[player])
     
    rooms: List = []
    half_width = map_width //2
    half_height = map_height //2
    quadrants = {
        1:(0,0, half_width, half_height), 
        2:(half_width, 0, half_width, half_height), 
        3:(0, half_height, half_width,half_height),
        4:(half_width,half_height, half_width,half_height),
    }

    center_of_last_room = (0, 0)
    center_of_first_room = (0,0)

    rooms_per_quadrant = max_rooms // 4 
    rooms_by_quadrant = {key: [] for key in quadrants} 

    for q_key in quadrants:
        for _ in range(rooms_per_quadrant):


            room_width = random.randint(room_min_size, room_max_size)
            room_height = random.randint(room_min_size, room_max_size)
            
            quad_x, quad_y, quad_w, quad_h = quadrants[q_key]
            x = random.randint(quad_x,quad_x+ quad_w- room_width - 1)
            y = random.randint(quad_y, quad_y+ quad_h - room_height - 1)
            new_room = RectRoom(x, y, room_width, room_height)
            
            if any(new_room.intersect(other_room)for other_room in rooms_by_quadrant[q_key]):
                continue
            
            current_quadrants_rooms = rooms_by_quadrant[q_key]
            
            station.tiles[new_room.area] = tile_types.floor

            
            

            if len(rooms) == 0:
                center_of_first_room = (new_room.center)
                player.place(*new_room.center, station)
                
        

            if len(current_quadrants_rooms) > 0:
                nearest_room = min(current_quadrants_rooms, key= lambda room:(room.center[0] - new_room.center[0]) ** 2 + (room.center[1] - new_room.center[1]) ** 2)
                for x, y in tunnels_between(nearest_room.center, new_room.center):
                    if station.tiles[x, y] != tile_types.floor:
                        station.tiles[x, y] = tile_types.floor

            if len(current_quadrants_rooms) == 0 and len(rooms) > 0:
                match q_key:
                    case 2:
                        target_quadrant = 1
                    case 3:
                        target_quadrant = 1
                    case 4:
                        target_quadrant = 2
                    case _:
                        target_quadrant = None
                
                if target_quadrant and rooms_by_quadrant[target_quadrant]:
                    bridge_room = min(
                        rooms_by_quadrant[target_quadrant],
                        key=lambda room: (room.center[0] - new_room.center[0]) ** 2 + 
                                    (room.center[1] - new_room.center[1]) ** 2
                    )
                    for x, y in tunnels_between(bridge_room.center, new_room.center):
                        if station.tiles[x, y] != tile_types.floor:
                            station.tiles[x, y] = tile_types.floor

            
            current_quadrants_rooms.append(new_room)

            place_entities(new_room, station, engine.game_world.current_floor)
            rooms.append(new_room)
            
            center_of_last_room = new_room.center
    
    
    station.tiles[center_of_first_room] = tile_types.up_stairs
    station.upstairs_location = center_of_first_room

    station.tiles[center_of_last_room] = tile_types.down_stairs
    station.downstairs_location = center_of_last_room
    
    for room in rooms:
        for x in range(room.x1, room.x2 + 1):
            for y in range(room.y1, room.y2 + 1):
                # Check only the wall boundary of the room
                if x == room.x1 or x == room.x2 or y == room.y1 or y == room.y2:
                    if station.tiles[x, y] == tile_types.floor:
                        if is_door_possible(station, x, y):
                            # 10% chance to skip or just place it
                            station.tiles[x, y] = tile_types.door_closed
                            station.doors[(x, y)] = False

    return station