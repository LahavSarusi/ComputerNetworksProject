"""
TCP client for connecting to the chat server.
"""

import asyncio
import socket
import threading
from .config import TCP_HOST, TCP_PORT


class TCPClient:
    """Manages a TCP connection to the chat server for a WebSocket client."""
    
    def __init__(self, username: str, event_loop=None):
        self.username = username
        self.socket = None
        self.connected = False
        self.receive_thread = None
        self.message_queue = asyncio.Queue()
        self.event_loop = event_loop
    
    def connect(self) -> tuple[bool, str]:
        """Connect to TCP server and register username."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((TCP_HOST, TCP_PORT))
            
            # Receive welcome message
            self.socket.recv(1024)
            
            # Send username to register (server expects just the username, no newline)
            self.socket.sendall(self.username.encode('utf-8'))
            
            # Receive registration response
            response = self.socket.recv(1024).decode('utf-8')
            
            if "ERROR" in response:
                self.connected = False
                self.socket.close()
                return False, response.strip()
            
            # Mark as connected only after successful registration
            self.connected = True
            print(f"TCP client connected for user '{self.username}', connected={self.connected}")
            
            # Start receiving messages in background thread
            # Only start if we have an event loop
            if self.event_loop is not None:
                self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
                self.receive_thread.start()
                # Small delay to ensure thread is started
                import time
                time.sleep(0.05)
                print(f"TCP receive thread started for user '{self.username}'")
            else:
                print("Warning: No event loop provided, TCP receive thread not started")
            
            return True, response.strip()
            
        except Exception as e:
            self.connected = False
            if self.socket:
                self.socket.close()
            return False, f"Connection error: {str(e)}"
    
    def _receive_loop(self):
        """Receive messages from TCP server and add to async queue."""
        try:
            while self.connected and self.socket:
                try:
                    data = self.socket.recv(1024)
                    if not data:
                        break
                    
                    message = data.decode('utf-8')
                    # Get the event loop - use the one passed in constructor
                    loop = self.event_loop
                    if loop is None:
                        # Fallback: try to get the running loop
                        try:
                            loop = asyncio.get_running_loop()
                        except RuntimeError:
                            # If no running loop in this thread, we can't proceed
                            print("Warning: No event loop available for TCP message queue")
                            break
                    
                    # Schedule the coroutine to run in the event loop
                    # Don't wait for result to avoid blocking the receive thread
                    asyncio.run_coroutine_threadsafe(
                        self.message_queue.put(message),
                        loop
                    )
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Error receiving TCP data: {e}")
                    break
        except Exception as e:
            print(f"Error in receive loop: {e}")
        finally:
            self.connected = False
    
    def send_message(self, target: str, content: str) -> bool:
        """Send message to target user via TCP server."""
        if not self.connected or not self.socket:
            return False
        
        try:
            # Add newline to match server's expected format
            self.socket.sendall(f"{target}:{content}\n".encode('utf-8'))
            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            self.connected = False
            return False
    
    def send_command(self, command: str) -> bool:
        """Send command to TCP server."""
        print(f"send_command called: connected={self.connected}, socket={self.socket is not None}, command='{command}'")
        if not self.connected:
            print(f"Not connected, cannot send command '{command}'")
            return False
        if not self.socket:
            print(f"No socket, cannot send command '{command}'")
            return False
        
        try:
            # Add newline to match server's expected format
            self.socket.sendall(f"{command}\n".encode('utf-8'))
            print(f"Command '{command}' sent successfully")
            return True
        except Exception as e:
            print(f"Error sending command '{command}': {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from TCP server."""
        self.connected = False
        if self.socket:
            try:
                self.socket.sendall("exit".encode('utf-8'))
            except:
                pass
            self.socket.close()
