class Requests:
    class Message:    
        STRING = "STRING"
    class File:
        class Client:
            FILE = "FILE:Client:INIT"
            OK="FILE:Client:OK"
            DENIED="FILE:Client:DENIED"
        class Server:
            END="FILE:Server:END"
            OK="FILE:Server:OK"
            DENIED="FILE:Server:DENIED"
