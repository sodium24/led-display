################################################################################
# snake.py
#-------------------------------------------------------------------------------
# Nibbles/snake-type game, partially based on Microsoft QBasic Nibbles.
#
# This game has been optimized for a 64x64 LED display, and is best played with
# a joystick, like an XBox controller.
# 
# By Malcolm Stagg
#
# Copyright (c) 2021 SODIUM-24, LLC
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
################################################################################

import time
import random
import threading
from rgbmatrix import graphics

from ..app_base import AppBase

class SnakeBody(object):
    """
    Object containing the coordinates of part of a snake
    """
    def __init__(self):
        self.row = -1
        self.col = -1

class SnakeInfo(object):
    """
    Object containing information about a snake's position and status
    """
    def __init__(self):
        self.head = 0
        self.length = 0
        self.row = 0
        self.col = 0
        self.direction = 0
        self.lives = 0
        self.score = 0
        self.scolor = 0
        self.alive = 0

# Constants
MAXSNAKELENGTH = 1000
START_OVER = 1
SAME_LEVEL = 2
NEXT_LEVEL = 3

arena = [[0 for x in range(64)] for y in range(64)]
current_level = 0

# Color configuration
ledColors = [
    (255, 255, 0),   # snake 1
    (0, 255, 255),   # snake 2 (unused)
    (255, 255, 255), # walls
    (0, 0, 0),       # background
    (255, 255, 255), # dialog
    (255, 0, 0),     # dialog background
    (255, 255, 255), # bright
    (255, 0, 0)      # number
]

def EraseSnake(display_handler, snake, snake_body):
    """
    Erase a snake from the screen
    """
    for c in range(10):
        for b in range(snake.length - c,-1,-10):
            tail = (snake.head + MAXSNAKELENGTH - b) % MAXSNAKELENGTH
            SetPixel(display_handler, snake_body[tail].row, snake_body[tail].col, 4)
        time.sleep(0.01)

def InitColors(display_handler):
    """
    Initialize screen colors
    """
    for row in range(64):
        for col in range(64):
            arena[row][col] = 4

    display_handler.Clear()

    # Add a screen border
    for col in range(64):
        SetPixel(display_handler, 0, col, 3)
        SetPixel(display_handler, 63, col, 3)

    for row in range(1, 63):
        SetPixel(display_handler, row, 0, 3)
        SetPixel(display_handler, row, 63, 3)

