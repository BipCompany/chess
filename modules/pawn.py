from modules.piece import Piece
from modules.constants import WHITE, BLACK


class Pawn(Piece):
    def __init__(self, field, color) -> None:
        super().__init__(field, color)
        self.char = "p"
        self.first_move = True

    def can_move(self, row, col) -> tuple[bool, str]:
        turn_condition = self.color == self.field.turn
        if not turn_condition:
            turn_word = "white's" if self.field.turn == WHITE else "black's"
            return (False, "It's " + turn_word + " turn")

        in_bounds_condition = 0 <= row <= 7 and 0 <= col <= 7
        if not in_bounds_condition:
            return (False, "Incorrect move")

        not_friendly_condition = (
            not self.board[row][col] or self.board[row][col].get_color() != self.color
        )
        if not not_friendly_condition:
            return (False, "Can't take your own pieces")

        move_delta = abs(self.row - row) + abs(self.col - col)
        move_delta_x = abs(self.row - row)
        move_delta_condition = (
            move_delta == 1 or self.first_move and move_delta == move_delta_x == 2
        ) and self.board[row][col] is None
        take_condition = (
            move_delta == 2 and move_delta_x == 1 and self.board[row][col] is not None
        )
        en_passant_condition = (
            self.field.en_passant_target is not None
            and (row, col) == self.field.en_passant_target
            and abs(self.col - col) == 1
            and abs(self.row - row) == 1
            and (
                (self.color == WHITE and self.row - row == 1)
                or (self.color == BLACK and row - self.row == 1)
            )
            and self.board[self.row][col] is not None
            and self.board[self.row][col].get_color() != self.color
        )
        if not move_delta_condition and not take_condition and not en_passant_condition:
            return (False, "Incorrect move")

        return (True, "")

    def move(self, row, col) -> tuple[bool, str]:
        can_move, message = self.can_move(row, col)
        if can_move:
            # En passant capture — captured piece is on same row, destination column
            if (
                self.field.en_passant_target is not None
                and (row, col) == self.field.en_passant_target
            ):
                self.field.capture_piece(self.row, col)
                self.board[self.row][self.col] = None
                self.row = row
                self.col = col
                self.board[row][col] = self
                self.first_move = False
                return (True, "")

            # Regular move
            old_row = self.row
            self.board[self.row][self.col] = None
            self.row = row
            self.col = col
            if self.board[row][col]:
                self.field.capture_piece(row, col)
            self.board[row][col] = self

            # Set en passant target on double advance
            if self.first_move and abs(old_row - row) == 2:
                self.field.en_passant_target = ((old_row + row) // 2, col)

            self.first_move = False
            return (True, "")
        return (False, message)
