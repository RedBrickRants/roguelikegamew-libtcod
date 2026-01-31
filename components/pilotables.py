# components/mech.py
from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from components.base_component import BaseComponent
import exceptions

if TYPE_CHECKING:
    from entity import Actor

class Pilotable(BaseComponent):
    parent: Actor
    
    def __init__(self, hp_bonus: int = 50, strength_bonus: int = 10, 
                 defence_bonus: int = 5, ap_cost_modifier: float = 1.5):
        self.hp_bonus = hp_bonus
        self.strength_bonus = strength_bonus
        self.defence_bonus = defence_bonus
        self.ap_cost_modifier = ap_cost_modifier  # Actions cost more AP in mech
        self.pilot: Optional[Actor] = None
    
    def enter(self, pilot: Actor) -> None:
        """Pilot enters the mech"""
        if self.pilot:
            raise exceptions.Impossible("Mech already occupied!")
        self.pilot = pilot
        # Apply bonuses
        self.parent.fighter.max_hp += self.hp_bonus
        self.parent.fighter.hp += self.hp_bonus
    
    def exit(self) -> Actor:
        """Pilot exits, returns the pilot"""
        if not self.pilot:
            raise exceptions.Impossible("No one in the mech!")
        pilot = self.pilot
        # Remove bonuses
        self.parent.fighter.max_hp -= self.hp_bonus
        self.parent.fighter.hp = min(self.parent.fighter.hp, self.parent.fighter.max_hp)
        self.pilot = None
        return pilot