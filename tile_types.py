from typing import Tuple
import numpy as np # type: ignore

#np.dtype cteayes a numpy datatype
graphic_data = np.dtype(
    [
        #int32 is a unicode codepoint
        #3B assgns 3 bytes for rgb colours
        ("ch", np.int32),
        ("fg", "3B"),
        ("bg", "3B")
    ]
)


tile_data = np.dtype(
    [
        # Walkable determins if entities can walk or spawn ontop the tile
        # Transparent determince if entities can see through the tile
        # dark represents a tile not in fov
        # ligth represents a tile in fov
        ("walkable", np.bool),
        ("transparent", np.bool),
        ("dark", graphic_data),
        ("light", graphic_data)
    ]
)

# tile defining function
def new_tile(
        *,
        walkable: int,
        transparent: int,
        dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
        light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
) -> np.ndarray:
    return np.array((walkable, transparent, dark, light), dtype = tile_data)

SHROUD = np.array((ord (" "), (255,255,255),(0,0,0)), dtype=graphic_data)

floor = new_tile( 
    walkable= True, 
    transparent= True, 
    dark=(ord(" "), (89,89,89), (0,0,0)), 
    light=(ord(" "),(255, 255, 255),(113, 121, 126))
    )

wall = new_tile( 
    walkable= False, 
    transparent= False, 
    dark=(ord("░"), (89,89,89), (0,0,0)), 
    light=(ord("▒"),(89,89,89),(62,62,62))
    )

door_closed = new_tile(
    walkable=False,  
    transparent=False,  
    dark=(ord('='), (89,89,89), (0, 0, 0)),
    light=(ord('='), (192,192,192), (113, 121, 126))
)

door_open = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord('-'), (89,89,89), (0, 0, 0)),
    light=(ord('-'), (192,192,192), (113, 121, 126))
)

down_stairs = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(">"), (0, 0, 100), (50, 50, 150)),
    light=(ord(">"), (255, 255, 255), (200, 180, 50)),
)

up_stairs =  new_tile(
    walkable=True,
    transparent=True,
    dark=(ord("<"), (0, 0, 100), (50, 50, 150)),
    light=(ord("<"), (255, 255, 255), (200, 180, 50)),
)