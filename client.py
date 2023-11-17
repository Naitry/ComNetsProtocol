import socket


class SimpleClient:
    def __init__(self,
                 host: str = '127.0.0.1',
                 port: int = 65433):
        self.host: str = host
        self.port: int = port
        self.on: bool = False

    def handshake(self, sock: socket) -> bool:
        print("sending handshake...")
        sock.sendall(bytes("connect", "utf-8"))
        reply = sock.recv(1024)
        return reply == b'yes'

    def runClient(self):
        #open socket client side
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            on: bool = self.handshake(s)
            while (on):
                send: str = input()
                if (send != ''):
                    s.sendall(bytes(send, 'utf-8'))
                    if (send == 'terminate'):
                        return
                    data = s.recv(1024)
                    print(f"Received from server: {data.decode()}")


if __name__ == "__main__":
    client = SimpleClient()
    client.runClient()
