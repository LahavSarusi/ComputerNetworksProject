"""
Configuration constants for WebSocket bridge.
"""
import os

# TCP server connection settings
TCP_HOST = os.environ.get("TCP_HOST", "127.0.0.1")
TCP_PORT = int(os.environ.get("TCP_PORT", "10000"))

# WebSocket server settings
WS_HOST = os.environ.get("WS_HOST", "0.0.0.0")  # 0.0.0.0 for production
# Render provides $PORT automatically - prioritize it over WS_PORT for production
WS_PORT = int(os.environ.get("PORT", os.environ.get("WS_PORT", "8765")))  # Render uses $PORT
