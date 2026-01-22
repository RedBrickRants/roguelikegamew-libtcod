#modifications.py
from __future__ import annotations
from typing import TYPE_CHECKING
from components.body import Body, BodyPart


class Modification:
    parent: BodyPart
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.parent = None
    
    def get_stat_bonuses(self) -> dict:
        """Override in subclasses to give stat bonuses"""
        return {}
    
    def on_hit(self, attacker, target):
        """Called when equipped actor hits something"""
        pass
    
    def on_damaged(self, attacker, damage):
        """Called when equipped actor takes damage"""
        pass
    
    def on_kill(self, attacker, target):
        """Called when equipped actor kills something"""
        pass
    
    def on_turn_start(self, actor):
        """Called at start of actor's turn"""
        pass




        
