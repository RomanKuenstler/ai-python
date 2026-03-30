import type { ReactNode } from "react";

type AppShellProps = {
  sidebar: ReactNode;
  content: ReactNode;
  onOpenArchive: () => void;
  onOpenPreferences: () => void;
};

export function AppShell({ sidebar, content, onOpenArchive, onOpenPreferences }: AppShellProps) {
  return (
    <div className="page-shell page">
      <header className="topbar">
        <div className="brand">
          <span className="brand-status-light ok" />
          <h1>Local RAG</h1>
        </div>
        <div className="header-center-spacer" />
        <div className="quick-actions">
          <button type="button" className="header-action header-chat-link" onClick={onOpenArchive}>
            Archive
          </button>
          <button type="button" className="header-action header-chat-link" onClick={onOpenPreferences}>
            Preferences
          </button>
        </div>
      </header>
      <aside className="side-nav">{sidebar}</aside>
      <main className="workspace">{content}</main>
    </div>
  );
}
