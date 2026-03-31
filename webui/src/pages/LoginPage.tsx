import { useState } from "react";

type LoginPageProps = {
  loading: boolean;
  error: string | null;
  onSubmit: (username: string, password: string) => Promise<void>;
};

export function LoginPage({ loading, error, onSubmit }: LoginPageProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  return (
    <div className="auth-screen">
      <form
        className="auth-card"
        onSubmit={(event) => {
          event.preventDefault();
          void onSubmit(username, password);
        }}
      >
        <div>
          <p className="auth-eyebrow">PyRAC</p>
          <h1>Sign in</h1>
          <p className="auth-copy">Use a provisioned username and password to access your isolated workspace.</p>
        </div>
        <div className="auth-form">
          <label>
            <span>Username</span>
            <input value={username} onChange={(event) => setUsername(event.target.value)} autoComplete="username" />
          </label>
          <label>
            <span>Password</span>
            <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" />
          </label>
        </div>
        {error ? <p className="chat-error">{error}</p> : null}
        <button className="primary-button auth-submit" type="submit" disabled={loading || !username.trim() || !password}>
          {loading ? "Signing in..." : "Login"}
        </button>
      </form>
    </div>
  );
}
