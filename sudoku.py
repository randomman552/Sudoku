#!/usr/bin/python3.7
import pygame
import random
import time

class game(object):
    """Object represents the entire game.\n
    tile_size arguments changes the size of the tiles. (size in px).\n
    All color arguments should be passed tuple in form (R,G,B).\n
    tile_color sets the color of the tiles.\n
    background_color sets the background color of the window.\n
    boundary_color sets the color of the boundary between the tileGroups."""

    def __init__(self, tile_size, tile_color, active_tile_color, background_color, boundary_color):
        pygame.init()
        pygame.font.init()
        self.__tile_size = tile_size
        self.__windowSize = (tile_size * 9, tile_size * 9)
        self.__window = pygame.display.set_mode(self.__windowSize)
        self.__tile_color = tile_color
        self.__active_tile_color = active_tile_color
        self.__active_tile = [0,0]
        #TODO: There must be a way to improve these key bindings?
        self.__key_bindings = {
            pygame.KMOD_LSHIFT: {
                pygame.K_TAB: lambda: self.__move_active([-1,0])
            },
            pygame.KMOD_RSHIFT: {
                pygame.K_TAB: lambda: self.__move_active([-1,0])
            },
            pygame.KMOD_NUM + pygame.KMOD_LSHIFT: {
                pygame.K_TAB: lambda: self.__move_active([-1,0])
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
                pygame.K_UP: lambda: self.__move_active([0,-1]),
                pygame.K_DOWN: lambda: self.__move_active([0,1]),
                pygame.K_LEFT: lambda: self.__move_active([-1,0]),
                pygame.K_RIGHT: lambda: self.__move_active([1,0]),
                pygame.K_w: lambda: self.__move_active([0,-1]),
                pygame.K_s: lambda: self.__move_active([0,1]),
                pygame.K_a: lambda: self.__move_active([-1,0]),
                pygame.K_d: lambda: self.__move_active([1,0]),
                pygame.K_TAB: lambda: self.__move_active([1,0]),
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
            },
        }
        # Create 9 tile groups
        # The font object for the tiles must be declared out here so that it is not duplicated a huge number of times (improves run time)
        self.__font = pygame.font.Font("freesansbold.ttf", tile_size // 2)
        self.__board = [
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0]
        ]
        self.__base_board = [
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0]

        ]
        # Set color attributes.
        self.__background_color = background_color
        self.__boundary_color = boundary_color
        pygame.display.set_caption("Sudoku")

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
            #For each coordinate on the board
            for x in range(0,9):
                for y in range(0,9):
                    #Assign varaibles for this tile
                    tile_size = self.__tile_size - 2
                    tile_position = [x * self.__tile_size + 1, y * self.__tile_size + 1]
                    tile_color = self.__tile_color
                    tile_value = self.__board[x][y]
                    #If this tile is active, draw a red boundary around it.
                    if [x,y] == self.__active_tile:
                        active_tile_color = self.__active_tile_color
                        pygame.draw.rect(self.__window, active_tile_color, (tile_position[0], tile_position[1], tile_size, tile_size))
                        pygame.draw.rect(self.__window, tile_color, (tile_position[0] + 2, tile_position[1] + 2, tile_size - 4, tile_size - 4))
                    else:
                        pygame.draw.rect(self.__window, tile_color, (tile_position[0], tile_position[1], tile_size, tile_size))
                    
                    #If the tile value is not 0, draw text on the tile
                    if tile_value != 0:
                        #Generate an inverted color of the text based on the tile color
                        text_color = (255 - tile_color[0], 255 - tile_color[1], 255 - tile_color[1])
                        #Create text object and draw it on the screen
                        text = self.__font.render(str(tile_value), True, text_color, tile_color)
                        text_rect = text.get_rect()
                        text_rect.center = (tile_position[0] + (tile_size // 2), tile_position[1] + (tile_size // 2))
                        self.__window.blit(text, text_rect)
        # Call functions
        self.__window.fill(self.__background_color)
        draw_boundaries()
        draw_tiles()
        pygame.display.update()

    def __mouseHandler(self):
        """Handle mouse actions."""
        pass
    
    def __move_active(self, vector):
        """Moves the active tile by the given vector."""
        new_active = [self.__active_tile[0] + vector[0], self.__active_tile[1] + vector[1]]
        #If the current active tile is off the left or right of the screen, wrap back to the other side.
        if new_active[0] == 9:
            new_active = [0, new_active[1] + 1]
        elif new_active[0] == -1:
            new_active = [8, new_active[1] - 1]
        #If the new_active is within the acceptable bounds, update the current active tile.
        if new_active[0] < 9 and new_active[1] < 9 and new_active[0] >= 0 and new_active[1] >= 0:
            self.__active_tile = new_active
    
    def __set_active(self, value):
        """Will set the active tile to the passed value, if it passes the __is_valid method."""
        if self.__is_valid(self.__active_tile, value):
            self.__board[self.__active_tile[0]][self.__active_tile[1]] = value

    def __is_valid(self, pos, value):
        """Validates the current board setup."""
        for x in range(9):
            for y in range(9):
                if value > 0:
                    #If the tile being checked is in a position where it needs to be checked, and isnt the same as pos
                    if (x // 3 == pos[0] // 3 and y // 3 == pos[1] // 3) or (x == pos[0] or y == pos[1]) and ([x, y] != pos):
                        if self.__board[x][y] == value:
                            return False
        return True
    
    def __keyHandler(self):
        """Handle key presses."""
        key_states = pygame.key.get_pressed()
        mod_state = pygame.key.get_mods()
        #Go though the mods in the key_bindings dict.
        for mod in self.__key_bindings:
            #Check if a mod is active and process the associated dict (this uses bitwise & operator)
            #Keybindings that are under KMOD_NONE are always checked, regardless of the mod_state
            if mod_state == mod or mod == 0:
                for binds in self.__key_bindings[mod]:
                    execute = True
                    #If the bind in the dict is a tuple (has multiple rules), check all rules in the tuple.
                    if isinstance(binds, tuple):
                        #Check all keys for a bind rule.
                        for bind in binds:
                            if not(key_states[bind]):
                                execute = False
                                break
                    else:
                        if not(key_states[binds]):
                            execute = False
                    
                    #If the key_state for all keys in a bind are true, execute the associated function.
                    if execute:
                        self.__key_bindings[mod][binds]()
                        #Show the users change immedietly.
                        self.__draw()
                        #Wait for 150 ms to prevent registering the same keypress multiple times.
                        pygame.time.delay(150)
                        #Break to prevent different bindings using the same key(s) from triggering.
                        break
                break

    def __check_win(self):
        """Check whether all of the tiles have a value, if they do then the game is complete.\n
        When win conditions are all present, returns True, else returns False."""
        # Cycle through all tiles, when all are set or locked, the game is complete
        return False
    
    def __generate_puzzle(self):
        """Generates a starting puzzle for the board (and verifies that it is possible and only has one solution)."""
        pass
    
    # Public methods

    def open(self):
        "Open main event loop."
        self.__running = True
        mouseDown, keyDown = False, False
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
            self.__draw()
            if self.__check_win():
                # Carry out win action
                pass
            #print("Time taken: " + str(end - strt))
        pygame.quit()
        quit()

    def close(self):
        "Close the game window"
        self.__running = False


class solver(object):
    """Class for solving a sudoku board.\n
    Board attribute should be a 9x9 matrix containing numbers between 1 and 9, or None if that tile is blank."""

    def __init__(self, board):
        # Board attribute used to store current state of the board, base board is used for comparisons.
        self.__board = []
        for row in board:
            self.__board.append(row[:])
        self.__baseBoard = []
        for row in self.__board:
            self.__baseBoard.append(row[:])
        self.solutions = []

    def __is_valid(self, pos, value):
        """Validates the current board setup."""
        for x in range(9):
            for y in range(9):
                #If the tile being checked is in a position where it needs to be checked, and isnt the same as pos
                if (x // 3 == pos[0] // 3 and y // 3 == pos[1] // 3) or (x == pos[0] or y == pos[1]) and ([x, y] != pos):
                    if self.__board[x][y] == value:
                        return False
        return True
    
    def update(self):
        """This is a placeholder update function, this is called for each tile attempt, and could be used to update another window or print to the console.\n
        This should be overwritten if this is desirable."""
        pass

    def solve(self, more_than_one=False, start_pos=[0,0]):
        """Backtracking algorithm for solving the sudoku board passed when initialised\n
        Once function is complete, the results can be found in the solver.solutions list\n
        If more_than_one is set to True, all solutions for the given board will be found. If it is false, then an exception will be raised if a second solution is found."""
        #Iterate over the coords in the board.
        self.update()
        for x in range(start_pos[0], len(self.__board)):
            #Reset start_pos x to 0 to prevent any missed tiles.
            start_pos[0] = 0
            for y in range(start_pos[1], len(self.__board)):
                start_pos[1] = 0
                if self.__baseBoard[x][y] == 0 and self.__board[x][y] == 0:
                    #Iterate of the numbers which could be inserted, when a valid one is found, insert it and call this function recursively.
                    for num in range(1,10):
                        if self.__is_valid([x, y], num):
                            self.__board[x][y] = num
                            self.solve(more_than_one, [x,y])
                            self.__board[x][y] = self.__baseBoard[x][y]
                    #If none of the above numbers have been valid, return back to the previous step.
                    return
        if len(self.solutions) >= 1 and not(more_than_one):
            raise Exception("More than one solution is possible!")
        else:
            solution = []
            for row in self.__board:
                solution.append(row.copy())
            self.solutions.append(solution)

if __name__ == "__main__":
    game = game(60, (255, 255, 255), (255,0,0), (128, 128, 128), (0, 0, 0))
    game.open()
    """board = [
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0]
    ]
    solver = solver(board)
    solver.solve()
    print(len(solver.solutions))"""
