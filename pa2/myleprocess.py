import uuid
import json
import socket
import threading
import time

class Message:
    def __init__(self, sender_uuid: uuid.UUID, flag: int = 0):
        self.uuid = sender_uuid
        self.flag = flag

    def to_json(self) -> str:
        """Serializes the Message instance into a JSON string."""
        # Custom encoder handling uuid.UUID objects by converting them to strings
        class MessageEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, uuid.UUID):
                    return str(obj)
                return super().default(obj)
        
        return json.dumps(self.__dict__, cls=MessageEncoder)

    @classmethod
    def from_json(cls, json_str: str):
        """Deserializes a JSON string back into a Message instance."""
        data = json.loads(json_str)
        # Convert the string representation back into a uuid.UUID object
        sender_uuid = uuid.UUID(data['uuid'])
        return cls(sender_uuid=sender_uuid, flag=data['flag'])
    
#leader_id =
state = 0

#parse config.txt
config_file = open("config.txt", "r")
s_line = config_file.readline().strip() #IP address as server
#not used as client; just to get to next line
c_line = config_file.readline().strip() #info exchanged w/ other student as client
config_file.close()

#socket stuff
cl_split = c_line.split(",")
C_HOST = cl_split[0] # server address, use when client
#S_HOST = s_line.split()[0] # client address, use when server
#^ not used as client
PORT = int(cl_split[1]) # port number; client and server should match (and do in config.txt)
BUFFER_SIZE = 1024


#client TCP socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c_sock:
    c_sock.connect((C_HOST, PORT)) #connect client w/ server
    #below is messaging from example code
    print(f"[TCP Client] Connected to {C_HOST}:{PORT}")
    #print("[TCP Client] Type a message and press Enter. Type 'quit' to exit.\n")
    #not user input for this
    
    while True:
        node_uuid = uuid.uuid4()
        message = Message(node_uuid, 0)

    
        if message.lower() == "quit":
            print("[TCP Client] Closing connection.")
            break
    
        if not message:
            continue
        
        print(f"Sent: uuid={message.uuid}, flag={message.flag}")    
        # encode() encodes the string to bytes, and sendall() sends it to the server.
        c_sock.sendall(message.to_json)
        with open("log1.txt", "a") as f:
            f.write(f"Sent: uuid={message.uuid}, flag={message.flag}")
    
        # recv() BLOCKS until the server sends data back.
        response = c_sock.recv(BUFFER_SIZE)
    
        print(f"Echo: {response.decode()}\n")

#log messages