"""
WebSocket connection handler for frontend clients.
"""

import asyncio
import json
import websockets
from .tcp_client import TCPClient


def _parse_tcp_message(message: str) -> dict:
    """Parse TCP server message and convert to WebSocket JSON format."""
    msg = message.strip()
    
    if msg.startswith("SYSTEM:"):
        return {"type": "system", "message": msg}
    if msg.startswith("Online users:"):
        users = [u.strip() for u in msg.replace("Online users:", "").split(",") if u.strip()]
        return {"type": "users", "users": users}
    if msg.startswith("ERROR:"):
        return {"type": "error", "message": msg.replace("ERROR:", "").strip()}
    if msg.startswith("Message sent to"):
        return {"type": "success", "message": msg}
    if ":" in msg and not msg.startswith("SUCCESS:"):
        parts = msg.split(":", 1)
        if len(parts) == 2:
            return {"type": "message", "from": parts[0].strip(), "content": parts[1].strip()}
    
    return {"type": "system", "message": msg} if msg else None


async def _process_tcp_messages(tcp_client: TCPClient, websocket):
    """Process messages from TCP server and forward to WebSocket client."""
    while tcp_client.connected:
        try:
            message = await asyncio.wait_for(tcp_client.message_queue.get(), timeout=0.1)
            parsed = _parse_tcp_message(message)
            if parsed:
                await websocket.send(json.dumps(parsed))
        except asyncio.TimeoutError:
            continue
        except:
            break


async def handle_websocket(websocket, path):
    """Handle a WebSocket connection from the frontend."""
    tcp_client = None
    tcp_task = None
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                msg_type = data.get("type")
                
                if msg_type == "register":
                    username = data.get("username", "").strip()
                    if not username:
                        await websocket.send(json.dumps({"type": "error", "message": "Username cannot be empty"}))
                        continue
                    
                    tcp_client = TCPClient(username, asyncio.get_event_loop())
                    success, response = tcp_client.connect()
                    
                    if success and tcp_client.connected:
                        await websocket.send(json.dumps({"type": "success", "message": response}))
                        tcp_task = asyncio.create_task(_process_tcp_messages(tcp_client, websocket))
                    else:
                        await websocket.send(json.dumps({"type": "error", "message": response}))
                        tcp_client = None
                
                elif msg_type == "message":
                    if not tcp_client or not tcp_client.connected:
                        await websocket.send(json.dumps({"type": "error", "message": "Not connected"}))
                        continue
                    
                    target = data.get("target", "").strip()
                    content = data.get("content", "").strip()
                    if target and content:
                        tcp_client.send_message(target, content)
                
                elif msg_type == "command":
                    if tcp_client and tcp_client.connected:
                        tcp_client.send_command(data.get("command", "").strip().lower())
                
                elif msg_type == "disconnect":
                    break
                    
            except json.JSONDecodeError:
                await websocket.send(json.dumps({"type": "error", "message": "Invalid JSON"}))
            except Exception as e:
                await websocket.send(json.dumps({"type": "error", "message": str(e)}))
                
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if tcp_task:
            tcp_task.cancel()
        if tcp_client:
            tcp_client.disconnect()
