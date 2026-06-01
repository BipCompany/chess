from modules.constants import WHITE, BLACK


class Piece:
    """A barebones base class for any kind of piece"""

    def __init__(self, field, color) -> None:
        self.field = field
        self.board = field.board
        self.color = color
        self.char = "P"
        self.row = None
        self.col = None

    def get_color(self):
        return self.color

    def get_char(self):
        if self.color == WHITE:
            return "w" + self.char
        else:
            return "b" + self.char

    def place(self, row, col) -> bool:
        if not self.board[row][col]:
            self.row = row
            self.col = col
            self.board[row][col] = self
            return True
        return False

    def can_move(self, row, col) -> bool:
        """This method is meant to be redefined for every kind of piece based on it's rules"""
        return False

    def move(self, row, col) -> tuple[bool, str]:
        can_move, message = self.can_move(row, col)
        if can_move:
            self.board[self.row][self.col] = None
            self.row = row
            self.col = col
            if self.board[row][col]:
                self.field.capture_piece(row, col)
            self.board[row][col] = self
            return (True, "")
        return (False, message)
