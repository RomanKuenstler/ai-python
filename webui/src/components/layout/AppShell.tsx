import type { ReactNode } from "react";

type AppShellProps = {
  sidebar: ReactNode;
  content: ReactNode;
};

export function AppShell({ sidebar, content }: AppShellProps) {
  return (
    <div className="page-shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-status-light ok" />
          <h1>Local RAG</h1>
        </div>
        <div className="quick-actions">
          <button type="button" className="header-action is-disabled" disabled>
            Archive
          </button>
          <button type="button" className="header-action is-disabled" disabled>
            Preferences
          </button>
        </div>
      </header>
      <aside className="side-nav">{sidebar}</aside>
      <main className="workspace">{content}</main>
    </div>
  );
}
