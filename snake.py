import numpy as np
import board
import neopixel
import time
import gpiozero
import random
import RPi.GPIO as GPIO
from operator import add


# Some useful definitions
timing = False # print timing information out as we run

#Configure GPIO
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP) #right
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)#left

# p1 directions
p1l_pressed = 0
p1r_pressed = 0

# And setup some interrupts on these pins
def p1l(channel):
    global p1l_pressed
    global p1r_pressed
    if p1l_pressed:
        return
    if p1r_pressed:
        p1r_pressed = 0
    p1l_pressed = 1
    return


def p1r(channel):
    global p1r_pressed
    global p1l_pressed
    if p1r_pressed:
        return
    if p1l_pressed:
        p1l_pressed = 0
    p1r_pressed = 1
    return



GPIO.add_event_detect(17, GPIO.FALLING, callback=p1l, bouncetime=300)
GPIO.add_event_detect(27, GPIO.FALLING, callback=p1r, bouncetime=300)


# Define some pixels to write to.
pixels = neopixel.NeoPixel(board.D18, 256, auto_write=False)





class snake():
    '''
    Class to hold salient information about a snake
    '''
    def __init__(self, length, position, colour, player_ix):
        self.length = length
        self.player_ix = player_ix
        self.position = position #position of head
        self.colour = colour
        self.locs = []
        self.alive = True
        self.direction = (1,0) # start in positive x direction
        self.left = 0
        self.right = 0
        for loc in range(0,length):
            # List of snake locations
            self.locs.append([position[0] - loc, position[1]])
    
    def move(self):
        '''
        Move the snake by one unit in a given direction
        '''
        if timing:
            move_start_time = time.time()
        if not self.check_valid_move(self.direction):
            # If requested move is invalid, ignore it
            if timing:
                print(f"TIMING: move (invalid return) {time.time() - move_start_time}")
            return
        print(f'New Direction = {self.direction}')
        print(f'old locs = {self.locs}')
        self.locs.insert(0, list(map(add, self.locs[0], list(self.direction))))
        print(f'New locs = {self.locs}')
        if len(self.locs) > self.length:
            self.locs.pop() #remove last element of list

        # check we haven't left the playable area
        if not self.snake_in_scope():
            self.alive = False
        if timing:
            print(f'TIMING: move {time.time() - move_start_time}s')

    def new_direction(self, left, right):
        '''
        Points the snake in a new direction
        '''
        # Make sure we can cancel any other pending moves:
        if self.player_ix == 1:
            global p1l_pressed, p1r_pressed
            p1l_pressed = 0
            p1r_pressed = 0
        print(f'Direction = {self.direction}, left = {left}, right = {right}')
        if left and right:
            # can't move all directions at once
            print('Cannot move all directions at once')
            return
        if not (left | right):
            # nothing to do
            print('Continuing in a straight line')
            return
        if self.direction == (1,0):
            if left:
                self.direction = (0,1)
                return
            if right:
                self.direction = (0,-1)
                return
        if self.direction == (0,1):
            if left:
                self.direction = (-1,0)
                return
            if right:
                self.direction = (1,0)
                return
        if self.direction == (-1,0):
            if left:
                self.direction = (0,-1)
                return
            if right:
                self.direction = (0,1)
                return
        if self.direction == (0,-1):
            if left:
                self.direction = (1,0)
                return
            if right:
                self.direction = (-1,0)
                return
        print('Something has gone properly wrong here...')


    def check_valid_move(self, direction):
        '''
        Checks whether a move is valid for a given snake
        '''
        # Check that single direction given
        if abs(direction[0]) == abs(direction[1]):
            return False

        if (abs(direction[0]) > 1) or (abs(direction[1]) > 1):
            return False

        new_head_pos = self.position + direction
        if new_head_pos in self.locs:
            # Check if the new head position will overlap with the body
            #kill the snake
            self.alive = False
            return False
        return True

    def snake_in_scope(self):
        '''
        Check whether the snake has left playable area
        '''
        if self.locs[0][0] < 0:
            return False
        elif self.locs[0][0] > 31:
            return False
        elif self.locs[0][1] < 0:
            return False
        elif self.locs[0][1] > 7:
            return False
        else:
            return True

    def change_len(self, amount):
        self.length += amount

    def to_canvas(self):
        '''
        Return a boolean canvas with the current snake on
        '''
        if timing:
            to_canvas_start_time = time.time()
        canvas = np.zeros([32, 8], dtype=np.bool_)
        for segment in self.locs:
            canvas[segment[0]][segment[1]] = True
        if timing:
            print(f'TIMING: to_canvas {time.time() - to_canvas_start_time}s')
        return canvas


