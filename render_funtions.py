from __future__ import annotations
from typing import TYPE_CHECKING
import colour

if TYPE_CHECKING:
    from tcod  import console

def render_bar( 
        console: console.Console, 
        current_value: int, 
        maximum_value: int, 
        total_width: int
    )->None:
    bar_width = int(float(current_value)/maximum_value * total_width)
    console.draw_rect(x=0, y=45, width= total_width, height= 1, ch=1, bg=colour.bar_empty)
    if bar_width>0:
        console.draw_rect(x=0, y=45, width=bar_width,height=1, ch=1, bg=colour.bar_filled)

    console.print(x=1, y=45, string=f"HP:{current_value}/{maximum_value}", fg=colour.bar_text)
