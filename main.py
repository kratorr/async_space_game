import time
import asyncio
import uuid as u
import curses

from random import randint, choice

from curses_tools import read_controls, draw_frame, read_controls, get_frame_size
from physics import update_speed
from obstacles import Obstacle, show_obstacles
from animations.frames.gameover import game_over_frame
from animations.explosion_frames import explosion_frames

coroutines = []
obstacles = []
obstacles_in_last_collisions = []
spaceship_frame = ''
TIC_TIMEOUT = 0.1
STAR_COUNT = 100
STAR_SYMBOLS = '+*.:'
GARBAGE_FRAMES = ['trash_x1.txt', 'trash_large.txt', 'trash_small.txt']


async def sleep(tics=1):
  for _ in range(tics):
    await asyncio.sleep(0)


async def run_spaceship(canvas, row, column):
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

        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                await show_gameover(canvas)
                return ''
        if space_pressed is True:
            coroutines.append(fire(canvas, row, column + 2, rows_speed=-0.3, columns_speed=0))


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot. Direction and speed can be specified."""
    #global obstacles
    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await sleep(0)
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
        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                obstacles_in_last_collisions.append(obstacle)
                return ''


async def show_gameover(canvas):
    max_row, max_column = canvas.getmaxyx()
    while True:
        draw_frame(canvas, max_row/2, max_column/2, game_over_frame)
        await sleep(1)


async def animate_spaceship(frame_1, frame_2, canvas):
    global spaceship_frame
    while True:
        spaceship_frame = frame_1 
        await sleep(1)
        spaceship_frame = frame_2
        await sleep(1)


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
        

async def fly_garbage(canvas, column, garbage_frame, speed=0.5, uid=None):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()
    column = max(column, 0)
    column = min(column, columns_number - 1)
    row = 0
    garbage_rows, garbabe_columns = get_frame_size(garbage_frame)
    obstacles.append(Obstacle(row, column, garbage_rows, garbabe_columns, uid=uid))
    try:
        while row < rows_number:
            hit_obstacles = list(filter(lambda x: x.uid == uid, obstacles_in_last_collisions))
            if hit_obstacles:
                obstacles_in_last_collisions.remove(hit_obstacles[0])
                await explode(canvas, row + garbage_rows / 2, column + garbabe_columns / 2)
                return ''

            draw_frame(canvas, row, column, garbage_frame)              
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, garbage_frame, negative=True)

            for obstacle in obstacles:
                if obstacle.uid == uid:
                    obstacle.row = row
                    obstacle.column = column
            row += speed
    finally:
        for obstacle in obstacles:
            if obstacle.uid == uid:
                obstacles.remove(obstacle)


async def explode(canvas, center_row, center_column):
    rows, columns = get_frame_size(explosion_frames[0])
    corner_row = center_row - rows / 2
    corner_column = center_column - columns / 2

    curses.beep()
    for frame in explosion_frames:
        draw_frame(canvas, corner_row, corner_column, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, corner_row, corner_column, frame, negative=True)
        await asyncio.sleep(0)


async def fill_orbit_with_garbage(canvas, garbage_list):
    global coroutines
    _, columns_number = canvas.getmaxyx()
    while True:
        rand_garbage_frame = garbage_list[randint(0, len(garbage_list)-1)]
        coroutines.append(fly_garbage(canvas, randint(0, columns_number), rand_garbage_frame, speed=0.5, uid=u.uuid4()))
        await sleep(5)


def create_stars(canvas, STARS_COUNT):
    stars = []
    border_width = 1
    rows_count, cols_count = canvas.getmaxyx()
    for _ in range(STARS_COUNT):
        row = randint(border_width, rows_count - 1 - border_width)
        col = randint(border_width, cols_count - 1 - border_width)
        symbol = choice(STAR_SYMBOLS)
        offset = randint(1, 5)
        stars.append(blink(canvas, row, col, symbol, offset))
    return stars


def open_animation_files():
    with open('animations/frames/rocket_frame_1.txt') as rocket_frame:
        rocket_frame_1 = rocket_frame.read()

    with open('animations/frames/rocket_frame_2.txt') as rocket_frame:
        rocket_frame_2 = rocket_frame.read()

    return rocket_frame_1, rocket_frame_2


def open_garbage_files():
    garbage_list = []
    for frame in GARBAGE_FRAMES:
        with open('animations/frames/{}'.format(frame), "r") as garbage_file:
            garbage = garbage_file.read()
        garbage_list.append(garbage)
    return garbage_list


async def count(canvas):
    global obstacles
    global coroutines
    while True:
        draw_frame(canvas, 10, 10, str(len(obstacles)) + 'obs', negative=False)
        draw_frame(canvas, 10, 20, str(len(coroutines)) + 'coro', negative=False)
        draw_frame(canvas, 10, 30, str(len(obstacles_in_last_collisions)) + 'coll', negative=False)
        await sleep(1)
        draw_frame(canvas, 10, 10, str(len(obstacles)) + 'obs', negative=True)
        draw_frame(canvas, 10, 20, str(len(coroutines)) + 'coro', negative=True)
        draw_frame(canvas, 10, 30, str(len(obstacles_in_last_collisions)) + 'coll', negative=True)


def draw(canvas):
    canvas.border(0)
    curses.curs_set(0)
    canvas.nodelay(True)
    max_row, max_column = canvas.getmaxyx()
    global coroutines
    global obstacles
    coroutines += create_stars(canvas, STAR_COUNT)

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


if __name__ == '__main__':
    ship_frame1, ship_frame2 = open_animation_files()
    garbage_list = open_garbage_files()

    curses.update_lines_cols()
    curses.wrapper(draw)
