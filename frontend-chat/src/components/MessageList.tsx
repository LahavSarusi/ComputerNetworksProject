import { useEffect, useRef } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { ChatMessageDisplay } from "@/types/chat";
import { formatTime } from "@/lib/utils";

interface MessageListProps {
  messages: ChatMessageDisplay[];
  currentUser: string | null;
}

/**
 * Component to display chat messages with auto-scroll
 * @param messages - Array of messages to display
 * @param currentUser - Current user's username
 * @returns Message list component
 */
export function MessageList({ messages, currentUser }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <Card className="flex-1 flex flex-col min-h-0 bg-card border-border">
      <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            <p className="text-base">No messages yet. Start a conversation!</p>
          </div>
        ) : (
          messages.map((message) => {
            if (message.type === "system") {
              return (
                <div key={message.id} className="flex justify-center">
                  <Badge
                    variant="outline"
                    className="text-xs bg-secondary text-secondary-foreground border-border"
                  >
                    {message.content}
                  </Badge>
                </div>
              );
            }

            const isSent = message.type === "sent";
            const senderName = isSent ? currentUser : message.from;

            return (
              <div
                key={message.id}
                className={`flex flex-col ${
                  isSent ? "items-end" : "items-start"
                }`}
              >
                <div
                  className={`max-w-[70%] rounded-lg p-3 ${
                    isSent
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted text-foreground"
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span
                      className={`text-xs font-semibold ${
                        isSent ? "opacity-95" : "opacity-90"
                      }`}
                    >
                      {isSent ? "You" : senderName}
                      {message.to && ` → ${message.to}`}
                    </span>
                  </div>
                  <p
                    className={`text-sm whitespace-pre-wrap break-words ${
                      isSent ? "text-primary-foreground" : "text-foreground"
                    }`}
                  >
                    {message.content}
                  </p>
                  <span
                    className={`text-xs mt-1 block ${
                      isSent
                        ? "opacity-80 text-primary-foreground"
                        : "opacity-75 text-muted-foreground"
                    }`}
                  >
                    {formatTime(message.timestamp)}
                  </span>
                </div>
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </CardContent>
    </Card>
  );
}
