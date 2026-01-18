"""
Simple startup script - runs both TCP server and WebSocket bridge.
Press Ctrl+C to stop both servers.
"""
import subprocess
import sys
import os
import signal

# Check for required dependencies
def check_dependencies():
    """Check if required packages are installed."""
    try:
        import websockets
    except ImportError:
        print("ERROR: Missing required dependency 'websockets'")
        print("\nPlease install dependencies first:")
        print("  pip install -r requirements.txt")
        sys.exit(1)

check_dependencies()

processes = []

def cleanup():
    """Stop all running processes."""
    print("\nShutting down servers...")
    for p in processes:
        try:
            p.terminate()
            p.wait(timeout=3)
        except:
            p.kill()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

# Start TCP server
print("Starting TCP server...")
tcp = subprocess.Popen([sys.executable, "server.py"], cwd=os.path.dirname(__file__))
processes.append(tcp)

# Wait for TCP server to start
import time
time.sleep(1)

if tcp.poll() is not None:
    print(f"ERROR: TCP server failed to start")
    cleanup()

# Start WebSocket bridge
print("Starting WebSocket bridge...")
ws_path = os.path.join(os.path.dirname(__file__), "websocket", "websocket_bridge.py")
ws = subprocess.Popen([sys.executable, ws_path], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
processes.append(ws)

time.sleep(1)

if ws.poll() is not None:
    print(f"ERROR: WebSocket bridge failed to start")
    stderr_output = ws.stderr.read().decode('utf-8') if ws.stderr else ""
    if stderr_output:
        print("\nError details:")
        print(stderr_output)
    cleanup()

print("\n✓ Both servers are running!")
print("  TCP Server: 127.0.0.1:10000")
print("  WebSocket: ws://127.0.0.1:8765")
print("\nPress Ctrl+C to stop\n")

# Keep running until interrupted
try:
    while True:
        if tcp.poll() is not None or ws.poll() is not None:
            break
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    cleanup()
