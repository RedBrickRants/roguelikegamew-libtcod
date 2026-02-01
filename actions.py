#actions.py
from __future__ import annotations
from typing import List, Optional, Tuple, TYPE_CHECKING
from components.body import BodyPart
from soundmanager import SoundManager
from components.equippable import RangedEquippable
import colour
import exceptions
import random
import tile_types
import tcod

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity, Item

sound_manager = SoundManager()
# actions.py
class Action:
    ap_cost = 1  # Default cost
    
    def __init__(self, entity: Actor) -> None:
        super().__init__()
        self.entity = entity
    
    @property
    def engine(self) -> Engine:
        return self.entity.gamemap.engine
    
    def get_ap_cost(self) -> int:
        """Override this to modify A cost"""
        return self.ap_cost
    
    def perform(self) -> None:
        """Centralized AP spending - don't override this unless you have a VERY good reason"""
        if hasattr(self.entity, "action_points"):
            cost = self.get_ap_cost()
            if not self.entity.action_points.spend(cost):
                raise exceptions.Impossible(
                    f"Not enough AP! Need {cost}, have {self.entity.action_points.ap}"
                )
        self.execute()
        
    def execute(self) -> None:
        """Override this to define what the action does"""
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
            self.entity.equipment.toggle_equip(self.item,self.item.equippable.current_slot)
        self.entity.inventory.drop(self.item)

class EquipAction(Action):
    ap_cost = 0
    def __init__(self, entity: Actor, item: Item, body_part: BodyPart):
        super().__init__(entity)
        self.item = item
        self.body_part = body_part

    def execute(self) -> None:
        slots_needed = self.item.equippable.slot_amount
        if slots_needed == 1:
            # Check what's currently in this slot
            current_item = self.entity.equipment.equipped_items.get(self.body_part)
            
            if current_item and current_item.equippable.slot_amount > 1:
                # Multi-slot item is equipped, need to unequip from all matching parts
                matching_parts = [
                    part for part in self.entity.body.parts 
                    if part.part_type == self.body_part.part_type
                ]
                
                for part in matching_parts:
                    if self.entity.equipment.equipped_items.get(part) == current_item:
                        self.entity.equipment.unequip_from_part(part, add_message=False)
                
                self.engine.message_log.add_message(
                    f"You unequip the {current_item.name}."
                )
            
            # Now equip the new item normally
            self.entity.equipment.toggle_equip(self.item, self.body_part)
        elif slots_needed > 1:
            matching_parts = [
            part for part in self.entity.body.parts 
            if part.part_type == self.body_part.part_type
        ]
            if len(matching_parts) < 2:
                raise exceptions.Impossible(f"Not enough {self.body_part.part_type.name} parts to equip {self.item.name}.")
            
            blocked_parts = [part for part in matching_parts if self.entity.equipment.equipped_items.get(part) is not None]
            if blocked_parts:
                for part in blocked_parts:
                    self.entity.equipment.unequip_from_part(part, add_message=False)
            
            for part in matching_parts:
                self.entity.equipment.equip_to_part(part, self.item, add_message=False)
            
            self.engine.message_log.add_message(
                f"You equip the {self.item.name} with both hands."
            )
        
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
    def normal_bump_behavior(self) -> None:
        # Normal bump behavior
        if self.target_actor:
            return MeleeAction(self.entity, self.dx, self.dy).perform()
        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()
        
    def execute(self) -> None:
        dest_x, dest_y = self.dest_xy
        
        # Check if there's a door at destination
        if (dest_x, dest_y) in self.engine.game_map.doors:
            is_open = self.engine.game_map.doors[(dest_x, dest_y)]
            if not is_open:
                return OpenAndMoveThroughDoorAction(self.entity, self.dx, self.dy).perform()
            else:
                return self.normal_bump_behavior()
        self.normal_bump_behavior()       
        

