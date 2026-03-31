import { useEffect, useState } from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation, useNavigate, useParams } from "react-router-dom";
import { ChatView } from "../components/chat/ChatView";
import { Dialog } from "../components/common/Dialog";
import { AppShell } from "../components/layout/AppShell";
import { LibraryPage } from "../components/library/LibraryPage";
import { PreferencesDialog } from "../components/preferences/PreferencesDialog";
import { Sidebar } from "../components/sidebar/Sidebar";
import { useChatApp } from "../hooks/useChatApp";
import type { AssistantMode } from "../types/chat";

type PreferencesTab = "general" | "personalization" | "settings" | "filter" | "archive";

function AppRoutes() {
  const app = useChatApp();
  const navigate = useNavigate();
  const location = useLocation();
  const activeView = location.pathname.startsWith("/library") ? "library" : "chat";
  const [preferencesTab, setPreferencesTab] = useState<PreferencesTab | null>(null);
  const [infoOpen, setInfoOpen] = useState(false);
  const [helpOpen, setHelpOpen] = useState(false);

  useEffect(() => {
    if (app.bootstrapping || app.chats.length === 0) {
      return;
    }

    if (location.pathname === "/") {
      navigate(`/chats/${app.activeChatId ?? app.chats[0].id}`, { replace: true });
    }
  }, [app.activeChatId, app.bootstrapping, app.chats, location.pathname, navigate]);

  async function openPreferences(tab: PreferencesTab = "general") {
    setPreferencesTab(tab);
    await app.loadSettings();
  }

  async function handleCreateChat() {
    const chat = await app.createChat();
    navigate(`/chats/${chat.id}`);
  }

  async function handleSelectChat(chatId: string) {
    await app.ensureChatLoaded(chatId);
    navigate(`/chats/${chatId}`);
  }

  async function handleRenameChat(chatId: string, chatName: string) {
    await app.renameChat(chatId, chatName);
  }

  async function handleArchiveChat(chatId: string) {
    const fallbackChatId = await app.archiveChat(chatId);
    if (fallbackChatId) {
      navigate(`/chats/${fallbackChatId}`);
      return;
    }
    navigate("/");
  }

  async function handleDeleteChat(chatId: string) {
    const fallbackChatId = await app.deleteChat(chatId);
    if (fallbackChatId) {
      navigate(`/chats/${fallbackChatId}`);
      return;
    }
    navigate("/");
  }

  const sidebar = (
    <Sidebar
      chats={app.chats}
      activeChatId={app.activeChatId}
      activeView={activeView}
      onCreateChat={() => void handleCreateChat()}
      onOpenLibrary={() => navigate("/library")}
      onOpenArchive={() => void openPreferences("archive")}
      onOpenInfo={() => setInfoOpen(true)}
      onOpenHelp={() => setHelpOpen(true)}
      onOpenPreferences={(tab) => void openPreferences(tab ?? "settings")}
      onSelectChat={(chatId) => void handleSelectChat(chatId)}
      onRenameChat={(chatId, chatName) => void handleRenameChat(chatId, chatName)}
      onArchiveChat={(chatId) => void handleArchiveChat(chatId)}
      onDownloadChat={(chatId) => void app.downloadChat(chatId)}
      onDeleteChat={(chatId) => void handleDeleteChat(chatId)}
    />
  );

  return (
    <>
      <AppShell
        sidebar={sidebar}
        assistantMode={app.assistantMode}
        availableModes={app.settings?.available_assistant_modes ?? ["simple", "refine"]}
        onAssistantModeChange={app.setAssistantMode}
        content={
          <Routes>
            <Route
              path="/library"
              element={
                <LibraryPage
                  library={app.library}
                  loading={app.libraryLoading}
                  error={app.libraryError}
                  uploading={app.uploading}
                  busyFileIds={app.busyFileIds}
                  onLoad={() => void app.loadLibrary()}
                  onToggleFile={(file) => void app.toggleLibraryFile(file)}
                  onDeleteFile={(fileId) => void app.deleteLibraryFile(fileId)}
                  onUploadFiles={(files, tagsByFile) => app.uploadLibraryFiles(files, tagsByFile)}
                />
              }
            />
            <Route
              path="/chats/:chatId"
              element={
                <ChatRoute
                  loading={app.loadingMessages}
                  error={app.appError}
                  messages={app.activeMessages}
                  sending={app.sending}
                  assistantMode={app.assistantMode}
                  attachmentRules={app.attachmentRules}
                  onOpenChat={(chatId) => void app.ensureChatLoaded(chatId)}
                  onSend={app.sendMessage}
                />
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        }
      />

      {preferencesTab ? (
        <PreferencesDialog
          initialTab={preferencesTab}
          archivedChats={app.archivedChats}
          settingsDraft={app.settingsDraft}
          availableModes={app.settings?.available_assistant_modes ?? ["simple", "refine"]}
          loading={app.settingsLoading}
          saving={app.settingsSaving}
          error={app.settingsError}
          success={app.settingsSuccess}
          onClose={() => setPreferencesTab(null)}
          onDownloadChat={(chatId) => void app.downloadChat(chatId)}
          onUnarchiveChat={(chatId) => void app.unarchiveChat(chatId)}
          onDeleteChat={(chatId) => void handleDeleteChat(chatId)}
          onFieldChange={app.updateSettingsDraft}
          onSaveSettings={() => void app.saveSettings()}
        />
      ) : null}

      {infoOpen ? (
        <Dialog
          title="Info"
          onClose={() => setInfoOpen(false)}
          className="dialog-wide info-dialog"
          actions={null}
        >
          <div className="info-panel">
            <section className="info-panel-section">
              <h4>Status</h4>
              <div className="info-table">
                {[
                  ["Backend", "Web API orchestration and chat handling."],
                  ["Retriever", "Retrieval, prompt assembly, and answer generation."],
                  ["Embedder", "Processes library files and maintains embeddings."],
                  ["OCR Scanner", "Extracts text from supported images when needed."],
                  ["Vector Db", "Stores nearest-neighbor retrieval vectors."],
                  ["Postgres", "Stores chats, messages, file metadata, and settings."],
                ].map(([label, description]) => (
                  <div className="info-row" key={label}>
                    <div className="info-copy">
                      <strong>{label}</strong>
                      <span>{description}</span>
                    </div>
                    <span className="status-pill enabled">Active</span>
                  </div>
                ))}
              </div>
            </section>
            <section className="info-panel-section">
              <h4>Storage</h4>
              <div className="info-table">
                <div className="info-row">
                  <div className="info-copy">
                    <strong>Knowledge Base</strong>
                  </div>
                  <span>Qdrant</span>
                </div>
                <div className="info-row">
                  <div className="info-copy">
                    <strong>Persistent Storage</strong>
                  </div>
                  <span>Postgres</span>
                </div>
              </div>
            </section>
          </div>
        </Dialog>
      ) : null}

      {helpOpen ? (
        <Dialog
          title="Help"
          onClose={() => setHelpOpen(false)}
          className="dialog-wide help-dialog"
          actions={null}
        >
          <div className="info-panel">
            <section className="info-panel-section">
              <h4>Chat Usage</h4>
              <p>Create chats from the sidebar, use one chat per topic when helpful, and open the chat menu to rename, download, archive, or delete a chat.</p>
              <p>Type in the bottom composer and press Enter to send or Shift+Enter for a new line.</p>
            </section>
            <section className="info-panel-section">
              <h4>Attachable File Extensions</h4>
              <div className="chip-row">
                {[".md", ".txt", ".html", ".htm", ".pdf", ".epub", ".csv", ".png", ".jpg", ".jpeg", ".webp"].map((extension) => (
                  <span key={extension} className="tag-pill">
                    {extension}
                  </span>
                ))}
              </div>
            </section>
            <section className="info-panel-section">
              <h4>Preferences</h4>
              <p>Use Preferences to review assistant modes, retrieval settings, personalization placeholders, and archived chats.</p>
            </section>
          </div>
        </Dialog>
      ) : null}

    </>
  );
}

type ChatRouteProps = {
  messages: ReturnType<typeof useChatApp>["activeMessages"];
  loading: boolean;
  sending: boolean;
  error: string | null;
  assistantMode: ReturnType<typeof useChatApp>["assistantMode"];
  attachmentRules: ReturnType<typeof useChatApp>["attachmentRules"];
  onOpenChat: (chatId: string) => void;
  onSend: ReturnType<typeof useChatApp>["sendMessage"];
};

function ChatRoute({
  messages,
  loading,
  sending,
  error,
  assistantMode,
  attachmentRules,
  onOpenChat,
  onSend,
}: ChatRouteProps) {
  const { chatId } = useParams();

  useEffect(() => {
    if (chatId) {
      onOpenChat(chatId);
    }
  }, [chatId, onOpenChat]);

  return (
    <ChatView
      messages={messages}
      sending={sending}
      loadingMessages={loading}
      error={error}
      assistantMode={assistantMode}
      attachmentRules={attachmentRules}
      onSend={onSend}
    />
  );
}

export function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}
