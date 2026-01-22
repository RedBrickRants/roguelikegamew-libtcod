from components.ai import HostileEnemy
from components import consumable, equippable
from components.equipment import Equipment
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from components.action_points import ActionPoints
from components.body import Body
from entity import Actor, Item
import components.body_templates

player = Actor(
    glyph="@", 
    colour=(255, 255, 255), 
    name="Player",
    ai_cls=HostileEnemy,
    equipment=Equipment(),  
    fighter=Fighter(hp=30, base_defence=2, base_strength=5),
    inventory=Inventory(capacity=26),
    level=Level(level_up_base=200),
    action_points=ActionPoints(),
    body= Body(parts = components.body_templates.humanoid())
)

orc = Actor(
    glyph="o", 
    colour=(63, 127, 63), 
    name="Orc",
    ai_cls=HostileEnemy,
    equipment=Equipment(), 
    fighter=Fighter(hp=10, base_defence=0, base_strength=3),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=35),
    action_points=ActionPoints(base_ap=3),
    body= Body(parts = components.body_templates.humanoid())
)
troll = Actor(
    glyph="T", 
    colour=(0, 127, 0), 
    name="Troll",
    ai_cls=HostileEnemy,
    equipment=Equipment(), 
    fighter=Fighter(hp=16, base_defence=1, base_strength=4),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=100),
    action_points=ActionPoints(base_ap=5),
    body= Body(parts = components.body_templates.humanoid())
)

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
confusion_scroll = Item(
    glyph="~",
    colour=(207, 63, 255),
    name="Confusion Scroll",
    consumable=consumable.ConfusionConsumable(number_of_turns=10),
)

fireball_scroll = Item(
    glyph="~",
    colour=(255, 0, 0),
    name="Fireball Scroll",
    consumable=consumable.FireballDamageConsumable(damage=12, radius=3),
)
dagger = Item(
    glyph="/", colour=(0, 191, 255), name="Dagger", equippable=equippable.Dagger()
)

sword = Item(glyph="/", colour=(0, 191, 255), name="Sword", equippable=equippable.Sword())

leather_armor = Item(
    glyph="[",
    colour=(139, 69, 19),
    name="Leather Armor",
    equippable=equippable.LeatherArmor(),
)

chain_mail = Item(
    glyph="[", colour=(139, 69, 19), name="Chain Mail", equippable=equippable.ChainMail()
)