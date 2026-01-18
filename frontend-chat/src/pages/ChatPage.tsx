import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { MessageList } from "@/components/MessageList";
import { MessageInput } from "@/components/MessageInput";
import { UserList } from "@/components/UserList";
import { ConnectionStatus } from "@/components/ConnectionStatus";
import { useWebSocketContext } from "@/contexts/WebSocketContext";

/**
 * Main chat page component with message display and input
 * @returns Chat interface component
 */
export function ChatPage() {
  const navigate = useNavigate();
  const {
    connectionState,
    messages,
    onlineUsers,
    sendMessage,
    sendCommand,
    disconnect,
  } = useWebSocketContext();
  const [selectedUser, setSelectedUser] = useState<string | null>(null);

  // Redirect to login if not connected
  useEffect(() => {
    if (!connectionState.connected || !connectionState.username) {
      navigate("/");
    }
  }, [connectionState.connected, connectionState.username, navigate]);

  // Request user list on mount and periodically (every 5 seconds)
  useEffect(() => {
    if (connectionState.connected && connectionState.username) {
      // Small delay to ensure WebSocket is fully ready
      const timeoutId = setTimeout(() => {
        sendCommand("list");
      }, 200);

      const interval = setInterval(() => {
        if (connectionState.connected) {
          sendCommand("list");
        }
      }, 5000); // Refresh every 5 seconds

      return () => {
        clearTimeout(timeoutId);
        clearInterval(interval);
      };
    }
  }, [connectionState.connected, connectionState.username, sendCommand]);

  const handleDisconnect = () => {
    disconnect();
    navigate("/");
  };

  const handleSendMessage = (target: string, content: string) => {
    sendMessage(target, content);
  };

  // If not connected, return null (will redirect to login page)
  if (!connectionState.connected) {
    return null; // Will redirect
  }

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-slate-800 via-blue-900 to-slate-800">
      {/* Header */}
      <div className="bg-card border-b border-border p-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-bold text-foreground">
            Gitam And Lahav's Chat
          </h1>
          <ConnectionStatus
            connected={connectionState.connected}
            username={connectionState.username}
          />
          {connectionState.error && connectionState.connected && (
            <p className="text-sm text-destructive font-medium animate-pulse">
              {connectionState.error}
            </p>
          )}
        </div>
        <Button
          variant="outline"
          onClick={handleDisconnect}
          className="border-border text-foreground hover:bg-secondary"
        >
          Disconnect
        </Button>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex gap-4 p-4 min-h-0">
        {/* Chat Area */}
        <div className="flex-1 flex flex-col min-w-0">
          <MessageList
            messages={messages}
            currentUser={connectionState.username}
          />
          <div className="mt-4">
            <MessageInput
              onlineUsers={onlineUsers}
              currentUser={connectionState.username}
              onSendMessage={handleSendMessage}
              disabled={!connectionState.connected}
              selectedUser={selectedUser}
              onUserSelect={setSelectedUser}
            />
          </div>
        </div>

        {/* User List Sidebar */}
        <div className="w-64 min-w-64">
          <UserList
            users={onlineUsers}
            currentUser={connectionState.username}
            onSelectUser={setSelectedUser}
            selectedUser={selectedUser}
          />
        </div>
      </div>
    </div>
  );
}
