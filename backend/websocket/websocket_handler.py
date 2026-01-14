"""
WebSocket connection handler for frontend clients.
Handles WebSocket connections and bridges them to the TCP chat server.
"""

import asyncio
import json
import websockets
from .tcp_client import TCPClient


def _parse_tcp_message(message: str) -> dict:
    """Parse TCP server message and convert to WebSocket JSON format."""
    message = message.strip()
    
    if message.startswith("SYSTEM:"):
        return {"type": "system", "message": message}
    elif message.startswith("Online users:"):
        users = [u.strip() for u in message.replace("Online users:", "").split(",") if u.strip()]
        return {"type": "users", "users": users}
    elif message.startswith("ERROR:"):
        return {"type": "error", "message": message.replace("ERROR:", "").strip()}
    elif message.startswith("Message sent to"):
        return {"type": "success", "message": message}
    elif ":" in message and not message.startswith("SUCCESS:"):
        # Regular chat message: "username: content"
        parts = message.split(":", 1)
        if len(parts) == 2:
            return {"type": "message", "from": parts[0].strip(), "content": parts[1].strip()}
    
    # Default: treat as system message
    return {"type": "system", "message": message} if message else None


async def _process_tcp_messages(tcp_client: TCPClient, websocket):
    """Process messages from TCP server and forward to WebSocket client."""
    while tcp_client and tcp_client.connected:
        try:
            message = await asyncio.wait_for(tcp_client.message_queue.get(), timeout=0.1)
            parsed = _parse_tcp_message(message)
            if parsed:
                await websocket.send(json.dumps(parsed))
        except asyncio.TimeoutError:
            continue
        except Exception as e:
            print(f"Error processing TCP message: {e}")
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
                        await websocket.send(json.dumps({
                            "type": "error",
                            "message": "Username cannot be empty"
                        }))
                        continue
                    
                    # Pass the event loop to TCPClient so it can properly schedule coroutines
                    loop = asyncio.get_event_loop()
                    tcp_client = TCPClient(username, event_loop=loop)
                    success, response = tcp_client.connect()
                    
                    if success:
                        # Verify connection is actually established
                        if not tcp_client.connected:
                            await websocket.send(json.dumps({
                                "type": "error",
                                "message": "Failed to establish TCP connection"
                            }))
                            tcp_client = None
                            continue
                        
                        # Small delay to ensure TCP connection and receive thread are fully established
                        await asyncio.sleep(0.2)
                        await websocket.send(json.dumps({
                            "type": "success",
                            "message": response
                        }))
                        tcp_task = asyncio.create_task(_process_tcp_messages(tcp_client, websocket))
                    else:
                        await websocket.send(json.dumps({
                            "type": "error",
                            "message": response
                        }))
                        tcp_client = None
                
                elif msg_type == "message":
                    if not tcp_client or not tcp_client.connected:
                        await websocket.send(json.dumps({
                            "type": "error",
                            "message": "Not connected to server"
                        }))
                        continue
                    
                    target = data.get("target", "").strip()
                    content = data.get("content", "").strip()
                    
                    if not target or not content:
                        await websocket.send(json.dumps({
                            "type": "error",
                            "message": "Target and content are required"
                        }))
                        continue
                    
                    tcp_client.send_message(target, content)
                
                elif msg_type == "command":
                    if not tcp_client:
                        await websocket.send(json.dumps({
                            "type": "error",
                            "message": "Not registered. Please register first."
                        }))
                        continue
                    
                    # Debug logging
                    print(f"Command received: {data.get('command')}, TCP client connected: {tcp_client.connected}, socket exists: {tcp_client.socket is not None}")
                    
                    if not tcp_client.connected:
                        print(f"TCP client not connected. Socket state: {tcp_client.socket is not None}")
                        await websocket.send(json.dumps({
                            "type": "error",
                            "message": "TCP connection not established"
                        }))
                        continue
                    
                    command = data.get("command", "").strip().lower()
                    success = tcp_client.send_command(command)
                    if not success:
                        print(f"Failed to send command '{command}' to TCP server")
                        await websocket.send(json.dumps({
                            "type": "error",
                            "message": "Failed to send command to server"
                        }))
                
                elif msg_type == "disconnect":
                    break
                    
            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
            except Exception as e:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": f"Error: {str(e)}"
                }))
                
    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if tcp_task:
            tcp_task.cancel()
        if tcp_client:
            tcp_client.disconnect()
