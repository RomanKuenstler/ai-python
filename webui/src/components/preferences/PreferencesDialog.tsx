import { useMemo, useState } from "react";
import type { AssistantMode, Chat, FilterTag, SettingsUpdate } from "../../types/chat";
import { Icon } from "../common/Icons";
import { Dialog } from "../common/Dialog";
import { FilterTables } from "../filters/FilterTables";

type PreferencesDialogProps = {
  initialTab?: "general" | "personalization" | "settings" | "filter" | "archive";
  archivedChats: Chat[];
  settingsDraft: SettingsUpdate | null;
  availableModes: AssistantMode[];
  globalFilterTags: FilterTag[];
  loading: boolean;
  saving: boolean;
  filterLoading: boolean;
  filterError: string | null;
  filterBusyKeys: string[];
  error: string | null;
  success: string | null;
  onClose: () => void;
  onDownloadChat: (chatId: string) => void;
  onUnarchiveChat: (chatId: string) => void;
  onDeleteChat: (chatId: string) => void;
  onFieldChange: (patch: Partial<SettingsUpdate>) => void;
  onSaveSettings: () => void;
  onOpenFilterTab: () => void;
  onToggleGlobalTag: (tag: FilterTag, isEnabled: boolean) => void;
};

const TABS = [
  { id: "general", label: "General", icon: "settings" },
  { id: "personalization", label: "Personalization", icon: "sparkles" },
  { id: "settings", label: "Settings", icon: "settings" },
  { id: "filter", label: "Filter", icon: "filter" },
  { id: "archive", label: "Archive", icon: "archive" },
] as const;

