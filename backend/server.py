import socket
import threading
import os

# Get configuration from environment variables or use hard-coded defaults
# For local network access, set TCP_HOST=0.0.0.0 in environment variables
# Default to 127.0.0.1 for localhost-only, but can be overridden for network access
HOST = os.environ.get("TCP_HOST", "0.0.0.0")
PORT = int(os.environ.get("TCP_PORT", "10000"))

# Client registry: maps username -> (connection, address)
# Protected by a lock for thread-safe access
clients = {}
clients_lock = threading.Lock()


def handle_client(conn, addr):
    """
    This function runs in a separate thread for each connected client.
    It handles the communication logic (receiving and sending messages).
    """
    print(f"Client connected: {addr}")
    username = None
    
    try:
        welcome_message = "Welcome to Lahav and Gitam's chat server!\nPlease enter your username: "
        conn.sendall(welcome_message.encode('utf-8'))
        
        # Receive the username from the client and validate it
        username_data = conn.recv(1024)
        if not username_data:
            return
        
        # Decode the username and strip any whitespace
        username = username_data.decode("utf-8").strip()
        
        # Check if username is already taken and register the client if it is not
        with clients_lock:
            # Check if the username is already taken
            if username in clients:
                conn.sendall("ERROR: Username already taken. Please choose a different username.\n".encode('utf-8'))
                return
            
            # Register the client
            clients[username] = (conn, addr)

            # Print the client registration and the active users to the server console
            print(f"Client {addr} registered as: {username}")
            print(f"Active users: {list(clients.keys())}")
        
        # Send confirmation and list of available users to the freshly registered client
        conn.sendall(f"SUCCESS: You are registered as '{username}'\n".encode('utf-8'))
        conn.sendall("To send a message, use format: TARGET_USERNAME:your message here\n".encode('utf-8'))
        conn.sendall("Type 'list' to see online users, 'exit' to disconnect\n".encode('utf-8'))
        conn.sendall("Type 'everyone:<message>' to send a message to everyone\n".encode('utf-8'))
        
        # Construct the broadcast message to everyone
        broadcast_message = f"SYSTEM: {username} has joined the chat\n"
        with clients_lock:
            # Run over all the other clients and send the broadcast message to them
            for other_username, (other_conn, _) in clients.items():
                # Skip the newly registered client
                if other_username != username:
                    # Try to send the broadcast message to the other client
                    try:
                        other_conn.sendall(broadcast_message.encode('utf-8'))
                    except (ConnectionResetError, BrokenPipeError, OSError):
                        pass  # Client might have disconnected

        # ---Main SERVER loop --- receive messages from the client and handle special commands
        while True:
            # Receive data from the client (buffer size is 1024 bytes)
            data = conn.recv(1024) 
            # The incoming data is None, break the loop
            if not data:
                break

            # Decode the received bytes back into a readable string
            message = data.decode("utf-8").strip()

            # Print the message from the client to the server console
            print(f"Message from {username} ({addr}): {message}")

            # Handle special commands (For now it's exit and list)
            if message.lower() == "exit":
                # If the client wants to exit, break the loop and close the connection
                break
            elif message.lower() == "list":
                # If the client wants to list the online users, send the list to the client
                with clients_lock:
                    # Construct the list of online users
                    user_list = ", ".join(clients.keys())
                    # Send the list of online users to the client
                conn.sendall(f"Online users: {user_list}\n".encode('utf-8'))
                continue

            # Handle a user sending a "everyone" message
            elif message.lower().startswith("everyone:"):
                # Extract and broadcast message to everyone
                _, everyone_message = message.split(":", 1)
                everyone_message = everyone_message.strip()
                
                if not everyone_message:
                    conn.sendall("ERROR: Message cannot be empty\n".encode('utf-8'))
                    continue
                
                with clients_lock:
                    formatted_message = f"{username}: {everyone_message}\n"
                    for other_username, (other_conn, _) in clients.items():
                        try:
                            other_conn.sendall(formatted_message.encode('utf-8'))
                        except (ConnectionResetError, BrokenPipeError, OSError):
                            pass
                    conn.sendall("Message sent to everyone\n".encode('utf-8'))
                
                print(f"Broadcast from {username}: {everyone_message}")
                continue
            
            # Handle "direct" texts (not really, it's peer-server-peer)
            # Parse the peer-server-peer message format: "TARGET_USERNAME:message"
            if ":" not in message:
                conn.sendall("ERROR: Invalid format. Use 'TARGET_USERNAME:your message'\n".encode('utf-8'))
                continue
            
            # Split the message into the target username and the actual message
            target_username, actual_message = message.split(":", 1)
            target_username = target_username.strip()
            actual_message = actual_message.strip()
            
            # Check if the actual message is empty
            if not actual_message:
                conn.sendall("ERROR: Message cannot be empty\n".encode('utf-8'))
                continue
            
            # After handling the message, forward it to the target client
            with clients_lock:
                # Check if the target username is in the clients registry
                if target_username not in clients:
                    conn.sendall(f"ERROR: User '{target_username}' is not online. Type 'list' to see available users.\n".encode('utf-8'))
                    continue
                
                # Get the connection and address of the target client
                target_conn, _ = clients[target_username]

                try:
                    # Construct the forward message
                    forward_message = f"{username}: {actual_message}\n"
                    # Send the forward message to the target client
                    target_conn.sendall(forward_message.encode('utf-8'))
                    # Send confirmation message to the sender
                    conn.sendall(f"Message sent to {target_username}\n".encode('utf-8'))
                    # Print the forward message to the server console
                    print(f"Forwarded message from {username} to {target_username}")

                # If the forward message fails, send an error message to the sender

                except (ConnectionResetError, BrokenPipeError, OSError) as e:
                    conn.sendall(f"ERROR: Failed to send message to {target_username}\n".encode('utf-8'))
                    print(f"Error forwarding message: {e}")

    except ConnectionResetError:
        print(f"Client disconnected abruptly: {addr}")
    except (socket.error, UnicodeDecodeError, ValueError) as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        # Clean up - remove disconnecting client from registry
        if username:
            with clients_lock:
                # Search client in the clients registry
                if username in clients:
                    # remove it from the registry
                    del clients[username]

                    # Print client disconnection and the active users to the server console
                    print(f"Client {username} ({addr}) disconnected")
                    print(f"Active users: {list(clients.keys())}")
                    
                    # Construct the broadcast message to everyone
                    broadcast_message = f"SYSTEM: {username} left the chat\n"
                    # Run over all the other clients and send the broadcast message to them
                    for other_username, (other_conn, _) in clients.items():
                        if other_username != username:
                            try:
                                other_conn.sendall(broadcast_message.encode('utf-8'))
                            except (ConnectionResetError, BrokenPipeError, OSError):
                                pass  # probably because the client disconnected
        conn.close()


def start_server():
    """
    Sets up the server socket and listens for incoming connections.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow address reuse

    # Fix for port reuse error
    try:
        server_socket.bind((HOST, PORT))
    except OSError as e:
        print(f"Error: Port {PORT} is already in use. Please stop the other server or use a different port.")
        return
    server_socket.listen()
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        conn, addr = server_socket.accept() # pauses execution and waits for a new connection
        client_thread = threading.Thread(target=handle_client, args=(conn, addr)) # Create a new Thread to handle this client
        client_thread.start() # Start the thread
        print(f"Active clients: {threading.active_count() - 1}") # Print the number of active threads


if __name__ == "__main__":
    start_server()