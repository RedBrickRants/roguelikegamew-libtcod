from __future__ import annotations
from typing import Tuple, Iterator, List, TYPE_CHECKING
from game_map import GameMap
import tile_types
import tcod
import random

if TYPE_CHECKING:
    from entity import Entity

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

    def create_rooms():
        pass
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

def generate_dungeon(max_rooms: int, room_min_size: int, room_max_size: int, map_width, map_height, player: Entity)-> GameMap:
    dungeon = GameMap(map_width, map_height)
    rooms: List[RectRoom] = []
    for room in range(max_rooms):
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        x = random.randint(0, dungeon.width - room_width -1)
        y = random.randint(0, dungeon.height - room_height - 1)
        new_room = RectRoom(x, y, room_width, room_height)

        if any(new_room.intersect(other_room)for other_room in rooms):
            continue
        dungeon.tiles[new_room.area] = tile_types.floor

        if len(rooms) == 0:
            player.x, player.y = new_room.center
        else:
            for x, y in tunnels_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x, y] = tile_types.floor
        rooms.append(new_room)

    return dungeon