from __future__ import annotations
from typing import TYPE_CHECKING
from components.body import BodyPart
if TYPE_CHECKING:
    pass
    
class BodyType:
    def __init__(self):
        pass
def humanoid():
    return[
        BodyPart("head", "head"),
        BodyPart("torso", "torso"),
        BodyPart("left arm", "arm"),
        BodyPart("right arm", "arm"),
        BodyPart("left leg", "leg"),
        BodyPart("right leg", "leg"),
    ]

def arachnid():
    parts = [BodyPart("head", "head"), BodyPart("thorax", "torso")]
    for i in range(8):
        parts.append(BodyPart(f"leg {i+1}", "leg"))
    return parts