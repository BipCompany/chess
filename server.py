import socket
import struct
import threading
import time

from modules.field import Field


class Server:
    def __init__(self, host="127.0.0.1", port=62743):
        self.host = host
        self.port = port

        self.kill = False
        self.thread_count = 0

        self.field = Field()  # __init__ calls setup() → start position, turn = WHITE

        self.game_over = False

        # Fixed slots: index = player color (0=WHITE, 1=BLACK)
        self.players: list[socket.socket | None] = [None, None]
        self.player_messages: list[str] = ["", ""]

    def serialize(self, player_id: int) -> bytes:
        """Build a packet for the given player (index in self.players)."""
        matrix_string = ""
        for row in self.field.get_board():
            for piece in row:
                matrix_string += piece.get_char() if piece else "  "
        matrix_bytes = matrix_string.encode("utf-8")
        message_bytes = self.player_messages[player_id].encode("utf-8")
        return struct.pack(
            "<B?B128s50s",
            self.field.turn,
            self.game_over,
            player_id,
            matrix_bytes,
            message_bytes,
        )

    def _find_player_index(self, conn: socket.socket) -> int | None:
        for i in range(2):
            if self.players[i] is conn:
                return i
        return None

    def _disconnect_player(self, conn: socket.socket) -> None:
        idx = self._find_player_index(conn)
        if idx is None:
            return
        self.players[idx] = None
        self.player_messages[idx] = ""

        other = 1 - idx
        if self.players[other] is not None:
            self.player_messages[other] = "Opponent disconnected — waiting for opponent"

        # Both slots empty → reset the game
        if self.players[0] is None and self.players[1] is None:
            self.field = Field()
            self.game_over = False
            self.player_messages = ["", ""]

    def run_listener(self, conn: socket.socket) -> None:
        self.thread_count += 1
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        conn.settimeout(1)
        with conn:
            while not self.kill:
                try:
                    data = conn.recv(4096)
                    if not data:
                        # Clean disconnect (EOF)
                        self._disconnect_player(conn)
                        break

                    if self.game_over:
                        continue

                    row1, col1, row2, col2 = struct.unpack_from("4B", data, 0)
                    player_id = self._find_player_index(conn)
                    if player_id is None:
                        break

                    # Both players required to make a move
                    if self.players[0] is None or self.players[1] is None:
                        self.player_messages[player_id] = "Waiting for opponent"
                        continue

                    result = self.field.move_piece(player_id, row1, col1, row2, col2)

                    if result.startswith("Checkmate!") or result == "Stalemate!":
                        self.game_over = True
                        self.player_messages[0] = result
                        self.player_messages[1] = result
                    elif result == "" or result == "Check!":
                        self.player_messages[player_id] = "It's opponents turn"
                        other = 1 - player_id
                        self.player_messages[other] = "It's your turn"
                    else:
                        self.player_messages[player_id] = result

                    time.sleep(0.001)
                except socket.timeout:
                    pass
                except (ConnectionResetError, ConnectionAbortedError, OSError):
                    self._disconnect_player(conn)
                    break
        self.thread_count -= 1

    def connection_listen_loop(self) -> None:
        self.thread_count += 1
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
            s.bind((self.host, self.port))

            while not self.kill:
                s.settimeout(1)
                s.listen()
                try:
                    conn, addr = s.accept()
                    print("new connection", conn, addr)

                    if self.players[0] is None:
                        self.players[0] = conn
                        self.player_messages[0] = "Waiting for opponent"
                        threading.Thread(target=self.run_listener, args=(conn,)).start()
                        if self.players[1] is not None:
                            self.player_messages[0] = "Game started! You are White."
                            self.player_messages[1] = "Game started! You are Black. Waiting for White."
                    elif self.players[1] is None:
                        self.players[1] = conn
                        self.player_messages[1] = "Game started! You are Black. Waiting for White."
                        threading.Thread(target=self.run_listener, args=(conn,)).start()
                        if self.players[0] is not None:
                            self.player_messages[0] = "Game started! You are White."
                            self.player_messages[1] = "Game started! You are Black. Waiting for White."
                    else:
                        print("declined — game is full")
                        conn.close()
                except socket.timeout:
                    continue
                time.sleep(0.01)
        self.thread_count -= 1

    def await_kill(self) -> None:
        self.kill = True
        while self.thread_count:
            time.sleep(0.01)
        print("killed")

    def run(self) -> None:
        threading.Thread(target=self.connection_listen_loop).start()
        try:
            while True:
                # Snapshot all packets first so every player sees
                # the same board state in this broadcast tick.
                packets: list[tuple[socket.socket, bytes]] = []
                for i in range(2):
                    conn = self.players[i]
                    if conn is not None:
                        try:
                            packets.append((conn, self.serialize(i)))
                        except OSError:
                            self._disconnect_player(conn)
                for conn, packet in packets:
                    try:
                        conn.sendall(packet)
                    except OSError:
                        self._disconnect_player(conn)
                time.sleep(0.05)
        except KeyboardInterrupt:
            self.await_kill()


if __name__ == "__main__":
    Server().run()
