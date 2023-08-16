import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import pyautogui as pg
from time import sleep
import cv2
import os


class SudokuSolver:
    def __init__(self):
        self.initialize_graph_and_adjacency_list()
        self.initialize_positions_and_colors()
        self.initialize_sudoku_board()

    def initialize_graph_and_adjacency_list(self):
        self.G = nx.sudoku_graph(3)
        self.adjacency_list = {
            node: list(nodes_dict.keys()) for node, nodes_dict in self.G.adjacency()
        }

    def initialize_positions_and_colors(self):
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

    def initialize_sudoku_board(self):
        self.sudoku_board = np.array(
            [
                [0, 0, 0, 0, 0, 5, 2, 9, 0],
                [0, 8, 9, 0, 2, 0, 0, 3, 0],
                [0, 6, 0, 0, 0, 0, 0, 0, 0],
                [0, 2, 3, 0, 5, 0, 0, 8, 0],
                [0, 0, 0, 4, 0, 0, 0, 0, 7],
                [1, 0, 0, 0, 0, 0, 0, 0, 0],
                [6, 0, 0, 0, 9, 0, 0, 0, 0],
                [5, 0, 0, 0, 0, 0, 0, 1, 0],
                [0, 9, 1, 0, 0, 7, 0, 0, 8],
            ]
        )

    def __map_colors(self, board):
        # przypisujemy wierzchołkowi kolor w zależności od wartości w planszy sudoku, dla wartości 0 kolorem oznaczającym "niepokolorowany" wierzchołek jest whitesmoke
        i = 0
        for row in board:
            for node in row:
                self.node_colors[i] = list(self.color_dict.keys())[node]
                i += 1

    def __backtracking_coloring(self):
        """Koloruje graf wykorzystując backtracking"""

        num_nodes = len(self.adjacency_list)

        # sprawdza, czy można przypisać kolor do wierzchołka, zwraca true jeżeli żaden z sąsiadów wierzchołka nie ma przypisanego danego koloru
        def is_valid(node, color):
            for neighbor in self.adjacency_list[node]:
                if self.node_colors[neighbor] == color:
                    return False
            return True

        # rekurencyjnie próbuje przypisać kolory wszystkim wierzchołkom, jeżeli się to uda zwraca true
        def backtrack(node):
            if node == num_nodes:
                return True

            # jeżeli wierzchołek ma już przypisany kolor, to kolorujemy następny wierzchołek
            if self.node_colors[node] != "whitesmoke":
                return backtrack(node + 1)

            # jeżeli nie ma przypisanego koloru próbujemy go przypisać z listy dostępnych kolorów
            for color in list(self.color_dict.keys())[1:10]:
                if is_valid(node, color):
                    self.node_colors[node] = color

                    # jeżeli udało się przypisać kolor to kolorujemy następny wierzchołek
                    if backtrack(node + 1):
                        return True

                    # jeżeli nie udało się przypisać koloru do następnych wierzchołków to cofamy się i próbujemy innych kolorów
                    self.node_colors[node] = "whitesmoke"

            # jeżeli nie udało się przypisać żadnego koloru do danego wierzchołka to zwracamy false
            return False

        # funkcja backtrack zaczyna od pierwszego tj. "zerowego" wierzchołka
        backtrack(0)

    def __map_solution_from_colors(self):
        """Ustala kolory wierzchołków na podstawie cyfr wpisanych w nierozwiązane sudoku"""
        solved_board = []

        for color in self.node_colors:
            solved_board.append(self.color_dict[color])

        return np.array(solved_board).reshape((9, 9))

    def load_board(self, path):
        board = cv2.imread(path)
        board_gray = cv2.cvtColor(board, cv2.COLOR_BGR2GRAY)
        return board_gray

    def detect_cells(self, cropped_board):
        n = 3

        BOARD_WIDTH = cropped_board.shape[1]
        BOARD_HEIGHT = cropped_board.shape[0]

        cell_size = BOARD_HEIGHT // 9

        cell_images = []
        y_start = 0
        x_start = 0

        y_end = BOARD_HEIGHT // 9
        x_end = BOARD_WIDTH // 9

        _, binary_board_img = cv2.threshold(
            cropped_board, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        cv2.line(binary_board_img, (0, 0), (0, BOARD_HEIGHT), (255, 255, 255), 20)
        cv2.line(
            binary_board_img,
            (BOARD_WIDTH, 0),
            (BOARD_WIDTH, BOARD_HEIGHT),
            (255, 255, 255),
            20,
        )
        cv2.line(
            binary_board_img,
            (0, BOARD_HEIGHT),
            (BOARD_WIDTH, BOARD_HEIGHT),
            (255, 255, 255),
            20,
        )
        cv2.line(binary_board_img, (0, 0), (BOARD_WIDTH, 0), (255, 255, 255), 20)

        line_coord_x = BOARD_WIDTH // 3
        line_coord_y = BOARD_HEIGHT // 3

        cv2.line(
            binary_board_img,
            (0, line_coord_y),
            (BOARD_WIDTH, line_coord_y),
            (255, 255, 255),
            20,
        )
        cv2.line(
            binary_board_img,
            (0, line_coord_y * 2),
            (BOARD_WIDTH, line_coord_y * 2),
            (255, 255, 255),
            20,
        )

        cv2.line(
            binary_board_img,
            (line_coord_x, 0),
            (line_coord_x, BOARD_HEIGHT),
            (255, 255, 255),
            20,
        )
        cv2.line(
            binary_board_img,
            (line_coord_x * 2, 0),
            (line_coord_x * 2, BOARD_HEIGHT),
            (255, 255, 255),
            20,
        )

        for i in range(1, 3 * 3 + 1):
            for j in range(1, 3 * 3 + 1):
                cell_images.append(
                    np.invert(binary_board_img[y_start:y_end, x_start:x_end])
                )
                x_start += cell_size
                x_end += cell_size

            x_start = 0
            x_end = cell_size

            y_start += cell_size
            y_end += cell_size

        return cell_images

    def process_board(self, board):
        board_copy = board.copy()

        ret, thresh_value = cv2.threshold(board_copy, 180, 255, cv2.THRESH_BINARY_INV)

        kernel = np.ones((5, 5), np.uint8)
        dilated_value = cv2.dilate(thresh_value, kernel, iterations=1)

        contours, hierarchy = cv2.findContours(
            dilated_value, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
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

        return cv2.resize(cropped_board, (252, 252))

    def solve(self, board):
        if isinstance(board, np.ndarray):
            proccessed_board = board

        else:
            board_image = self.__load_board(board)
            proccessed_board = self.__process_board(board_image)

        self.__map_colors(board)
        self.__backtracking_coloring()

        return self.__map_solution_from_colors()

    def automate_sudokucom(self, solution):
        """Symuluje klawiaturę w celu wpisywania rozwiazania na sudoku.com"""
        for i in range(4):
            print(f"Start in {3 - i}")
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
