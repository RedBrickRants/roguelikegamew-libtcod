from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from components.base_component import BaseComponent
from exceptions import Impossible
from input_handlers import ActionOrHandler, AreaRangedAttackHandler, SingleRangedAttackHandler

import actions
import colour

if TYPE_CHECKING:
    from entity import Actor, Item

class Body(BaseComponent):
    parent: Actor