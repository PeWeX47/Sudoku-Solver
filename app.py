import curses
import numpy as np
from solver import SudokuSolver
import tensorflow as tf
import keras
import os

# menu options
menu = [
    "Solve the sudoku from image",
    "Enter sudoku manually",
    "Credits",
    "Exit",
]
exit_menu = ["Yes", "No"]
ASCII_LOGO = r"""
   \\t_____           _       _               _____       _                              ___  
  / ____|         | |     | |             / ____|     | |                            |__ \ 
 | (___  _   _  __| | ___ | | ___   _    | (___   ___ | |_   _____ _ __      __   __    ) |
  \___ \| | | |/ _` |/ _ \| |/ / | | |    \___ \ / _ \| \ \ / / _ \ '__|     \ \ / /   / / 
  ____) | |_| | (_| | (_) |   <| |_| |    ____) | (_) | |\ V /  __/ |     _   \ V /   / /_ 
 |_____/ \__,_|\__,_|\___/|_|\_\\__,_|   |_____/ \___/|_| \_/ \___|_|    (_)   \_/   |____|                                               
"""


def print_menu(stdscr, selected_row_idx):
    """Displays the main menu"""
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    logo_lines = ASCII_LOGO.replace("\\t", "  ").strip().split("\n")
    logo_height = len(logo_lines)
    logo_width = max(len(line) for line in logo_lines)
    logo_x = w // 2 - logo_width // 2

    for line_idx, line in enumerate(logo_lines):
        stdscr.addstr(h // 6 + line_idx, logo_x, line)

    for idx, row in enumerate(menu):
        x = w // 2 - len(row) // 2
        y = h // 2 - len(menu) // 2 + idx
        if idx == selected_row_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, row)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, row)
    stdscr.refresh()


def print_exit_menu(stdscr, selected_col_idx):
    """Displays the exit menu"""
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(h // 2 - len(exit_menu) // 2 - 2, w // 2 - 6, "Are you sure?")
    for idx, col in enumerate(exit_menu):
        x = w // 2 - len(col) // 2
        y = h // 2 - len(exit_menu) // 2 + idx
        if idx == selected_col_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, col)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, col)
    stdscr.refresh()


def print_board(stdscr, board, cursor_y, cursor_x):
    """Displays the sudoku board"""
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    start_y = h // 2 - len(board) // 2
    start_x = w // 2 - (len(board[0]) * 3) // 2

    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            if y == cursor_y and x == cursor_x:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(start_y + y, start_x + x * 3, f"{cell:^3}")
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(start_y + y, start_x + x * 3, f"{cell:^3}")

    print_keybinds(stdscr)
    stdscr.refresh()


def print_keybinds(stdscr):
    """Displays keybinds"""
    keybinds = [
        "KEY BINDS",
        "R - Reset",
        "S - Solve",
        "A - Automate",
        "Q - Go back",
    ]

    h, w = stdscr.getmaxyx()
    for y, keybind in enumerate(keybinds):
        stdscr.addstr(h // 3 + y, w - 20, keybind)


def reset_board():
    """Resets the sudoku board"""
    return np.zeros((9, 9), dtype=int).tolist()


def get_image_path(stdscr):
    """Gets board image path from user"""
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    message = "Path to board image:"
    stdscr.addstr(h // 3, w // 2 - len(message), message)

    curses.echo()
    image_path = stdscr.getstr(h // 3 + 1, w // 2 - len(message), curses.COLS - 1)
    curses.noecho()

    stdscr.refresh()
    return image_path.decode("utf-8")


def main(stdscr):
    """Runs the sudoku solver"""
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # Initialize variables for menu navigation and board interaction
    current_row = 0
    current_col = 0
    options_selected = False
    cursor_y = 0
    cursor_x = 0
    model = keras.models.load_model(r"model\CNN_MNIST.h5")
    solver = SudokuSolver(model)
    initial_board = reset_board()

    print_menu(stdscr, current_row)

    # Main loop
    while True:
        if not options_selected:
            key = stdscr.getch()

            if key == curses.KEY_UP and current_row > 0 and not options_selected:
                current_row -= 1

            elif (
                key == curses.KEY_DOWN
                and current_row < len(menu) - 1
                and not options_selected
            ):
                current_row += 1

        if key == curses.KEY_ENTER or key in [10, 13] or options_selected:
            options_selected = True

            if current_row == len(menu) - 1:
                print_exit_menu(stdscr, current_col)
                key = stdscr.getch()

                if key == curses.KEY_UP and current_col > 0:
                    current_col -= 1

                elif key == curses.KEY_DOWN and current_col < len(exit_menu) - 1:
                    current_col += 1

                elif key == curses.KEY_ENTER or key in [10, 13]:
                    if current_col == 0:
                        break

                    else:
                        options_selected = False
                        current_row = 0
                        current_col = 0

            elif current_row == len(menu) - 3:
                print_board(stdscr, initial_board, cursor_y, cursor_x)
                key = stdscr.getch()
                if key == ord("q"):
                    options_selected = False
                    initial_board = reset_board()
                    current_row = 0
                    current_col = 0

                elif key == ord("r"):
                    initial_board = reset_board()

                elif key == ord("s"):
                    initial_board = solver.solve(initial_board)

                elif key == ord("a"):
                    solver.automate_sudokucom(initial_board)

                elif key == curses.KEY_DOWN and cursor_y < len(initial_board) - 1:
                    cursor_y += 1
                elif key == curses.KEY_UP and cursor_y > 0:
                    cursor_y -= 1
                elif key == curses.KEY_RIGHT and cursor_x < len(initial_board[0]) - 1:
                    cursor_x += 1
                elif key == curses.KEY_LEFT and cursor_x > 0:
                    cursor_x -= 1
                elif key >= 48 and key <= 57:
                    initial_board[cursor_y][cursor_x] = int(chr(key))

            elif current_row == len(menu) - 4:
                image_path = get_image_path(stdscr)
                if os.path.exists(image_path):
                    initial_board = solver.load_board(image_path)
                    current_row = len(menu) - 3

                elif image_path == "q":
                    options_selected = False
                    initial_board = reset_board()
                    current_row = 0
                    current_col = 0

            elif current_row == len(menu) - 2:
                options_selected = False

        if not options_selected:
            print_menu(stdscr, current_row)


if __name__ == "__main__":
    curses.wrapper(main)
