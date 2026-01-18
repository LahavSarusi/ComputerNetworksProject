import { Routes, Route, Navigate } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import { LoginPage } from "./pages/LoginPage";
import { ChatPage } from "./pages/ChatPage";
import { WebSocketProvider } from "./contexts/WebSocketContext";
import "react-toastify/dist/ReactToastify.css";
import "./App.css";

/**
 * Main app component with routing setup
 * @returns App component with routes
 */
function App() {
  return (
    <WebSocketProvider>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <ToastContainer
        position="top-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="dark"
      />
    </WebSocketProvider>
  );
}

export default App;
