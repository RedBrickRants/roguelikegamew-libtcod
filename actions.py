#actions.py

class Action:
    pass

class EscapeAction(Action):
    pass

class MovementAction(Action):
    def __init__(self, dx: int, dy: int):
        super().__init__()
        self.destination_x = dx
        self.destination_y = dy