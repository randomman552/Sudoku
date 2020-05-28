from solver import Solver
import random
import json
from multiprocessing import Pool
import shlex
import argparse
import string
import os

from typing import Any

#Location the puzzles are stored
puzzle_store = "puzzles.json"

def get_random_string(length: int) -> str:
    """Function generates a random string and returns it."""
    result = "".join([random.choice(string.ascii_letters +
                                    string.digits) for i in range(length)])
    return result


def generate_puzzle(seed: Any) -> dict:
    """Generate a dict of boards (one for each difficulty)"""

    def _generate(difficulty_scalar: float, seed: Any):
        """Generate a puzzle of a given difficulty"""
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
            a = Solver(board)
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
            # This value is floored to 17, as there are no boards with unique solutions with fewer than 17 clues
            minimum_unvisited = 17 + (64 * (1 - difficulty_scalar))
            while len(unvisited) > minimum_unvisited:
                random_num = random.randint(0, len(unvisited) - 1)
                pos = unvisited.pop(random_num)
                value_removed = board[pos[0]][pos[1]]
                board[pos[0]][pos[1]] = 0
                a = Solver(board, no_of_solutions=2)
                a.solve()
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

    difficulty_mapping = {
        "easy": 0.5,
        "medium": 0.75,
        "hard": 1,
    }

    output = {}
    for difficulty in difficulty_mapping:
        output[difficulty] = _generate(difficulty_mapping[difficulty], seed)
    return output

def load_boards() -> dict:
    """
    Load the puzzles from file.
    If the file doesn't exist, an empty dict will be returned.
    """

    puzzles = dict()
    try:
        with open(puzzle_store, "r") as file:
            puzzles = json.load(file)
    except FileNotFoundError:
        pass
    return puzzles

def save_boards(boards) -> None:
    """Save the given boards to the puzzle storage location."""
    with open(puzzle_store, "w") as file:
        json.dump(boards, file, indent=4)

def main():
    # Create the generate arg parser
    gen_parser = argparse.ArgumentParser(
        "gen", description="Generate a new sudoku board")
    gen_parser.add_argument("number", default=1,
                            help="The number of puzzles to generate", type=int)

    # Create the exit and help arg parsers
    exit_parser = argparse.ArgumentParser(
        "exit", description="Exit the generator")
    help_parser = argparse.ArgumentParser(
        "help", description="List the commands")

    # Create dict of parser for printing help message
    parser_dict = {
        gen_parser.prog: gen_parser,
        exit_parser.prog: exit_parser,
        help_parser.prog: help_parser
    }

    # Create a multiprocessing pool object to generate boards on separate processes
    pool = Pool()

    # Load existing puzzles
    puzzles = load_boards()

    running = True
    print("--==Sudoku Puzzle Generator==--")
    print("Enter help for list of commands.")
    while running:
        command = input("> ")
        command = shlex.split(command)

        try:
            if command[0] == "help":
                print(f"gen - {gen_parser.description}")
                print(f"help - {help_parser.description}")
                print(f"exit - {exit_parser.description}")
                print("Enter a command followed by -h for help.")
            elif command[0] == "exit":
                running = False
            elif command[0] == "gen":
                # Extract the namespace from the parser
                namespace = parser_dict[command[0]].parse_args(command[1:])

                results = []
                print(f"Generating {namespace.number} boards...")
                # Create a number of boards equal to the number requested
                for _ in range(namespace.number):
                    seed = get_random_string(10)

                    result_obj = pool.apply_async(generate_puzzle, (seed,))

                    results.append((seed, result_obj))

                # Collect the results from the results object dict, continue until we have all of them
                got_all = False
                while not got_all:
                    for result in results:
                        got_all = True
                        try:
                            #If the seed is not already present in the puzzles
                            if result[0] not in puzzles:
                                puzzles[result[0]] = result[1].get(0.25)
                                print(f"Puzzle generated with seed '{result[0]}'")
                        except:
                            #If we fail to get one of the puzzles
                            got_all = False

                save_boards(puzzles)
                print("Generation complete")

        except SystemExit:
            # Catch the system exit exception raised by argparse if it fails
            pass

    # Save our changes
    save_boards(puzzles)


if __name__ == "__main__":
    main()
