import threading
import logging
import socket
import ssl
import os

class Server(socket.socket):
    def __init__(self, certs_dir, threaded=False):
        self.logger = logging.getLogger("Server")
        
        self.logger.info("Starting server...")
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.cert_file = os.path.join(certs_dir, "cert.crt")
        self.key_file = os.path.join(certs_dir, "private.key")
        
        self.logger.debug("Initializing SSL context...")
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_cert_chain(self.cert_file, self.key_file)
        
        self.logger.debug("Wrapping socket with SSL context...")
        self = context.wrap_socket(self, server_side=True)
        
        self.logger.debug("Binding to localhost:8080...")
        self.bind(("localhost", 8080))
        
        self.running = True
        
        if threaded is True:
            self.logger.info("Starting main loop thread...")
            threading.Thread(target=self.waiter_loop).start()
        else:
            self.logger.info("Listening for any connection...")
            self.wait_connections()
    def wait_connections(self):
        self.listen()
        self.logger.info("Accepting connection...")
        client_socket, addr = self.accept()
        self.logger.info("User with address '%s' connected!", addr)
        self.handle_client(client_socket)
        
    def close(self):
        self.logger.info("Closing server...")
        self.running = False
        try:
            self.close()
        except Exception:
            self.logger.exception("Failed to close server!")
        
    def waiter_loop(self):
        while self.running:
            self.logger.info("Listening for any connection...")
            self.listen()
            self.logger.info("Accepting connection...")
            client_socket, addr = self.accept()
            self.logger.info("User with address '%s' connected!", addr)
            self.logger.info("Creating thread for client...")    
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()
    
    def handle_client(self, client_socket):
        pass