import { Badge } from "@/components/ui/badge";

/**
 * Props for ConnectionStatus component
 * @param connected - Whether connected to server
 * @param username - Current username
 */
interface ConnectionStatusProps {
  connected: boolean;
  username: string | null;
}

/**
 * Component to display connection status and username
 * @param connected - Whether connected to server
 * @param username - Current username
 * @returns Connection status badge component
 */
export function ConnectionStatus({
  connected,
  username,
}: ConnectionStatusProps) {
  return (
    <div className="flex items-center gap-2">
      <Badge
        variant={connected ? "default" : "destructive"}
        className={
          connected
            ? "bg-primary text-primary-foreground"
            : "bg-destructive text-destructive-foreground"
        }
      >
        <span
          className={`w-2 h-2 rounded-full mr-2 ${
            connected ? "bg-green-400" : "bg-red-400"
          }`}
        />
        {connected ? "Connected" : "Disconnected"}
      </Badge>
      {username && (
        <span className="text-sm text-muted-foreground font-medium">
          as {username}
        </span>
      )}
    </div>
  );
}
