import threading
import pystyle
import socket
import json
import tqdm
import ssl
import os

from modules.log import SameLogger

from modules.requests import Requests

class Server(socket.socket):
    HEADER_TEMPLATE = {
        "request":None,
        "data":None
    }
    def __init__(self, certs_dir, args, block=True):
        """
        Initializes the server with the given `certs_dir`, `args`, and `block` parameters.
        
        Parameters:
            certs_dir (str): The directory containing the SSL certificates.
            args (object): The arguments object containing the server address and port.
            block (bool, optional): Whether the server should run in a blocking manner. 
                                    Defaults to True.
        """
        self.logging = SameLogger()
        self.logger = self.logging.getLogger("Server")
        
        self.logger.info("Starting server...")
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.cert_file = os.path.join(certs_dir, "certificate.crt")
        self.key_file = os.path.join(certs_dir, "private.key")
        
        self.logger.debug("Initializing SSL context...")
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(self.cert_file, self.key_file)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        self.logger.debug("Wrapping socket with SSL...")
        self.sock = context.wrap_socket(self, server_side=True)
        
        self.logger.debug("Binding to %s:%d...", args.address, args.port)
        self.sock.bind((args.address, args.port))
        
        self.running = True
        
        if block is False:
            self.logger.info("Starting main loop thread...")
            threading.Thread(target=self.waiter_loop).start()
        else:
            self.logger.info("Listening for any connection...")
            self.wait_connections()
    def wait_connections(self):
        """
        Waits for incoming connections and handles them.

        Parameters:
            self (object): The instance of the class.
        
        Returns:
            None
        """
        self.sock.listen(1)
        client_socket, addr = self.sock.accept()
        self.logger.info("User with address '%s' connected!", addr)
        self.handle_client(client_socket)
        
    def exit(self):
        self.logger.info("Closing server...")
        self.running = False
        try:
            self.sock.close()
        except Exception:
            self.logger.exception("Failed to close server!")
        
    def waiter_loop(self):
        """
        Listen for connections and handle them in separate threads.

        This function continuously listens for incoming connections while the 'running' flag is True.
        Once a connection is established, a new thread is created to handle the client.
        
        Returns:
            None
        """
        while self.running:
            self.logger.info("Listening for any connection...")
            self.sock.listen()
            self.logger.info("Accepting connection...")
            client_socket, addr = self.sock.accept()
            
            self.logger.info("User with address '%s' connected!", addr)
            self.logger.info("Creating thread for client...")    
            threading.Thread(target=self.handle_client_thread, args=(client_socket,{"ip":addr})).start()
        
    def sendCustomHeader(self, request_type, data):
        self.logger.debug("Creating header...")
        header = self.HEADER_TEMPLATE.copy()
        header["request"] = request_type
        header["data"] = data

        self.logger.debug("Sending header...")
        self.sock.sendall(json.dumps(header).encode())
    
    def handle_client(self, client_socket: socket.socket):
        """
        Handle the client connection.

        Args:
            client_socket (socket.socket): The socket object representing the client connection.

        Returns:
            None
        """
        request = json.loads(client_socket.recv(1024))
        if request["request"] == "STRING":
            print(f"[{pystyle.Colorate.Horizontal(pystyle.Colors.blue_to_red, 'RECIEVED')}] {request['data']}")
            self.logger.info("Recieved: %s", request["data"])
        elif request["request"] == Requests.File.Client.FILE:
            self.logger.info("FILE request received!")
            self.logger.info("Size: %s", request["data"])
            self.logger.info("Creating file...")
            path = input(f"[{pystyle.Colorate.Horizontal(pystyle.Colors.blue_to_red, 'INFO')}] File path: ")
            self.logger.info("Path: %s", path)

            # The root directory is saved into the n variable
            if (n:=os.path.dirname(path)) != "":
                os.makedirs(n, exist_ok=True)
            
            progress = tqdm.tqdm(total=int(request["data"]), unit="B", colour="#A6E3A1", unit_scale=True, unit_divisor=1024)
            with open(path, "wb") as file:
                while True:
                    data = client_socket.recv(1024)
                    if data == "END":
                        break
                    file.write(data)
                    progress.update(len(data))
            self.sendCustomHeader(Requests.File.Server.END, '')
            progress.close()
                
        

        client_socket.close()
        self.exit()
    
    def handle_client_thread(self, client_socket: socket.socket, client_data: dict):
        """
        Handle the client connection.

        Args:
            client_socket (socket.socket): The socket object representing the client connection.

        Returns:
            None
        """
        
        while True:
            try:
                request = json.loads(client_socket.recv(1024))
                if request["request"] == "STRING":
                    print(f"[{pystyle.Colorate.Horizontal(pystyle.Colors.blue_to_red, 'RECIEVED')}] {request['data']}")
                    self.logger.info("Recieved: %s", request["data"])
                    continue
                elif request["request"] == Requests.File.Client.FILE:
                    self.logger.info("FILE request received!")
                    self.logger.info("Size: %s", request["data"])
                    self.logger.info("Creating file...")
                    path = input(f"[{pystyle.Colorate.Horizontal(pystyle.Colors.blue_to_red, 'INFO')}] File path: ")
                    self.logger.info("Path: %s", path)

                    # The root directory is saved into the n variable
                    if (n:=os.path.dirname(path)) != "":
                        os.makedirs(n, exist_ok=True)
                    
                    progress = tqdm.tqdm(total=int(request["data"]), unit="B", colour="#A6E3A1", unit_scale=True, unit_divisor=1024)
                    with open(path, "wb") as file:
                        while True:
                            data = client_socket.recv(1024)
                            if data == "END":
                                break
                            file.write(data)
                            progress.update(len(data))
                    self.sendCustomHeader(Requests.File.Server.END, '')
                    progress.close()
            except (ConnectionAbortedError, ConnectionResetError, ConnectionError):
                self.logger.info("User with address '%s' disconnected!", client_data["ip"])
                
        client_socket.close()
        self.exit()