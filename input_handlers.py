#input_handlers.py

from typing import Optional #allows for things to be set to none for graceful handling
import tcod.event
from actions import Action, EscapeAction, MovementAction


class EventHandler(tcod.event.EventDispatch[Action]):
    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        action: Optional[Action] = None

        key_code = event.sym

        match key_code:
            case tcod.event.KeySym.UP:
                action = MovementAction(dx = 0, dy= -1)
            case tcod.event.KeySym.DOWN:
                action = MovementAction(dx = 0, dy= 1)
            case tcod.event.KeySym.LEFT:
                action = MovementAction(dx = -1, dy= 0)
            case tcod.event.KeySym.RIGHT:
                action = MovementAction(dx = 1, dy= 0)
            case tcod.event.KeySym.ESCAPE:
                action = EscapeAction
            case _:
                return action

