import Header from "./components/Header";
import ChatWindow from "./components/ChatWindow";
import InputBar from "./components/InputBar";
import { useSession } from "./hooks/useSession";
import { useChat } from "./hooks/useChat";

export default function App() {
  const { sessionId, initialMessages, loading, newChat } = useSession();
  const { messages, status, error, send } = useChat(sessionId, initialMessages);

  return (
    <div className="flex flex-col h-screen bg-surface text-gray-200">
      <Header onNewChat={newChat} />
      <ChatWindow
        messages={messages}
        status={status}
        error={error}
        loadingHistory={loading}
      />
      <InputBar
        onSend={send}
        disabled={status === "streaming" || status === "searching"}
      />
    </div>
  );
}
