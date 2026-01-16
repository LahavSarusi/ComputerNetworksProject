import socket
import threading

HOST = "192.168.0.11" # The target server's IP address.
PORT = 10000


def receive_messages(client_socket):
    """
    Runs in a separate thread to listen for incoming messages from the server.
    This allows receiving messages even while the user is typing.
    """
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                print("\n[DISCONNECTED] Server closed connection.")
                client_socket.close()
                break
            print(f"\n{message}\nYour message: ", end="")
        except:
            print("\n[ERROR] An error occurred while receiving data.")
            client_socket.close()
            break


def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        print(f"Attempting to connect to {HOST}:{PORT}...")
        client_socket.connect((HOST, PORT))

        # Receive the "Enter your username" prompt
        initial_msg = client_socket.recv(1024).decode('utf-8')
        print(initial_msg, end="")

        # Send the username
        username = input()
        client_socket.sendall(username.encode('utf-8'))

        # Start a thread to listen for incoming messages
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.daemon = True  # Thread ends when the main program ends
        receive_thread.start()

        # Main loop for sending messages
        while True:
            msg = input("Your message (format: User:Msg or 'exit'): ")
            if msg.lower() == 'exit':
                break
            client_socket.sendall(msg.encode('utf-8'))

    except ConnectionRefusedError:
        print("Connection failed. Check IP address and ensure server is running.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        print("Client closed.")


if __name__ == "__main__":
    start_client()