"""
Main WebSocket bridge server entry point.
"""

import asyncio
from websockets.server import serve
from .config import TCP_HOST, TCP_PORT, WS_HOST, WS_PORT
from .websocket_handler import handle_websocket


async def main():
    """Start the WebSocket bridge server."""
    print(f"WebSocket bridge server starting on ws://{WS_HOST}:{WS_PORT}")
    print(f"Connecting to TCP server at {TCP_HOST}:{TCP_PORT}")
    
    # Start WebSocket server and run forever
    async with serve(handle_websocket, WS_HOST, WS_PORT):
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    try:
        # Run the server
        asyncio.run(main())
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\nShutting down WebSocket bridge server...")
