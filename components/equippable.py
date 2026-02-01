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

class RangedEquippable(Equippable):
    def __init__(
        self,
        equipment_type: EquipmentType,
        equip_category: EquipmentCategory,
        strength_bonus: int = 0,
        defence_bonus: int = 0,
        damage: int = 0,
        pierce: int = 0,
        max_range: int = 0,
        ammo_type: Optional[str] = None,
        max_ammo: int = 0,
        current_ammo: Optional[int] = 0,
    ):
        super().__init__(
            equipment_type,
            equip_category,
            strength_bonus,
            defence_bonus
        )
        self.damage = damage
        self.pierce = pierce
        self.max_range = max_range
        self.ammo_type = ammo_type
        self.max_ammo = max_ammo
        self.current_ammo = current_ammo if current_ammo is not None else max_ammo

        self._current_slot_ref: Optional[weakref.ReferenceType[BodyPart]]= None

    def has_ammo(self) -> bool:
        return self.current_ammo is not None and self.current_ammo > 0
    def consume_ammo(self, amount: int = 1) -> None:
        if self.current_ammo is not None:
            self.current_ammo = max(0, self.current_ammo - amount)

    def reload(self, amount: Optional[int] = None) -> int:
        """Reload weapon, return amount reloaded"""
        if amount is None:
            amount = self.max_ammo - self.current_ammo
        
        old_ammo = self.current_ammo
        self.current_ammo = min(self.max_ammo, self.current_ammo + amount)
        return self.current_ammo - old_ammo


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

class Pistol(RangedEquippable):
    def __init__(self) -> None:
        super().__init__(
            equipment_type=EquipmentType.RANGEDWEAPON,
            equip_category=EquipmentCategory.ARM,
            damage=8,
            pierce=0,
            max_range=8,
            ammo_type="bullet",
            max_ammo=12,
        )


class Rifle(RangedEquippable):
    def __init__(self) -> None:
        super().__init__(
            equipment_type=EquipmentType.RANGEDWEAPON,
            equip_category=EquipmentCategory.ARM,
            damage=12,
            pierce=2,
            max_range=15,
            ammo_type="bullet",
            max_ammo=8,
        )


class LaserPistol(RangedEquippable):
    def __init__(self) -> None:
        super().__init__(
            equipment_type=EquipmentType.RANGEDWEAPON,
            equip_category=EquipmentCategory.ARM,
            damage=10,
            pierce=1,
            max_range=10,
            ammo_type="energy",
            max_ammo=20,
        )

class PlasmaRifle(RangedEquippable):
    def __init__(self) -> None:
        super().__init__(
            equipment_type=EquipmentType.RANGEDWEAPON,
            equip_category=EquipmentCategory.ARM,
            damage=15,
            pierce=3,
            max_range=12,
            ammo_type="energy",
            max_ammo=15,
        )