import { useState, useRef, useEffect } from "react";

export default function InputBar({ onSend, disabled }) {
  const [text, setText] = useState("");
  const textareaRef = useRef(null);

  useEffect(() => {
    if (!disabled && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [disabled]);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (!text.trim() || disabled) return;
    onSend(text);
    setText("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleChange = (e) => {
    setText(e.target.value);
    e.target.style.height = "auto";
    e.target.style.height = `${Math.min(e.target.scrollHeight, 160)}px`;
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="p-4 border-t border-border bg-surface flex items-end gap-2 max-w-4xl w-full mx-auto"
    >
      <textarea
        ref={textareaRef}
        rows={1}
        value={text}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder="Ask anything…"
        disabled={disabled}
        className="flex-1 bg-card text-gray-100 placeholder-gray-500 border border-border rounded-xl px-4 py-2.5 text-sm resize-none focus:outline-none focus:border-accent disabled:opacity-50 transition-colors"
      />
      <button
        type="submit"
        disabled={disabled || !text.trim()}
        className="h-[42px] px-5 rounded-xl bg-accent hover:bg-blue-600 disabled:opacity-40 disabled:hover:bg-accent text-white text-sm font-medium transition-colors cursor-pointer disabled:cursor-not-allowed select-none"
      >
        Send
      </button>
    </form>
  );
}
