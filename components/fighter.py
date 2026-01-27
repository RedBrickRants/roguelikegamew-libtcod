from __future__ import annotations
from typing import TYPE_CHECKING
from components.base_component import BaseComponent
from render_order import RenderOrder

import colour
if TYPE_CHECKING:
    from entity import Actor

class Fighter(BaseComponent):
    parent: Actor
    def __init__(self, hp: int, base_defence: int, base_strength: int):
        self.max_hp = hp
        self._hp = hp
        self.base_defence = base_defence
        self.base_strength = base_strength

    @property
    def hp(self)-> int:
        return self._hp
    
    @hp.setter
    def hp(self, value: int)->None:
        self._hp = max(0, min(value, self.max_hp))
        if self._hp == 0 and self.parent.ai:
            self.die()
    
    @property
    def defence(self) -> int:
        return self.base_defence + self.defence_bonus

    @property
    def strength(self) -> int:
        return self.base_strength + self.strength_bonus

    @property
    def defence_bonus(self) -> int:
        if self.parent.equipment:
            return self.parent.equipment.defence_bonus
        else:
            return 0

    @property
    def strength_bonus(self) -> int:
        bonus = 0
        if self.parent.equipment:
            bonus += self.parent.equipment.strength_bonus
    
        if self.parent.body:
            bonus += self.parent.body.stat_bonuses.get("strength", 0)
       
        
        return bonus


    def heal(self, amount: int)-> int:
        if self.hp == self.max_hp:
            return 0
        new_hp_value = self.hp +amount
        if new_hp_value>self.max_hp:
            new_hp_value = self.max_hp
        amount_recovered =  new_hp_value-self.hp
        self.hp = new_hp_value
        return amount_recovered
    
    def take_damage(self, amount: int)-> None:
        self.hp -=amount

    def die(self)-> None:
        if self.engine.player is self.parent:
            death_message = "You Died!"
            death_message_colour = colour.player_die
        else:
            death_message = f"{self.parent.name} is dead!"
            death_message_colour = colour.enemy_die
        
        self.parent.glyph = "%"
        self.parent.colour = (191, 0, 0)
        self.parent.blocks_movement = False
        self.parent.ai = None
        self.parent.name = f"remains of {self.parent.name}"
        self.parent.render_order = RenderOrder.CORPSE
        self.engine.message_log.add_message(death_message, death_message_colour)
        self.engine.player.level.add_xp(self.parent.level.xp_given)

