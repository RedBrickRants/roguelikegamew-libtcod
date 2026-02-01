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
import random
from components.body_modification import ExtraBrain, NumbDown, MuscleMAX
from components.equippable import Pistol, Rifle, LaserPistol
from equipment_types import ModificationType


player = Actor(
    glyph="@", 
    colour=(115, 147, 179), 
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
    name="Morphine Syringe",
    consumable=consumable.HealingConsumable(amount=4),
)

strength_potion = Item(
    glyph ="!",
    colour=(255, 135, 50),
    name="Strength Serum",
    consumable=consumable.MuscleBoostConsumabe(amount=2),
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



# Equipment Items
dagger = Item(
    glyph="/", colour=(0, 191, 255), name="Dagger", equippable=equippable.Dagger(),
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



# Modification Items
brain_mod_item = Item(
    glyph=":",
    colour=(255, 100, 255),
    name="Neural Enhancer",
    consumable=consumable.ModificationConsumable(
        modification_class=ExtraBrain,
        initial_level=1
    )
)

numb_down_item = Item(
    glyph=":",
    colour=(250, 100, 250),
    name="Painkiller Overdose",
    consumable=consumable.ModificationConsumable(
        modification_class=NumbDown,
        initial_level=1
    )
)

big_arm_item = Item(
    glyph=":",
    colour=(200, 50, 50),
    name="Muscle Growth Serum",
    consumable=consumable.ModificationConsumable(
        modification_class=MuscleMAX,
        initial_level=1
    )
)

# Basic pistol
pistol = Item(
    glyph="~", 
    colour=(150, 150, 150), 
    name="Pistol",
    equippable=Pistol()
)

# High-damage rifle
rifle = Item(
    glyph="~",
    colour=(100, 100, 100),
    name="Rifle", 
    equippable=Rifle()
)

# Energy weapon
laser_pistol = Item(
    glyph="~",
    colour=(0, 255, 255),
    name="Laser Pistol",
    equippable=LaserPistol()
)
