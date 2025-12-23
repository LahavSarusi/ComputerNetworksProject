import socket
import threading

HOST = "127.0.0.1"
PORT = 10000


def handle_client(conn, addr):
    """
    This function runs in a separate thread for each connected client.
    It handles the communication logic (receiving and sending messages).
    """
    print(f"Client connected: {addr}")
    try:
        welcome_message = "Welcome"
        conn.sendall(welcome_message.encode('utf-8')) # converts the string into bytes

        while True:
            data = conn.recv(1024) # Receive data from the client (buffer size is 1024 bytes)
            if not data:
                break

            data_d = data.decode("utf-8") # Decode the received bytes back into a readable string
            print(f"Message from client {addr}: {data_d}")

            response = f"Server received: {data_d.upper()}"
            conn.sendall(response.encode('utf-8')) # Send the response back to the client

    except ConnectionResetError:
        print(f"Client disconnected abruptly: {addr}")
    finally:
        conn.close()


def start_server():
    """
    Sets up the server socket and listens for incoming connections.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a socket object
    server_socket.bind((HOST, PORT)) # Bind the socket to the specified HOST and PORT
    server_socket.listen() # Enable the server to accept connections
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        conn, addr = server_socket.accept() # pauses execution and waits for a new connection
        client_thread = threading.Thread(target=handle_client, args=(conn, addr)) # Create a new Thread to handle this client
        client_thread.start() # Start the thread
        print(f"Active clients: {threading.active_count() - 1}") # Print the number of active threads


if __name__ == "__main__":
    start_server()