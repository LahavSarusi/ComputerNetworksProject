import { useState, useEffect } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useWebSocketContext } from "@/contexts/WebSocketContext";
import { useToast } from "@/hooks/useToast";

/**
 * Login page component for username entry and server connection
 * @returns Login form component
 */
export function LoginPage() {
  const [username, setUsername] = useState("");
  const [isConnecting, setIsConnecting] = useState(false);
  const navigate = useNavigate();
  const { connect, connectionState } = useWebSocketContext();
  const { showSuccessToast } = useToast();

  // Navigate to chat when successfully connected
  useEffect(() => {
    console.log("Connection state changed:", connectionState);
    if (
      connectionState.connected &&
      connectionState.username &&
      !connectionState.error
    ) {
      console.log("Navigating to chat page");
      showSuccessToast(
        `Welcome, ${connectionState.username}! Successfully connected to chat.`
      );
      navigate("/chat");
    } else if (connectionState.error && isConnecting) {
      console.log("Connection error:", connectionState.error);
      setIsConnecting(false);
    }
  }, [
    connectionState.connected,
    connectionState.username,
    connectionState.error,
    navigate,
    isConnecting,
    showSuccessToast,
  ]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!username.trim()) {
      return;
    }

    setIsConnecting(true);
    connect(username.trim());
  };

  return (
    <div className="min-h-screen flex flex-col bg-linear-to-br from-slate-800 via-blue-900 to-slate-800">
      {/* Header */}
      <div className="bg-card border-b border-border p-4">
        <h1 className="text-3xl font-bold text-center text-foreground">
          Gitam And Lahav's Chat
        </h1>
      </div>

      {/* Login Card */}
      <div className="flex-1 flex items-center justify-center p-4">
        <Card className="w-full max-w-md shadow-2xl border-2">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl font-bold text-center text-foreground">
              Join Chat
            </CardTitle>
            <CardDescription className="text-center text-muted-foreground">
              Enter your username to connect to the chat server
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Input
                  type="text"
                  placeholder="Enter your username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  disabled={isConnecting}
                  className="w-full bg-input text-foreground placeholder:text-muted-foreground"
                  autoFocus
                />
                {connectionState.error && (
                  <p className="text-sm text-destructive mt-2 font-medium">
                    {connectionState.error}
                  </p>
                )}
              </div>
              <Button
                type="submit"
                className="w-full bg-primary text-primary-foreground hover:opacity-90"
                disabled={isConnecting || !username.trim()}
              >
                {isConnecting ? "Connecting..." : "Connect"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
