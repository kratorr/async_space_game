import asyncio
import curses
from curses_tools import draw_frame, read_controls
import time

async def animate_spaceship(canvas, row, column, frame_1, frame_2):
    ship_height, ship_width = 9, 5
    max_row, max_column = canvas.getmaxyx()
    rows_direction = 0
    columns_direction = 0

    while True:
        draw_frame(canvas, row, column, frame_1, negative=False)       
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, frame_1, negative=True)
        
        draw_frame(canvas, row, column, frame_2, negative=False)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, frame_2, negative=True)
        
        if column + columns_direction != 0: 
            if column + columns_direction < max_column - ship_width:
                column = column + columns_direction

        if row + rows_direction != 0:
            if row + rows_direction < max_row - ship_height :
                row = row + rows_direction
       
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
