from modules.piece import Piece
from modules.constants import WHITE, BLACK


class King(Piece):
    def __init__(self, field, color) -> None:
        super().__init__(field, color)
        self.char = 'K'

    def can_move(self, row, col) -> tuple[bool, str]:
        turn_condition = self.color == self.field.turn
        in_bounds_condition = 0 <= row <= 7 and 0 <= col <= 7
        not_friendly_condition = (
                not self.board[row][col] or
                self.board[row][col].get_color() != self.color
            )
        # King moves one square in any direction
        one_step_condition = abs(self.row - row) <= 1 and abs(self.col - col) <= 1
        not_stationary = not (self.row == row and self.col == col)
        move_condition = one_step_condition and not_stationary

        if not turn_condition:
            turn_word = "white's" if self.field.turn == WHITE else "black's"
            return (False, "It's " + turn_word + " turn")
        if not in_bounds_condition or not move_condition:
            return (False, "Incorrect move")
        if not not_friendly_condition:
            return (False, "Can't take your own pieces")

        # King cannot move into a square under attack by the opponent
        if self.field.is_under_attack(row, col, self.color ^ 1):
            return (False, "Can't move into check")

        return (True, "")
