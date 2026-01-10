import { useState, useEffect } from "react";
import type { FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface MessageInputProps {
  onlineUsers: string[];
  currentUser: string | null;
  onSendMessage: (target: string, content: string) => void;
  disabled?: boolean;
  selectedUser?: string | null;
  onUserSelect?: (user: string) => void;
}

/**
 * Message input component with user selector and send button
 * @param onlineUsers - List of online users
 * @param currentUser - Current user's username
 * @param onSendMessage - Callback when message is sent
 * @param disabled - Whether input is disabled
 * @param selectedUser - Currently selected target user
 * @param onUserSelect - Callback when user is selected
 * @returns Message input form component
 */
export function MessageInput({
  onlineUsers,
  currentUser,
  onSendMessage,
  disabled,
  selectedUser,
  onUserSelect,
}: MessageInputProps) {
  const [target, setTarget] = useState<string>(selectedUser || "");
  const [content, setContent] = useState("");

  // Update target when selectedUser changes
  useEffect(() => {
    if (selectedUser) {
      setTarget(selectedUser);
    }
  }, [selectedUser]);

  const otherUsers = onlineUsers.filter((user) => user !== currentUser);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();

    if (!target.trim() || !content.trim()) {
      return;
    }

    onSendMessage(target.trim(), content.trim());
    setContent("");
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <Select
        value={target}
        onValueChange={(value) => {
          setTarget(value);
          onUserSelect?.(value);
        }}
        disabled={disabled || otherUsers.length === 0}
      >
        <SelectTrigger className="w-[180px] bg-input text-foreground border-border">
          <SelectValue placeholder="Select user" />
        </SelectTrigger>
        <SelectContent className="bg-popover border-border">
          {otherUsers.map((user) => (
            <SelectItem key={user} value={user} className="text-foreground">
              {user}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Input
        type="text"
        placeholder="Type your message..."
        value={content}
        onChange={(e) => setContent(e.target.value)}
        disabled={disabled || !target || otherUsers.length === 0}
        className="flex-1 bg-input text-foreground placeholder:text-muted-foreground border-border"
      />
      <Button
        type="submit"
        disabled={
          disabled || !target || !content.trim() || otherUsers.length === 0
        }
        className="bg-primary text-primary-foreground hover:opacity-90"
      >
        Send
      </Button>
    </form>
  );
}
