"use client";

import React, { useState, useCallback } from "react";
import { MessageList } from "./MessageList";
import { InputBox } from "./InputBox";
import { sendChatMessage } from "../lib/api";
import { Message, ChatResponse } from "../lib/types";
import { v4 as uuidv4 } from "uuid";

export const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId] = useState(uuidv4());

  const handleSendMessage = useCallback(
    async (userInput: string) => {
      setError(null);

      const userMessage: Message = {
        id: uuidv4(),
        text: userInput,
        sender: "user",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);

      try {
        const response: ChatResponse = await sendChatMessage(
          userInput,
          sessionId
        );

        const assistantMessage: Message = {
          id: uuidv4(),
          text: response.response,
          sender: "assistant",
          timestamp: new Date(),
          toolsUsed: response.tools_used,
          executionTime: response.execution_time_ms,
        };

        setMessages((prev) => [...prev, assistantMessage]);
      } catch (err: any) {
        setError(err.message);
        const errorMessage: Message = {
          id: uuidv4(),
          text: `Error: ${err.message}`,
          sender: "assistant",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId]
  );

  return (
    <div className="chat-wrapper">
      <div className="chat-header">
        <h1>🤖 Database Chat Agent</h1>
        <p style={{ fontSize: "14px", marginTop: "5px", opacity: 0.9 }}>
          Query students, courses, and transactions using natural language
        </p>
      </div>

      {error && (
        <div style={{ padding: "10px 20px" }}>
          <div className="error-message">{error}</div>
        </div>
      )}

      <MessageList messages={messages} isLoading={isLoading} />

      <div className="stats-bar">
        Session: {sessionId.slice(0, 8)}... | Messages: {messages.length}
      </div>

      <InputBox onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  );
};
