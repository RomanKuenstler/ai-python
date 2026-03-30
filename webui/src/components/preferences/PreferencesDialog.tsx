import { useMemo, useState } from "react";
import type { AssistantMode, Chat, SettingsUpdate } from "../../types/chat";
import { Dialog } from "../common/Dialog";

type PreferencesDialogProps = {
  initialTab?: "general" | "personalization" | "settings" | "archive";
  archivedChats: Chat[];
  settingsDraft: SettingsUpdate | null;
  availableModes: AssistantMode[];
  loading: boolean;
  saving: boolean;
  error: string | null;
  success: string | null;
  onClose: () => void;
  onDownloadChat: (chatId: string) => void;
  onUnarchiveChat: (chatId: string) => void;
  onDeleteChat: (chatId: string) => void;
  onFieldChange: (patch: Partial<SettingsUpdate>) => void;
  onSaveSettings: () => void;
};

const TABS = [
  { id: "general", label: "General" },
  { id: "personalization", label: "Personalization" },
  { id: "settings", label: "Settings" },
  { id: "archive", label: "Archive" },
] as const;

export function PreferencesDialog({
  initialTab = "general",
  archivedChats,
  settingsDraft,
  availableModes,
  loading,
  saving,
  error,
  success,
  onClose,
  onDownloadChat,
  onUnarchiveChat,
  onDeleteChat,
  onFieldChange,
  onSaveSettings,
}: PreferencesDialogProps) {
  const [activeTab, setActiveTab] = useState<(typeof TABS)[number]["id"]>(initialTab);
  const settingsValidation = useMemo(() => {
    if (!settingsDraft) {
      return null;
    }
    if (settingsDraft.min_similarities > settingsDraft.max_similarities) {
      return "Min similarities cannot be greater than max similarities.";
    }
    return null;
  }, [settingsDraft]);

  const actions =
    activeTab === "settings" ? (
      <>
        <button className="secondary-button" type="button" onClick={onClose}>
          Close
        </button>
        <button className="primary-button" type="button" onClick={onSaveSettings} disabled={saving || loading || !!settingsValidation || !settingsDraft}>
          {saving ? "Saving..." : "Save"}
        </button>
      </>
    ) : (
      <button className="secondary-button" type="button" onClick={onClose}>
        Close
      </button>
    );

  return (
    <Dialog title="Preferences" onClose={onClose} actions={actions}>
      <div className="preferences-dialog">
        <div className="preferences-tabs" role="tablist" aria-label="Preferences tabs">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              type="button"
              role="tab"
              className={`preferences-tab${tab.id === activeTab ? " active" : ""}`}
              aria-selected={tab.id === activeTab}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="preferences-panel">
          {activeTab === "general" ? (
            <div className="preferences-section">
              <p className="preferences-copy">Available assistant modes for this Step 6 system.</p>
              <div className="preferences-mode-list">
                {availableModes.map((mode) => (
                  <div key={mode} className="preferences-mode-card">
                    <strong>{mode}</strong>
                    <span>{mode === "simple" ? "Single-step retrieval and answer generation." : "Two-stage draft and refinement pipeline."}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : null}

          {activeTab === "personalization" ? (
            <div className="preferences-section">
              <p className="preferences-copy">Personalization is reserved for a future step.</p>
              <div className="preferences-placeholder">Placeholder UI for user-specific instructions and tone settings.</div>
            </div>
          ) : null}

          {activeTab === "settings" ? (
            <div className="preferences-section">
              <div className="settings-grid" role="table" aria-label="Live retrieval settings">
                <div className="settings-grid-head" role="row">
                  <span>Setting</span>
                  <span>Value</span>
                  <span>Constraints</span>
                </div>
                <div className="settings-grid-row" role="row">
                  <label htmlFor="history-limit">Chat history messages count</label>
                  <input
                    id="history-limit"
                    className="dialog-input"
                    type="number"
                    min={1}
                    max={50}
                    value={settingsDraft?.chat_history_messages_count ?? ""}
                    onChange={(event) => onFieldChange({ chat_history_messages_count: Number(event.target.value) })}
                    disabled={loading || saving}
                  />
                  <span>1 to 50</span>
                </div>
                <div className="settings-grid-row" role="row">
                  <label htmlFor="max-similarities">Max similarities</label>
                  <input
                    id="max-similarities"
                    className="dialog-input"
                    type="number"
                    min={1}
                    max={50}
                    value={settingsDraft?.max_similarities ?? ""}
                    onChange={(event) => onFieldChange({ max_similarities: Number(event.target.value) })}
                    disabled={loading || saving}
                  />
                  <span>1 to 50</span>
                </div>
                <div className="settings-grid-row" role="row">
                  <label htmlFor="min-similarities">Min similarities</label>
                  <input
                    id="min-similarities"
                    className="dialog-input"
                    type="number"
                    min={1}
                    max={50}
                    value={settingsDraft?.min_similarities ?? ""}
                    onChange={(event) => onFieldChange({ min_similarities: Number(event.target.value) })}
                    disabled={loading || saving}
                  />
                  <span>1 to 50, must be {"<="} max</span>
                </div>
                <div className="settings-grid-row" role="row">
                  <label htmlFor="score-threshold">Similarity score threshold</label>
                  <input
                    id="score-threshold"
                    className="dialog-input"
                    type="number"
                    min={0}
                    max={1}
                    step={0.01}
                    value={settingsDraft?.similarity_score_threshold ?? ""}
                    onChange={(event) => onFieldChange({ similarity_score_threshold: Number(event.target.value) })}
                    disabled={loading || saving}
                  />
                  <span>0.00 to 1.00</span>
                </div>
              </div>

              {settingsValidation ? <p className="inline-error">{settingsValidation}</p> : null}
              {error ? <p className="inline-error">{error}</p> : null}
              {success ? <p className="inline-success">{success}</p> : null}
            </div>
          ) : null}

          {activeTab === "archive" ? (
            <div className="preferences-section">
              {archivedChats.length === 0 ? (
                <div className="preferences-placeholder">No archived chats yet.</div>
              ) : (
                <div className="archive-list">
                  {archivedChats.map((chat) => (
                    <div key={chat.id} className="archive-row">
                      <div className="archive-meta">
                        <strong>{chat.chat_name}</strong>
                        <span>Updated {new Date(chat.updated_at).toLocaleString()}</span>
                      </div>
                      <div className="archive-actions">
                        <button className="secondary-button" type="button" onClick={() => onDownloadChat(chat.id)}>
                          Download
                        </button>
                        <button className="secondary-button" type="button" onClick={() => onUnarchiveChat(chat.id)}>
                          Unarchive
                        </button>
                        <button className="danger-button" type="button" onClick={() => onDeleteChat(chat.id)}>
                          Delete
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : null}
        </div>
      </div>
    </Dialog>
  );
}
