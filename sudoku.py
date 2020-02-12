#!/usr/bin/python3.7
import pygame


class tile(object):
    """Class to represent a sudoku tile."""

    def __init__(self, value, position, tileSize, tileColor, window, MinMax=(0, 10)):
        self.value = value
        self.__defaultValue = value
        self.__position = position
        self.__size = tileSize
        self.__color = tileColor
        self.__MinMax = MinMax
        self.__window = window
        self.__activeColor = (255, 0, 0)
        self.state = "normal"

    def click(self, state):
        """Handle the click action on this tile.\n
        Is passed mouse button states."""
        # state is a list that represents M1, M3, M2 (in that order, where M means mouse button)
        if state[0]:
            # If the tile has not already been set, set it as the active tile.
            if self.state != "set":
                self.state = "active"
        elif state[1]:
            pass
        elif state[2]:
            # Reset the tile to normal state, and set it to its default value
            self.state = "normal"
            self.value = self.__defaultValue

    def draw(self):
        """Draw the tile on screen."""
        def drawText():
            "This function draws the text on the tile."
            if self.state != "set":
                textColor = (
                    255 - self.__color[0] // 2, 255 - self.__color[1] // 2, 255 - self.__color[2] // 2)
            else:
                textColor = (
                    255 - self.__color[0], 255 - self.__color[1], 255 - self.__color[2])
            # Create font and draw a rectangle containing the text onto the tile.
            font = pygame.font.Font("freesansbold.ttf", self.__size // 2)
            text = font.render(str(self.value), True, textColor, self.__color)
            text_rect = text.get_rect()
            text_rect.center = (
                self.__position[0] + (self.__size // 2), self.__position[1] + (self.__size // 2))
            self.__window.blit(text, text_rect)

        # If the state is active, draw the active color rectangle first to provide an outline of the activeColor.
        if self.state == "active":
            # First draw the active color rect, then the normal color rect.
            # Uses self.__size and self.__position to calculate the correct position of the rect.
            pygame.draw.rect(self.__window, self.__activeColor, (
                self.__position[0] + 1, self.__position[1] + 1, self.__size - 2, self.__size - 2))
            pygame.draw.rect(self.__window, self.__color, (self.__position[0] + self.__size // 10, self.__position[1] +
                                                           self.__size // 10, self.__size - self.__size // 5, self.__size - self.__size // 5))
        else:
            # Otherwise draw the normal rect
            pygame.draw.rect(self.__window, self.__color, (
                self.__position[0] + 1, self.__position[1] + 1, self.__size - 2, self.__size - 2))
        # If the tile has a value, draw it on the tile as text.
        if self.value != None:
            drawText()

    def change(self, change_to):
        """Changes the value this tile holds if it is within the acceptable range."""
        # Check if in range
        if change_to < self.__MinMax[1] and change_to >= self.__MinMax[0]:
            # Change value
            self.value = change_to
        # Revert state to normal to deselect this as an active tile (currently done by main game class)
        #self.state = "normal"


class tileGroup(object):
    "Class to represent the groups of 9 tiles in sudoku (3x3 tiles)."

    def __init__(self, position, tileSize, tileColor, window):
        self.position = position
        # Create the tiles for this tileGroup as specified by position
        self.tiles = [tile(None, (x + 1, y + 1), tileSize - 2, tileColor, window) for x in range(position[0],
                                                                                                 position[0] + 3 * tileSize, tileSize) for y in range(position[1], position[1] + 3 * tileSize, tileSize)]
        self.__tileSize = tileSize

    def click(self, state, position):
        """Carry out the click action on the required tile"""
        def getTile(position):
            "Get the tilegroup at the current position"
            x = int(position[0] / (self.__tileSize))
            y = int(position[1] / (self.__tileSize))
            return self.tiles[y + x * 3]
        # Normalise position for use within this tile
        position = (position[0] - self.position[0],
                    position[1] - self.position[1])
        getTile(position).click(state)

    def draw(self):
        """Draw all tiles from this tilegroup on the display."""
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
        # Create 9 tile groups
        self.__tileGroups = [tileGroup((x, y), tileSize, tileColor, self.__window) for x in range(
            0, tileSize * 9, tileSize * 3) for y in range(0, tileSize * 9, tileSize * 3)]
        # Set color attributes.
        self.__bgColor = bgColor
        self.__boundaryColor = boundaryColor
        pygame.display.set_caption("Sudoku")

    def __draw(self):
        """Draw everything on the window."""
        # Define draw subfunctions.
        def draw_tileGroups():
            """Call the draw methods of all of the tileGroups."""
            for tileGroup in self.__tileGroups:
                tileGroup.draw()

        def draw_boundaries():
            """Draw the boundaries between the tileGroups."""
            # Draw boundaries along the board
            for x in range(self.__tileSize * 3, self.__tileSize * 9 - 1, self.__tileSize * 3):
                pygame.draw.rect(self.__window, self.__boundaryColor,
                                 (x-2, 0, 4, self.__windowSize[1]))
            # Draw boundaries down the board
            for y in range(self.__tileSize * 3, self.__tileSize * 9 - 1, self.__tileSize * 3):
                pygame.draw.rect(self.__window, self.__boundaryColor,
                                 (0, y - 2, self.__windowSize[0], 4))

        # Call functions
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
        if self.__getActiveTile() == None:
            gettileGroup(position).click(state, position)

    def __keyHandler(self):
        """Handle key presses."""
        keyStates = pygame.key.get_pressed()
        # Get the current active tile
        tile = self.__getActiveTile()
        if tile != None:
            # If the enter key was not the key that was pressed, check which number to swtich the active tile to
            if not(keyStates[pygame.K_RETURN]):
                # Check which what is to be entered into the tile
                keyList = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                           pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]
                for i in range(len(keyList)):
                    # Check each keystate from the keyList
                    if keyStates[keyList[i]]:
                        # When matching key is found, change the tile to that number and return
                        tile.change(i)
                        return
                # If an invalid kye is pressed, deselect the tile
                tile.state = "normal"
            else:
                # Submit tile if entry is valid
                if self.__validateTile(tile):
                    tile.state = "set"
        else:
            # If there is no active tile, use global key actions
            pass

    def __validateTile(self, tile):
        """Check that the tile entry is valid for all places where this tile appears."""
        if tile.value != None:
            return True
        # Return False if validation fails in any way.
        return False

    def __getActiveTile(self):
        """Returns the first tile which is active, otherwise return none."""
        for tileGroup in self.__tileGroups:
            for tile in tileGroup.tiles:
                if tile.state == "active":
                    return tile
        return None

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
        pygame.quit()
        quit()

    def close(self):
        "Close the game window"
        self.__running = False


if __name__ == "__main__":
    game = game(60, (255, 255, 255), (128, 128, 128), (0, 0, 0))
    game.open()
