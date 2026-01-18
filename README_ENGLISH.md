# TCP Chat System

**Gitam and Lahav present:** A Computer Networking class project - A real-time chat application with TCP backend and React frontend.

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start the Server

```bash
python server.py
```


### 3. Start the Client

You have two options to test the chat:

#### Option A: Terminal Client (Original)

```bash
python client.py
```

You can open as many terminal client instances as you'd like to test the core functionality!

#### Option B: Web Frontend (Bonus Feature!)

We built a nice-looking React GUI frontend! 🎨

**Note:** The project requirements were to build this **WITHOUT** websockets. **BUT**, to implement a nice looking GUI we were obligated to build it WITH websocket.
Because of that, We have added a BONUS (in addition to the original server.py) super simple WebSocket bridge that forwards messages in real-time - think of it as a bonus feature so you can test out our awesome frontend!

**Step 1:** Start the server with WebSocket bridge:

```bash
python start_for_frontend.py
```

This starts both the TCP server and WebSocket bridge.

**Step 2:** Start the frontend:

```bash
cd frontend-chat
npm install
npm run dev
```

Then open the app in your browser. You can open multiple browser tabs to simulate multiple users!

### 4. Bonus: Demo Script

Want to see it in action without manually testing? Run our demo:

```bash
cd backend
python demo.py
```

This automatically starts the server and connects 4 clients (Alice, Bob, Charlie, Diana) that have a conversation together. Perfect for seeing how everything works!

## Usage

### Terminal Client
1. Enter a username when prompted
2. Send messages using format: `username:your message`
3. Type `list` to see online users
4. Type `everyone:message` to broadcast to all users
5. Type `exit` to disconnect

### Web Frontend
1. Open the app in your browser
2. Enter a username to connect
3. Select a user or "Everyone" from the dropdown
4. Type your message and send

## Project Structure

- `backend/` - Python TCP server and WebSocket bridge
- `frontend-chat/` - React frontend application
- `client.py` - Terminal-based client

## Requirements

- Python 3.6+
- Node.js and npm (for frontend)
- `websockets` package (installed via requirements.txt)
