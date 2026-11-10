import { useState, useEffect, useRef, useCallback } from "react";
import { getUserTimeZone } from "../lib/time";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

export function useChat(sessionId, initialMessages = []) {
  const [messages, setMessages] = useState([]);
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState(null);
  const activeMessageRef = useRef(null);
  const frameRef = useRef(null);

  useEffect(() => {
    setMessages(initialMessages);
  }, [initialMessages]);

  const updateStreamingUI = useCallback(() => {
    if (frameRef.current) return;
    frameRef.current = requestAnimationFrame(() => {
      frameRef.current = null;
      if (activeMessageRef.current) {
        setMessages((prev) => {
          const lastIdx = prev.length - 1;
          if (lastIdx >= 0 && prev[lastIdx].role === "assistant") {
            const updated = [...prev];
            updated[lastIdx] = { ...activeMessageRef.current };
            return updated;
          }
          return [...prev, { ...activeMessageRef.current }];
        });
      }
    });
  }, []);

  const send = useCallback(
    async (text) => {
      if (!text.trim() || status !== "idle") return;

      setError(null);
      const userMsg = {
        id: `user-${Date.now()}`,
        role: "user",
        content: text.trim(),
        sources: [],
        createdAt: new Date().toISOString(),
      };

      const botMsg = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: "",
        sources: [],
        createdAt: new Date().toISOString(),
      };

      activeMessageRef.current = botMsg;
      setMessages((prev) => [...prev, userMsg, botMsg]);
      setStatus("streaming");

      try {
        const res = await fetch(`${API_BASE}/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            session_id: sessionId,
            message: text.trim(),
            timezone: getUserTimeZone(),
          }),
        });

        if (!res.ok) {
          throw new Error("Can't reach the server. Try again.");
        }

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const parts = buffer.split("\n\n");
          buffer = parts.pop() || "";

          for (const chunk of parts) {
            for (const line of chunk.split("\n")) {
              if (!line.startsWith("data: ")) continue;
              const payload = line.slice(6).trim();
              if (!payload) continue;

              const ev = JSON.parse(payload);
              if (ev.type === "token") {
                activeMessageRef.current.content += ev.content;
                updateStreamingUI();
              } else if (ev.type === "status" && ev.status === "searching") {
                setStatus("searching");
              } else if (ev.type === "source") {
                activeMessageRef.current.sources.push({
                  title: ev.title,
                  url: ev.url,
                });
                updateStreamingUI();
              } else if (ev.type === "error") {
                throw new Error(ev.message || "An error occurred during search.");
              }
            }
          }
        }

        if (frameRef.current) cancelAnimationFrame(frameRef.current);
        frameRef.current = null;
        setMessages((prev) => {
          const updated = [...prev];
          if (updated.length && activeMessageRef.current) {
            updated[updated.length - 1] = { ...activeMessageRef.current };
          }
          return updated;
        });
        setStatus("idle");
      } catch (err) {
        if (frameRef.current) cancelAnimationFrame(frameRef.current);
        frameRef.current = null;
        setError(err.message || "Can't reach the server. Try again.");
        setStatus("error");
      } finally {
        activeMessageRef.current = null;
      }
    },
    [sessionId, status, updateStreamingUI]
  );

  return { messages, status, error, send };
}
