import logging
import socket
import json
import tqdm
import ssl
import os

from modules.requests import Requests

class Client():
    HEADER_TEMPLATE = {
        "request":None,
        "data":None
    }
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
        
    def formatCustomHeader(self, request_type, data):
        self.logger.debug("Creating header...")
        header = self.HEADER_TEMPLATE.copy()
        header["request"] = request_type
        header["data"] = data

        self.logger.debug("Sending header...")
        self.sock.sendall(json.dumps(header).encode())
    
    def sendFile(self, file_path):
        file_len = os.path.getsize(file_path)
        self.formatCustomHeader("FILE", file_len)
        if self.sock.recv(1024) == Requests.File.Server.DENIED:
            self.logger.info("Server denied the file request!")
            self.logger.info("Closing connection...")
            self.sock.close()
            return
        
        progress = tqdm.tqdm(total=int(file_len), unit="B", colour="#A6E3A1", unit_scale=True, unit_divisor=1024)
        with open(file_path, "rb") as file:
            while True:
                data = file.read(1024)
                if not data:
                    self.sock.sendall("END".encode())
                    break
                self.sock.sendall(data)
                progress.update(len(data))
        progress.close()
        self.logger.info("Recieved: %s", self.sock.recv(1024))
        self.sock.recv(1024)

    
    def sendMessage(self, message):
        self.formatCustomHeader("STRING", message)
    def exit(self):
        self.logger.info("Closing client...")
        self.sock.close()