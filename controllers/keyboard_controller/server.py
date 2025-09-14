import socket


class CameraServer:
    def __init__(self, host = "127.0.0.1", port = 5550):
        self.host = host
        self.port = port
        self.address = (self.host, self.port)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.address)
        self.server.listen(1)
     
    
    def establish_connection(self):
        connection, client_address = self.server.accept()
        return connection
        
        
class ProximitySensorServer:
    def __init__(self, host = "127.0.0.1", port = 5551):
        self.host = host
        self.port = port
        self.address = (self.host, self.port)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.address)
        self.server.listen(1)
     
    
    def establish_connection(self):
        connection, client_address = self.server.accept()
        return connection