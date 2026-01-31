# entity_spawning.py
"""Logic for spawning entities with random modifications."""
from __future__ import annotations
from typing import TYPE_CHECKING
import random
from components.body_modification import ExtraBrain, NumbDown, MuscleMAX
from equipment_types import ModificationType

if TYPE_CHECKING:
    from entity import Actor


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
        MuscleMAX,
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
    new_mod = mod_class(level=mod_level)
    
    # Pick a random body part
    body_part = random.choice(actor.body.parts)
    
    # Apply based on type
    if new_mod.mod_type == ModificationType.INTERNAL:
        if body_part.internal_modification is None:
            body_part.internal_modification = new_mod
            new_mod.parent = body_part
    elif new_mod.mod_type == ModificationType.EXTERNAL:
        if body_part.external_modification is None:
            body_part.external_modification = new_mod
            new_mod.parent = body_part
    elif new_mod.mod_type == ModificationType.INTRINSIC:
        if actor.body.intrinsic_modification is None:
            actor.body.intrinsic_modification = new_mod
            new_mod.parent = body_part