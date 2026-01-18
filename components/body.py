from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Actor, Item

class BodyPart:
    parent: Body
    def __init__(self, name: str, part_type):
        self.name = name
        self.part_type = part_type
        self.augment = None
        self.mutation =  None
        self.parent = None


class Body(BaseComponent):
    parent: Actor
    def __init__(self, parts: List[BodyPart]):
        self.parts = parts
        for part in self.parts:
            part.parent = self
    
    @property
    def ap_bonuses(self) -> int:
        total = 0
        for part in self.parts:
            if part.augment:
                total += part.augment.ap_bonus
        return total
        