def Level(display_handler, level_event, snake):
    """
    Setup the screen for a level
    """
    global current_level
    if level_event == START_OVER:
        current_level = 1
    elif level_event == NEXT_LEVEL:
        current_level += 1

    # Initialize Snake
    snake.head = 1 
    snake.length = 2
    snake.alive = True

    InitColors(display_handler)

    if current_level == 1:
        snake.row = 31
        snake.col = 47
        snake.direction = 4

    elif current_level == 2:
        for i in range(16, 48):
            SetPixel(display_handler, 31, i, 3)

        snake.row = 6
        snake.col = 47
        snake.direction = 3

    elif current_level == 3:
        for i in range(16, 48):
            SetPixel(display_handler, i, 15, 3)
            SetPixel(display_handler, i, 47, 3)

        snake.row = 31
        snake.col = 42
        snake.direction = 1

    elif current_level == 4:
        for i in range(1, 32):
            SetPixel(display_handler, i, 15, 3)
            SetPixel(display_handler, 64 - i, 47, 3)

        for i in range(1, 32):
            SetPixel(display_handler, 47, i, 3)
            SetPixel(display_handler, 15, 64 - i, 3)

        snake.row = 6
        snake.col = 42
        snake.direction = 3

    elif current_level == 5:
        for i in range(17, 46):
            SetPixel(display_handler, i, 15, 3)
            SetPixel(display_handler, i, 47, 3)

        for i in range(17, 46):
            SetPixel(display_handler, 15, i, 3)
            SetPixel(display_handler, 47, i, 3)

        snake.row = 31
        snake.col = 42
        snake.direction = 1

    elif current_level == 6:
        for i in range(1, 63):
            if i > 37 or i < 24:
                SetPixel(display_handler, i, 7, 3)
                SetPixel(display_handler, i, 15, 3)
                SetPixel(display_handler, i, 23, 3)
                SetPixel(display_handler, i, 31, 3)
                SetPixel(display_handler, i, 39, 3)
                SetPixel(display_handler, i, 47, 3)
                SetPixel(display_handler, i, 55, 3)

        snake.row = 6
        snake.col = 42
        snake.direction = 2

    elif current_level == 7:
        for i in range(1, 63, 2):
            SetPixel(display_handler, i, 31, 3)

        snake.row = 6
        snake.col = 47
        snake.direction = 2

    elif current_level == 8:
        for i in range(1, 48):
            SetPixel(display_handler, i, 7, 3)
            SetPixel(display_handler, 64-i, 15, 3)
            SetPixel(display_handler, i, 23, 3)
            SetPixel(display_handler, 64-i, 31, 3)
            SetPixel(display_handler, i, 39, 3)
            SetPixel(display_handler, 64-i, 47, 3)
            SetPixel(display_handler, i, 55, 3)

        snake.row = 6
        snake.col = 51
        snake.direction = 2

    elif current_level == 9:
        for i in range(3, 45):
            SetPixel(display_handler, i+16, i, 3)
            SetPixel(display_handler, i, i+16, 3)

        snake.row = 39
        snake.col = 59
        snake.direction = 1

    else:
        for i in range(1, 63, 2):
            SetPixel(display_handler, i, 7, 3)
            SetPixel(display_handler, i+1, 15, 3)
            SetPixel(display_handler, i, 23, 3)
            SetPixel(display_handler, i+1, 31, 3)
            SetPixel(display_handler, i, 39, 3)
            SetPixel(display_handler, i+1, 47, 3)
            SetPixel(display_handler, i, 55, 3)

        snake.row = 6
        snake.col = 51
        snake.direction = 2

