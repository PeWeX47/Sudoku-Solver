import curses
import numpy as np
from solver import SudokuSolver

menu = ["Enter sudoku with a picture (WILL BE ADDED)", "Enter sudoku manually", "Exit"]
exit_menu = ["Yes", "No"]
ASCII_LOGO = r"""

   _____           _       _               _____       _                              __ 
  / ____|         | |     | |             / ____|     | |                            /_ |
 | (___  _   _  __| | ___ | | ___   _    | (___   ___ | |_   _____ _ __      __   __  | |
  \___ \| | | |/ _` |/ _ \| |/ / | | |    \___ \ / _ \| \ \ / / _ \ '__|     \ \ / /  | |
  ____) | |_| | (_| | (_) |   <| |_| |    ____) | (_) | |\ V /  __/ |     _   \ V /   | |
 |_____/ \__,_|\__,_|\___/|_|\_\\__,_|   |_____/ \___/|_| \_/ \___|_|    (_)   \_/    |_|
                                                                                         
                                                                                         
                                                   
"""


def print_menu(stdscr, selected_row_idx):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(h // 6, w // 2, ASCII_LOGO)
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

    stdscr.refresh()


def reset_board():
    return [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]


def print_center(stdscr, text):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    x = w // 2 - len(text) // 2
    y = h // 2
    stdscr.addstr(y, x, text)
    stdscr.refresh()


def main(stdscr):
    curses.curs_set(0)

    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    current_row = 0
    current_col = 0
    options_selected = False
    cursor_y = 0
    cursor_x = 0
    solver = SudokuSolver()

    initial_board = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]

    print_menu(stdscr, current_row)

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

            elif current_row == len(menu) - 2:
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
                    initial_board = solver.solve(np.array(initial_board))

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

            elif current_row == len(menu) - 3:
                options_selected = False

        if not options_selected:
            print_menu(stdscr, current_row)


curses.wrapper(main)
