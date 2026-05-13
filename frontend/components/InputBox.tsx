"use client";

import React, { useState, useRef, useEffect } from "react";

interface InputBoxProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

export const InputBox: React.FC<InputBoxProps> = ({ onSendMessage, isLoading }) => {
  const [input, setInput] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!isLoading) {
      inputRef.current?.focus();
    }
  }, [isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input);
      setInput("");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="input-area">
      <input
        ref={inputRef}
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Ask about students, courses, or transactions..."
        disabled={isLoading}
      />
      <button type="submit" disabled={!input.trim() || isLoading}>
        {isLoading ? "Processing..." : "Send"}
      </button>
    </form>
  );
};
