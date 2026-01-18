import socket
import threading


HOST = "127.0.0.1"  # The target server's IP address.
PORT = 10000


def receive_messages(client_socket):
    """
    Continuously receive messages from the server in a separate thread.
    This allows the client to receive messages while the user is typing.
    """
    try:
        # Main loop: receive messages from the server
        while True:
            # Receive data from the server (buffer size is 1024 bytes)
            data = client_socket.recv(1024)
            if not data:
                print("\nConnection closed by server.")
                break
            
            # Decode the received bytes back into a readable string
            message = data.decode('utf-8')
            # Print received messages (from other clients or server notifications)
            print(f"\n{message}", end="")
            print("You: ", end="", flush=True)  # Re-print prompt
            
    except (ConnectionResetError, OSError):
        # TODO: Lahav - This happens when client disconnects, so we don't need to print an error or do anything
        pass
    except Exception as e:
        # only print unexpected errors
        print(f"\nUnexpected error receiving messages: {e}")


def start_client():
    """
    Sets up the client socket and connects to the server.
    """
    # Create the client socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((HOST, PORT)) # Attempt to connect to the server
        print(f"Connected to server at: {HOST}:{PORT}")

        # Receive welcome message and username prompt
        welcome = client_socket.recv(1024).decode('utf-8')
        print(f"{welcome}", end="")
        
        # Get username from user
        username = input().strip()
        if not username:
            print("Username cannot be empty!")
            return
        
        # Send username to server
        client_socket.sendall(username.encode('utf-8'))
        
        # Receive registration confirmation
        response = client_socket.recv(1024).decode('utf-8')
        print(f"{response}", end="")
        
        # Start a thread to receive messages from other clients (even when typing)
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,), daemon=True)
        receive_thread.start()
        
        # Print the instructions for the user
        print("\nYou can now chat! Use format: TARGET_USERNAME:your message")
        print("Type 'list' to see online users, 'exit' to disconnect\n")
        
        # Main loop: send messages to other clients
        while True:
            message = input("You: ")
            
            if message.lower() == "exit":
                try:
                    client_socket.sendall("exit".encode('utf-8'))
                except:
                    pass  # TODO: Lahav - probably because the socket is already closed
                break

            # Send message to server (which will forward to target client)
            # The receive_thread will handle all incoming responses
            try:
                client_socket.sendall(message.encode('utf-8'))
            except (OSError, ConnectionResetError):
                print("\nConnection lost. Exiting...")
                break

    except ConnectionRefusedError:
        print("Connection failed. Is the server running?")
    except KeyboardInterrupt:
        print("\nDisconnecting...")
        try:
            client_socket.sendall("exit".encode('utf-8'))
        except:
            pass
    finally:
        # Shutdown socket before closing to signal the receive thread
        try:
            client_socket.shutdown(socket.SHUT_RDWR)
        except:
            pass
        client_socket.close()
        print("Disconnected from server.")


if __name__ == "__main__":
    start_client()