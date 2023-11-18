import socket


class SimpleClient:
    def __init__(self,
                 host: str = '127.0.0.1',
                 port: int = 65433):
        self.host: str = host
        self.port: int = port
        self.on: bool = False

    def handshake(self, sock: socket):
        print("sending handshake...")
        sock.sendall(bytes("connect", "utf-8"))
        reply = sock.recv(1024)
        return reply == b'PONG'
    commands = {'terminate', 'otherCommand1', 'otherCommand2'}

    def runClient(self):
        # open socket client side
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            self.on = self.handshake(s)
            while (self.on):
                send: str = input()
                if (send != ''):
                    if send in self.commands:
                        if send == b'terminate':
                            s.sendall(b'TERM')
                    else:
                        s.sendall("MESG")

                        data = s.recv(1024)
                        print(f"Received from server: {data.decode()}")


if __name__ == "__main__":
    client = SimpleClient()
    client.runClient()
