import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface UserListProps {
  users: string[];
  currentUser: string | null;
  onSelectUser?: (username: string) => void;
  selectedUser?: string | null;
}

/**
 * Component to display list of online users
 * @param users - Array of online usernames
 * @param currentUser - Current user's username (excluded from list)
 * @param onSelectUser - Callback when a user is clicked
 * @param selectedUser - Currently selected user
 * @returns User list sidebar component
 */
export function UserList({
  users,
  currentUser,
  onSelectUser,
  selectedUser,
}: UserListProps) {
  // Filter out the current user from the list of users (so we won't display ourselves in the list)
  const otherUsers = users.filter((user) => user !== currentUser);

  return (
    <Card className="h-full bg-card border-border">
      <CardHeader>
        <CardTitle className="text-lg text-foreground">Online Users</CardTitle>
      </CardHeader>
      <CardContent>
        {otherUsers.length === 0 ? (
          <p className="text-sm text-muted-foreground">No other users online</p>
        ) : (
          <div className="space-y-2">
            {otherUsers.map((user) => (
              <div
                key={user}
                onClick={() => onSelectUser?.(user)}
                className={`p-2 rounded-md cursor-pointer transition-colors ${
                  selectedUser === user
                    ? "bg-primary text-primary-foreground"
                    : "hover:bg-muted text-foreground"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span
                    className={`text-sm font-medium ${
                      selectedUser === user
                        ? "text-primary-foreground"
                        : "text-foreground"
                    }`}
                  >
                    {user}
                  </span>
                  <Badge
                    variant="secondary"
                    className="text-xs bg-secondary text-secondary-foreground"
                  >
                    Online
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
