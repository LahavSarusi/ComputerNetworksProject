import { createContext, useContext } from "react";
import type { ReactNode } from "react";
import { useWebSocket } from "@/hooks/useWebSocket";
import type { ConnectionState, ChatMessageDisplay } from "@/types/chat";

interface WebSocketContextType {
  connectionState: ConnectionState;
  messages: ChatMessageDisplay[];
  onlineUsers: string[];
  connect: (username: string) => void;
  sendMessage: (target: string, content: string) => void;
  sendCommand: (command: "list" | "exit") => void;
  disconnect: () => void;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(
  undefined
);

/**
 * Provider component that wraps the app and provides WebSocket functionality
 */
export function WebSocketProvider({ children }: { children: ReactNode }) {
  const websocket = useWebSocket();

  return (
    <WebSocketContext.Provider value={websocket}>
      {children}
    </WebSocketContext.Provider>
  );
}

/**
 * Hook to access WebSocket context
 * @throws Error if used outside WebSocketProvider
 */
export function useWebSocketContext(): WebSocketContextType {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error(
      "useWebSocketContext must be used within a WebSocketProvider"
    );
  }
  return context;
}
