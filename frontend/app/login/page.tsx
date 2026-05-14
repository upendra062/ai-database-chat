"use client";
export const dynamic = "force-dynamic";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "../../lib/supabase";

const DEMO_EMAIL = "demo@rockyai.dev";
const DEMO_PASSWORD = "Demo@12345";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [demoLoading, setDemoLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const doLogin = async (em: string, pw: string) => {
    const { error } = await supabase.auth.signInWithPassword({ email: em, password: pw });
    if (error) throw error;
    router.push("/chat");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(""); setSuccess(""); setLoading(true);
    try {
      if (mode === "signup") {
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
          options: { data: { full_name: name } },
        });
        if (error) throw error;
        // If session exists, user is auto-confirmed — go to chat
        if (data.session) {
          router.push("/chat");
        } else {
          setSuccess("Account created! Check your email to confirm, then sign in.");
          setMode("login");
        }
      } else {
        await doLogin(email, password);
      }
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setError(""); setDemoLoading(true);
    try {
      await doLogin(DEMO_EMAIL, DEMO_PASSWORD);
    } catch (err: any) {
      setError(err.message || "Demo login failed");
    } finally {
      setDemoLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">
          <div className="auth-logo-icon">🤖</div>
          <span className="auth-logo-text">Rocky AI</span>
        </div>

        <h1 className="auth-title">{mode === "login" ? "Welcome back" : "Create account"}</h1>
        <p className="auth-subtitle">
          {mode === "login" ? "Sign in to your Rocky AI account" : "Start chatting with your database"}
        </p>

        {error && <div className="auth-error" style={{ marginBottom: 16 }}>{error}</div>}
        {success && <div className="auth-success" style={{ marginBottom: 16 }}>{success}</div>}

        <form className="auth-form" onSubmit={handleSubmit}>
          {mode === "signup" && (
            <div className="form-group">
              <label className="form-label">Full name</label>
              <input className="form-input" type="text" placeholder="Your name" value={name}
                onChange={e => setName(e.target.value)} required />
            </div>
          )}
          <div className="form-group">
            <label className="form-label">Email</label>
            <input className="form-input" type="email" placeholder="you@example.com" value={email}
              onChange={e => setEmail(e.target.value)} required />
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input className="form-input" type="password" placeholder="••••••••" value={password}
              onChange={e => setPassword(e.target.value)} required minLength={6} />
          </div>
          <button className="auth-btn" type="submit" disabled={loading || demoLoading}>
            {loading ? "Please wait..." : mode === "login" ? "Sign in" : "Create account"}
          </button>
        </form>

        <div className="auth-divider" style={{ margin: "20px 0" }}>or</div>

        {/* Demo login */}
        <button className="auth-google-btn" onClick={handleDemoLogin} disabled={loading || demoLoading}
          style={{ border: "1px dashed #7c6cf8", color: "#9d91ff" }}>
          {demoLoading ? "Signing in..." : "🚀  Try Demo Account"}
        </button>
        <p style={{ textAlign: "center", fontSize: 11, color: "#555", marginTop: 8 }}>
          demo@rockyai.dev · Demo@12345
        </p>

        <div className="auth-switch">
          {mode === "login" ? "Don't have an account? " : "Already have an account? "}
          <button className="auth-link"
            onClick={() => { setMode(mode === "login" ? "signup" : "login"); setError(""); setSuccess(""); }}>
            {mode === "login" ? "Sign up" : "Sign in"}
          </button>
        </div>
      </div>
    </div>
  );
}
