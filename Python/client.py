import configparser
import socket
import sys
from os import path

from typing import Optional

config = configparser.ConfigParser()
configPath:  str = '../clientConfig.ini'
config.read(configPath)


class SimpleClient:
    def __init__(self):
        host: Optional[str] = None
        port: Optional[int] = None
        if path.exists(configPath):
            host: Optional[str] = config['DEFAULT']['Host']
            port: Optional[int] = int(config['DEFAULT']['Port'])

        self.host: str = host if host else "127.0.0.1"
        self.port: int = port if port else 55222
        self.on: bool = False

    def handshake(self,
                  sock: socket.socket) -> bool:
        print("Sending handshake...")
        sock.sendall(b'PING')
        reply: bytes = sock.recv(1024)
        return reply == b'PONG'

    def run_client(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            self.on = self.handshake(s)
            while self.on:
                send: str = input("Enter command or message: ")
                if send:
                    # CASE: user sends terminate message
                    if send == 'terminate':
                        s.sendall(b'TERM')
                        password: str = input("Enter input a password: ")
                        s.sendall(('PASS ' + password).encode('utf-8'))
                        response: bytes = s.recv(1024)
                        # CASE: Password correct
                        if response == b'PWOK':
                            print("Password correct, terminating the server")
                            s.close()
                            break
                        # CASE: Password incorrect
                        elif response == b'PWNO':
                            print("Invalid password, server continues to run")
                        # CASE: Password format invalid
                        elif response == b'PWIV':
                            print("Invalid password format, server continues to run")
                        sys.exit()
                    # CASE: user sends regular text message
                    else:
                        s.sendall(('MESG ' + send).encode('utf-8'))

                    data: bytes = s.recv(1024)
                    if data:
                        print(f"Received from server: {data.decode()}")


if __name__ == "__main__":
    client = SimpleClient()
    client.run_client()