export function PreferencesDialog({
  initialTab = "general",
  archivedChats,
  settingsDraft,
  availableModes,
  globalFilterTags,
  loading,
  saving,
  filterLoading,
  filterError,
  filterBusyKeys,
  error,
  success,
  onClose,
  onDownloadChat,
  onUnarchiveChat,
  onDeleteChat,
  onFieldChange,
  onSaveSettings,
  onOpenFilterTab,
  onToggleGlobalTag,
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

  return (
    <Dialog
      title="Preferences"
      onClose={onClose}
      actions={null}
      hideHeader
      className="dialog-wide panel-modal-with-tabs"
      contentClassName="preferences-dialog-content"
      bodyClassName="preferences-dialog panel-modal-tab-layout"
    >
      <div className="preferences-tabs panel-tab-nav" role="tablist" aria-label="Preferences tabs">
          <div className="panel-tab-nav-top">
            <button className="ghost-button panel-close panel-close-sidebar" type="button" onClick={onClose} aria-label="Close preferences dialog">
              x
            </button>
          </div>
          {TABS.map((tab) => (
            <button
              key={tab.id}
              type="button"
              role="tab"
              className={`preferences-tab panel-tab-button${tab.id === activeTab ? " active" : ""}`}
              aria-selected={tab.id === activeTab}
              onClick={() => {
                setActiveTab(tab.id);
                if (tab.id === "filter") {
                  onOpenFilterTab();
                }
              }}
            >
              <span className="panel-tab-button-icon" aria-hidden="true">
                <Icon name={tab.icon} />
              </span>
              <span>{tab.label}</span>
            </button>
          ))}
      </div>

      <div className="preferences-panel">
          {activeTab === "general" ? (
            <div className="preferences-section info-groups">
              <section className="info-group-card">
                <h4>Assistant Modes</h4>
                <p className="preferences-copy">Available assistant modes for this system.</p>
              </section>
              <div className="preferences-mode-list assistant-mode-grid">
                {availableModes.map((mode) => (
                  <div key={mode} className="preferences-mode-card assistant-mode-card">
                    <strong>{mode}</strong>
                    <span>{mode === "simple" ? "Single-step retrieval and answer generation." : "Two-stage draft and refinement pipeline."}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : null}

          {activeTab === "personalization" ? (
            <div className="preferences-section info-groups">
              <section className="info-group-card personalization-section-card">
                <h4>Personalization</h4>
              <p className="preferences-copy">Personalization is reserved for a future step.</p>
              <div className="preferences-placeholder">Placeholder UI for user-specific instructions and tone settings.</div>
              </section>
            </div>
          ) : null}

          {activeTab === "settings" ? (
            <div className="preferences-section config-sections">
              <section className="settings-grid info-group-card general-settings-card config-live-table-card">
                <div className="settings-grid-head config-live-table-head" role="row">
                  <span>Setting</span>
                  <span>Value</span>
                </div>
                <div className="settings-grid-row config-live-table-row" role="row">
                  <div className="config-setting-cell">
                    <strong>History Messages</strong>
                    <small>Retrieval</small>
                  </div>
                  <div className="config-edit-form">
                    <input
                      id="history-limit"
                      className="dialog-input config-input"
                      type="number"
                      min={1}
                      max={50}
                      value={settingsDraft?.chat_history_messages_count ?? ""}
                      onChange={(event) => onFieldChange({ chat_history_messages_count: Number(event.target.value) })}
                      disabled={loading || saving}
                    />
                    <button
                      className="primary-button config-apply-save-button"
                      type="button"
                      onClick={onSaveSettings}
                      disabled={saving || loading || !!settingsValidation || !settingsDraft}
                      aria-label="Save History Messages"
                      title="Save History Messages"
                    >
                      {saving ? "..." : "Save"}
                    </button>
                  </div>
                </div>
                <div className="settings-grid-row config-live-table-row" role="row">
                  <div className="config-setting-cell">
                    <strong>Max Similarities</strong>
                    <small>Retrieval</small>
                  </div>
                  <div className="config-edit-form">
                    <input
                      id="max-similarities"
                      className="dialog-input config-input"
                      type="number"
                      min={1}
                      max={50}
                      value={settingsDraft?.max_similarities ?? ""}
                      onChange={(event) => onFieldChange({ max_similarities: Number(event.target.value) })}
                      disabled={loading || saving}
                    />
                    <button
                      className="primary-button config-apply-save-button"
                      type="button"
                      onClick={onSaveSettings}
                      disabled={saving || loading || !!settingsValidation || !settingsDraft}
                      aria-label="Save Max Similarities"
                      title="Save Max Similarities"
                    >
                      {saving ? "..." : "Save"}
                    </button>
                  </div>
                </div>
                <div className="settings-grid-row config-live-table-row" role="row">
                  <div className="config-setting-cell">
                    <strong>Min Similarities</strong>
                    <small>Retrieval</small>
                  </div>
                  <div className="config-edit-form">
                    <input
                      id="min-similarities"
                      className="dialog-input config-input"
                      type="number"
                      min={1}
                      max={50}
                      value={settingsDraft?.min_similarities ?? ""}
                      onChange={(event) => onFieldChange({ min_similarities: Number(event.target.value) })}
                      disabled={loading || saving}
                    />
                    <button
                      className="primary-button config-apply-save-button"
                      type="button"
                      onClick={onSaveSettings}
                      disabled={saving || loading || !!settingsValidation || !settingsDraft}
                      aria-label="Save Min Similarities"
                      title="Save Min Similarities"
                    >
                      {saving ? "..." : "Save"}
                    </button>
                  </div>
                </div>
                <div className="settings-grid-row config-live-table-row" role="row">
                  <div className="config-setting-cell">
                    <strong>Cosine Limit</strong>
                    <small>Retrieval</small>
                  </div>
                  <div className="config-edit-form">
                    <input
                      id="score-threshold"
                      className="dialog-input config-input"
                      type="number"
                      min={0}
                      max={1}
                      step={0.01}
                      value={settingsDraft?.similarity_score_threshold ?? ""}
                      onChange={(event) => onFieldChange({ similarity_score_threshold: Number(event.target.value) })}
                      disabled={loading || saving}
                    />
                    <button
                      className="primary-button config-apply-save-button"
                      type="button"
                      onClick={onSaveSettings}
                      disabled={saving || loading || !!settingsValidation || !settingsDraft}
                      aria-label="Save Cosine Limit"
                      title="Save Cosine Limit"
                    >
                      {saving ? "..." : "Save"}
                    </button>
                  </div>
                </div>
              </section>

              {settingsValidation ? <p className="inline-error config-settings-error">{settingsValidation}</p> : null}
              {error ? <p className="inline-error config-settings-error">{error}</p> : null}
              {success ? <p className="inline-success preferences-inline-success">{success}</p> : null}
            </div>
          ) : null}

          {activeTab === "filter" ? (
            <div className="preferences-section info-groups">
              {filterError ? <p className="inline-error">{filterError}</p> : null}
              {filterLoading ? (
                <section className="info-group-card">
                  <div className="preferences-placeholder">Loading global filters...</div>
                </section>
              ) : (
                <FilterTables
                  mode="global"
                  tags={globalFilterTags}
                  files={[]}
                  busyKeys={filterBusyKeys}
                  showFiles={false}
                  onToggleTag={onToggleGlobalTag}
                  onToggleFile={() => undefined}
                />
              )}
            </div>
          ) : null}

          {activeTab === "archive" ? (
            <div className="preferences-section">
              {archivedChats.length === 0 ? (
                <div className="preferences-placeholder">No archived chats yet.</div>
              ) : (
                <div className="archive-list archive-table-wrapper">
                  {archivedChats.map((chat) => (
                    <div key={chat.id} className="archive-row archive-table-row">
                      <div className="archive-meta">
                        <strong className="archive-chat-name">{chat.chat_name}</strong>
                        <span className="archive-chat-date">Updated {new Date(chat.updated_at).toLocaleString()}</span>
                      </div>
                      <div className="archive-actions archive-row-actions">
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
    </Dialog>
  );
}