class treat():
    types = ['longer', 'shorter', 'reverse']
    def __init__():
        self.seed = random.seed(a=None)
        self.new()
        return

    def new():
        # select a type
        self.current_type = random.choice(self.types)
        self.get_colour()

    def get_colour():
        # select a colour
        if self.current_type == 'longer':
            self.colour = (255,0,0)
        elif self.current_type == 'shorter':
            self.colour = (0,255,0)
        elif self.current_type == 'reverse':
            self.colour = (0,0,255)
        else:
            raise NameError(f'Unknown treat type {self.current_type}.')


def xy2ix(x, y):
    '''
    Covert an x-y coordinate to a location in pixel space
    '''
    x = 31 - x
    base = x * 8
    if x%2:
        ix = base + y
    else:
        ix = base + 7 - y
    return ix


def array2lin(array):
    '''
    Takes a 2-d numpy array, and returns a 1-d numpy array
    '''
    if timing:
        array2lin_start_time = time.time()
    output_array = np.zeros((32*8, 1), dtype=(np.uint8, 3))
    for x in range(0,32):
        for y in range(0,8):
            output_array[xy2ix(x, y)] = array[x][y]
            #print(array[x][y])
    if timing:
        print(f'TIMING: array2lin {time.time() - array2lin_start_time}s')
    #print(output_array)
    return output_array


def overlay(canvas, image):
    '''
    Overlays an overlay onto a camnvas.
    '''
    return trim_maxima(canvas + image)


def trim_maxima(array):
    '''
    Checks that no values are greater than 255. Clips where necessary
    '''
    if timing:
        trim_maxima_start_time = time.time()
    for x in range(0,32):
        for y in range(0,8):
            for colour in range(0,3):
                if array[x][y][colour] > 255:
                    array[x][y][colour] = 255
    if timing:
        print(f'TIMING: trim_maxima {time.time() - trima_maxima_start_time}s')
    return array


def colourmod(array, colour):
    '''
    Take an array containing raw values and converts it to tuples of the specified colour
    '''

    if timing:
        colourmod_start_time = time.time()
    output_array = np.zeros([32, 8], dtype=(np.uint8,3))
    for x in range(0,32):
        for y in range(0,8):
            if array[x][y]:
                output_array[x][y] = colour
                #print(output_array[x][y])
                
    for x in range(0, 32):
        for y in range(0, 8):
            for z in range (0, 3):
                if output_array[x][y][z] == -1:
                    output_array[x][y][z] = 255
    if timing:
        print(f'TIMING: colourmod {time.time() - colourmod_start_time}s')
    #print(output_array)
    return output_array


def write_to_pixels(array, pixels_object):
    '''
    It would be great if we could do this without the loop.
    '''
    # TODO: remove the loop requirement
    if timing:
        write_to_pixels_start_time = time.time()
    count = 0
    for item in array:
        #print(item)
        pixels_object[count] = tuple(item[0])
        count += 1
    pixels_object.show()
    if timing:
        print(f'TIMING: write_to_pixels {time.time() - write_to_pixels_start_time}s')

def get_new_dir_p1():
    '''
    read the input signals for the requested player, and return the corresponding tuple of (L,R)
    '''
    return (p1l_pressed, p1r_pressed)


def new_snake():
    return snake(4, (8, 4), (255,255,255), 1)



if __name__ == '__main__':
    my_snake = new_snake()
    current_dir = (1,0)
    iter_count = 1 # use this to add random treats
    while(1):
        mainloop_start_time = time.time()

        # Evaluate any treats
        if not iter_count%30:
            # change treats every 30 seconds
            treat = treat.new()
            iter_count = 1

        # Get any control signal:
        new_dir = get_new_dir_p1() # player 1
        # Send the snake in the new direction
        my_snake.new_direction(new_dir[0], new_dir[1])
        my_snake.move()



        #check if snake still alive
        if not my_snake.alive:
            break #TODO: something better for when a snake dies
        
        #draw this on canvas
        bool_canvas = my_snake.to_canvas()
        canvas = colourmod(bool_canvas, (100,100,100))

        # convert the canvas into something that can be written
        lin = array2lin(canvas)

        # and write it
        write_to_pixels(lin, pixels)

        # Make sure we don't run too fast. Maybe 4fps is a playable speed?
        while ((time.time() - mainloop_start_time) < 0.25):
            None

