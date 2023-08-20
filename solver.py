import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import pyautogui as pg
from time import sleep
import cv2
import os


class SudokuSolver:
    def __init__(self, model):
        self.__initialize_graph_and_adjacency_list()
        self.__initialize_positions_and_colors()
        self.model = model

    def __initialize_graph_and_adjacency_list(self):
        """Initialize the Sudoku graph and it's adjacency list"""
        self.G = nx.sudoku_graph(3)
        self.adjacency_list = {
            node: list(nodes_dict.keys()) for node, nodes_dict in self.G.adjacency()
        }

    def __initialize_positions_and_colors(self):
        """Initialize positions and colors for nodes in the graph, whitesmoke = uncolored"""
        self.pos = dict(zip(list(self.G.nodes()), nx.grid_2d_graph(9, 9)))
        self.node_colors = ["whitesmoke"] * len(self.adjacency_list)
        self.color_dict = {
            "whitesmoke": 0,
            "red": 1,
            "green": 2,
            "blue": 3,
            "yellow": 4,
            "orange": 5,
            "purple": 6,
            "pink": 7,
            "brown": 8,
            "gray": 9,
        }

    def __map_colors(self, board):
        """Map colors to graph nodes based on Sudoku board values"""
        i = 0
        for row in board:
            for node in row:
                self.node_colors[i] = list(self.color_dict.keys())[node]
                i += 1

    def __backtracking_coloring(self):
        """Backtracking-based graph coloring algorithm"""

        num_nodes = len(self.adjacency_list)

        def is_valid(node, color):
            for neighbor in self.adjacency_list[node]:
                if self.node_colors[neighbor] == color:
                    return False
            return True

        def backtrack(node):
            if node == num_nodes:
                return True

            if self.node_colors[node] != "whitesmoke":
                return backtrack(node + 1)

            for color in list(self.color_dict.keys())[1:10]:
                if is_valid(node, color):
                    self.node_colors[node] = color

                    if backtrack(node + 1):
                        return True

                    self.node_colors[node] = "whitesmoke"

            return False

        backtrack(0)

    def __map_solution_from_colors(self):
        """Map node colors back to numbers to obtain the Sudoku solution"""
        solved_board = []

        for color in self.node_colors:
            solved_board.append(self.color_dict[color])

        return np.array(solved_board).reshape((9, 9))

    def load_board(self, path):
        """Load the Sudoku board from an image file"""
        board = cv2.imread(path)
        proc = cv2.GaussianBlur(board.copy(), (9, 9), 0)
        proc = cv2.cvtColor(proc, cv2.COLOR_BGR2GRAY)
        proc = cv2.adaptiveThreshold(
            proc, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        proc = cv2.bitwise_not(proc, proc)

        return self.__process_board(proc)

    def __process_board(self, board):
        """Process the loaded board image"""
        board_copy = board.copy()

        contours, hierarchy = cv2.findContours(
            board_copy, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )
        largest_area = 0
        largest_contour = None

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > largest_area:
                largest_area = area
                largest_contour = cnt

        if largest_contour is not None:
            x, y, w, h = cv2.boundingRect(largest_contour)
            cropped_board = board_copy[y : y + h, x : x + w]

        cropped_board = cropped_board[5:-5, 5:-5]
        resized_board = cv2.resize(cropped_board, (450, 450))

        board_size = 450
        cell_size = board_size // 9

        for i in range(1, 9):
            x = i * cell_size
            cv2.line(resized_board, (x, 0), (x, board_size), (0, 0, 0), 8)

        for i in range(1, 9):
            y = i * cell_size
            cv2.line(resized_board, (0, y), (board_size, y), (0, 0, 0), 8)

        grid = np.zeros([9, 9])
        for i in range(9):
            for j in range(9):
                image = resized_board[i * 50 : (i + 1) * 50, j * 50 : (j + 1) * 50]
                if image.sum() > 25000:
                    grid[i][j] = self.__predict_number(image)
                else:
                    grid[i][j] = 0
        grid = grid.astype(int)

        return grid

    def __predict_number(self, image):
        """Predict a number from an image using a CNN model"""
        image_resized = cv2.resize(image, (28, 28))
        image_reshaped = image_resized.reshape(1, 28, 28, 1)
        pred = self.model.predict(image_reshaped, verbose=0)

        return pred[0].tolist().index(max(pred[0]))

    def solve(self, board):
        """Solve the Sudoku puzzle using graph coloring and backtracking"""
        loaded_board = board

        self.__map_colors(loaded_board)
        self.__backtracking_coloring()

        return self.__map_solution_from_colors()

    def automate_sudokucom(self, solution):
        """Simulate keyboard input to fill the solution on sudoku.com"""
        for i in range(4):
            # print(f"Start in {3 - i}")
            sleep(1)

        for id, row in enumerate(solution):
            if id % 2 == 0:
                for cell in row:
                    pg.press(f"{cell}")
                    pg.press("right")

            elif id % 2 == 1:
                for cell in reversed(row):
                    pg.press(f"{cell}")
                    pg.press("left")

            pg.press("down")