class MeleeAction(ActionWithADirection):
    ap_cost = 2  # Normal cost

    def get_ap_cost(self) -> int:
        """Calculate actual AP cost based on current AP"""
        current_ap = self.entity.action_points.ap
        
        if current_ap >= self.ap_cost:
            # Normal attack 
            return self.ap_cost
        elif current_ap > 0:
            # Exhausted attack
            return current_ap
        else:
            # No AP at all - can't attack
            return self.ap_cost  

    def execute(self) -> None:
        target = self.target_actor
        if not target:
            raise exceptions.Impossible("Nothing to attack.")
        
        # Check if this was an exhausted attack
        exhausted = self.entity.action_points.ap == 0  # We just spent all remaining AP
        
        # Exhausted attacks have a chance to miss entirely
        if exhausted and random.random() > 0.3:  # 70% chance to miss when exhausted
            self.engine.message_log.add_message(
                f"{self.entity.name} swings exhaustedly and misses!",
                colour.player_atk if self.entity is self.engine.player else colour.enemy_atk
            )
            sound_manager.play("miss")
            return
        
        # Calculate damage
        damage = self.entity.fighter.strength - target.fighter.defence
        
        # Exhausted attacks do half damage
        if exhausted:
            damage = damage // 2
        
        attack_colour = colour.player_atk if self.entity is self.engine.player else colour.enemy_atk
        
        if damage > 0:
            if exhausted:
                self.engine.message_log.add_message(
                    f"{self.entity.name} takes an exhausted swing and hits {target.name} for {damage} damage!",
                    attack_colour
                )
            else:
                self.engine.message_log.add_message(
                    f"{self.entity.name} attacks {target.name} for {damage} damage.",
                    attack_colour
                )
            target.fighter.hp -= damage
        else:
            self.engine.message_log.add_message(
                f"{self.entity.name} attacks {target.name} but does no damage.",
                attack_colour
            )
            sound_manager.play("miss")
        # Play appropriate sound
        if self.entity is self.engine.player:
            sound_manager.play("player_hit")
        else:
            sound_manager.play("soft_enemy_hit")
        
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
        if self.entity is self.engine.player:
            sound_manager.play("move")
        elif self.engine.game_map.visible[self.entity.x, self.entity.y]:
            sound_manager.play("move")

class PickupSpecificItemAction(Action):
    """Pick up a specific item."""
    ap_cost = 0
    
    def __init__(self, entity: Actor, item: Item):
        super().__init__(entity)
        self.item = item
    
    def execute(self) -> None:
        inventory = self.entity.inventory
        
        if len(inventory.items) >= inventory.capacity:
            raise exceptions.Impossible("Your inventory is full")
        
        self.engine.game_map.entities.remove(self.item)
        self.item.parent = self.entity.inventory
        inventory.items.append(self.item)
        
        self.engine.message_log.add_message(f"You picked up the {self.item.name}!")


class PickupAllAction(Action):
    """Pick up all items at a location."""
    ap_cost = 0
    
    def __init__(self, entity: Actor, items: list):
        super().__init__(entity)
        self.items = items
    
    def execute(self) -> None:
        inventory = self.entity.inventory
        picked_up = []
        
        for item in self.items:
            if len(inventory.items) >= inventory.capacity:
                self.engine.message_log.add_message(
                    f"Your inventory is full! Picked up {len(picked_up)} items.",
                    colour.impossible
                )
                return
            
            self.engine.game_map.entities.remove(item)
            item.parent = self.entity.inventory
            inventory.items.append(item)
            picked_up.append(item.name)
        
        self.engine.message_log.add_message(
            f"You picked up {len(picked_up)} items!"
        )

class OpenAndMoveThroughDoorAction(ActionWithADirection):
    """Open a door and move through it - costs 1 AP total"""
    ap_cost = 1
    
    def execute(self) -> None:
        dest_x, dest_y = self.dest_xy
        
        if (dest_x, dest_y) not in self.engine.game_map.doors:
            raise exceptions.Impossible("There's no door there!")
        
        # Open the door
        self.engine.game_map.tiles[dest_x, dest_y] = tile_types.door_open
        self.engine.game_map.doors[(dest_x, dest_y)] = True
        self.engine.message_log.add_message("You open the door and move through.")
        
        # Move through
        self.entity.move(self.dx, self.dy)
        self.engine.update_fov()


class ToggleDoorAction(ActionWithADirection):
    """Toggle door open/closed - costs NO AP"""
    ap_cost = 0
    
    def execute(self) -> None:
        dest_x, dest_y = self.dest_xy
        
        if (dest_x, dest_y) not in self.engine.game_map.doors:
            raise exceptions.Impossible("There's no door there!")
        
        is_open = self.engine.game_map.doors[(dest_x, dest_y)]
        
        if is_open:
            # Close door
            if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
                raise exceptions.Impossible("Something is in the way!")
            self.engine.game_map.tiles[dest_x, dest_y] = tile_types.door_closed
            self.engine.game_map.doors[(dest_x, dest_y)] = False
            self.engine.message_log.add_message("You close the door.")
        else:
            # Open door
            self.engine.game_map.tiles[dest_x, dest_y] = tile_types.door_open
            self.engine.game_map.doors[(dest_x, dest_y)] = True
            self.engine.message_log.add_message("You open the door.")
        
        self.engine.update_fov()

