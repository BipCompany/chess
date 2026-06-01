from modules.field import Field
import os
from modules.constants import WHITE, BLACK


def draw_board(board) -> None:
    print("    a    b    c    d    e    f    g    h")
    for i in range(8):
        print("  " + "+----" * 8 + "+")
        print(i + 1, end=" ")
        for j in range(8):
            piece_char = "  " if not board[i][j] else board[i][j].get_char()
            print("| " + piece_char + " ", end="")
        print("|")
    print("  " + "+----" * 8 + "+")


def clear_terminal() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def main():
    field = Field()
    field.start_position()
    message = ""
    game_over = False
    while True:
        clear_terminal()
        draw_board(field.get_board())
        print(message)
        if game_over:
            break
        turn = input("White's turn\n" if field.turn == WHITE else "Black's turn\n")
        try:
            cell1, cell2 = turn.split()
        except ValueError:
            message = "Invalid input — expected two squares (e.g. e2 e4)"
            continue
        cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
        try:
            col1 = cols[cell1[0]]
            row1 = int(cell1[1]) - 1
            col2 = cols[cell2[0]]
            row2 = int(cell2[1]) - 1
        except (KeyError, IndexError, ValueError):
            message = "Invalid square — use format like e2 e4"
            continue
        result = field.move_piece(row1, col1, row2, col2)
        if result.startswith("Checkmate!") or result == "Stalemate!":
            game_over = True
        message = result


if __name__ == "__main__":
    main()
