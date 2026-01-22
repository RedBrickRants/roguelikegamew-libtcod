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

#Every limb can have one internal and one external slot
#the body itself will have a singular intrinsic mod slot which will provide some sort of wacky bonus to either the player or his extremities
#In addition Mutations can also give another extremity at random or specific.

class ExtraBrain(Modification):
    #INTERNAL
    #Develop an advanced Growth on the left side of your brain:
    #Gives player an additional Action Point
    pass

class TheTism(Modification):
    #INTRINSIC? its on the rocks
    #extra lore stuff
    pass

class Tripod(Modification):#
    #ADDITIONAL
    #Grow a  third Leg 
    #eleminates knockback
    pass

#something that give the player info they dont already have
class Schizo(Modification):
    #INTRINSIC
    #player can now "hear enemies in closed rooms"
    pass

class ADHD(Modification):
    #INTRINSIC
    #if you dont move on a turn the next turn costs more ap however if you do move at least once you get an ap bonus on your next turn
    pass

class ExtraChromie(Modification):
    #INTRINSIC
    #gives an additional intrinsic/ modification slot on any extremity
    pass

class MegaMash(Modification):
    #ARM EXTERNAL
    #gives extra strength
    pass

class DermaMAX(Modification):
    #INTERNAL TORSO
    #Give extra defence to player
    pass

        
