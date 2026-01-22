import { useState, useEffect, useRef, useCallback } from "react";
import type {
  ServerMessage,
  ChatMessageDisplay,
  ConnectionState,
} from "@/types/chat";

// WebSocket server URL
// TODO: Replace with your local machine's IP address (run 'ipconfig' in CMD to find it)
const WS_URL = "ws://192.168.0.11:8765";

/** Return type for useWebSocket hook */
interface UseWebSocketReturn {
  connectionState: ConnectionState;
  messages: ChatMessageDisplay[];
  onlineUsers: string[];
  connect: (username: string) => void;
  sendMessage: (target: string, content: string) => void;
  sendCommand: (command: "list" | "exit") => void;
  disconnect: () => void;
}

/**
 * Custom hook for managing WebSocket connection to chat server
 * @returns WebSocket connection state and methods
 */
export function useWebSocket(): UseWebSocketReturn {
  const [connectionState, setConnectionState] = useState<ConnectionState>({
    connected: false,
    username: null,
    error: null,
  });
  const [messages, setMessages] = useState<ChatMessageDisplay[]>([]);
  const [onlineUsers, setOnlineUsers] = useState<string[]>([]);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(
    null
  );
  const messageIdCounter = useRef(0);
  const connectedRef = useRef(false);

  /** Add a message to the messages list */
  const addMessage = useCallback((message: ChatMessageDisplay) => {
    setMessages((prev) => [...prev, message]);
  }, []);

  /** Handle incoming server messages and update state accordingly */
  const handleServerMessage = useCallback(
    (data: ServerMessage) => {
      // Clear any previous errors when receiving any message (except errors)
      if (data.type !== "error") {
        setConnectionState((prev) => {
          if (prev.error) {
            console.log("Clearing error due to successful message:", data.type);
            return { ...prev, error: null };
          }
          return prev;
        });
      }

      switch (data.type) {
        case "success":
          addMessage({
            id: `msg-${messageIdCounter.current++}`,
            type: "system",
            content: data.message,
            timestamp: new Date(),
          });
          break;

        case "error":
          setConnectionState((prev) => ({ ...prev, error: data.message }));
          addMessage({
            id: `msg-${messageIdCounter.current++}`,
            type: "system",
            content: `Error: ${data.message}`,
            timestamp: new Date(),
          });
          break;

        case "message":
          addMessage({
            id: `msg-${messageIdCounter.current++}`,
            type: "received",
            from: data.from,
            content: data.content,
            timestamp: new Date(),
          });
          break;

        case "system":
          addMessage({
            id: `msg-${messageIdCounter.current++}`,
            type: "system",
            content: data.message,
            timestamp: new Date(),
          });
          break;

        case "users":
          setOnlineUsers(data.users);
          // Clear error when we successfully receive user list (connection is working)
          setConnectionState((prev) => {
            if (prev.error && prev.connected) {
              console.log("Clearing error - received user list successfully");
              return { ...prev, error: null };
            }
            return prev;
          });
          break;
      }
    },
    [addMessage]
  );

  /**
   * Connect to WebSocket server and register username
   * @param username - Username to register with the server
   */
  const connect = useCallback(
    (username: string) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        return;
      }

      try {
        const ws = new WebSocket(WS_URL);
        wsRef.current = ws;

        ws.onopen = () => {
          console.log("WebSocket opened, sending registration...");
          connectedRef.current = false;
          setConnectionState({
            connected: false, // Not connected until registration succeeds
            username: null,
            error: null,
          });

          // Send registration message
          try {
            ws.send(
              JSON.stringify({
                type: "register",
                username,
              })
            );
            console.log("Registration message sent for username:", username);
          } catch (error) {
            console.error("Error sending registration:", error);
            setConnectionState((prev) => ({
              ...prev,
              error: "Failed to send registration",
            }));
          }
        };

        ws.onmessage = (event) => {
          try {
            const data: ServerMessage = JSON.parse(event.data);
            console.log("Received message from server:", data);

            // Handle messages that don't have a message property (like "users")
            if (data.type === "users") {
              handleServerMessage(data);
              return;
            }

            // Handle registration response
            // Check for successful registration (server sends "SUCCESS: You are registered as...")
            // Only check message property if it exists
            if (data.type === "success" && "message" in data) {
              const messageLower = data.message.toLowerCase();
              if (
                messageLower.includes("registered") ||
                messageLower.includes("success")
              ) {
                console.log("Registration successful:", data.message);
                console.log("WebSocket state:", {
                  exists: !!wsRef.current,
                  readyState: wsRef.current?.readyState,
                });
                connectedRef.current = true;
                setConnectionState({
                  connected: true,
                  username,
                  error: null,
                });
                // Request user list after a delay to ensure TCP client is fully ready on backend
                // The backend needs time to fully establish the TCP connection and start the receive thread
                setTimeout(() => {
                  if (wsRef.current?.readyState === WebSocket.OPEN) {
                    console.log("Sending initial list command");
                    wsRef.current.send(
                      JSON.stringify({ type: "command", command: "list" })
                    );
                  } else {
                    console.warn(
                      "Cannot send initial list command - WebSocket not open",
                      {
                        readyState: wsRef.current?.readyState,
                      }
                    );
                  }
                }, 500); // Increased delay to ensure backend TCP client is ready
              }
            } else if (
              data.type === "error" &&
              "message" in data &&
              (data.message.includes("Username") ||
                data.message.includes("ERROR") ||
                data.message.toLowerCase().includes("error"))
            ) {
              connectedRef.current = false;
              setConnectionState({
                connected: false,
                username: null,
                error: data.message,
              });
              ws.close();
            } else {
              // Handle all other messages normally
              handleServerMessage(data);
            }
          } catch (error) {
            console.error("Error parsing server message:", error, event.data);
            setConnectionState((prev) => ({
              ...prev,
              error: "Failed to parse server response",
            }));
          }
        };

        ws.onerror = (error) => {
          console.error("WebSocket error:", error);
          connectedRef.current = false;
          setConnectionState((prev) => ({
            ...prev,
            connected: false,
            error:
              "Failed to connect to server. Please make sure the server is running.",
          }));
        };

        ws.onclose = (event) => {
          console.log("WebSocket closed", {
            code: event.code,
            reason: event.reason,
            wasClean: event.wasClean,
            wasConnected: connectedRef.current,
          });
          const wasConnected = connectedRef.current;
          connectedRef.current = false;
          setConnectionState((prev) => ({
            ...prev,
            connected: false,
            // Only set error if we were previously connected and it wasn't a clean close
            error:
              wasConnected && !event.wasClean
                ? "Connection lost. Please try reconnecting."
                : null,
          }));
          wsRef.current = null;
        };
      } catch (error) {
        console.error("Failed to create WebSocket:", error);
        connectedRef.current = false;
        setConnectionState((prev) => ({
          ...prev,
          connected: false,
          error:
            "Failed to connect to server. Please check if the server is running.",
        }));
      }
    },
    [handleServerMessage]
  );

  /**
   * Send a chat message to a target user
   * @param target - Username of the recipient
   * @param content - Message content
   */
  const sendMessage = useCallback(
    (target: string, content: string) => {
      if (!wsRef.current) {
        console.warn("Cannot send message: WebSocket ref is null");
        if (connectionState.connected) {
          setConnectionState((prev) => ({
            ...prev,
            error: "Not connected to server. Please try again.",
          }));
        }
        return;
      }

      if (wsRef.current.readyState !== WebSocket.OPEN) {
        console.warn("Cannot send message: WebSocket not open", {
          readyState: wsRef.current.readyState,
          readyStateName:
            wsRef.current.readyState === WebSocket.CONNECTING
              ? "CONNECTING"
              : wsRef.current.readyState === WebSocket.OPEN
              ? "OPEN"
              : wsRef.current.readyState === WebSocket.CLOSING
              ? "CLOSING"
              : wsRef.current.readyState === WebSocket.CLOSED
              ? "CLOSED"
              : "UNKNOWN",
          connected: connectionState.connected,
        });
        // Only set error if we're supposed to be connected and this is a user-initiated action
        if (connectionState.connected) {
          setConnectionState((prev) => ({
            ...prev,
            error: "Not connected to server. Please try again.",
          }));
        }
        return;
      }

      try {
        wsRef.current.send(
          JSON.stringify({
            type: "message",
            target,
            content,
          })
        );

        // Add sent message to UI immediately
        addMessage({
          id: `msg-${messageIdCounter.current++}`,
          type: "sent",
          to: target,
          content,
          timestamp: new Date(),
        });
      } catch (error) {
        console.error("Error sending message:", error);
        setConnectionState((prev) => ({
          ...prev,
          error: "Failed to send message",
        }));
      }
    },
    [addMessage, connectionState.connected]
  );

  /**
   * Send a command to the server
   * @param command - Command to send ("list" or "exit")
   */
  const sendCommand = useCallback(
    (command: "list" | "exit") => {
      if (!wsRef.current) {
        console.warn("Cannot send command: WebSocket ref is null", { command });
        return;
      }

      if (wsRef.current.readyState !== WebSocket.OPEN) {
        console.warn("Cannot send command: WebSocket not open", {
          command,
          readyState: wsRef.current.readyState,
          readyStateName:
            wsRef.current.readyState === WebSocket.CONNECTING
              ? "CONNECTING"
              : wsRef.current.readyState === WebSocket.OPEN
              ? "OPEN"
              : wsRef.current.readyState === WebSocket.CLOSING
              ? "CLOSING"
              : wsRef.current.readyState === WebSocket.CLOSED
              ? "CLOSED"
              : "UNKNOWN",
          connected: connectionState.connected,
        });
        // Don't set error for commands - they're automatic and non-critical
        return;
      }

      try {
        wsRef.current.send(
          JSON.stringify({
            type: "command",
            command,
          })
        );
        console.log("Command sent successfully:", command);
      } catch (error) {
        console.error("Error sending command:", error);
        // Only set error if we're supposed to be connected
        if (connectionState.connected) {
          setConnectionState((prev) => ({
            ...prev,
            error: "Failed to send command",
          }));
        }
      }
    },
    [connectionState.connected]
  );

  /** Disconnect from WebSocket server and reset state */
  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.send(JSON.stringify({ type: "disconnect" }));
      wsRef.current.close();
      wsRef.current = null;
    }
    connectedRef.current = false;
    setConnectionState({
      connected: false,
      username: null,
      error: null,
    });
    setMessages([]);
    setOnlineUsers([]);
  }, []);

  // Cleanup on unmount - only close if explicitly disconnecting
  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      // Don't close WebSocket on unmount - let it persist across route changes
      // Only close if the component is truly unmounting (app closing)
    };
  }, []);

  return {
    connectionState,
    messages,
    onlineUsers,
    connect,
    sendMessage,
    sendCommand,
    disconnect,
  };
}
