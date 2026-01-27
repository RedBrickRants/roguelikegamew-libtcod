#modifications.py
from __future__ import annotations
from typing import TYPE_CHECKING
from components.body import Body, BodyPart


class Modification:
    parent: BodyPart
    
    def __init__(self, name: str, description: str, mod_type: str, level: int = 1):
        self.name = name
        self.description = description
        self.mod_type = mod_type
        self.parent = None
        self.level = level  
        self.max_level = 5 


    
    @property
    def get_mod_location(self) -> str:
        return self.mod_type
    
    def can_level_up(self) -> bool:
        """Check if this mod can level up"""
        return self.level < self.max_level
    
    def level_up(self) -> bool:
        """Increase mod level by 1. Returns True if successful."""
        if self.can_level_up():
            self.level += 1
            return True
        return False

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
    def __init__(self, level: int = 1):
        super().__init__(
            "Xtra Brain", 
            "Develop an advanced Growth which allows for faster though processing",
            "internal",
            level
        )
    
    def get_stat_bonuses(self): 
        # Scales with level: +1 AP per level
        return {"max_ap": 1 * self.level}

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

class BigArm(Modification):
    #ARM EXTERNAL
    #gives extra strength
    def __init__(self, level :int = 1):
        super().__init__(
            "Mega[RM]", 
            "Mega Removable Appendage, Increase size and density of a user's Upper extremity", 
            "internal",
            level
            )
    def get_stat_bonuses(self):
        return{"strength": 3}
        
class DermaMAX(Modification):
    #INTERNAL TORSO
    #Give extra defence to player
    pass

class NumbDown(Modification):
    #INTRINSIC
    #Makes player character "dumber, reduces ap to 2 but greatly increases attack and defence
    def __init__(self, level = 1):
        super().__init__(
            "Induced RPD",
            "Extreme Dosage off an in development Multi purpose painkiller caused induced encephalopathy",
            "intrinsic",   
        )

            
    def get_stat_bonuses(self):
    
        return {"max_ap": -2 , 
                "strength": 2* self.level, 
                "defence": 2* self.level
                }

        
