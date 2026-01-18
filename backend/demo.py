import socket
import threading
import time
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HOST = "127.0.0.1"
PORT = 10000

# Import server function
try:
    from server import start_server
except ImportError:
    print("Error: Could not import server. Make sure server.py is in the same directory.")
    sys.exit(1)

# Regular names
CLIENT_NAMES = ["Alice", "Bob", "Charlie", "Diana"]

# Sequential conversation script - each entry is (sender_index, target_name, message, delay_after)
# This ensures the conversation flows naturally
CONVERSATION_SCRIPT = [
    (0, "Bob", "Hey Bob, how's your day going?", 2),
    (1, "Alice", "Hi Alice! It's going well, thanks for asking. How about you?", 2),
    (0, "Bob", "I'm doing great, thanks!", 2),
    (0, "Charlie", "Charlie, did you finish that project we discussed?", 2),
    (2, "Alice", "Yes, I finished it yesterday. Thanks for checking!", 2),
    (1, "Charlie", "Charlie, what time is the meeting today?", 2),
    (2, "Bob", "The meeting is at 3 PM in the conference room", 2),
    (1, "Diana", "Diana, did you see the email about the schedule change?", 2),
    (3, "Bob", "Yes, I saw it. Thanks for the heads up!", 2),
    (0, "Diana", "Diana, are we still meeting for lunch tomorrow?", 2),
    (3, "Alice", "Yes, lunch tomorrow sounds great! See you at noon", 2),
    (2, "Diana", "Diana, can you send me those files when you get a chance?", 2),
    (3, "Charlie", "Sure, I'll send them over in a few minutes", 2),
]


def automated_client(name, client_socket):
    """
    Creates an automated client that connects, registers, and can send messages.
    """
    try:
        # Receive welcome message
        welcome = client_socket.recv(1024).decode('utf-8')
        
        # Send username
        client_socket.sendall(name.encode('utf-8'))
        
        # Receive registration confirmation
        response = client_socket.recv(1024).decode('utf-8')
        print(f"[{name}] Connected!")
        
        # Start receiving thread
        def receive():
            try:
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    message = data.decode('utf-8')
                    if not message.startswith("SYSTEM:") and not message.startswith("Message sent"):
                        print(f"[{name}] Received: {message.strip()}")
            except:
                pass
        
        receive_thread = threading.Thread(target=receive, daemon=True)
        receive_thread.start()
        
        # Return the socket so the main thread can send messages
        return client_socket
        
    except Exception as e:
        print(f"[{name}] Error: {e}")
        return None


def demo():
    """
    Demo that initializes server and 4 clients having a regular conversation.
    """
    print("=" * 60)
    print("Chat Server Demo")
    print("=" * 60)
    print("\nStarting server...")
    
    # Start server in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(1)
    print("Server started!\n")
    
    print("Connecting clients...\n")
    
    # Connect all clients first
    client_sockets = {}
    for i, name in enumerate(CLIENT_NAMES):
        time.sleep(0.3)  # Stagger connections
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((HOST, PORT))
            client_sockets[name] = automated_client(name, sock)
        except Exception as e:
            print(f"Error connecting {name}: {e}")
    
    # Wait for all clients to be ready
    time.sleep(1)
    print("\nStarting conversation...\n")
    
    # Execute conversation script sequentially
    for sender_idx, target_name, message, delay in CONVERSATION_SCRIPT:
        sender_name = CLIENT_NAMES[sender_idx]
        if sender_name in client_sockets and client_sockets[sender_name]:
            full_message = f"{target_name}:{message}"
            try:
                client_sockets[sender_name].sendall(full_message.encode('utf-8'))
                print(f"[{sender_name}] → {target_name}: {message}")
            except Exception as e:
                print(f"Error sending from {sender_name}: {e}")
        time.sleep(delay)
    
    # Keep connection alive to see final messages
    time.sleep(2)
    
    # Disconnect all clients
    print("\nDisconnecting clients...\n")
    for name, sock in client_sockets.items():
        if sock:
            try:
                sock.sendall("exit".encode('utf-8'))
                sock.close()
                print(f"[{name}] Disconnected")
            except:
                pass
    
    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    demo()

