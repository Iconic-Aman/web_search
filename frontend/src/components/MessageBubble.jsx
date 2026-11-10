import React, { memo } from "react";
import Markdown from "react-markdown";
import SourceChips from "./SourceChips";
import { formatTime } from "../lib/time";

function MessageBubbleComponent({ message, isStreaming = false }) {
  const isUser = message.role === "user";
  const formattedTime = formatTime(message.createdAt);

  return (
    <div
      className={`flex flex-col mb-4 max-w-[85%] md:max-w-[75%] ${
        isUser ? "ml-auto items-end" : "mr-auto items-start"
      }`}
    >
      <div
        className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
          isUser
            ? "bg-accent text-white rounded-br-xs"
            : "bg-card text-gray-200 border border-border rounded-bl-xs"
        }`}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div>
            {message.content ? (
              <div className="prose prose-invert max-w-none text-sm break-words">
                <Markdown>{message.content}</Markdown>
              </div>
            ) : isStreaming ? (
              <div className="flex gap-1 py-1">
                <span className="w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce"></span>
                <span className="w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce [animation-delay:0.2s]"></span>
                <span className="w-1.5 h-1.5 rounded-full bg-gray-400 animate-bounce [animation-delay:0.4s]"></span>
              </div>
            ) : null}

            <SourceChips sources={message.sources} />
          </div>
        )}
      </div>

      {formattedTime && (
        <span className="text-[11px] text-gray-500 mt-1 px-1 select-none">
          {formattedTime}
        </span>
      )}
    </div>
  );
}

export default memo(MessageBubbleComponent);
