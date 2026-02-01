from __future__ import annotations
from typing import Optional, TYPE_CHECKING, Dict
from components.base_component import BaseComponent
from equipment_types import EquipmentType

if TYPE_CHECKING:
    from entity import Actor, Item
    from components.body import BodyPart


class Equipment(BaseComponent):
    parent: Actor

    def __init__(self):
        # We can't access parent.body.parts here yet because parent doesn't exist
        # So we initialize as empty dict and populate it later
        self.equipped_items: Dict[BodyPart, Optional[Item]] = {}
        self._initialized = False
    
    @property
    def parent(self):
        return self._parent
    
    @parent.setter
    def parent(self, value):
        self._parent = value
        if value and not self._initialized:
            self.initialize_slots()
            self._initialized = True

    def initialize_slots(self) -> None:
        """Called after parent is set to populate equipment slots from body parts"""
        if hasattr(self.parent, 'body') and self.parent.body:
            for part in self.parent.body.parts:
                if part not in self.equipped_items:
                    self.equipped_items[part] = None

    @property
    def defence_bonus(self) -> int:
        """Sum defense bonuses from all equipped items"""
        bonus = 0
        for item in self.equipped_items.values():
            if item is not None and item.equippable is not None:
                bonus += item.equippable.defence_bonus
        return bonus

    @property
    def strength_bonus(self) -> int:
        """Sum strength bonuses from all equipped items"""
        bonus = 0
        for item in self.equipped_items.values():
            if item is not None and item.equippable is not None:
                bonus += item.equippable.strength_bonus
        return bonus

    def item_is_equipped(self, item: Item) -> bool:
        """Check if item is equipped on any body part"""
        return item in self.equipped_items.values()

    def get_equipped_part(self, item: Item) -> Optional[BodyPart]:
        """Get which body part an item is equipped on, or None"""
        for part, equipped_item in self.equipped_items.items():
            if equipped_item == item:
                return part
        return None

    def get_valid_parts_for_item(self, item: Item) -> list[BodyPart]:
        """Get list of body parts that can equip this item"""
        if not item.equippable:
            return []
        #print(f"DEBUG: Item category: {item.equippable.equip_category}")
        #print(f"DEBUG: Equipment slots keys: {list(self.equipped_items.keys())}")
        
        valid_parts = []
        for part in self.equipped_items.keys():
            #print(f"DEBUG: Checking part {part.name}, type: {part.part_type}")
            if part.part_type == item.equippable.equip_category:
                valid_parts.append(part)
        #print(f"DEBUG: Valid parts found: {[p.name for p in valid_parts]}")
        return valid_parts

    def unequip_message(self, item_name: str, part_name: str) -> None:
        self.parent.gamemap.engine.message_log.add_message(
            f"You remove the {item_name} from your {part_name}."
        )

    def equip_message(self, item_name: str, part_name: str) -> None:
        self.parent.gamemap.engine.message_log.add_message(
            f"You equip the {item_name} to your {part_name}."
        )

    def equip_to_part(self, body_part: BodyPart, item: Item, add_message: bool = True) -> None:
        """
        Equips an item to a specific body part. 
        If the item is already equipped elsewhere, it is moved.
        """
        old_slot = item.equippable.current_slot
        if old_slot is not None:
            if old_slot is body_part:
                return
            self.equipped_items[old_slot] = None
        if self.equipped_items.get(body_part) is not None:
            old_item = self.equipped_items[body_part]
            if old_item:
                old_item.equippable.current_slot = None

                if old_item.equippable.slot_amount > 1:
                    for slot, equipped in self.equipped_items.items():
                        if equipped is old_item:
                            self.equipped_items[slot] = None
        self.equipped_items[body_part] = item
        item.equippable.current_slot = body_part
        if add_message:
            self.equip_message(item.name, body_part.name)
        
        """self.unequip_from_part(body_part, add_message=add_message)
        for slot, equipped_item in self.equipped_items.items():
            if equipped_item is item:  
                self.equipped_items[slot] = None
                self.parent.gamemap.engine.message_log.add_message(
            f"You swapped the {equipped_item.name} to another hand.")
        
        if self.equipped_items.get(body_part) is not None:
            self.unequip_from_part(body_part, add_message=add_message)

        self.equipped_items[body_part] = item

        if add_message:
            self.equip_message(item.name, body_part.name)"""

    def unequip_from_part(self, body_part: BodyPart, add_message: bool = True) -> None:
        """Unequip item from a specific body part"""
        current_item = self.equipped_items.get(body_part)
        if current_item:
            current_item.equippable.current_slot = None
        if current_item is None:
            return

        if add_message:
            self.unequip_message(current_item.name, body_part.name)

        self.equipped_items[body_part] = None

    def toggle_equip(self, equippable_item: Item, body_part: BodyPart, add_message: bool = True) -> None:
        """Toggle equipment on a specific body part"""
        current_item = self.equipped_items.get(body_part)
        
        if current_item == equippable_item:
            # Unequip if already equipped here
            self.unequip_from_part(body_part, add_message)
        else:
            # Equip to this part
            self.equip_to_part(body_part, equippable_item, add_message)