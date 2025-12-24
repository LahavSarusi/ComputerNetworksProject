# Computer Networks Project

**Authors:** Gitam Shimoni and Lahav Sarusi

## Description

A simple client-server networking implementation using Python sockets. The server supports multiple concurrent clients using threading, and the client can send messages to the server which responds by echoing them back in uppercase.

## Components

- **Server** (`backend/server.py`): Multi-threaded TCP server that listens on port 10000 and handles client connections
- **Client** (`backend/client.py`): TCP client that connects to the server and enables bidirectional communication

## Usage

1. Start the server: `python backend/server.py`
2. Run the client: `python backend/client.py`

## To be implemented -

Need to build the frontend, we will probably use React for that to create a super simple nice looking UI for a chat app.
