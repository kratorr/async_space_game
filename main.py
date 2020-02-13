import time
import asyncio
import curses
from random import randint, choice
from animations.fire_animation import fire
from animations.spaceship_animation import animate_spaceship, run_spaceship
#from animations.space_garbage import fly_garbage
from curses_tools import read_controls, draw_frame, read_controls
from space_ship_physics import update_speed
from obstacles import Obstacle
import uuid as u


coroutines = []
obstacles = []
obstacles_in_last_collisions = []

TIC_TIMEOUT = 0.1
STAR_COUNT = 100
STAR_SYMBOLS = '+*.:'
GARBAGE_FRAMES = ['trash_x1.txt', 'trash_large.txt', 'trash_small.txt']


async def sleep(tics=1):
  for _ in range(tics):
    await asyncio.sleep(0)


async def blink(canvas, row, column, symbol='*', offset=0):
   
    await sleep(offset)

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(20)

        canvas.addstr(row, column, symbol)
        await sleep(3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(5)

        canvas.addstr(row, column, symbol)
        await sleep(3)
        

async def fill_orbit_with_garbage(canvas, garbage_list):
    global coroutines
    _, columns_number = canvas.getmaxyx()
    while True:
        rand_garbage_frame = garbage_list[randint(0, len(garbage_list)-1)]
        coroutines.append(fly_garbage(canvas, randint(0,columns_number), rand_garbage_frame, speed=0.5, uid=u.uuid4()))
        await sleep(5)


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
    #with open('/home/kratorr/projects/devman/async_space_game/animations/rocket_frame_1.txt') as rocket_frame:
    with open('animations/rocket_frame_1.txt') as rocket_frame:
        rocket_frame_1 = rocket_frame.read()

    #with open('/home/kratorr/projects/devman/async_space_game/animations/rocket_frame_2.txt') as rocket_frame:
    with open('animations/rocket_frame_2.txt') as rocket_frame:
        rocket_frame_2 = rocket_frame.read()

    return rocket_frame_1, rocket_frame_2


def open_garbage_files():
    garbage_list = []
    for frame in GARBAGE_FRAMES:
        with open('animations/{}'.format(frame), "r") as garbage_file:
            garbage = garbage_file.read()
        garbage_list.append(garbage)
    return garbage_list

async def count(canvas):
    global obstacles
    while True:
        draw_frame(canvas, 10, 10, str(len(obstacles)), negative=False)
        await sleep(1)
        draw_frame(canvas, 5, 5, str(len(obstacles)), negative=True)


def draw(canvas):
    canvas.border(0)
    curses.curs_set(0)
    canvas.nodelay(True) 
    max_row, max_column = canvas.getmaxyx()
    global coroutines
    global obstacles
    coroutines +=  create_stars(canvas, STAR_COUNT)


    coroutines.append(run_spaceship(canvas, int(max_row/2), int(max_column/2)))

    coroutines.append(animate_spaceship(ship_frame1, ship_frame2, canvas))
    
    coroutines.append(fill_orbit_with_garbage(canvas, garbage_list))
   
    coroutines.append(show_obstacles(canvas, obstacles))

    coroutines.append(count(canvas))    

    while True:
        
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()
        canvas.border(0)
        time.sleep(TIC_TIMEOUT)






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


        draw_frame(canvas, row, column, spaceship_frame)
        last_frame = spaceship_frame
        await sleep(1)
        draw_frame(canvas, row, column, last_frame, negative=True)
      
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        
        row_speed, column_speed = update_speed(
            row_speed, column_speed, rows_direction, columns_direction
        )
        row = row + row_speed
        column = column + column_speed

        if space_pressed is True:
            coroutines.append(fire(canvas, row, column + 2, rows_speed=-0.3, columns_speed=0))


async def animate_spaceship(frame_1, frame_2, canvas):

    global spaceship_frame
    while True:
        spaceship_frame = frame_1 
        await sleep(1)
        spaceship_frame = frame_2
        await sleep(1)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot. Direction and speed can be specified."""
    global obstacles
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

   # curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed
        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                return ''
            


from curses_tools import draw_frame
import asyncio
from obstacles import show_obstacles
from curses_tools import get_frame_size

async def fly_garbage(canvas, column, garbage_frame, speed=0.5, uid=None):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()
    column = max(column, 0)
    column = min(column, columns_number - 1)
    global obstacles
    row = 0
    garbage_rows, garbabe_columns = get_frame_size(garbage_frame)
    obstacles.append(Obstacle(row, column, garbage_rows, garbabe_columns, uid=uid))
    try:
        while row < rows_number:
            
            draw_frame(canvas, row, column, garbage_frame)              
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, garbage_frame, negative=True)
            
            for obstacle in obstacles:
                if obstacle.uid == uid:
                    obstacle.row = row
                    obstacle.column = column
            row += speed

    finally:

        pass
       # obstacles.remove(obstacle)

if __name__ == '__main__':
    #print('Список всех препятствий:')
    #for obstacle in obstacles:
    #    print(obstacle.row, obstacle.column, obstacle.rows_size, obstacle.columns_size, obstacle.uid)
    
    ship_frame1, ship_frame2 = open_animation_files()
    garbage_list = open_garbage_files()
    curses.update_lines_cols()
    curses.wrapper(draw)
    