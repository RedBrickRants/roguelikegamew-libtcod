from enum import auto, Enum


class EquipmentType(Enum):
    WEAPON = auto()
    ARMOR = auto()

class EquipmentCategory(Enum):
    ARM = auto()
    TORSO = auto()
    HEAD=auto()
    