import { useState } from "react";
import type { CurrentUser } from "../types/chat";

type PasswordChangePageProps = {
  user: CurrentUser;
  loading: boolean;
  error: string | null;
  onSubmit: (currentPassword: string | null, newPassword: string, confirmPassword: string) => Promise<void>;
  onLogout: () => Promise<void>;
  requiresCurrentPassword?: boolean;
  compact?: boolean;
  showLogout?: boolean;
};

export function PasswordChangePage({
  user,
  loading,
  error,
  onSubmit,
  onLogout,
  requiresCurrentPassword = false,
  compact = false,
  showLogout = true,
}: PasswordChangePageProps) {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  return (
    <div className={compact ? "password-card-shell" : "auth-screen"}>
      <form
        className={compact ? "auth-card auth-card-compact" : "auth-card"}
        onSubmit={(event) => {
          event.preventDefault();
          void onSubmit(requiresCurrentPassword ? currentPassword : null, newPassword, confirmPassword);
        }}
      >
        <div>
          <p className="auth-eyebrow">{user.displayname}</p>
          <h1>{requiresCurrentPassword ? "Change password" : "Set a new password"}</h1>
          <p className="auth-copy">
            {requiresCurrentPassword ? "Update your credentials to keep using the app." : "You need to change the default password before accessing the app."}
          </p>
        </div>
        <div className="auth-form">
          {requiresCurrentPassword ? (
            <label>
              <span>Current password</span>
              <input type="password" value={currentPassword} onChange={(event) => setCurrentPassword(event.target.value)} autoComplete="current-password" />
            </label>
          ) : null}
          <label>
            <span>New password</span>
            <input type="password" value={newPassword} onChange={(event) => setNewPassword(event.target.value)} autoComplete="new-password" />
          </label>
          <label>
            <span>Confirm password</span>
            <input type="password" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} autoComplete="new-password" />
          </label>
        </div>
        {error ? <p className="chat-error">{error}</p> : null}
        <div className="auth-actions">
          {showLogout ? (
            <button className="secondary-button" type="button" onClick={() => void onLogout()}>
              Logout
            </button>
          ) : (
            <span />
          )}
          <button className="primary-button auth-submit" type="submit" disabled={loading || !newPassword || !confirmPassword}>
            {loading ? "Saving..." : "Save password"}
          </button>
        </div>
      </form>
    </div>
  );
}
