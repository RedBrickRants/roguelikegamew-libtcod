from entity import Entity

player = Entity(glyph="@", colour=(255, 255, 255), name="Player", blocks_movement=True)

orc = Entity(glyph="o", colour=(63, 127, 63), name="Orc", blocks_movement=True)
troll = Entity(glyph="T", colour=(0, 127, 0), name="Troll", blocks_movement=True)