class RangedAttackAction(Action):
    def __init__(self, entity: Actor, target_xy: Tuple[int, int], weapon: RangedEquippable):
        super().__init__(entity)

        self.target_xy = target_xy
        self.weapon = weapon
        ap_cost = weapon.use_ap_cost

    def get_targets_in_line(self) -> List[Actor]:
            """Get all actors in the line of fire, respecting pierce"""

            
            x0, y0 = self.entity.x, self.entity.y
            x1, y1 = self.target_xy
            
            # Get line of sight
            line = tcod.los.bresenham((x0, y0), (x1, y1)).tolist()
            
            # Remove starting position
            if line and line[0] == (x0, y0):
                line.pop(0)
            
            targets = []
            for x, y in line:
                # Check for walls/blocking terrain
                if not self.engine.game_map.tiles["transparent"][x, y]:
                    break  # Can't shoot through walls
                
                # Check for actors
                actor = self.engine.game_map.get_actor_at_location(x, y)
                if actor and actor != self.entity:
                    targets.append(actor)
            
            return targets
        
    def execute(self) -> None:
        # Check ammo
        if not self.weapon.has_ammo():
            raise exceptions.Impossible(f"The {self.weapon.parent.name} is out of ammo!")
        
        # Check range
        distance = max(
            abs(self.target_xy[0] - self.entity.x),
            abs(self.target_xy[1] - self.entity.y)
        )
        
        if distance > self.weapon.max_range:
            raise exceptions.Impossible("Target is out of range!")
        
        # Check line of sight
        if not self.engine.game_map.visible[self.target_xy]:
            raise exceptions.Impossible("You cannot target an area you cannot see!")
        
        # Consume ammo
        self.weapon.consume_ammo(1)
        
        # Get all potential targets in line
        targets = self.get_targets_in_line()
        
        if not targets:
            self.engine.message_log.add_message(
                f"{self.entity.name} fires the {self.weapon.parent.name} but misses!",
                colour.player_atk if self.entity is self.engine.player else colour.enemy_atk
            )
            return
        
        # Apply damage with piercing
        pierce_remaining = self.weapon.pierce
        hit_count = 0
        
        for target in targets:
            # Calculate if shot pierces this enemy
            effective_defense = max(0, target.fighter.defence - pierce_remaining)
            damage = max(0, self.weapon.damage - effective_defense)
            
            if damage > 0:
                target.fighter.hp -= damage
                hit_count += 1
                
                self.engine.message_log.add_message(
                    f"{self.entity.name} shoots {target.name} for {damage} damage!",
                    colour.player_atk if self.entity is self.engine.player else colour.enemy_atk
                )
                
                # Reduce pierce after each hit
                pierce_remaining = max(0, pierce_remaining - 1)
                
                # Stop if pierce runs out
                if pierce_remaining < 0:
                    break
            else:
                # Shot stopped by defense
                self.engine.message_log.add_message(
                    f"The shot is stopped by {target.name}'s armor!",
                    colour.impossible
                )
                break
        
        # Ammo count message
        if self.entity is self.engine.player:
            self.engine.message_log.add_message(
                f"Ammo: {self.weapon.current_ammo}/{self.weapon.max_ammo}",
                colour.white
            )


class ReloadAction(Action):
    """Reload a ranged weapon"""
    
    def __init__(self, entity: Actor, weapon: RangedEquippable):
        super().__init__(entity)
        self.weapon = weapon
        ap_cost = self.weapon.reload_ap_cost
    
    def execute(self) -> None:
        """Reload the weapon"""
        if self.weapon.current_ammo == self.weapon.max_ammo:
            raise exceptions.Impossible("Weapon is already fully loaded!")
        
        # TODO: Check for ammo in inventory when you add ammo items

        reloaded = self.weapon.reload()
        
        self.engine.message_log.add_message(
            f"You reload the {self.weapon.parent.name}. ({reloaded} rounds)",
            colour.white
        )