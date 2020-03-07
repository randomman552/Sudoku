from sudoku import solver
import random
import time
from io import StringIO
import json

def generate_puzzle(difficulty_scalar, seed):
    """Generates a random puzzle. Difficultyy scalar defines how many clues are present in the puzzle (not exact number but rough guide)."""
    def is_valid(board, pos, value):
        """Validates the current board setup."""
        # Check all tiles in the same group, row, and collumn as the tile in the given position
        for x in range(9):
            for y in range(9):
                if value > 0:
                    # If the tile being checked is in a position where it needs to be checked, and isnt the same as pos
                    if (x // 3 == pos[0] // 3 and y // 3 == pos[1] // 3) or (x == pos[0] or y == pos[1]) and ([x, y] != pos):
                        if board[x][y] == value:
                            return False
        return True

    def inital_random():
        """Randomly allocate values to a random row, this then causes the rest of the generated solution to change.
        Function retrusn the board variable (list of 9 rows of the sudoku board)."""
        board = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
        y = random.randint(0, 8)
        for x in range(0, 9):
            while True:
                value = random.randint(1, 9)
                if is_valid(board, [x, y], value):
                    board[x][y] = value
                    break
        a = solver(board)
        a.solve()
        return a.solutions[0]

    def remove_tiles(board, difficulty_scalar):
        """This function removes tiles randomly from the board in order to produce a partially filled board with the minimum number of required clues.\n
        Difficulty scalar is a number between 0 and 1, 0 would mean that all of the clues are present on the board (already complete) whereas 1 would try to remove as many as possible.\n
        Harder puzzles do take longer to generate as it requies more passes."""
        unvisited = []
        for x in range(0, 9):
            for y in range(0, 9):
                unvisited.append([x, y])
        # Scale the minimum_unvisited to the difficulty scalar to control how many numbers may be removed from the board.
        #This value is floored to 17, as there are no boards with unique solutions with fewer than 17 clues
        minimum_unvisited = 17 + (64 * (1 - difficulty_scalar))
        while len(unvisited) > minimum_unvisited:
            random_num = random.randint(0, len(unvisited) - 1)
            pos = unvisited.pop(random_num)
            value_removed = board[pos[0]][pos[1]]
            board[pos[0]][pos[1]] = 0
            a = solver(board)
            a.solve(2)
            if len(a.solutions) > 1:
                board[pos[0]][pos[1]] = value_removed

    def blender(board):
        """This mixes the columns and rows randomly in order to make the board look more random."""
        def blend_rows():
            # Iterate over each band of 3 rows
            for x in range(0, 9, 3):
                # Iterate over the 3 rows in the band.
                for row_num in range(x, x+3):
                    # Select a random row from the band
                    random_row = random.randint(x, x+2)
                    # Switch the specified rows
                    board[row_num], board[random_row] = board[random_row], board[row_num]

        def blend_columns():
            # Iterate over each band of 3 columns
            for y in range(0, 9, 3):
                # Iterate over the 3 columns in the band.
                for column_num in range(y, y+3):
                    # Select a random colu n from the band
                    random_column = random.randint(y, y+2)
                    # Switch the specified columns
                    for row_num in range(0, 9):
                        board[row_num][column_num], board[row_num][random_column] = board[
                            row_num][random_column], board[row_num][column_num]

        blend_rows()
        blend_columns()

    # Set the seed, allowing for the same board to be genereated again with the same seed.
    random.seed(seed)
    board = inital_random()
    blender(board)
    remove_tiles(board, difficulty_scalar)
    return board

if __name__ == "__main__":
    puzzles = dict()
    difficulty_maping = {
        "easy": 0.5,
        "medium": 0.75,
        "hard": 1,
    }
    for i in range(100):
        print(i)
        for difficulty_str in ["easy", "medium", "hard"]:
            puzzle = generate_puzzle(difficulty_maping[difficulty_str], i)
            if difficulty_str in puzzles:
                puzzles[difficulty_str].append(puzzle)
            else:
                puzzles[difficulty_str] = []
                puzzles[difficulty_str].append(puzzle)
    
    with open("puzzles.json", "w") as file:
        json.dump(puzzles, file, indent=4)