def PlayGame(display_handler, input_handler, speed, increase_speed):
    """
    Main function for game play
    """
    snake_body = [SnakeBody() for i in range(MAXSNAKELENGTH)]
    snake = SnakeInfo()

    snake.lives = 5
    snake.score = 0
    snake.scolor = 1

    Level(display_handler, START_OVER, snake)

    start_row = snake.row
    start_col = snake.col

    cur_speed = speed

    SpacePause(display_handler, input_handler, "Level " + str(current_level))

    exit_now = False
    game_over = False
    while snake.lives > 0 and not exit_now:
        # need to add food to the display
        no_food = True
        # score multiplier
        number = 1 

        player_died = False

        while not player_died and not exit_now and not input_handler.stop_event.is_set():
            if no_food:
                while no_food:
                    food_row = random.randint(1, 63)
                    food_col = random.randint(1, 63)

                    if not PointIsThere(food_row, food_col, 4):
                        no_food = False

                SetPixel(display_handler, food_row, food_col, 8)

            # Snake speed adjustment
            time.sleep(cur_speed * 0.0005)

            axis_y = input_handler.axis_state('rz')
            axis_x = input_handler.axis_state('z')
            pause = input_handler.button_state('b')
            exit_now = input_handler.button_state('start')

            if axis_x is not None and axis_y is not None:
                # Use the joystick
                if axis_y < -0.5 and abs(axis_y) > abs(axis_x):   # up
                    if snake.direction != 2:
                        snake.direction = 1
                elif axis_y > 0.5 and abs(axis_y) > abs(axis_x):  # down
                    if snake.direction != 1:
                        snake.direction = 2
                elif axis_x < -0.5 and abs(axis_x) > abs(axis_y): # left
                    if snake.direction != 4:
                        snake.direction = 3
                elif axis_x > 0.5 and abs(axis_x) > abs(axis_y):  # right
                    if snake.direction != 3:
                        snake.direction = 4
                elif pause:
                    SpacePause(display_handler, input_handler, "Paused")

            else:
                # Fallback to normal inputs
                input_event = input_handler.get_input_event()
                if input_event == "up":
                    if snake.direction != 2:
                        snake.direction = 1
                elif input_event == "down":
                    if snake.direction != 1:
                        snake.direction = 2
                elif input_event == "left":
                    if snake.direction != 4:
                        snake.direction = 3
                elif input_event == "right":
                    if snake.direction != 3:
                        snake.direction = 4
                elif input_event == "pause":
                    SpacePause(display_handler, input_handler, "Paused")

            # Move Snake
            if snake.direction == 1:
                snake.row -= 1
            elif snake.direction == 2:
                snake.row += 1
            elif snake.direction == 3:
                snake.col -= 1
            elif snake.direction == 4:
                snake.col += 1

            # Eat the food
            if food_row == snake.row and food_col == snake.col:
                SetPixel(display_handler, food_row, food_col, 4)
                if snake.length < (MAXSNAKELENGTH - 30):
                    snake.length += number * 4

                snake.score += number

                number += 1
                if number == 10:
                    EraseSnake(display_handler, snake, snake_body)
                    Level(display_handler, NEXT_LEVEL, snake)
                    SpacePause(display_handler, input_handler, "Level " + str(current_level))
                    number = 1
                    if increase_speed:
                        speed = speed - 10
                        cur_speed = speed
                no_food = True
                if cur_speed < 1:
                    cur_speed = 1

            # Check for obstacles
            if PointIsThere(snake.row, snake.col, 4):
                SetPixel(display_handler, food_row, food_col, 4)
               
                player_died = True
                snake.alive = False
                snake.lives -= 1

            # Otherwise, move the snake, and erase the tail
            else:
                snake.head = (snake.head + 1) % MAXSNAKELENGTH
                snake_body[snake.head].row = snake.row
                snake_body[snake.head].col = snake.col
                tail = (snake.head + MAXSNAKELENGTH - snake.length) % MAXSNAKELENGTH
                SetPixel(display_handler, snake_body[tail].row, snake_body[tail].col, 4)
                snake_body[tail].row = -1
                SetPixel(display_handler, snake.row, snake.col, snake.scolor)

        # player died: reset speed and erase snake
        cur_speed = speed
        EraseSnake(display_handler, snake, snake_body)

        if not snake.alive:
            snake.score -= 10
            SpacePause(display_handler, input_handler, "You Died")

        Level(display_handler, SAME_LEVEL, snake)

def PointIsThere(row, col, acolor):
    """
    Check for an obstacle point different from acolor
    """
    if row >= 0:
        return arena[row][col] != acolor
    else:
        return False

def SetPixel(display_handler, row, col, acolor):
    """
    Set a pixel on the display
    """
    if row >= 0:
        display_handler.SetPixel(col, row, acolor)
        arena[row][col] = acolor

def SpacePause(display_handler, input_handler, short_text):
    """
    Pause and wait for user input to continue
    """
    input_handler.get_input_event()

    display_handler.Rect(1, 26, 62, 35, 4)
    display_handler.DrawText(6, (64-len(short_text)*6)/2, 34, short_text, 6)

    input_event = input_handler.get_input_event()

    while not input_handler.button_state('a') and not input_event:
        input_event = input_handler.get_input_event()
        if input_handler.stop_event.wait(0.1):
            break

    while input_handler.button_state('a') and not input_event:
        if input_handler.stop_event.wait(0.01):
            break

    # Restore the screen background
    for i in range(26, 36):
        for j in range(64):
            SetPixel(display_handler, i, j, arena[i][j])

def StillWantsToPlay(display_handler, input_handler):
    """
    On game over, ask the user if they still want to play.
    """
    input_handler.get_input_event()

    if input_handler.button_state('start'):
        return False

    short_text = "Game Over"
    display_handler.Rect(1, 26, 62, 35, 4)
    display_handler.DrawText(6, (64-len(short_text)*6)/2, 34, short_text, 6)

    input_event = input_handler.get_input_event()

    while not input_handler.button_state('a') and not input_handler.button_state('b') and not input_handler.button_state('start') and not input_event:
        input_event = input_handler.get_input_event()
        if input_handler.stop_event.wait(0.1):
            break

    if input_handler.button_state('a') or input_event == "select":
        selection = True
    else:
        display_handler.Clear()
        selection = False

    while (input_handler.button_state('a') or input_handler.button_state('b') or input_handler.button_state('start')) and not input_handler.stop_event.is_set():
        if input_handler.stop_event.wait(0.1):
            break

    return selection

