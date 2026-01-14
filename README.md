# Computer Networks Project

**Authors:** Gitam Shimoni and Lahav Sarusi

## Description

A simple client-server networking implementation using Python sockets with a modern React frontend. The server supports multiple concurrent clients using threading, and includes a WebSocket bridge to enable real-time chat through a web interface.

## Components

### Backend

- **Server** (`backend/server.py`): Multi-threaded TCP server that listens on port 10000 and handles client connections
- **Client** (`backend/client.py`): TCP client that connects to the server and enables bidirectional communication
- **WebSocket Bridge** (`backend/websocket_bridge.py`): Bridges WebSocket connections from the frontend to the TCP server
- **Demo** (`backend/demo.py`): Automated demo with multiple clients

### Frontend

- **React Chat Application** (`frontend-chat/`): Modern web-based chat interface built with React, TypeScript, Tailwind CSS, and shadcn/ui

## Setup

### Backend Setup

1. Install Python dependencies:

   ```bash
   pip install websockets
   ```

   Or use a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```

2. Start the TCP server:

   ```bash
   python backend/server.py
   ```

3. In a separate terminal, start the WebSocket bridge:
   ```bash
   python backend/websocket_bridge.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:

   ```bash
   cd frontend-chat
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Start the development server:

   ```bash
   npm run dev
   ```

4. Open your browser to the URL shown (typically `http://localhost:5173`)

## Usage

### Web Interface

1. Start both the TCP server and WebSocket bridge (see Setup above)
2. Start the frontend development server
3. Open the application in your browser
4. Enter a username on the login page
5. Once connected, you can:
   - See online users in the sidebar
   - Select a user from the dropdown or click on them in the user list
   - Send messages to other users
   - View message history
   - Disconnect when done

### Command Line Client

1. Start the TCP server:

   ```bash
   python backend/server.py
   ```

2. In another terminal, run the client:

   ```bash
   python backend/client.py
   ```

3. Enter your username when prompted
4. Send messages using format: `TARGET_USERNAME:your message here`
5. Type `list` to see online users
6. Type `exit` to disconnect

### Demo

Run the automated demo:

```bash
python backend/demo.py
```

## Architecture

```
Frontend (React) ←→ WebSocket Bridge (port 8765) ←→ TCP Server (port 10000)
```

The WebSocket bridge translates between:

- WebSocket JSON messages (frontend ↔ bridge)
- TCP text protocol (bridge ↔ TCP server)

## Features

- Real-time messaging between multiple users
- Username registration and validation
- Online users list
- System notifications (user joined/left)
- Modern, responsive UI
- Error handling and connection management

## Technology Stack

### Backend

- Python 3
- Socket programming
- Threading
- WebSockets (websockets library)

### Frontend

- React 19
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui components
- React Router
