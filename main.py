import time
import asyncio
import curses
from random import randint, choice
from animations.fire_animation import fire
from animations.spaceship_animation import animate_spaceship
from curses_tools import read_controls

TIC_TIMEOUT = 0.1
STAR_COUNT = 100
STAR_SYMBOLS = '+*.:'

async def blink(canvas, row, column, symbol='*', offset=0):
   
    for _ in range(offset):
        await asyncio.sleep(0)

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(20):
            await asyncio.sleep(0)
    
        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)
        

def create_stars(canvas, STARS_COUNT):
    stars = []
    border_width = 1
    rows_count, cols_count = canvas.getmaxyx()
    for _ in range(STARS_COUNT):
        row = randint(border_width, rows_count - 1 - border_width)
        col = randint(border_width, cols_count - 1 - border_width)  
        symbol = choice(STAR_SYMBOLS)
        offset = randint(1,5)
        stars.append(blink(canvas, row, col, symbol, offset))
    return stars

def open_animation_files():
    with open('animations/rocket_frame_1.txt') as f:
        rocket_frame_1 = f.read()

    with open('animations/rocket_frame_2.txt') as f:
        rocket_frame_2 = f.read()
    return rocket_frame_1, rocket_frame_2

def draw(canvas):
    canvas.border(0)
    curses.curs_set(0)
    canvas.nodelay(True) 
    max_row, max_column = canvas.getmaxyx()
    coroutines = create_stars(canvas, STAR_COUNT)
    coroutines.append(fire(canvas, max_row-1, max_column/2, rows_speed=-0.3, columns_speed=0))
    coroutines.append(animate_spaceship(canvas, int(max_row/2), int(max_column/2) ,ship_frame1, ship_frame2))
   
    while True:
        for coroutine in coroutines:
            try:                        
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)
        


if __name__ == '__main__':
    ship_frame1, ship_frame2 = open_animation_files()
    curses.update_lines_cols()
    curses.wrapper(draw)
    