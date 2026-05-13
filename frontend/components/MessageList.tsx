"use client";

import React, { useEffect, useRef } from "react";
import { Message } from "../lib/types";

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  isLoading,
}) => {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div className="chat-messages">
      {messages.length === 0 && (
        <div
          style={{
            textAlign: "center",
            color: "#999",
            marginTop: "40px",
          }}
        >
          <p>Start a conversation by asking about students, courses, or transactions.</p>
          <p style={{ fontSize: "12px", marginTop: "10px" }}>
            Example: &quot;Show me all students with GPA above 3.5&quot;
          </p>
        </div>
      )}

      {messages.map((message) => (
        <div key={message.id} className={`message ${message.sender}`}>
          <div>
            <div className="message-content">{message.text}</div>
            {message.toolsUsed && message.toolsUsed.length > 0 && (
              <div className="tools-used">
                Tools used:{" "}
                {message.toolsUsed.map((tool) => (
                  <span key={tool} className="tool-badge">
                    {tool}
                  </span>
                ))}
              </div>
            )}
            {message.executionTime !== undefined && (
              <div className="tools-used">
                Execution time: {message.executionTime.toFixed(2)}ms
              </div>
            )}
            <div className="message-time">
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        </div>
      ))}

      {isLoading && (
        <div className="message assistant">
          <div className="typing-indicator">
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
          </div>
        </div>
      )}

      <div ref={endRef} />
    </div>
  );
};
