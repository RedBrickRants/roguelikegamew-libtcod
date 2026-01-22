#actions.py
from __future__ import annotations
from typing import Optional, Tuple, TYPE_CHECKING

import colour
import exceptions
if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity, Item


class Action:
    ap_cost = 1
    def __init__(self, entity:Actor)->None:
        super().__init__()
        self.entity = entity
    @property
    def engine(self)-> Engine:
        return self.entity.gamemap.engine
    
    def perform(self) -> None:

        if hasattr(self.entity, "action_points"):
            if not self.entity.action_points.spend(self.ap_cost):
                raise exceptions.Impossible(
                    f"Not enough AP! Need {self.ap_cost}, have {self.entity.action_points.ap}"
                )
        self.execute()
        
    def execute (self)-> None:
        raise NotImplementedError
    
class PickupAction(Action):
    ap_cost = 0
    """Pickup an item and add it to the inventory, if there is room for it."""
    def __init__(self, entity:Actor):
        super().__init__(entity)
    
    def execute(self)-> None:
        actor_location_x =self.entity.x
        actor_location_y =self.entity.y
        inventory =self.entity.inventory

        for item in self.engine.game_map.items:
            if actor_location_x==item.x and actor_location_y == item.y:
                if len(inventory.items)>=inventory.capacity:
                    raise exceptions.Impossible("Your inventory is full")
                self.engine.game_map.entities.remove(item)
                item.parent = self.entity.inventory
                inventory.items.append(item)

                self.engine.message_log.add_message(f"You picked up the {item.name}!")
                return
        raise exceptions.Impossible("Theres nothing there to pickup")

class ItemAction(Action):
    def __init__(self, entity:Actor, item: Item, target_xy: Optional[Tuple[int, int]]=None):
        super().__init__(entity)
        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy
    
    @property
    def target_actor(self)-> Optional[Actor]:
        return self.engine.game_map.get_actor_at_location(*self.target_xy)
    
    def execute(self)-> None:
        self.item.consumable.activate(self)

class EscapeAction(Action):
    ap_cost = 0
    def execute (self)-> None:
        raise SystemExit()
    
class DropItem(ItemAction):
    ap_cost = 0
    def execute(self)-> None:
        if self.entity.equipment.item_is_equipped(self.item):
            self.entity.equipment.toggle_equip(self.item)

class EquipAction(Action):
    ap_cost = 0
    def __init__(self, entity: Actor, item: Item):
        super().__init__(entity)

        self.item = item

    def execute(self) -> None:
        self.entity.equipment.toggle_equip(self.item)

        
class WaitAction(Action):
    def execute(self)-> None:
        pass


class TakeStairsAction(Action):
    ap_cost = 0
    def execute(self) -> None:
        """
        Take the stairs, if any exist at the entity's location.
        """
        if (self.entity.x, self.entity.y) == self.engine.game_map.downstairs_location:
            self.engine.game_world.traverse_floors("down")
            self.engine.message_log.add_message(
                "You descend the staircase.", colour.descend
            )
        elif (self.entity.x, self.entity.y) == self.engine.game_map.upstairs_location:
            self.engine.game_world.traverse_floors("up")
            self.engine.message_log.add_message(
                "You ascend the staircase.", colour.descend
            )
        else:
            raise exceptions.Impossible("There are no stairs here.")
   
class ActionWithADirection(Action):
    def __init__(self, entity:Actor, dx: int, dy: int):
        super().__init__(entity)
        self.dx = dx
        self.dy = dy
    
    @property
    def dest_xy(self)->Tuple[int, int]:
        return self.entity.x +self.dx, self.entity.y +self.dy
    
    @property
    def blocking_entity(self)-> Optional[Entity]:
        return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)
    
    @property
    def target_actor(self)->Optional[Actor]:
        return self.engine.game_map.get_actor_at_location(*self.dest_xy)

    def execute(self)-> None:
        return NotImplementedError
    
class BumpAction(ActionWithADirection):
    ap_cost = 0 
    def execute(self)->None:
        if self.target_actor:
            return MeleeAction(self.entity, self.dx, self.dy).perform()
        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()
        
class MeleeAction(ActionWithADirection):
    ap_cost = 2
    def execute(self)-> None:
        
        target = self.target_actor
        if not target:
            raise exceptions.Impossible("Nothing to attack.")
        
        damage = self.entity.fighter.strength - target.fighter.defence
        attack_description = f"{self.entity.name.capitalize()} attacks {target.name}"
        if self.entity is self.engine.player:
            attac_colour = colour.player_atk
        else: 
            attac_colour = colour.enemy_atk
        if damage > 0:
            self.engine.message_log.add_message(f"{attack_description} for {damage} damage.",attac_colour)
            target.fighter.hp -= damage
        else:
            self.engine.message_log.add_message(f"{attack_description} but does no damage", attac_colour)

class MovementAction(ActionWithADirection):

    def execute (self)-> None:
        dest_x, dest_y = self.dest_xy
        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            raise exceptions.Impossible("That way is blocked.")
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            raise exceptions.Impossible("That way is blocked.")
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            raise exceptions.Impossible("That way is blocked.")
        self.entity.move(self.dx, self.dy)

