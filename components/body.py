from __future__ import annotations
from typing import TYPE_CHECKING, List 
from components.base_component import BaseComponent
from equipment_types import EquipmentCategory

if TYPE_CHECKING:
    from entity import Actor

class BodyPart:
    parent: Body
    def __init__(self, name: str, part_type):
        self.name = name
        self.part_type = EquipmentCategory
        self.internal_modification = None
        self.external_modification = None
        self.parent = None


class Body():
    parent: Actor
    def __init__(self, parts: List[BodyPart]):
        self.parts = parts
        self.intrinsic_modification = None
        for part in self.parts:
            part.parent = self
    
    @property
    def applied_mods(self) -> List:
        mods = []
        for part in self.parts:
            if part.external_modification:
                part_mod = part.external_modification.name
                mods.append(part_mod)
            if part.internal_modification:
                part_mod = part.internal_modification.name
                mods.append(part_mod)
        
        if self.intrinsic_modification:
            mod = self.intrinsic_modification.name
            mods.append(mod)
        return mods
    
    @property
    def stat_bonuses(self) -> dict:
        """Aggregate all stat bonuses from all body parts"""
        bonuses = {}
        
        # Check body parts
        for part in self.parts:

            if part.internal_modification:
                part_bonuses = part.internal_modification.get_stat_bonuses()
                for stat, value in part_bonuses.items():
                    bonuses[stat] = bonuses.get(stat, 0) + value
                
            
            if part.external_modification:
                part_bonuses = part.external_modification.get_stat_bonuses()
                for stat, value in part_bonuses.items():
                    bonuses[stat] = bonuses.get(stat, 0) + value
        
        # Check intrinsic mod
        if self.intrinsic_modification:
            intrinsic_bonuses = self.intrinsic_modification.get_stat_bonuses()
            for stat, value in intrinsic_bonuses.items():
                bonuses[stat] = bonuses.get(stat, 0) + value
        
        return bonuses