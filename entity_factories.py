from components.ai import HostileEnemy
from components import consumable
from components.fighter import Fighter
from components.inventory import Inventory
from entity import Actor, Item

player = Actor(glyph="@", colour=(255, 255, 255), name="Player",ai_cls=HostileEnemy,  fighter=Fighter(hp=30, defence=2, power=5),inventory=Inventory(capacity=26),)

orc = Actor(glyph="o", colour=(63, 127, 63), name="Orc",ai_cls=HostileEnemy, fighter=Fighter(hp=10, defence=0, power=3),inventory=Inventory(capacity=0),)
troll = Actor(glyph="T", colour=(0, 127, 0), name="Troll",ai_cls=HostileEnemy, fighter=Fighter(hp=16, defence=1, power=4),inventory=Inventory(capacity=0),)

health_potion = Item(
    glyph="!",
    colour=(127, 0, 255),
    name="Health Potion",
    consumable=consumable.HealingConsumable(amount=4),
)
lightning_scroll = Item(
    glyph="~",
    colour=(255, 255, 0),
    name="Lightning Scroll",
    consumable=consumable.LightningDamageConsumable(damage=20, maximum_range=5),
)