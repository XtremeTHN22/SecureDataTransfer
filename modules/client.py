from modules.log import SameLogger
import socket
import json
import ssl
import os


class Client():
    HEADER_TEMPLATE = {
        "request":None,
        "data":None
    }
    def __init__(self, certs_dir, args):
        self.logging = SameLogger()
        self.logger = self.logging.getLogger("Client")

        self.logger.debug("Initializing client...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.cert_file = os.path.join(certs_dir, "certificate.crt")
        self.key_file = os.path.join(certs_dir, "private.key")
        
        self.logger.debug("Initializing SSL context...")
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        self.logger.debug("Wrapping socket with SSL context...")
        self.logger.debug("Connecting to %s:%d...", args.address, args.port)
        self.sock = context.wrap_socket(sock, server_hostname=args.address)
        self.sock.connect((args.address, args.port))
        
        self.logger.info("Sending data...")
        self.sendMessage("Hello from client!")    
    def formatCustomHeader(self, request_type, data):
        self.logger.debug("Creating header...")
        header = self.HEADER_TEMPLATE.copy()
        header["request"] = request_type
        header["data"] = data
        header = json.dumps(header).encode()

        self.logger.debug("Sending header...")
        self.sock.sendall(header)
    
    def sendFile(self, file_path):
        self.formatCustomHeader("FILE", os.path.getsize(file_path))
        with open(file_path, "rb") as file:
            while True:
                data = file.read(1024)
                if not data:
                    self.sock.sendall("END".encode())
                    break
                self.sock.sendall(data)
        self.logger.info("Recieved: %s", self.sock.recv(1024))
        

    
    def sendMessage(self, message):
        self.formatCustomHeader("STRING", message)
    def exit(self):
        self.logger.info("Closing client...")
        self.sock.close()