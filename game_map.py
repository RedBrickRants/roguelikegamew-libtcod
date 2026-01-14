import numpy as np #type: ignore
from tcod.console import Console

import tile_types

class GameMap:
    #initializer takes width and height and assigns them
    def __init__(self, width: int, height: int):
        self.width, self.height = width, height
        self.tiles = np.full((width, height), fill_value = tile_types.wall, order = "F")

        #list slicing allows for access to the specific rows and columns of the tiles array
        #[row, columns]
        #self.tiles[30:33, 22]=tile_types.wall


    #Inbounds returns true if the x and y are out of the map bounds
    def in_bounds(self, x:  int, y: int)->bool:
        return 0 <=x <self.width and 0 <= y< self.height
    
    def render(self, console: Console)->None:
        #Using the Console class’s tiles_rgb method, we can quickly render the entire map
        console.rgb[0:self.width, 0:self.height] = self.tiles["dark"]
