from __future__ import annotations
from typing import List, Optional, Tuple, TYPE_CHECKING

import numpy as np #type: ignore
import tcod
import random

from actions import Action, BumpAction, MeleeAction, MovementAction, WaitAction


if TYPE_CHECKING:
    from entity import Actor

class BaseAI(Action):

    def execute(self)-> None:
        raise NotImplementedError()
    
    def get_path_to(self, dest_x:int, dest_y: int)-> List[Tuple[int, int]]:
        cost = np.array(self.entity.gamemap.tiles["walkable"], dtype=np.int8)

        for entity in self.entity.gamemap.entities:
            #check that an entity bloxks movement and the cost isnt 0(blocking.)
            # Add to the cost of a blocked position.
            # A lower number means more enemies will crowd behind each other in
            # hallways.  A higher number means enemies will take longer paths in
            # order to surround the player.
            if entity.blocks_movement and cost[entity.x, entity.y]:
                cost[entity.x, entity.y]+=10
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal = 3)
        pathfinder = tcod.path.Pathfinder(graph)

        pathfinder.add_root((self.entity.x, self.entity.y))# start position

        path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

        return[(index[0], index[1]) for index in path]

class ConfusedEnemy(BaseAI):
    """
    A confused enemy will stumble around aimlessly for a given number of turns, then revert back to its previous AI.
    If an actor occupies a tile it is randomly moving into, it will attack.
    """

    def __init__(
        self, entity: Actor, previous_ai: Optional[BaseAI], turns_remaining: int
    ):
        super().__init__(entity)

        self.previous_ai = previous_ai
        self.turns_remaining = turns_remaining

    def execute(self) -> None:
        # Revert the AI back to the original state if the effect has run its course.
        if self.turns_remaining <= 0:
            self.engine.message_log.add_message(
                f"The {self.entity.name} is no longer confused."
            )
            self.entity.ai = self.previous_ai
        else:
            # Pick a random direction
            direction_x, direction_y = random.choice(
                [
                    (-1, -1),  # Northwest
                    (0, -1),  # North
                    (1, -1),  # Northeast
                    (-1, 0),  # West
                    (1, 0),  # East
                    (-1, 1),  # Southwest
                    (0, 1),  # South
                    (1, 1),  # Southeast
                ]
            )

            self.turns_remaining -= 1

            # The actor will either try to move or attack in the chosen random direction.
            # Its possible the actor will just bump into the wall, wasting a turn.
            return BumpAction(self.entity, direction_x, direction_y,).perform()

class HostileEnemy(BaseAI):
    def __init__(self, entity: Actor):
        super().__init__(entity)
        self.path: List[Tuple[int, int]] = []
        self.target: Optional[Actor] = None
        self.target_last_seen_at: Optional[Tuple[int, int]] = None
    
    def execute(self):
        ap = self.entity.action_points.ap
        if ap <= 0:
            return None
        if not self.engine.game_map.visible[self.entity.x, self.entity.y]:
            return None  # do nothing, no AP spent
        
        self.target = self.engine.player
        
        # Update last seen position if we can see the player
        if self.engine.game_map.visible[self.target.x, self.target.y]:
            self.target_last_seen_at = (self.target.x, self.target.y)
        
        # If we have a last known position, use it
        if self.target_last_seen_at:
            t_x, t_y = self.target_last_seen_at
        else:
            return WaitAction(self.entity)
        
        # If we've reached the last known position, do one search move then forget
        if (self.entity.x, self.entity.y) == (t_x, t_y):
            self.target_last_seen_at = None
            direction_x, direction_y = random.choice(
                [
                    (-1, -1), (0, -1), (1, -1),
                    (-1, 0), (1, 0),
                    (-1, 1), (0, 1), (1, 1),
                ]
            )
            return BumpAction(self.entity, direction_x, direction_y)  # REMOVED .perform()
        
        # Calculate distance to target (use actual position if visible, else last seen)
        if self.engine.game_map.visible[self.target.x, self.target.y]:
            dx = self.target.x - self.entity.x
            dy = self.target.y - self.entity.y
        else:
            dx = t_x - self.entity.x
            dy = t_y - self.entity.y
        
        distance = max(abs(dx), abs(dy))
        
        # Melee if adjacent AND can see player
        if distance <= 1 and self.engine.game_map.visible[self.target.x, self.target.y]:
            return MeleeAction(self.entity, dx, dy)
        
        # Pathfind to last known position
        self.path = self.get_path_to(t_x, t_y)
        if self.path:
            dest_x, dest_y = self.path.pop(0)
            return MovementAction(
                self.entity, dest_x - self.entity.x, dest_y - self.entity.y,
            )
        
        return WaitAction(self.entity)