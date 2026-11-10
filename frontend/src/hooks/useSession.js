import { useState, useEffect, useCallback } from "react";

const STORAGE_KEY = "search_chat_session_id";
const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

export function useSession() {
  const [sessionId, setSessionId] = useState(() => {
    return localStorage.getItem(STORAGE_KEY) || crypto.randomUUID();
  });
  const [initialMessages, setInitialMessages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, sessionId);
    let isMounted = true;

    async function loadHistory() {
      setLoading(true);
      try {
        const res = await fetch(`${API_BASE}/sessions/${sessionId}/messages`);
        if (res.ok) {
          const data = await res.json();
          if (isMounted) {
            setInitialMessages(
              data.map((m) => ({
                id: m.id,
                role: m.role,
                content: m.content,
                sources: m.sources || [],
                createdAt: m.created_at,
              }))
            );
          }
        } else {
          if (isMounted) setInitialMessages([]);
        }
      } catch {
        if (isMounted) setInitialMessages([]);
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    loadHistory();
    return () => {
      isMounted = false;
    };
  }, [sessionId]);

  const newChat = useCallback(() => {
    const nextId = crypto.randomUUID();
    localStorage.setItem(STORAGE_KEY, nextId);
    setInitialMessages([]);
    setSessionId(nextId);
  }, []);

  return { sessionId, initialMessages, loading, newChat };
}
