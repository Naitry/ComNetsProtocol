import socket


class SimpleServer:
    def __init__(self,
                 host: str = '127.0.0.1',
                 port: int = 65433):
        self.host = host
        self.port = port
        self.client = False

    def awaitHandshake(self,
                       conn: socket.socket):
        recv = conn.recv(1024)
        if recv == b'connect':
            conn.sendall(b'yes')
            print('Correct handshake!')
            self.client = True
        else:
            print('Handshake failed')
            self.client = False

    def runServer(self):
        #bind socket on server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            conn, addr = s.accept()
            while (True):
                with conn:
                    print(f"Connected by {addr}")
                    self.awaitHandshake(conn)
                    while self.client:
                        data = conn.recv(1024)
                        if (data == b'terminate'):
                            return
                        conn.sendall(data)
                        print(f"Received and sent back: {data.decode()}")


if __name__ == "__main__":
    server = SimpleServer()
    server.runServer()
