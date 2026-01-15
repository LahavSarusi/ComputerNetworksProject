/**
 * WebSocket message types sent from client to server
 */

/** Message to register a username with the server */
export interface RegisterMessage {
  type: "register";
  username: string;
}

/** Message to send a chat message to a target user */
export interface ChatMessage {
  type: "message";
  target: string;
  content: string;
}

/** Message to send a command (list users or exit) */
export interface CommandMessage {
  type: "command";
  command: "list" | "exit";
}

/** Message to disconnect from the server */
export interface DisconnectMessage {
  type: "disconnect";
}

/** Union type of all client-to-server messages */
export type ClientMessage =
  | RegisterMessage
  | ChatMessage
  | CommandMessage
  | DisconnectMessage;

/**
 * WebSocket message types received from server
 */

/** Success response from server */
export interface SuccessMessage {
  type: "success";
  message: string;
}

/** Error response from server */
export interface ErrorMessage {
  type: "error";
  message: string;
}

/** Chat message received from another user */
export interface ReceivedMessage {
  type: "message";
  from: string;
  content: string;
}

/** System notification message */
export interface SystemMessage {
  type: "system";
  message: string;
}

/** List of online users */
export interface UsersListMessage {
  type: "users";
  users: string[];
}

/** Union type of all server-to-client messages */
export type ServerMessage =
  | SuccessMessage
  | ErrorMessage
  | ReceivedMessage
  | SystemMessage
  | UsersListMessage;

/**
 * UI types
 */

/** Chat message displayed in the UI */
export interface ChatMessageDisplay {
  id: string;
  type: "sent" | "received" | "system";
  from?: string;
  to?: string;
  content: string;
  timestamp: Date;
}

/** Current WebSocket connection state */
export interface ConnectionState {
  connected: boolean;
  username: string | null;
  error: string | null;
}
