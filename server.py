import socket
import os
import threading
import time
from typing import Dict, Tuple


class SimpleServer:
    def __init__(self, host: str = '127.0.0.1', port: int = 65443):
        self.host: str = host
        self.port: int = port
        self.connections: Dict[Tuple[str, int], socket.socket] = {}
        self.running: bool = False
        self.server_socket: socket.socket = None

    def await_handshake(self,
                        conn: socket.socket,
                        addr: Tuple[str, int],
                        log: str):
        try:
            recv: bytes = conn.recv(1024)
            if recv == b'PING':
                conn.sendall(b'PONG')
                print(f'Correct handshake with {addr}!')
                self.connections[addr] = conn
                self.handle_client(conn, addr, log)
            else:
                print(f'Handshake failed with {addr}')
                conn.close()
        except Exception as e:
            print(f"Error with client {addr}: {e}")
            conn.close()

    def handle_client(self,
                      conn: socket.socket,
                      addr: Tuple[str, int],
                      log: str):
        while self.running:
            try:
                data: bytes = conn.recv(1024)
                if not data:
                    break
                if data.startswith(b'MESG'):
                    with open(log, "a") as file:
                        file.write(data[5:].decode('utf-8') + "\n")
                    conn.sendall(data)
                    print(f"Message received and sent back: {data[5:].decode()}")
                elif data == b'TERM':
                    print("terminating server")
                    self.stop_server()
            except ConnectionResetError:
                break
            except Exception as e:
                print(f"Error with client {addr}: {e}")
                break

        print(f"Connection with {addr} closed.")
        conn.close()
        self.connections.pop(addr, None)

        print(f"Connection with {addr} closed.")
        conn.close()
        del self.connections[addr]

    def run_server(self, log: str):
        self.running = True
        if not os.path.exists(log):
            with open(log, 'w') as file:
                file.write('')

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"Server running on {self.host}:{self.port}")

        while self.running:
            try:
                conn, addr = self.server_socket.accept()
                if conn:
                    threading.Thread(target=self.await_handshake,
                                     args=(conn, addr, log)).start()
            except OSError:
                break

    def accept_connection(self):
        self.server_socket.settimeout(1.0)
        try:
            return self.server_socket.accept()
        except socket.timeout:
            return None, None

    def stop_server(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        for addr, conn in list(self.connections.items()):
            conn.close()
        print("Server stopped.")

    def start_ui(self):
        while True:
            cmd = input("Enter command (start, stop, exit): ").lower()
            if cmd == "start":
                if not self.running:
                    threading.Thread(target=self.run_server,
                                     args=("./log.txt",)).start()
                else:
                    print("Server is already running.")
            elif cmd == "stop":
                if self.running:
                    self.stop_server()
                else:
                    print("Server is not running.")
            elif cmd == "exit":
                if self.running:
                    self.stop_server()
                break


if __name__ == "__main__":
    server = SimpleServer()
    server.start_ui()
