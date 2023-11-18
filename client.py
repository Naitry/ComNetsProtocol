import socket


class SimpleClient:
    def __init__(self,
                 host: str = '127.0.0.1',
                 port: int = 65443):
        self.host: str = host
        self.port: int = port
        self.on: bool = False

    def handshake(self, sock: socket.socket) -> bool:
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
                    if send == 'terminate':
                        s.sendall(b'TERM')
                        s.close()
                        break
                    else:
                        s.sendall(('MESG ' + send).encode('utf-8'))

                    data: bytes = s.recv(1024)
                    if data:
                        print(f"Received from server: {data.decode()}")


if __name__ == "__main__":
    client = SimpleClient()
    client.run_client()