class DisplayHandler(object):
    """
    Wrapper for the LED display
    """
    def __init__(self, matrix, font_6_9):
        self.matrix = matrix
        self.font_6_9 = font_6_9

    def Rect(self, x1, y1, x2, y2, acolor):
        drawColor = graphics.Color(ledColors[acolor-1][0], ledColors[acolor-1][1], ledColors[acolor-1][2])
        for y in range(y1, y2+1):
            graphics.DrawLine(self.matrix, x1, y, x2, y, drawColor)

    def DrawText(self, size, x, y, text, acolor):
        textColor = graphics.Color(ledColors[acolor-1][0], ledColors[acolor-1][1], ledColors[acolor-1][2])
        if size == 6:
            graphics.DrawText(self.matrix, self.font_6_9, x, y, textColor, text)

    def Clear(self):
        self.matrix.Clear()

    def SetPixel(self, x, y, acolor):
        self.matrix.SetPixel(x, y, ledColors[acolor-1][0], ledColors[acolor-1][1], ledColors[acolor-1][2])

class InputHandler(object):
    """
    Wrapper for the input device
    """
    def __init__(self, stop_event):
        self.stop_event = stop_event
        self.button_states = {}
        self.axis_states = {}
        self.last_input_event = None
        self.button_state_lock = threading.Lock()
        self.axis_state_lock = threading.Lock()
        self.input_event_lock = threading.Lock()

    def on_input_event(self, input_event):
        with self.input_event_lock:
            self.last_input_event = input_event
        return True

    def on_joystick_press(self, button, button_states):
        with self.button_state_lock:
            self.button_states = button_states
        return True

    def on_joystick_release(self, button, button_states):
        with self.button_state_lock:
            self.button_states = button_states
        return True

    def on_joystick_axis(self, axis_states):
        with self.axis_state_lock:
            self.axis_states = axis_states
        return True

    def button_state(self, button):
        with self.button_state_lock:
            return self.button_states.get(button)

    def axis_state(self, axis):
        with self.axis_state_lock:
            return self.axis_states.get(axis)

    def get_input_event(self):
        with self.input_event_lock:
            input_event = self.last_input_event
            self.last_input_event = None
            return input_event

class SnakeGame(AppBase):
    """
    Snake/Nibbles-like game, optimized for playing on a 64x64 LED display.
    """
    def __init__(self, *args, **kwargs):
        super(SnakeGame, self).__init__(*args, **kwargs)
        self.input_handler = None

    def on_input_event(self, input_event):
        if self.input_handler is not None:
            return self.input_handler.on_input_event(input_event)
        return False

    def on_joystick_press(self, button, button_states):
        if self.input_handler is not None:
            return self.input_handler.on_joystick_press(button, button_states)
        return False

    def on_joystick_release(self, button, button_states):
        if self.input_handler is not None:
            return self.input_handler.on_joystick_release(button, button_states)
        return False

    def on_joystick_axis(self, axis_states):
        if self.input_handler is not None:
            return self.input_handler.on_joystick_axis(axis_states)
        return False

    def run(self):
        font_6_9 = self.load_font("6x9")
        display_handler = DisplayHandler(self.matrix, font_6_9)
        display_handler.Clear()
        self.input_handler = InputHandler(self.stop_event)

        speed = float(self.app_config.get("speed", 100))
        increase_speed = self.app_config.get("increaseSpeed", False)

        try:
            continue_playing = True
            while continue_playing and not self.stop_event.is_set():
                PlayGame(display_handler, self.input_handler, speed, increase_speed)
                continue_playing = StillWantsToPlay(display_handler, self.input_handler)

        except Exception as err:
            print("Exception: %s" % err)

