from __future__ import annotations
from typing import TYPE_CHECKING, List 
from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Actor

class BodyPart:
    parent: Body
    def __init__(self, name: str, part_type):
        self.name = name
        self.part_type = part_type
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
    def ap_bonuses(self) -> int:
        total = 0
        for part in self.parts:
            if part.modification:
                total += part.modification.ap_bonus
        return total
    @property
    def stat_bonuses(self) -> dict:
        """Aggregate all stat bonuses from all body parts"""
        bonuses = {}
        
        for part in self.parts:
            if part.modification:  # Check if modification exists
                part_bonuses = part.modification.get_stat_bonuses()
                for stat, value in part_bonuses.items():
                    bonuses[stat] = bonuses.get(stat, 0) + value
        
        return bonuses
        