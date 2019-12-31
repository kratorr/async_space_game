import asyncio
import curses
import time
from curses_tools import draw_frame, read_controls
from space_ship_physics import update_speed
#from main import coroutines
#from async_space_game.main import coroutines

async def sleep(tics=1):
  for _ in range(tics):
    await asyncio.sleep(0)

spaceship_frame = ''


async def run_spaceship(canvas, row, column):
    global coroutines
    global spaceship_frame
    ship_height, ship_width = 9, 5
    max_row, max_column = canvas.getmaxyx()
    rows_direction = 0
    columns_direction = 0
    row_speed = column_speed = 0
    while True:
        global spaceship_frame
        global coroutines
        last_frame = spaceship_frame
        
        draw_frame(canvas, row, column, spaceship_frame, negative=False)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, last_frame, negative=True)
        last_frame = spaceship_frame
        draw_frame(canvas, row, column, spaceship_frame, negative=False)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, last_frame, negative=True)
        


        if column + columns_direction != 0: 
            if column + columns_direction < max_column - ship_width:
                column = column + columns_direction

        if row + rows_direction != 0:
            if row + rows_direction < max_row - ship_height :
                row = row + rows_direction
        
        
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        
        row_speed, column_speed = update_speed(
            row_speed, column_speed, rows_direction, columns_direction
        )
        row = row + row_speed
        column = column + column_speed

        coroutines.append(fire(canvas, max_row-1, max_column/2, rows_speed=-0.3, columns_speed=0))

        #fire(canvas, max_row-1, max_column/2, rows_speed=-0.3, columns_speed=0)

async def animate_spaceship(frame_1, frame_2, canvas):

    global spaceship_frame
    while True:
        spaceship_frame = frame_1 
        await sleep(1)
        spaceship_frame = frame_2
        await sleep(1)





import asyncio
import curses


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot. Direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed