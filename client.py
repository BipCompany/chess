import os
import socket
import struct
import threading
import time

from modules.constants import BLACK, WHITE
from modules.field import Field


def clear_terminal() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def format_time(seconds: int) -> str:
    """Format seconds into mm:ss string."""
    m = seconds // 60
    s = seconds % 60
    return f"{m}:{s:02d}"


class Chess:
    def __init__(self, host="127.0.0.1", port=62743):
        self.host = host
        self.port = port

        self.kill = False

        self.turn = None
        self.board = [
            ['br', 'bk', 'bb', 'bq', 'bK', 'bb', 'bk', 'br'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  '],
            ['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  '],
            ['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  '],
            ['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  '],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wr', 'wk', 'wb', 'wq', 'wK', 'wb', 'wk', 'wr']
        ]
        self.message = "Connecting..."
        self.white_time = None
        self.black_time = None
        self.history = ""
        self.captured = ""
        self.color = None
        self.moved = False
        self.game_over = False

        self.socket = None

    def draw_board(self) -> None:
        if self.color == BLACK:
            row_col_range = range(7, -1, -1)
            print("    h    g    f    e    d    c    b    a")
        else:
            row_col_range = range(8)
            print("    a    b    c    d    e    f    g    h")
        for i in row_col_range:
            print("  " + "+----" * 8 + "+")
            print(i + 1, end=" ")
            for j in row_col_range:
                piece_char = self.board[i][j]
                print("| " + piece_char + " ", end="")
            print("|")
        print("  " + "+----" * 8 + "+")

    def draw_info(self) -> None:
        """Print timer, captured pieces, and move history below the board."""
        # Timer line
        white_str = format_time(self.white_time) if self.white_time is not None else "--:--"
        black_str = format_time(self.black_time) if self.black_time is not None else "--:--"
        print(f"  White: {white_str}  |  Black: {black_str}")

        # Captured pieces
        if self.captured:
            print(f"  {self.captured}")

        # Move history — wrap if long
        if self.history:
            history_str = self.history
            # Trim to ~80 chars per line, wrap
            while len(history_str) > 0:
                line = history_str[:80]
                print(f"  {line}")
                history_str = history_str[80:]

    def deserialize(self, data):
        fmt_size = struct.calcsize("<B?Bii128s256s256s50s")
        offset = 0
        while offset + fmt_size <= len(data):
            turn, game_over, color, wt, bt, board_bytes, history_bytes, captured_bytes, message_bytes = \
                struct.unpack_from("<B?Bii128s256s256s50s", data, offset)
            self.turn = turn
            if self.turn == self.color:
                self.moved = False
            self.game_over = game_over
            self.color = color
            self.white_time = wt
            self.black_time = bt

            board_string = board_bytes.decode("utf-8")
            new_board = [["  "] * 8 for _ in range(8)]
            for row in range(8):
                for col in range(8):
                    new_board[row][col] = board_string[row * 16 + col * 2] + board_string[row * 16 + col * 2 + 1]
            self.board = new_board

            self.history = history_bytes.decode("utf-8").rstrip("\x00").strip()
            self.captured = captured_bytes.decode("utf-8").rstrip("\x00").strip()
            self.message = message_bytes.decode("utf-8").rstrip("\x00")
            offset += fmt_size

    def run_listener(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
            s.connect((self.host, self.port))
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
            s.settimeout(1)
            print("connected", s)
            self.socket = s
            while not self.kill:
                try:
                    data = self.socket.recv(4096)
                    if len(data):
                        self.deserialize(data)
                except socket.timeout:
                    pass
                except Exception:
                    break
                time.sleep(0.001)

    def run(self):
        threading.Thread(target=self.run_listener).start()
        while True:
            clear_terminal()
            self.draw_board()
            self.draw_info()
            print(self.message)
            if self.game_over:
                self.kill = True
                break
            if self.color is None or self.turn is None:
                time.sleep(0.01)
                continue
            # If waiting or opponent disconnected, just show message and wait
            if "Waiting for opponent" in self.message or "disconnected" in self.message:
                time.sleep(0.01)
                continue

            print("White's turn" if self.turn == WHITE else "Black's turn")
            if self.turn != self.color or self.moved:
                time.sleep(0.01)
                continue
            turn = input()
            try:
                cell1, cell2 = turn.split()
            except ValueError:
                self.message = "Invalid input — expected two squares (e.g. e2 e4)"
                continue
            cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
            try:
                col1 = cols[cell1[0]]
                row1 = int(cell1[1]) - 1
                col2 = cols[cell2[0]]
                row2 = int(cell2[1]) - 1
            except (KeyError, IndexError, ValueError):
                self.message = "Invalid square — use format like e2 e4"
                continue
            if self.socket:
                try:
                    self.socket.sendall(struct.pack("4B", row1, col1, row2, col2))
                except OSError:
                    self.message = "Connection to server lost"
                    time.sleep(1)
            self.moved = True


if __name__ == "__main__":
    Chess().run()
