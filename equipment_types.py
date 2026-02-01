from enum import auto, Enum


class EquipmentType(Enum):
    RANGEDWEAPON = auto()
    WEAPON = auto()
    ARMOR = auto()

class EquipmentCategory(Enum):
    ARM = auto()
    TORSO = auto()
    HEAD=auto()
    LEG = auto()

class ModificationType(Enum):
    INTRINSIC = auto()
    INTERNAL = auto()
    EXTERNAL = auto()

class ModificationSlot(Enum):
    BODY = auto()
    ARM = auto()
    TORSO = auto()
    HEAD=auto()
    LEG = auto()