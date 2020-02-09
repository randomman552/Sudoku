import pygame

class tile(object):
    "Class to represent a sudoku tile."
    def __init__(self, value, position, tileSize, tileColor, window, MinMax = (0, 10)):
        self.value = value
        self.__position = position
        self.__size = tileSize
        self.__color = tileColor
        self.__MinMax = MinMax
        self.__window = window

    def click(self, state):
        """Handle the click action on this tile.\n
        Is passed mouse button states."""
        if state[0]:
            self.__color = (0,0,0)
        elif state[1]:
            self.__color = (255,255,255)
        elif state[2]:
            self.__color = (128,128,128)

    def draw(self):
        "Draw the tile on screen."
        pygame.draw.rect(self.__window, self.__color, (self.__position[0] + 1, self.__position[1] + 1, self.__size - 2, self.__size - 2))

    def change(self, change_to):
        "Changes the value this tile holds if it is within the acceptable range."
        if change_to < self.__MinMax[1] and change_to >= self.__MinMax[0]:
            self.value = change_to

class tileGroup(object):
    "Class to represent the groups of 9 tiles in sudoku."
    def __init__(self, position, tileSize, tileColor, window):
        self.position = position
        #Create the tiles for this tileGroup as specified by position
        self.tiles = [tile(None, (x + 1,y + 1), tileSize - 2, tileColor, window) for x in range(position[0], position[0] +  3 * tileSize, tileSize) for y in range(position[1], position[1] + 3 * tileSize, tileSize)]
        self.__tileSize = tileSize
    
    def click(self, state, position):
        """Carry out the click action on the required tile"""
        def gettile(position):
            "Get the tilegroup at the current position"
            x = int(position[0] / (self.__tileSize))
            y = int(position[1] / (self.__tileSize))
            return self.tiles[y + x * 3]
        #Normalise position for use within this tile
        position = (position[0] - self.position[0], position[1] - self.position[1])
        gettile(position).click(state)

    def draw(self):
        "Draw all tiles from this tilegroup on the display."
        for tile in self.tiles:
            tile.draw()

class game(object):
    """Object represents the entire game.\n
    tileSize arguments changes the size of the tiles. (size in px).\n
    All color arguments should be passed tuple in form (R,G,B).\n
    tileColor sets the color of the tiles.\n
    bgColor sets the background color of the window.\n
    boundaryColor sets the color of the boundary between the tileGroups."""
    def __init__(self, tileSize, tileColor, bgColor, boundaryColor):
        pygame.init()
        pygame.font.init()
        self.__tileSize = tileSize
        self.__windowSize = (tileSize * 9, tileSize * 9)
        self.__window = pygame.display.set_mode(self.__windowSize)
        #Create 9 tile groups
        self.__tileGroups = [tileGroup((x, y), tileSize, tileColor, self.__window) for x in range(0, tileSize * 9, tileSize * 3) for y in range(0, tileSize * 9, tileSize * 3)]
        #Set color attributes.
        self.__bgColor = bgColor
        self.__boundaryColor = boundaryColor
        pygame.display.set_caption("Sudoku")
    
    def __draw(self):
        """Draw everything on the window."""
        #Define draw subfunctions.
        def draw_tileGroups():
            """Call the draw methods of all of the tileGroups."""
            for tileGroup in self.__tileGroups:
                tileGroup.draw()
        def draw_boundaries():
            """Draw the boundaries between the tileGroups."""
            #Draw boundaries along the board
            for x in range(self.__tileSize * 3, self.__tileSize * 9 - 1, self.__tileSize * 3):
                pygame.draw.rect(self.__window, self.__boundaryColor, (x-2, 0, 4, self.__windowSize[1]))
            #Draw boundaries down the board
            for y in range(self.__tileSize * 3, self.__tileSize * 9 - 1, self.__tileSize * 3):
                pygame.draw.rect(self.__window, self.__boundaryColor, (0, y - 2, self.__windowSize[0], 4))
        
        #Call functions
        self.__window.fill(self.__bgColor)
        draw_tileGroups()
        draw_boundaries()
        pygame.display.update()

    def __mouseHandler(self):
        """Handle mouse actions."""
        def gettileGroup(position):
            "Get the tilegroup at the current position"
            x = int(position[0] / (self.__tileSize * 3))
            y = int(position[1] / (self.__tileSize * 3))
            return self.__tileGroups[y + (x * 3)]
        
        state = pygame.mouse.get_pressed()
        position = pygame.mouse.get_pos()
        gettileGroup(position).click(state, position)
    
    def __keyHandler(self):
        """Handle key presses."""
        pass
    
    def open(self):
        "Open main event loop."
        self.__running = True
        mouseDown, keyDown = False, False
        while self.__running:
            #Event handler
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
            
            #If mouseDown or keyDown are true, call their respective functions.
            if mouseDown:
                self.__mouseHandler()
            if keyDown:
                self.__keyHandler()
            self.__draw()
        pygame.quit()
        quit()

    def close(self):
        "Close the game window"
        self.__running = False

if __name__ == "__main__":
    game = game(50, (255,255,255), (128,128,128), (0,0,0))
    game.open()