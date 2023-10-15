import logging
import socket
import ssl
import os

class Client():
    HEADER_TEMPLATE="{};{};{}"
    def __init__(self, certs_dir, args):
        self.logger = logging.getLogger("Client")

        self.logger.debug("Initializing client...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.cert_file = os.path.join(certs_dir, "certificate.crt")
        self.key_file = os.path.join(certs_dir, "private.key")
        
        self.logger.debug("Initializing SSL context...")
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        self.logger.debug("Wrapping socket with SSL context...")
        self.sock = context.wrap_socket(sock, server_hostname=args.address)
        self.sock.connect((args.address, args.port))
        
        self.logger.info("Sending data...")
        self.sendMessage("Hello from client!")    
    def formatCustomHeader(self, request_type, data_lenght):
        self.logger.debug("Creating header...")
        header = self.HEADER_TEMPLATE.format(request_type, data_lenght).encode()

        self.sock.sendall(header)
    
    def sendFile(self, file_path):
        self.formatCustomHeader("FILE", os.path.getsize(file_path))
        with open(file_path, "rb") as file:
            while True:
                data = file.read(1024)
                if not data:
                    break
                self.sock.sendall(data)
    
    def sendMessage(self, message):
        self.formatCustomHeader("STRING", len(message))
        self.sock.sendall(message)

    def exit(self):
        self.logger.info("Closing client...")
        self.sock.close()