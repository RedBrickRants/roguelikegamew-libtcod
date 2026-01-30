from __future__ import annotations
import weakref
from typing import TYPE_CHECKING, Optional
from components.base_component import BaseComponent
from equipment_types import EquipmentType, EquipmentCategory

if TYPE_CHECKING:
    from entity import Item
    from components.body import BodyPart


class Equippable(BaseComponent):
    parent: Item

    def __init__(
        self,
        equipment_type: EquipmentType,
        equip_category: EquipmentCategory,
        strength_bonus: int = 0,
        defence_bonus: int = 0,
    ):
        self.equipment_type = equipment_type
        self.equip_category = equip_category
        self.strength_bonus = strength_bonus
        self.defence_bonus = defence_bonus

        self._current_slot_ref: Optional[weakref.ReferenceType[BodyPart]]= None

        
    @property
    def current_slot(self) -> Optional[BodyPart]:
        # If the object still exists, return it. Otherwise, return None.
        if self._current_slot_ref is not None:
            return self._current_slot_ref()
        return None

    @current_slot.setter
    def current_slot(self, slot: BodyPart):
        if slot is None:
            self._current_slot_ref = None
        else:
            # Create the weak reference
            self._current_slot_ref = weakref.ref(slot)


class Dagger(Equippable):
    def __init__(self) -> None:
        super().__init__(
            equipment_type=EquipmentType.WEAPON,
            equip_category=EquipmentCategory.ARM,
            strength_bonus=2
        )


class Sword(Equippable):
    def __init__(self) -> None:
        super().__init__(
            equipment_type=EquipmentType.WEAPON,
            equip_category=EquipmentCategory.ARM,
            strength_bonus=4
        )


class LeatherArmor(Equippable):
    def __init__(self) -> None:
        super().__init__(
            equipment_type=EquipmentType.ARMOR,
            equip_category=EquipmentCategory.TORSO,
            defence_bonus=1
        )


class ChainMail(Equippable):
    def __init__(self) -> None:
        super().__init__(
            equipment_type=EquipmentType.ARMOR,
            equip_category=EquipmentCategory.TORSO,
            defence_bonus=3
        )