from components.ai import HostileEnemy
from components.fighter import Fighter
from entity import Actor

player = Actor(glyph="@", colour=(255, 255, 255), name="Player",ai_cls=HostileEnemy,  fighter=Fighter(hp=30, defense=2, power=5),)

orc = Actor(glyph="o", colour=(63, 127, 63), name="Orc",ai_cls=HostileEnemy, fighter=Fighter(hp=10, defense=0, power=3),)
troll = Actor(glyph="T", colour=(0, 127, 0), name="Troll",ai_cls=HostileEnemy, fighter=Fighter(hp=16, defense=1, power=4),)