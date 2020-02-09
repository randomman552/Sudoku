import pygame

class tile(object):
    "Class to represent a sudoku tile."
    def __init__(self, value, position, tileSize, MinMax = (0, 10)):
        self.value = value
        self.__position = position
        self.__size = tileSize
        self.__MinMax = MinMax

    def click(self, button):
        """Handle the click action on this tile.\n
        Can be passed 1, 2, or 3. Each corresponds to one of the mouse buttons."""
        pass

    def draw(self):
        "Draw the tile on screen."
        pass

    def change(self, change_to):
        "Changes the value this tile holds if it is within the acceptable range."
        if change_to < self.__MinMax[1] and change_to >= self.__MinMax[0]:
            self.value = change_to

class tileGroup(object):
    "Class to represent the groups of 9 tiles in sudoku."
    def __init__(self, position, tileSize):
        self.position = position
        self.tiles = [tile(None, (x + 1,y + 1), tileSize) for x in range(position[0], 3 * tileSize, tileSize) for y in range(position[1], 3 * tileSize, tileSize)]
        self.__tileSize = tileSize

    def draw(self):
        "Draw all tiles from this tilegroup on the display."
        pass

class game(object):
    def __init__(self, tileSize):
        "Size attribute sets the maximum size of the game window."
        pygame.init()
        pygame.font.init()
        self.__tileSize = tileSize
        self.__windowSize = (tileSize * 9, tileSize * 9)
        self.__window = pygame.display.set_mode(self.__windowSize)
        pygame.display.set_caption("Sudoku")
    
    def open(self):
        "Open main event loop."
        self.__running = True
        mouseDown, keyDown = False, False
        while self.__running:
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
            pygame.display.update()
        pygame.quit()
        quit()

    def close(self):
        "Close the game window"
        self.__running = False

if __name__ == "__main__":
    game = game(50)
    game.open()