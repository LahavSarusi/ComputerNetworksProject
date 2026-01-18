"""
TCP client for connecting to the chat server.
"""

import asyncio
import socket
import threading
from .config import TCP_HOST, TCP_PORT


class TCPClient:
    """Manages a TCP connection to the chat server for a WebSocket client."""
    
    def __init__(self, username: str, event_loop):
        self.username = username
        self.socket = None
        self.connected = False
        self.message_queue = asyncio.Queue()
        self.event_loop = event_loop
    
    def connect(self) -> tuple[bool, str]:
        """Connect to TCP server and register username."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((TCP_HOST, TCP_PORT))
            self.socket.recv(1024)  # Welcome message
            self.socket.sendall(self.username.encode('utf-8'))
            
            response = self.socket.recv(1024).decode('utf-8')
            
            if "ERROR" in response:
                self.socket.close()
                return False, response.strip()
            
            self.connected = True
            threading.Thread(target=self._receive_loop, daemon=True).start()
            return True, response.strip()
            
        except Exception as e:
            if self.socket:
                self.socket.close()
            return False, f"Connection error: {str(e)}"
    
    def _receive_loop(self):
        """Receive messages from TCP server and add to async queue."""
        while self.connected and self.socket:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break
                asyncio.run_coroutine_threadsafe(
                    self.message_queue.put(data.decode('utf-8')),
                    self.event_loop
                )
            except:
                break
        self.connected = False
    
    def send_message(self, target: str, content: str) -> bool:
        """Send message to target user via TCP server."""
        if not self.connected or not self.socket:
            return False
        try:
            self.socket.sendall(f"{target}:{content}\n".encode('utf-8'))
            return True
        except:
            self.connected = False
            return False
    
    def send_command(self, command: str) -> bool:
        """Send command to TCP server."""
        if not self.connected or not self.socket:
            return False
        try:
            self.socket.sendall(f"{command}\n".encode('utf-8'))
            return True
        except:
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
