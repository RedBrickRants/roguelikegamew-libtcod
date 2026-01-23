#constants.py
 
# Screen Dimensions
SCREEN_WIDTH = 140  
SCREEN_HEIGHT = 67  

# Map viewport (visible portion on screen)
CAMERA_WIDTH = SCREEN_WIDTH
CAMERA_HEIGHT = SCREEN_HEIGHT

# Actual map size (can be much larger when you add camera)
MAP_WIDTH = 100  # Will increase to 200+ later
MAP_HEIGHT = 50  # Will increase to 100+ later

# UI Panel dimensions
STATS_PANEL_X = 61
STATS_PANEL_Y = 0
STATS_PANEL_WIDTH = 19
STATS_PANEL_HEIGHT = 21

INVENTORY_PANEL_X = 61
INVENTORY_PANEL_Y = 22
INVENTORY_PANEL_WIDTH = 19
INVENTORY_PANEL_HEIGHT = 21

LOG_PANEL_X = 0
LOG_PANEL_Y = 44
LOG_PANEL_WIDTH = 80
LOG_PANEL_HEIGHT = 6

# Dungeon generation
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 50

MAX_MONSTERS_PER_ROOM = 2
MAX_ITEMS_PER_ROOM = 2