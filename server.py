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

        self.field = Field()
        self.field.start_position()

        self.game_over = False
        self.message = ""

        self.players = []
        self.player_messages = {}

    def serialize(self, player_conn):
        matrix_string = ""
        for row in self.field.get_board():
            for piece in row:
                matrix_string += piece.get_char() if piece else "  "
        matrix_bytes = matrix_string.encode("utf-8")
        message_bytes = self.player_messages[player_conn].encode("utf-8")
        player_id = self.players.index(player_conn)
        return struct.pack("<B?B128s50s", self.field.turn, self.game_over, player_id, matrix_bytes, message_bytes)

    def run_listener(self, conn):
        self.thread_count += 1
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        conn.settimeout(1)
        with conn:
            while not self.kill:
                try:
                    data = conn.recv(4096)
                    if len(data) and not self.game_over:
                        row1, col1, row2, col2 = struct.unpack_from("4B", data, 0)
                        player_id = self.players.index(conn)
                        result = self.field.move_piece(player_id, row1, col1, row2, col2)
                        if result.startswith("Checkmate!") or result == "Stalemate!":
                            self.game_over = True
                            for player_conn in self.players:
                                self.player_messages[player_conn] = result
                        elif result == "" or result == "Check!":
                            self.player_messages[conn] = "It's opponents turn"
                            for player_conn in self.players:
                                if player_conn != conn:
                                    self.player_messages[player_conn] = "It's your turn"
                        else:
                            self.player_messages[conn] = result
                except socket.timeout:
                    pass
        self.thread_count -= 1

    def connection_listen_loop(self):
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
                    if len(self.players) < 2:
                        self.players.append(conn)
                        self.player_messages[conn] = ""
                        threading.Thread(target=self.run_listener, args=(conn,)).start()
                except socket.timeout:
                    continue
                time.sleep(0.01)
        self.thread_count -= 1

    def await_kill(self):
        self.kill = True
        while self.thread_count:
            time.sleep(0.01)
        print("killed")

    def run(self):
        threading.Thread(target=self.connection_listen_loop).start()
        try:
            while True:
                # Snapshot all packets before sending any, so every
                # player sees the same board state in this tick.
                packets = []
                for player_conn in self.players:
                    try:
                        packets.append((player_conn, self.serialize(player_conn)))
                    except OSError:
                        pass
                for player_conn, packet in packets:
                    try:
                        player_conn.sendall(packet)
                    except OSError:
                        pass
                time.sleep(0.05)
        except KeyboardInterrupt:
            self.await_kill()


Server().run()
