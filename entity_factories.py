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
from components.body_modification import ExtraBrain, NumbDown, BigArm

def apply_random_modification(actor: Actor, floor_level: int = 0) -> None:
    """
    Apply a random modification to a random body part on an actor.
    Higher floor levels = higher mod levels and more mods
    """
    if not actor.body or not actor.body.parts:
        return  # No body to modify
    
    # Available modifications (expand this list as you create more)
    available_mods = [
        ExtraBrain,
        NumbDown,
        BigArm,
    ]
    
    # Chance to get a mod increases with floor level
    # Floor 0: 20%, Floor 5: 50%, Floor 10+: 80%
    mod_chance = min(0.2 + (floor_level * 0.06), 0.8)
    
    if random.random() > mod_chance:
        return  # No mod for this enemy
    
    # Determine mod level based on floor
    # Floor 0-2: level 1
    # Floor 3-5: level 1-2
    # Floor 6-8: level 2-3
    # Floor 9+: level 3-5
    if floor_level < 3:
        mod_level = 1
    elif floor_level < 6:
        mod_level = random.randint(1, 2)
    elif floor_level < 9:
        mod_level = random.randint(2, 3)
    else:
        mod_level = random.randint(3, 5)
    
    # Pick a random mod class
    mod_class = random.choice(available_mods)
    
    # Create the modification
    new_mod = mod_class(level = mod_level)
    
    # Pick a random body part
    body_part = random.choice(actor.body.parts)
    
    # Apply based on type
    if new_mod.mod_type == "internal":
        if body_part.internal_modification is None:
            body_part.internal_modification = new_mod
            new_mod.parent = body_part
    elif new_mod.mod_type == "external":
        if body_part.external_modification is None:
            body_part.external_modification = new_mod
            new_mod.parent = body_part
    elif new_mod.mod_type == "intrinsic":
        if actor.body.intrinsic_modification is None:
            actor.body.intrinsic_modification = new_mod
            new_mod.parent = body_part


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
        modification_class=BigArm,
        initial_level=1
    )
)