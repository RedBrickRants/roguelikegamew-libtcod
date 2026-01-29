from __future__ import annotations
from typing import TYPE_CHECKING
from components.body import BodyPart
from equipment_types import EquipmentCategory
if TYPE_CHECKING:
    pass
    
class BodyType:
    def __init__(self):
        pass
def humanoid():
    return[
        BodyPart("head", part_type= EquipmentCategory.HEAD),
        BodyPart("torso", part_type= EquipmentCategory.TORSO),
        BodyPart("left arm", part_type= EquipmentCategory.ARM),
        BodyPart("right arm", part_type= EquipmentCategory.ARM),
        BodyPart("left leg", part_type= EquipmentCategory.LEG),
        BodyPart("right leg", part_type= EquipmentCategory.LEG),
    ]

def arachnid():
    parts = [BodyPart("head",  part_type= EquipmentCategory.HEAD), BodyPart("thorax",  part_type= EquipmentCategory.TORSO)]
    for i in range(8):
        parts.append(BodyPart(f"leg {i+1}",  part_type= EquipmentCategory.LEG))
    return parts