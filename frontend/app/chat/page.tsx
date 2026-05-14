"use client";
export const dynamic = "force-dynamic";
import { useEffect, useState, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "../../lib/supabase";
import { streamChatMessage } from "../../lib/api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Plus, Send, LogOut, MessageSquare, Zap } from "lucide-react";
import { v4 as uuidv4 } from "uuid";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  streaming?: boolean;
  ts: Date;
};

type Chat = {
  id: string;
  title: string;
  messages: Message[];
  sessionId: string;
};

const SUGGESTIONS = [
  "Show me all students",
  "List available courses",
  "What transactions are pending?",
  "How many students are enrolled?",
];

export default function ChatPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [chats, setChats] = useState<Chat[]>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const activeChat = chats.find((c) => c.id === activeChatId);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }: { data: { session: any } }) => {
      if (!data.session) { router.replace("/login"); return; }
      setUser(data.session.user);
      newChat();
    });
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chats, isLoading]);

  const newChat = useCallback(() => {
    const id = uuidv4();
    const chat: Chat = { id, title: "New conversation", messages: [], sessionId: uuidv4() };
    setChats((prev) => [chat, ...prev]);
    setActiveChatId(id);
  }, []);

  const updateChat = (chatId: string, updater: (c: Chat) => Chat) => {
    setChats((prev) => prev.map((c) => (c.id === chatId ? updater(c) : c)));
  };

  const handleSend = async () => {
    const text = input.trim();
    if (!text || isLoading || !activeChatId) return;

    setInput("");
    if (textareaRef.current) textareaRef.current.style.height = "24px";

    const userMsg: Message = { id: uuidv4(), role: "user", content: text, ts: new Date() };
    const aiMsgId = uuidv4();
    const aiMsg: Message = { id: aiMsgId, role: "assistant", content: "", streaming: true, ts: new Date() };

    // Update title on first message
    updateChat(activeChatId, (c) => ({
      ...c,
      title: c.messages.length === 0 ? text.slice(0, 40) : c.title,
      messages: [...c.messages, userMsg, aiMsg],
    }));

    setIsLoading(true);
    const sessionId = activeChat?.sessionId || uuidv4();

    await streamChatMessage(
      text,
      sessionId,
      (token) => {
        updateChat(activeChatId, (c) => ({
          ...c,
          messages: c.messages.map((m) =>
            m.id === aiMsgId ? { ...m, content: m.content + token } : m
          ),
        }));
      },
      () => {
        updateChat(activeChatId, (c) => ({
          ...c,
          messages: c.messages.map((m) =>
            m.id === aiMsgId ? { ...m, streaming: false } : m
          ),
        }));
        setIsLoading(false);
        textareaRef.current?.focus();
      },
      (err) => {
        updateChat(activeChatId, (c) => ({
          ...c,
          messages: c.messages.map((m) =>
            m.id === aiMsgId ? { ...m, content: `Error: ${err}`, streaming: false } : m
          ),
        }));
        setIsLoading(false);
      }
    );
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    e.target.style.height = "24px";
    e.target.style.height = Math.min(e.target.scrollHeight, 160) + "px";
  };

  const signOut = async () => {
    await supabase.auth.signOut();
    router.replace("/login");
  };

  const userName = user?.user_metadata?.full_name || user?.email?.split("@")[0] || "User";
  const userInitial = userName.charAt(0).toUpperCase();

  return (
    <div className="app-shell">
      {/* SIDEBAR */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="sidebar-logo">🤖</div>
          <span className="sidebar-brand">Rocky AI</span>
        </div>

        <button className="sidebar-new-btn" onClick={newChat}>
          <Plus size={14} />
          New conversation
        </button>

        <div className="sidebar-section">Conversations</div>

        <div className="sidebar-chats">
          {chats.map((chat) => (
            <div
              key={chat.id}
              className={`chat-history-item ${chat.id === activeChatId ? "active" : ""}`}
              onClick={() => setActiveChatId(chat.id)}
            >
              <MessageSquare size={13} style={{ flexShrink: 0 }} />
              <span>{chat.title}</span>
            </div>
          ))}
        </div>

        <div className="sidebar-footer">
          <div className="user-card">
            <div className="user-avatar">{userInitial}</div>
            <div className="user-info">
              <div className="user-name">{userName}</div>
              <div className="user-email">{user?.email}</div>
            </div>
            <button className="signout-btn" onClick={signOut} title="Sign out">
              <LogOut size={15} />
            </button>
          </div>
        </div>
      </aside>

      {/* MAIN */}
      <main className="chat-main">
        <div className="chat-topbar">
          <span className="chat-topbar-title">
            {activeChat?.title || "Rocky AI"}
          </span>
          <span className="chat-topbar-meta">
            <Zap size={10} style={{ display: "inline", marginRight: 4 }} />
            llama-3.3-70b
          </span>
        </div>

        <div className="messages-area">
          {!activeChat || activeChat.messages.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">🤖</div>
              <h2>Rocky AI Agent</h2>
              <p>Ask me anything about students, courses, and transactions — or just say hi!</p>
              <div className="suggestions">
                {SUGGESTIONS.map((s) => (
                  <button key={s} className="suggestion-chip" onClick={() => { setInput(s); textareaRef.current?.focus(); }}>
                    {s}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            activeChat.messages.map((msg) => (
              <div key={msg.id} className={`message-row ${msg.role}`}>
                <div className={`msg-avatar ${msg.role === "assistant" ? "ai" : "user"}`}>
                  {msg.role === "assistant" ? "R" : userInitial}
                </div>
                <div className="msg-body">
                  <div className="msg-bubble">
                    {msg.role === "assistant" ? (
                      <>
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {msg.content || " "}
                        </ReactMarkdown>
                        {msg.streaming && <span className="streaming-cursor" />}
                      </>
                    ) : (
                      msg.content
                    )}
                    {msg.streaming && !msg.content && (
                      <div className="typing-dots">
                        <div className="typing-dot" />
                        <div className="typing-dot" />
                        <div className="typing-dot" />
                      </div>
                    )}
                  </div>
                  <div className="msg-meta">
                    {msg.ts.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  </div>
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-area">
          <div className="input-wrapper">
            <textarea
              ref={textareaRef}
              className="chat-textarea"
              placeholder="Ask anything..."
              value={input}
              onChange={handleTextareaChange}
              onKeyDown={handleKeyDown}
              rows={1}
              disabled={isLoading}
            />
            <button className="send-btn" onClick={handleSend} disabled={!input.trim() || isLoading}>
              <Send size={15} color="white" />
            </button>
          </div>
          <div className="input-hint">Enter to send · Shift+Enter for new line</div>
        </div>
      </main>
    </div>
  );
}
