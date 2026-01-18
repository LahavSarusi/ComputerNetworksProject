import { useState } from "react";
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

  // Update target when selectedUser changes (use selectedUser as source of truth when provided)
  const currentTarget = selectedUser || target;

  const otherUsers = onlineUsers.filter((user) => user !== currentUser);
  const EVERYONE_OPTION = "everyone";

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();

    if (!currentTarget.trim() || !content.trim()) {
      return;
    }

    onSendMessage(currentTarget.trim(), content.trim());
    setContent("");
  };

  return (
    <div className="space-y-2">
      <form onSubmit={handleSubmit} className="flex gap-2">
      <Select
        value={currentTarget}
        onValueChange={(value) => {
          setTarget(value);
          onUserSelect?.(value);
        }}
        disabled={disabled}
      >
        <SelectTrigger className="w-[180px] bg-input text-foreground border-border cursor-pointer">
          <SelectValue 
            placeholder={
              otherUsers.length === 0 
                ? "No users online" 
                : "👤 Select user to message..."
            }
          />
        </SelectTrigger>
        <SelectContent className="bg-popover border-border">
          <SelectItem 
            value={EVERYONE_OPTION} 
            className="text-foreground hover:bg-amber-700/50 cursor-pointer font-semibold"
          >
            📢 Everyone
          </SelectItem>
          {otherUsers.length > 0 && (
            <div className="border-t border-border my-1" />
          )}
          {otherUsers.map((user) => (
            <SelectItem key={user} value={user} className="text-foreground hover:bg-amber-700/50 cursor-pointer">
              {user}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
        <Input
        type="text"
        placeholder={
          !currentTarget 
            ? "⚠️ Select a user first..." 
            : currentTarget === EVERYONE_OPTION
            ? "Type message to everyone..."
            : "Type your message..."
        }
        value={content}
        onChange={(e) => setContent(e.target.value)}
        disabled={disabled || !currentTarget || (otherUsers.length === 0 && currentTarget !== EVERYONE_OPTION)}
        className="flex-1 bg-input text-foreground placeholder:text-muted-foreground border-border"
      />
      <Button
        type="submit"
        disabled={
          disabled || !currentTarget || !content.trim() || (otherUsers.length === 0 && currentTarget !== EVERYONE_OPTION)
        }
        className="bg-primary text-primary-foreground hover:opacity-90"
      >
        Send
      </Button>
      </form>
      {!currentTarget && (
        <p className="text-xs text-muted-foreground px-1">
          💡 Select "Everyone" or a user from the dropdown above to start messaging
        </p>
      )}
    </div>
  );
}
