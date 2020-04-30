#!/usr/bin/python3.7
import pygame
import random
import time
from tkinter import messagebox as ms_box
import tkinter as tk
import threading
import json


class game(object):
    """Object represents the entire game.\n
    tile_size arguments changes the size of the tiles. (size in px).\n
    All color arguments should be passed tuple in form (R,G,B).\n
    tile_color sets the color of the tiles.\n
    background_color sets the background color of the window.\n
    boundary_color sets the color of the boundary between the tileGroups."""

    def __init__(self, tile_size=60, tile_color=(255, 255, 255), active_color=(255, 0, 0), locked_color=(0, 0, 255), background_color=(128, 128, 128), boundary_color=(0, 0, 0)):
        # Pygame setup
        pygame.init()
        pygame.font.init()

        # Window setup
        self.__windowSize = (tile_size * 9, tile_size * 9)
        self.__window = pygame.display.set_mode(self.__windowSize)
        pygame.display.set_caption("Sudoku")
        self.__font = pygame.font.Font("freesansbold.ttf", tile_size // 2)

        # Tile setup
        self.__tile_size = tile_size
        self.__active_tile = [0, 0]

        # Threading lock
        self.__lock = threading.Lock()

        # Message display attributes
        self.__display_message = ""
        self.__message_queue = []
        self.__message_duration = 0

        # Help function
        def __display_help():
            """Function to display help information on screen."""
            self.__display_message = ""
            self.__message_duration = 0
            self.__message_queue = []
            self.flash_messages(["Arrow keys, or mouse to change tile", "Press enter to self solve",
                                 "Press r to reset the board", "Press a number to fill the current tile"], [4000, 4000, 4000, 4000])

        # TODO: There must be a way to improve these key bindings?
        self.__key_bindings = {
            pygame.KMOD_LSHIFT: {
                pygame.K_TAB: lambda: self.__move_active([0, -1])
            },
            pygame.KMOD_RSHIFT: {
                pygame.K_TAB: lambda: self.__move_active([0, -1])
            },
            pygame.KMOD_NUM + pygame.KMOD_LSHIFT: {
                pygame.K_TAB: lambda: self.__move_active([0, -1])
            },
            pygame.KMOD_NUM + pygame.KMOD_RSHIFT: {
                pygame.K_TAB: lambda: self.__move_active([0, -1])
            },
            pygame.KMOD_NUM: {
                pygame.K_KP0: lambda: self.__set_active(0),
                pygame.K_KP1: lambda: self.__set_active(1),
                pygame.K_KP2: lambda: self.__set_active(2),
                pygame.K_KP3: lambda: self.__set_active(3),
                pygame.K_KP4: lambda: self.__set_active(4),
                pygame.K_KP5: lambda: self.__set_active(5),
                pygame.K_KP6: lambda: self.__set_active(6),
                pygame.K_KP7: lambda: self.__set_active(7),
                pygame.K_KP8: lambda: self.__set_active(8),
                pygame.K_KP9: lambda: self.__set_active(9)
            },
            pygame.KMOD_NONE: {
                pygame.K_UP: lambda: self.__move_active([-1, 0]),
                pygame.K_DOWN: lambda: self.__move_active([1, 0]),
                pygame.K_LEFT: lambda: self.__move_active([0, -1]),
                pygame.K_RIGHT: lambda: self.__move_active([0, 1]),
                pygame.K_w: lambda: self.__move_active([-1, 0]),
                pygame.K_s: lambda: self.__move_active([1, 0]),
                pygame.K_a: lambda: self.__move_active([0, -1]),
                pygame.K_d: lambda: self.__move_active([0, 1]),
                pygame.K_TAB: lambda: self.__move_active([0, 1]),
                pygame.K_BACKSPACE: lambda: self.__set_active(0),
                pygame.K_DELETE: lambda: self.__set_active(0),
                pygame.K_0: lambda: self.__set_active(0),
                pygame.K_1: lambda: self.__set_active(1),
                pygame.K_2: lambda: self.__set_active(2),
                pygame.K_3: lambda: self.__set_active(3),
                pygame.K_4: lambda: self.__set_active(4),
                pygame.K_5: lambda: self.__set_active(5),
                pygame.K_6: lambda: self.__set_active(6),
                pygame.K_7: lambda: self.__set_active(7),
                pygame.K_8: lambda: self.__set_active(8),
                pygame.K_9: lambda: self.__set_active(9),
                pygame.K_ESCAPE: lambda: self.close(),
                pygame.K_r: lambda: self.__reset(),
                pygame.K_RETURN: lambda: self.solve(),
                pygame.K_F1: lambda: __display_help(),
            },
        }

        # Attribute for storing worker thread
        self.worker_thread = None

        # Set color attributes.
        self.__background_color = background_color
        self.__boundary_color = boundary_color
        self.__tile_color = tile_color
        self.__active_color = active_color
        self.__locked_color = locked_color

        # Load puzzles into memory
        self.__puzzles = dict()
        with open("puzzles.json", "r") as file:
            self.__puzzles = json.load(file)

        # Call reset method
        self.__reset()
    # Private methods

    def __draw(self):
        """Draw everything on the window."""
        # Define draw subfunctions.
        def draw_boundaries():
            """Draw the boundaries between the tileGroups."""
            # Draw boundaries along the board
            for x in range(self.__tile_size * 3, self.__tile_size * 9 - 1, self.__tile_size * 3):
                pygame.draw.rect(self.__window, self.__boundary_color,
                                 (x-2, 0, 4, self.__windowSize[1]))
            # Draw boundaries down the board
            for y in range(self.__tile_size * 3, self.__tile_size * 9 - 1, self.__tile_size * 3):
                pygame.draw.rect(self.__window, self.__boundary_color,
                                 (0, y - 2, self.__windowSize[0], 4))

        def draw_tiles():
            """Draw the tiles on the screen."""
            # For each coordinate on the board
            for x in range(0, 9):
                for y in range(0, 9):
                    # Assign varaibles for this tile
                    # X and y are flipped here so that the tiles are drawn correctly.
                    tile_size = self.__tile_size - 2
                    tile_position = [y * self.__tile_size +
                                     1, x * self.__tile_size + 1]
                    tile_color = self.__tile_color
                    tile_value = self.__board[x][y]
                    # If this tile is active, draw a red boundary around it.
                    if [x, y] == self.__active_tile:
                        if self.__base_board[x][y] == 0:
                            active_tile_color = self.__active_color
                        else:
                            active_tile_color = self.__locked_color
                        pygame.draw.rect(self.__window, active_tile_color,
                                         (tile_position[0], tile_position[1], tile_size, tile_size))
                        pygame.draw.rect(self.__window, tile_color, (
                            tile_position[0] + 2, tile_position[1] + 2, tile_size - 4, tile_size - 4))
                    else:
                        pygame.draw.rect(
                            self.__window, tile_color, (tile_position[0], tile_position[1], tile_size, tile_size))

                    # If the tile value is not 0, draw text on the tile
                    if tile_value != 0:
                        # Generate an inverted color of the text based on the tile color
                        text_color = (
                            255 - tile_color[0], 255 - tile_color[1], 255 - tile_color[1])
                        # Create text object and draw it on the screen
                        text = self.__font.render(
                            str(tile_value), True, text_color, tile_color)
                        text_rect = text.get_rect()
                        text_rect.center = (
                            tile_position[0] + (tile_size // 2), tile_position[1] + (tile_size // 2))
                        self.__window.blit(text, text_rect)

        def draw_message():
            """Draw the current display message on the screen."""
            # Check whether a new message needs to be displayed
            if len(self.__message_queue) > 0 and self.__message_duration <= 0:
                # Remove the message from the queue and add it to active variables
                message = self.__message_queue.pop(0)
                self.__message_duration = message[0]
                self.__display_message = message[1]
            # Display the message if its duration is greater than 0
            if self.__message_duration > 0:
                self.__message_duration -= 10
                text_color = (
                    255 - self.__tile_color[0], 255 - self.__tile_color[1], 255 - self.__tile_color[2])
                text = self.__font.render(
                    self.__display_message, True, text_color, self.__tile_color)
                text_rect = text.get_rect()
                text_rect.center = (
                    self.__windowSize[0] // 2, self.__windowSize[1] // 2)
                self.__window.blit(text, text_rect)

        # Call functions
        self.__window.fill(self.__background_color)
        draw_boundaries()
        draw_tiles()
        draw_message()
        pygame.display.update()

    def __mouseHandler(self):
        """Handle mouse actions."""
        mouse_preses = pygame.mouse.get_pressed()
        pos = pygame.mouse.get_pos()
        # Positions are reveresed here due to the way the tiles are drawn on screen
        tile_x = pos[1] // self.__tile_size
        tile_y = pos[0] // self.__tile_size
        if mouse_preses[0]:
            self.__move_active([tile_x, tile_y], absolute=True)

    def __move_active(self, vector, absolute=False):
        """Moves the active tile by the given vector when absolute is false.\n
        Moves the active tile TO the given vector when absolute is true."""
        if absolute:
            self.__active_tile = vector[:]
        else:
            new_active = [self.__active_tile[0] + vector[0],
                          self.__active_tile[1] + vector[1]]
            # If the current active tile is off the left or right of the screen, wrap back to the other side.
            if new_active[0] == 9:
                new_active = [0, new_active[1] + 1]
            elif new_active[0] == -1:
                new_active = [8, new_active[1] - 1]
            # If the new_active is within the acceptable bounds, update the current active tile.
            if new_active[0] < 9 and new_active[1] < 9 and new_active[0] >= 0 and new_active[1] >= 0:
                self.__active_tile = new_active

    def __set_active(self, value):
        """Will set the active tile to the passed value, if it passes the __is_valid method."""
        if self.__is_valid(self.__active_tile, value):
            self.__board[self.__active_tile[0]][self.__active_tile[1]] = value

    def __is_valid(self, pos, value):
        """Validates the current board setup."""
        # Check whether the specified tile is writable.
        if self.__base_board[pos[0]][pos[1]] != 0:
            return False
        # Check all tiles in the same group, row, and collumn as the tile in the given position
        for x in range(9):
            for y in range(9):
                if value > 0:
                    # If the tile being checked is in a position where it needs to be checked, and isnt the same as pos
                    if (x // 3 == pos[0] // 3 and y // 3 == pos[1] // 3) or (x == pos[0] or y == pos[1]) and ([x, y] != pos):
                        if self.__board[x][y] == value:
                            return False
        return True

    def __keyHandler(self):
        """Handle key presses."""
        key_states = pygame.key.get_pressed()
        mod_state = pygame.key.get_mods()
        # Go though the mods in the key_bindings dict.
        for mod in self.__key_bindings:
            # Check if a mod is active and process the associated dict (this uses bitwise & operator)
            # Keybindings that are under KMOD_NONE are always checked, regardless of the mod_state
            if mod_state == mod or mod == 0:
                for binds in self.__key_bindings[mod]:
                    execute = True
                    # If the bind in the dict is a tuple (has multiple rules), check all rules in the tuple.
                    if isinstance(binds, tuple):
                        # Check all keys for a bind rule.
                        for bind in binds:
                            if not(key_states[bind]):
                                execute = False
                                break
                    else:
                        if not(key_states[binds]):
                            execute = False

                    # If the key_state for all keys in a bind are true, execute the associated function.
                    if execute:
                        self.__key_bindings[mod][binds]()
                        # Show the users change immedietly.
                        self.__draw()
                        # Wait for 150 ms to prevent registering the same keypress multiple times.
                        pygame.time.delay(150)
                        # Break to prevent different bindings using the same key(s) from triggering.
                        break
                break

    def __load_puzzle(self, difficulty):
        """Loads a random puzzle from the puzzles.json file genereated by the puzzle generator.\n
        The puzzle is blended and rotated, so even if the same puzzle is loaded, it should look different."""
        # Copy one of the boards from the puzzles dictionary for the required difficulty
        to_copy = random.choice(self.__puzzles[difficulty])
        self.__board = []
        for row in to_copy:
            self.__board.append(row.copy())

        def blender():
            """This mixes the columns and rows randomly in order to make the board look more random."""
            def blend_rows():
                # Iterate over each band of 3 rows
                for x in range(0, 9, 3):
                    # Iterate over the 3 rows in the band.
                    for row_num in range(x, x+3):
                        # Select a random row from the band
                        random_row = random.randint(x, x+2)
                        # Switch the specified rows
                        self.__board[row_num], self.__board[random_row] = self.__board[random_row], self.__board[row_num]

            def blend_columns():
                # Iterate over each band of 3 columns
                for y in range(0, 9, 3):
                    # Iterate over the 3 columns in the band.
                    for column_num in range(y, y+3):
                        # Select a random colu n from the band
                        random_column = random.randint(y, y+2)
                        # Switch the specified columns
                        for row_num in range(0, 9):
                            self.__board[row_num][column_num], self.__board[row_num][random_column] = self.__board[
                                row_num][random_column], self.__board[row_num][column_num]

            blend_rows()
            blend_columns()

        def rotate():
            """Rotate the board a random multiple of 90 degrees."""
            for _ in range(random.randint(0, 3)):
                # Rotate board by 90 degrees
                self.__board = [*zip(*self.__board[::-1])]
                # Convert tuples back into lists
                self.__board = [list(row) for row in self.__board]

        blender()
        rotate()
        self.__base_board = []
        for row in self.__board:
            self.__base_board.append(row[:])

    def __reset(self):
        """Reset the game to its default state."""
        if self.worker_thread:
            self.worker_thread.stop()
        self.__load_puzzle("hard")
        self.worker_thread = None
        self.complete = False

    def __check_win(self):
        """Checks whether the sudoku board has been completed."""
        if self.complete:
            return False
        else:
            for row in self.__board:
                for num in row:
                    # If any of the numbers are still 0, then the board has been been completed.
                    if num == 0:
                        return False
            self.complete = True
            return True

    # Public methods
    def flash_message(self, message, delay):
        """Add message to the message queue."""
        message = (delay, message)
        self.__message_queue.append(message)

    def flash_messages(self, message_list, delay_list):
        """Adds passed messages with given delays to the message queue."""
        messages = zip(delay_list, message_list)
        self.__message_queue += messages

    def solve(self):
        def update_active(active_pos):
            """This function is used by the solver to update the active tile position, so that it is drawn on screen correctly."""
            with self.__lock:
                self.__move_active(active_pos, True)
                self.__draw()
        # Start the solver thread if one is not already running
        if not self.worker_thread:
            s = solver(self.__board, False, update_active)
            self.worker_thread = s
            self.worker_thread.start()

    def open(self):
        "Open main event loop."
        self.__running = True
        mouseDown, keyDown = False, False
        self.flash_message("Press F1 for help.", 4000)
        while self.__running:
            # Event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouseDown = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    mouseDown = False
                elif event.type == pygame.KEYDOWN:
                    keyDown = True
                elif event.type == pygame.KEYUP:
                    keyDown = False
            # If mouseDown or keyDown are true, call their respective functions.
            if mouseDown:
                self.__mouseHandler()
            if keyDown:
                self.__keyHandler()

            with self.__lock:
                self.__draw()

            if self.__check_win():
                # Carry out win action
                self.flash_message("Board Completed!", 1500)
            # print("Time taken: " + str(end - strt))
            # Delay of 10 ms to set framerate to 100fps
            pygame.time.delay(10)
        pygame.quit()
        quit()

    def close(self):
        "Close the game window"
        self.worker_thread.stop()
        self.__running = False


class solver(threading.Thread):
    """Class for solving a sudoku board.\n
    Board attribute should be a 9x9 matrix containing numbers between 1 and 9, or 0 if that tile is blank.\n
    If separate is set to True, a new copy of the board is made for this solver (to prevent editing the previous version."""

    def __init__(self, board, separate=True, update_function=None, no_of_solutions=1):

        # Initalise the Thread
        super().__init__(name="Solver")

        # If the boards are supposed to be separated from the passed lists, create copies of them
        if separate:
            self.__board = []
            for row in board:
                self.__board.append(row[:])
        else:
            self.__board = board
        self.__baseBoard = []
        for row in self.__board:
            self.__baseBoard.append(row[:])

        # List to store solutions
        self.solutions = []

        # Store the update function, this is called for each recursive step in the backtracking algorithm
        self.__update_function = update_function

        # Store the requested number of solutions
        self.no_of_solutions = no_of_solutions

        # Stop event allows this thread to be stopped before it finishes if required
        self.stop_event = threading.Event()

    def __is_valid(self, pos, value):
        """Validates the current board setup."""
        for x in range(9):
            for y in range(9):
                # If the tile being checked is in a position where it needs to be checked, and isnt the same as pos
                if (x // 3 == pos[0] // 3 and y // 3 == pos[1] // 3) or (x == pos[0] or y == pos[1]) and ([x, y] != pos):
                    if self.__board[x][y] == value:
                        return False
        return True

    def update(self, position):
        """This is a placeholder update function, this is called for each tile attempt, and could be used to update another window or print to the console.\n
        This should be overwritten if this is desirable."""
        if self.__update_function != None:
            self.__update_function(position)

    def solve(self):
        """Begins the solving process, no_of_solutions is the number of solutions found before the solver stops."""
        # This is split off into another function in order to allow the aborting of this
        try:
            self.__solve(self. no_of_solutions)
        except RuntimeError as error:
            print(error)

    def __solve(self, no_of_solutions=1, start_pos=[0, 0]):
        """
        Backtracking algorithm for solving the sudoku board passed when initialised\n
        Once function is complete, the results can be found in the solver.solutions list\n
        no_of_solutions can be set to restrict the number of solutions to be found by the algorithm.
        """

        # If the stop even it not present, proceed with the next step
        if not self.stop_event.is_set():

            self.update(start_pos)

            # Iterate over the coords in the board.
            for x in range(start_pos[0], len(self.__board)):

                # Reset start_pos x to 0 to prevent any missed tiles.
                start_pos[0] = 0
                for y in range(start_pos[1], len(self.__board)):
                    start_pos[1] = 0
                    if self.__baseBoard[x][y] == 0 and self.__board[x][y] == 0:

                        # Iterate of the numbers which could be inserted, when a valid one is found, insert it and call this function recursively.
                        for num in range(1, 10):
                            if self.__is_valid([x, y], num):
                                self.__board[x][y] = num
                                self.__solve(no_of_solutions, [x, y])
                                self.__board[x][y] = self.__baseBoard[x][y]

                        # If none of the above numbers have been valid, return back to the previous step.
                        return
            solution = []
            for row in self.__board:
                solution.append(row.copy())
            self.solutions.append(solution)
            if len(self.solutions) >= no_of_solutions:
                # An exception is raised to break out of the recurrsion.
                raise RuntimeError("Max solutions reached... Aborting...")

        # If the stop_event is set, then raise an exception to abort the execution
        else:
            raise RuntimeError("Thread aborted")

    def stop(self):
        self.stop_event.set()

    def run(self):
        self.solve()


if __name__ == "__main__":
    game = game()
    game.open()
    """board = [
        [0,0,0,8,0,0,0,5,0],
        [0,0,0,0,7,0,8,0,2],
        [1,0,0,5,0,0,6,0,0],
        [0,0,9,4,0,0,0,6,0],
        [0,7,0,9,0,1,0,4,0],
        [0,4,0,0,0,2,9,0,0],
        [0,0,5,0,0,7,0,0,6],
        [2,0,3,0,9,0,0,0,0],
        [0,8,0,0,0,6,0,0,0]
    ]
    solver = solver(board)
    solver.solve()
    for row in solver.solutions[0]:
        print(row)"""
