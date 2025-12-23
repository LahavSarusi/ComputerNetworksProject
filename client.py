import socket


HOST = "192.168.0.11" # The target server's IP address.
PORT = 10000


def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create the client socket

    try:
        client_socket.connect((HOST, PORT)) # Attempt to connect to the server
        print(f"Connected to server at: {HOST}:{PORT}")

        welcome = client_socket.recv(1024).decode('utf-8') # We read up to 1024 bytes and decode them from bytes to a string
        print(f"Server says: {welcome}")

        while True:
            message = input("Send message to server or type 'exit': ")
            if message.lower() == "exit":
                break

            client_socket.sendall(message.encode('utf-8')) # Send the message to the server

            response = client_socket.recv(1024).decode('utf-8') # Wait for the server's response
            print(f"Server response: {response}")

    except ConnectionRefusedError:
        print("Connection failed. Is the server running?")

    finally:
        client_socket.close()


if __name__ == "__main__":
    start_client()