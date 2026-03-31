import { useEffect, useRef, useState, type ReactNode } from "react";
import { Icon } from "../common/Icons";
import type { AssistantMode } from "../../types/chat";

type AppShellProps = {
  sidebar: ReactNode;
  content: ReactNode;
  assistantMode: AssistantMode;
  availableModes: AssistantMode[];
  onAssistantModeChange: (mode: AssistantMode) => void;
};

export function AppShell({ sidebar, content, assistantMode, availableModes, onAssistantModeChange }: AppShellProps) {
  const [modeOpen, setModeOpen] = useState(false);
  const modeRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    function handlePointerDown(event: MouseEvent) {
      if (modeRef.current && !modeRef.current.contains(event.target as Node)) {
        setModeOpen(false);
      }
    }

    function handleEscape(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setModeOpen(false);
      }
    }

    document.addEventListener("mousedown", handlePointerDown);
    document.addEventListener("keydown", handleEscape);
    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
      document.removeEventListener("keydown", handleEscape);
    };
  }, []);

  return (
    <div className="page-shell page">
      <header className="topbar">
        <div className="brand">
          <span className="brand-status-light ok" />
          <h1>PyRAC</h1>
        </div>
        <div className="header-center-spacer" />
        <div className="quick-actions">
          <div className={`header-mode-picker${modeOpen ? " open" : ""}`} ref={modeRef}>
            <button type="button" className="header-mode-trigger" aria-expanded={modeOpen} onClick={() => setModeOpen((current) => !current)}>
              <span className="header-mode-label">{assistantMode.toUpperCase()}</span>
              <Icon name="chevron-down" className="header-mode-chevron" />
            </button>
            {modeOpen ? (
              <div className="header-mode-menu" role="menu">
              {availableModes.map((mode) => (
                  <button
                    key={mode}
                    type="button"
                    className={`header-mode-option${mode === assistantMode ? " active" : ""}`}
                    onClick={() => {
                      onAssistantModeChange(mode);
                      setModeOpen(false);
                    }}
                  >
                    <span className="header-mode-option-copy">
                      <strong>{mode[0].toUpperCase() + mode.slice(1)}</strong>
                      <small>{mode === "simple" ? "For everyday simple tasks" : "For getting refined answers"}</small>
                    </span>
                    {mode === assistantMode ? <Icon name="check" className="header-mode-option-check" /> : null}
                  </button>
                ))}
              </div>
            ) : null}
          </div>
        </div>
      </header>
      <aside className="side-nav">{sidebar}</aside>
      <main className="workspace">{content}</main>
    </div>
  );
}
