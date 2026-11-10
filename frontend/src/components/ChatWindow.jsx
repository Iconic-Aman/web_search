import { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";
import StatusLine from "./StatusLine";

export default function ChatWindow({ messages, status, error, loadingHistory }) {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, status, error]);

  return (
    <main
      ref={scrollRef}
      className="flex-1 overflow-y-auto px-4 py-6 max-w-4xl w-full mx-auto"
    >
      {loadingHistory ? (
        <div className="flex justify-center items-center h-full text-gray-500 text-sm">
          Loading history…
        </div>
      ) : messages.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-full text-center text-gray-500 space-y-2">
          <span className="text-3xl">💬</span>
          <p className="text-sm">Ask a question to start searching the web.</p>
        </div>
      ) : (
        messages.map((msg, index) => (
          <MessageBubble
            key={msg.id || index}
            message={msg}
            isStreaming={status === "streaming" && index === messages.length - 1}
          />
        ))
      )}

      <StatusLine status={status} error={error} />
    </main>
  );
}
