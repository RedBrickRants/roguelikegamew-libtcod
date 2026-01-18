from __future__ import annotations
from typing import TYPE_CHECKING
from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Actor, Item


class ActionPoints(BaseComponent):
    parent: Actor

    def __init__(self, base_ap: int = 4 ):
        self._base_ap = base_ap
        self._ap = base_ap

        

    @property
    def ap(self)-> int:
        return self._ap
    @ap.setter
    def ap(self, value: int)-> None:
        self._ap = max(0, min(value, self.max_ap))

    @property
    def max_ap(self) -> int:
        """Total AP including bonuses from body/augments"""
        return self._base_ap + self.ap_bonuses
    
    @property
    def ap_bonuses(self) -> int:
        """Get AP bonuses from body parts/augments"""
        if hasattr(self.parent, 'body') and self.parent.body:
            return self.parent.body.ap_bonuses
        return 0
    
    def restore(self, amount: int)-> int:
        """restore missing ap"""
        if self.ap == self.max_ap:
            return 0
        new_ap = self.ap + amount
        if new_ap > self.max_ap:
            new_ap = self.max_ap
        amount_recovered = new_ap-self.ap
        self.ap = new_ap
        return amount_recovered
    
    def refresh(self) -> None:
        """Full restore at start of turn"""
        self._ap = self.max_ap
    
    def spend(self, amount: int)-> bool:
        """Spends points and returns success"""
        if self.ap >= amount:
            self.ap -= amount
            return True
        return False
    
    def can_act(self)->bool:
        "Do we have Any AP left?"
        return self.ap >0