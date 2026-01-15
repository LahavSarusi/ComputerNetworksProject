"""
Production server startup script - so we could run this server on Render.com
Runs both the TCP server and WebSocket bridge.
For production deployment (Render for backend, Netlify for frontend)
"""
import subprocess
import sys
import os
import signal
import time

# Processes to manage
processes = []

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully."""
    print("\nShutting down servers...")
    for process in processes:
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Start TCP server
print("Starting TCP server...")
tcp_process = subprocess.Popen(
    [sys.executable, "server.py"],
    cwd=os.path.dirname(__file__)
)
processes.append(tcp_process)

# Wait a moment for TCP server to start
time.sleep(2)

# Start WebSocket bridge
print("Starting WebSocket bridge...")
ws_process = subprocess.Popen(
    [sys.executable, "websocket_bridge.py"],
    cwd=os.path.dirname(__file__)
)
processes.append(ws_process)

print("Both servers are running!")
print(f"TCP Server: {os.environ.get('TCP_HOST', '127.0.0.1')}:{os.environ.get('TCP_PORT', '10000')}")
# PORT is Render's assigned port - prioritize it over WS_PORT
print(f"WebSocket Server: {os.environ.get('WS_HOST', '0.0.0.0')}:{os.environ.get('PORT', os.environ.get('WS_PORT', '8765'))}")

# Wait for processes (keep running until one exits)
try:
    # Wait for either process to exit
    while True:
        if tcp_process.poll() is not None:
            print("TCP server exited, shutting down...")
            break
        if ws_process.poll() is not None:
            print("WebSocket bridge exited, shutting down...")
            break
        time.sleep(1)
except KeyboardInterrupt:
    signal_handler(None, None)
finally:
    signal_handler(None, None)
