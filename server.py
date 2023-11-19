import socket
import os
import sys
import threading
from typing import Dict, Tuple, List


class SimpleServer:
    def __init__(self, host: str = '127.0.0.1', port: int = 65443):
        self.host: str = host
        self.port: int = port
        self.connections: Dict[Tuple[str, int], socket.socket] = {}
        self.threads: List[threading.Thread] = []
        self.running: bool = False
        self.server_socket: socket.socket = None
        self.lock: threading.Lock = threading.Lock()

    def await_handshake(self,
                        conn: socket.socket,
                        addr: Tuple[str, int],
                        log: str):
        try:
            recv: bytes = conn.recv(1024)
            if recv == b'PING':
                conn.sendall(b'PONG')
                print(f'Correct handshake with {addr}!')
                with self.lock:
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
                    print("Terminating server")
                    self.stop_server()
            except ConnectionResetError:
                break
            except Exception as e:
                print(f"Error with client {addr}: {e}")
                break

        print(f"Connection with {addr} closed.")
        conn.close()
        with self.lock:
            self.connections.pop(addr, None)

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
                    thread = threading.Thread(target=self.await_handshake,
                                              args=(conn, addr, log))
                    thread.start()
                    self.threads.append(thread)
            except OSError:
                break

    def stop_server(self):
        print("Stopping Server...")
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        for index, addr, conn in enumerate(list(self.connections.items())):
            conn.close()
        # Join all threads
        for thread in self.threads:
            thread.join()
        self.threads.clear()
        print("Server stopped.")

    def start_ui(self):
        while True:
            cmd = input("Enter command (start, stop, exit): ").lower()
            print()
            # CASE: start server
            if cmd == "start":
                if not self.running:
                    print("Starting Server...")
                    threading.Thread(target=self.run_server,
                                     args=("./log.txt",)).start()
                else:
                    print("Server is already running.")
            # CASE: stop server
            elif cmd == "stop":
                if self.running:
                    self.stop_server()
                else:
                    print("Server is not running.")
            # CASE: terminate application entirely
            elif cmd == "exit":
                if self.running:
                    self.stop_server()
                sys.exit()


if __name__ == "__main__":
    server = SimpleServer()
    server.start_ui()
