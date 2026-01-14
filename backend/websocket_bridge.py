"""
Legacy entry point - redirects to new websocket package.
Run this file to start the WebSocket bridge server.
"""
import websockets
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from websocket.server import main

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down WebSocket bridge server...")
