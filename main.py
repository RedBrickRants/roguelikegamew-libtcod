#main.py
import tcod
import constants as const
from actions import Action,  EscapeAction, MovementAction
from input_handlers import EventHandler

def main():
    
    event_handler = EventHandler()
    player_x = const.SCREEN_WIDTH//2
    player_y = const.SCREEN_WIDTH//2

    tileset = tcod.tileset.load_tilesheet(
        "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )
    console = tcod.console.Console(const.SCREEN_WIDTH, const.SCREEN_HEIGHT, order="F") 
    with tcod.context.new(
        columns= console.width, rows= console.height, tileset= tileset
        ) as context:
        
        #Game Loop:
        while True:
            console.clear()
            console.print(player_x,player_y, string="@")
            context.present(console)

            for event in tcod.event.wait():
                action = event_handler.dispatch(event)
                match action:
                    case None:
                        print ("No action")
                        continue
                    case MovementAction():
                        print ("move")
                        player_x += action.dx
                        player_y +=action.dy
                    case EscapeAction():
                        print("leave")
                        raise SystemExit
                    
if __name__ == "__main__":
    main()