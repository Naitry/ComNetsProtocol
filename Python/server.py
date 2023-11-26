import configparser
from typing import Optional
import os
import signal
import socket
import sys
import threading
from os import path
from typing import Dict, Tuple, List


config = configparser.ConfigParser()
configPath:  str = '../serverConfig.ini'
config.read(configPath)


class SimpleServer:
    def __init__(self):
        host: Optional[str] = None
        port: Optional[int] = None
        password: Optional[str] = None
        if path.exists(configPath):
            host = config['DEFAULT']['Host']
            port = int(config['DEFAULT']['Port'])
            password = config['DEFAULT']['Password']

        self.host: str = host if host else "127.0.0.1"
        self.port: int = port if port else 55222
        self.password: str = password if password else "password"
        self.connections: Dict[Tuple[str, int], socket.socket] = {}
        self.threads: List[threading.Thread] = []
        self.running: bool = False
        self.server_socket: socket.socket = None
        self.lock: threading.Lock = threading.Lock()
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signum, frame):
        print("\nReceived interrupt signal, shutting down...")
        self.stop_server()
        sys.exit(0)

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
                    if self.validate_credentials(conn):
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

    def validate_credentials(self,
                             conn: socket) -> bool:
        """
        Prompts user for a password, awaits a response, returning a bool
        indicating accuracy

        :param sock: socket used for TCP communication.
        :return: True if server response matches password
                 False otherwise.
        """
        password_attempt: bytes = conn.recv(1024)

        # CASE: Password command header received
        if password_attempt.startswith(b'PASS '):
            received_password: str = password_attempt[5:].decode('utf-8')
            # CASE: Correct password
            if received_password == self.password:
                conn.sendall(b'PWOK')
                return True
            # CASE: Incorrect password
            else:
                conn.sendall(b'PWNO')
                return False
        # CASE: incorrect password response format
        else:
            conn.sendall(b'PWIV')
            return False

    def run_server(self, log: str):
        self.running = True
        try:
            if not os.path.exists(log):
                with open(log, 'w') as file:
                    file.write('')

            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
                except socket.error as e:
                    # Handle specific socket errors if necessary
                    if not self.running:
                        break
                    print(f"Socket error: {e}")
        finally:
            # Ensure the socket is closed in case of an error
            self.server_socket.close()

    def stop_server(self):
        print("Stopping Server...")
        self.running = False

        # Temporarily create a new connection to unblock accept() call
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as temp_socket:
            try:
                temp_socket.connect((self.host, self.port))
            except socket.error:
                pass

        # Close the server socket
        self.server_socket.close()

        # Close all client connections
        with self.lock:
            for addr, conn in self.connections.items():
                print(f"Closing connection: {addr}")
                conn.close()

        # Wait for all threads to finish
        current_thread = threading.current_thread()
        for thread in self.threads:
            if thread is not current_thread:
                thread.join()
        self.threads.clear()
        print("Server stopped.")

    def are_threads_active(self) -> bool:
        """
        Check if there are any active threads in the list.
        """
        return any(thread.is_alive() for thread in self.threads)

    def start_ui(self):
        while True:
            cmd = input("Enter command (start, stop, exit): ").lower()
            print()
            if cmd == "start":
                if not self.running and not self.are_threads_active():
                    print("Starting Server...")
                    threading.Thread(target=self.run_server, args=("./log.txt",)).start()
                else:
                    print("Server is either already running or previous threads are still active.")
            elif cmd == "stop":
                if self.running:
                    self.stop_server()
                else:
                    print("Server is not running.")
            elif cmd == "exit":
                if self.running:
                    self.stop_server()
                sys.exit()


if __name__ == "__main__":
    server = SimpleServer()
    try:
        server.start_ui()
    except Exception as e:
        print(f"Unhandled exception: {e}")
        server.stop_server()
    except KeyboardInterrupt:
        print("Interrupt received, shutting down...")
        server.stop_server()