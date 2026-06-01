from modules.piece import Piece
from modules.constants import WHITE, BLACK


class Knight(Piece):
    def __init__(self, field, color) -> None:
        super().__init__(field, color)
        self.char = "k"
        self.first_move = True

    def can_move(self, row, col) -> tuple[bool, str]:
        turn_condition = self.color == self.field.turn
        in_bounds_condition = 0 <= row <= 7 and 0 <= col <= 7
        not_friendly_condition = (
            not self.board[row][col] or self.board[row][col].get_color() != self.color
        )
        move_delta = abs(self.row - row) + abs(self.col - col)
        move_delta_condition = move_delta == 3

        if not turn_condition:
            turn_word = "white's" if self.field.turn == WHITE else "black's"
            return (False, "It's " + turn_word + " turn")
        if not in_bounds_condition or not move_delta_condition:
            return (False, "Incorrect move")
        if not not_friendly_condition:
            return (False, "Can't take your own pieces")

        return (True, "")
