from modules.piece import Piece
from modules.constants import WHITE, BLACK


class Queen(Piece):
    def __init__(self, field, color) -> None:
        super().__init__(field, color)
        self.char = 'q'

    def can_move(self, row, col) -> tuple[bool, str]:
        turn_condition = self.color == self.field.turn
        in_bounds_condition = 0 <= row <= 7 and 0 <= col <= 7
        not_friendly_condition = (
                not self.board[row][col] or
                self.board[row][col].get_color() != self.color
            )
        # Queen moves like rook (straight) or bishop (diagonal)
        straight_condition = self.row == row or self.col == col
        diagonal_condition = abs(self.row - row) == abs(self.col - col)
        move_condition = straight_condition or diagonal_condition
        if self.row == row and self.col == col:
            move_condition = False

        if not turn_condition:
            turn_word = "white's" if self.field.turn == WHITE else "black's"
            return (False, "It's " + turn_word + " turn")
        if not in_bounds_condition or not move_condition:
            return (False, "Incorrect move")
        if not not_friendly_condition:
            return (False, "Can't take your own pieces")

        # Line-of-sight check — no pieces between source and destination
        if self.row == row:
            # Horizontal move
            step = 1 if col > self.col else -1
            for c in range(self.col + step, col, step):
                if self.board[row][c] is not None:
                    return (False, "Can't jump over pieces")
        elif self.col == col:
            # Vertical move
            step = 1 if row > self.row else -1
            for r in range(self.row + step, row, step):
                if self.board[r][col] is not None:
                    return (False, "Can't jump over pieces")
        else:
            # Diagonal move
            row_step = 1 if row > self.row else -1
            col_step = 1 if col > self.col else -1
            r = self.row + row_step
            c = self.col + col_step
            while r != row and c != col:
                if self.board[r][c] is not None:
                    return (False, "Can't jump over pieces")
                r += row_step
                c += col_step

        return (True, "")
