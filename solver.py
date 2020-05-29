import threading
from typing import List, Optional, Callable, Tuple

class Solver(threading.Thread):
    """
    Class for solving a sudoku board (sub class of threading.Thread)
        Init parameters:
            board (list) - 9 by 9 matrix containg numbers between 0 and 9, 0 for a blank tile.
            separate (bool) - Optional bool, controls whether the given board is copied or linked to the passed list.
            update_function (callable) - Optional callable, is called once per loop of the solver, the update function must take the current position and board (in that order) as arguments.
            no_of_solutions (int) - Optional int, defines the number of solutions for the solver to generate, defaults to 1. The solver will terminate when it reaches this number.
    """

    def __init__(self, board:List[List[int]], separate:Optional[bool]=True, update_function:Optional[Callable]=None, no_of_solutions:Optional[int]=1):

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

    def __is_valid(self, pos:Tuple[int, int], value:int):
        """Validates the current board setup."""
        for x in range(9):
            for y in range(9):
                # If the tile being checked is in a position where it needs to be checked, and isnt the same as pos
                if (x // 3 == pos[0] // 3 and y // 3 == pos[1] // 3) or (x == pos[0] or y == pos[1]) and ([x, y] != pos):
                    if self.__board[x][y] == value:
                        return False
        return True

    def update(self, position:Tuple[int, int], board:List[List[int]]):
        """
        This is a placeholder update function, this is called for each tile attempt, and could be used to update another window or print to the console.
        This can be overridden by subclassing if desireable.
        """
        if self.__update_function != None:
            self.__update_function(position, board)

    def solve(self):
        """Begins the solving process, no_of_solutions is the number of solutions found before the solver stops."""
        # This is split off into another function in order to allow the aborting of this
        try:
            self.__solve(self.no_of_solutions)
        except RuntimeError as error:
            #print(error)
            pass

    def __solve(self, no_of_solutions:Optional[int]=1, start_pos:Optional[Tuple[int, int]]=[0, 0]):
        """
        Backtracking algorithm for solving the sudoku board passed when initialised\n
        Once function is complete, the results can be found in the solver.solutions list\n
        no_of_solutions can be set to restrict the number of solutions to be found by the algorithm.
        """

        # If the stop even it not present, proceed with the next step
        if not self.stop_event.is_set():

            self.update(start_pos, self.__board)

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
        """Abort the solver"""
        self.stop_event.set()

    def run(self):
        """Start the solver"""
        self.solve()
