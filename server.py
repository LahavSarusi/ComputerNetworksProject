import socket
import threading

HOST = "0.0.0.0"
PORT = 10000

# Dictionary to store connected clients: {username: connection_socket}
clients = {}
clients_lock = threading.Lock()


def handle_client(conn, addr):
    """
    Handles communication with a single client in a separate thread.
    """
    print(f"[NEW CONNECTION] {addr} connected.")
    username = ""

    try:
        # Step 1: Request a unique username from the client
        conn.sendall("Enter your username: ".encode('utf-8'))
        username = conn.recv(1024).decode('utf-8').strip()

        # Check if the username is taken and add to the list
        with clients_lock:
            if username in clients:
                conn.sendall("Username already taken. Disconnecting.".encode('utf-8'))
                conn.close()
                return
            clients[username] = conn

        print(f"[REGISTERED] User '{username}' added from {addr}")
        conn.sendall(f"Welcome {username}! To chat, type: TargetName:Message".encode('utf-8'))

        # Step 2: Main loop for handling messages
        while True:
            data = conn.recv(1024)
            if not data:
                break  # Client disconnected

            message = data.decode("utf-8")
            print(f"[{username}]: {message}")

            # Parse the message to identify the recipient
            # Expected format: TargetName:Message content
            if ":" in message:
                target_name, msg_content = message.split(":", 1)
                target_name = target_name.strip()

                # Send the message to the target client if they exist
                with clients_lock:
                    if target_name in clients:
                        target_conn = clients[target_name]
                        formatted_msg = f"[{username}]: {msg_content}"
                        target_conn.sendall(formatted_msg.encode('utf-8'))
                    else:
                        conn.sendall(f"User '{target_name}' not found.".encode('utf-8'))
            else:
                conn.sendall("Invalid format. Use: TargetName:Message".encode('utf-8'))

    except ConnectionResetError:
        print(f"[ERROR] Client {addr} disconnected abruptly.")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        # Remove the client from the list upon disconnection
        with clients_lock:
            if username in clients:
                del clients[username]
                print(f"[DISCONNECT] User '{username}' removed.")
        conn.close()


def start_server():
    """
    Sets up the server socket and listens for incoming connections.
    """
    print("[STARTING] Server is starting...")
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the specified HOST and PORT
    server_socket.bind((HOST, PORT))

    # Enable the server to accept connections
    server_socket.listen()

    # Print the machine's local IP address so you know what to put in the client code
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")
    print(f"--> Tell the client to connect to IP: {local_ip}")

    while True:
        # pauses execution and waits for a new connection
        conn, addr = server_socket.accept()

        # Create and start a new Thread to handle this client
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


if __name__ == "__main__":
    start_server()
