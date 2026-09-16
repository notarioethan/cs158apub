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
    

#parse config.txt
config_file = open("config.txt", "r")
s_line = config_file.readline().strip() #IP address as server
#c_line = config_file.readline().strip() #info exchanged w/ other student as client
#^ not used as server
config_file.close()

#socket stuff
sl_split = s_line.split()
#C_HOST = cl_split[0] # server address, use when client
#^ not used as server
S_HOST = sl_split[0] # client address, use when server
PORT = sl_split[1] # port number; client and server should match (and do in config.txt)
BUFFER_SIZE = 1024

#multithreading here; 1 process to run server side, 1 to run client side
#3 client side for self demo
#do server 1 thread, then client another
#copied from multi-thread-programming/threaded_server.py
def handle_client(conn, addr):
    """Talk to one client until it disconnects. Runs in its own thread.

    Each call to this function owns a separate `conn` socket, so many copies
    can run concurrently without interfering with one another.
    """
    # threading.current_thread().name labels the log so you can SEE that
    # different clients are served by different threads.
    thread_name = threading.current_thread().name
    print(f"[{thread_name}] Connected by {addr}")

    # `with conn` guarantees the socket is closed when this client leaves,
    # whether through a normal disconnect or an exception.
    with conn:
        while True:
            # recv() BLOCKS this thread until data arrives. Crucially, it only
            # blocks THIS thread — the main thread and other workers run on.
            data = conn.recv(BUFFER_SIZE)

            if not data:
                # Empty bytes means the client closed the connection.
                print(f"[{thread_name}] Client {addr} disconnected.")
                break
            print(f"Received: uuid={data.uuid}, flag={data.flag}, ")

            # sendall() echoes every byte back, retrying internally if needed.
            conn.sendall(data)
            print(f"[{thread_name}] Echoed back to {addr}.")


#server TCP socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s_sock:
    s_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #allow reusing port after server stops
    s_sock.bind((S_HOST, PORT)) #bind socket for host, port (OS knows where to send packets)
    s_sock.listen(3) #start listening; expect only 1 client connection, 3 for self

    print(f"[TCP Server] Listening on port {PORT} ... (multi-threaded)")

    try:
        while True:
            # The main thread does ONE job: accept connections. accept()
            # blocks until a client connects, then returns a fresh socket
            # dedicated to that client.
            conn, addr = s_sock.accept()

            # Spawn a worker thread to serve this client, then immediately
            # loop back to accept() the next one. daemon=True lets the program
            # exit on Ctrl+C without waiting for active clients to finish.
            client_thread = threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True,
            )
            client_thread.start()

            # active_count() includes the main thread, so subtract 1 to show
            # how many clients are currently being served.
            print(f"[Main] Active clients: {threading.active_count() - 1}")

    except KeyboardInterrupt:
        print("\n[Main] Shutting down.")

